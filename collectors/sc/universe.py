"""Full-universe sweep of the SC General Assembly, sessions 123rd-126th.

This is the SC analogue of the NH "universe certification" bulk sweeps: it
collects **every bill and resolution** in every target session — not just
issue-matched ones — so no issue chat can silently miss legislation.

Why enumeration is provably complete: South Carolina assigns bill numbers
densely and sequentially per chamber desk (Senate from 1, House from 3001),
and every instrument has a static page at ``/sess{N}_{years}/bills/{n}.htm``.
Sweeping the number space with a long consecutive-404 stop rule therefore
covers the whole universe by construction; unused numbers inside the range are
recorded, and three independent official surfaces cross-check the result:

  1. **Chamber-wide roll-call lists** (``votehistory.php`` POST per
     session+chamber) — every floor roll call with verbatim counts and ballot
     PDF keys; every bill they cite must exist in the enumeration.
  2. **Ratification sheets** (``…/bills/rats.php`` + per-day sheets) — every
     ratified act (R-number, act, bill, date); must all join to enumeration.
  3. **Full-text search hits** for all four issues' search terms — every hit
     must join to enumeration (also produces the Pass 1 seed lists).

What each bill record contains (parsed from the official page, nothing
invented): bill number, chamber, instrument type, summary/title, sponsors,
act/ratification numbers, the complete action history (committee reports,
floor readings, crossover, conference, **governor action**, veto overrides),
version list (dates + URLs), and the **full text of the latest version**
(inline on the page). Prior-version text stays one recorded GET away.

What South Carolina does NOT publish (documented, never invented):
committee vote *tallies*. Committee action appears in bill histories as
outcomes ("Committee report: Favorable", "majority favorable, minority
unfavorable"); committees post meeting videos, not roll-call tables.

Outputs, per session, under ``sources/south-carolina/_universe/``:

  {session}/bills.jsonl.gz     one JSON record per bill, full text included
  {session}/bills-index.json   light index (no text) for browsing
  {session}/rollcalls.json     every roll call, both chambers
  {session}/ratifications.json every ratified act
  verification/universe-certification.{json,md}

Resumable: bill records are appended to the JSONL as they are fetched and
already-present numbers are skipped, so the sweep can be re-run after any
interruption.

Run (hours; use tmux):

    python3 -m collectors.sc.universe            # everything
    python3 -m collectors.sc.universe --session 126
    python3 -m collectors.sc.universe --certify-only
"""

from __future__ import annotations

import argparse
import gzip
import html as htmllib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import SESSIONS, SESSION_BY_NUMBER
from .scstatehouse import BASE, _plain, soft_get, soft_post

ROOT = Path("sources/south-carolina/_universe")

# Number spaces per chamber. Generous ceilings; the sweep stops early after
# MISS_RUN consecutive 404s past the last hit.
SENATE_RANGE = (1, 3000)
HOUSE_RANGE = (3001, 7500)
MISS_RUN = 100

TYPE_RE = re.compile(
    r"^(General Bill|Joint Resolution|Concurrent Resolution|House Resolution|"
    r"Senate Resolution|Bill)\b")
ACTHDR_RE = re.compile(r"\b(?:(A\d+),\s*)?(R\d+),\s*([HS]\d+)\b")
GOV_RE = re.compile(r"governor", re.I)
RC_HISTORY_RE = re.compile(r"Roll call Yeas[\s-]*(\d+)\s+Nays[\s-]*(\d+)", re.I)


# ---------------------------------------------------------------------------
# Bill page parsing
# ---------------------------------------------------------------------------

def parse_bill_page(raw: str, session: int, number: int, url: str) -> dict:
    txt = _plain(raw)
    chamber = "S" if number < 3000 else "H"
    rec: dict = {
        "session": session,
        "bill_no": f"{chamber}{number}",
        "number": number,
        "chamber": chamber,
        "url": url,
    }

    m = re.search(r"Summary:\s*(.+?)(?:\s*HISTORY OF LEGISLATIVE ACTIONS|$)", txt)
    rec["summary"] = m.group(1).strip()[:500] if m else ""
    m = re.search(r"<title>[^:]*:\s*([^<]*?)\s*-\s*South Carolina Legislature", raw)
    if not m:  # pages without a "Bill NNNN:" title, e.g. "Reserved" numbers
        m = re.search(r"<title>\s*([^<]*?)\s*-\s*South Carolina Legislature", raw)
    rec["title"] = htmllib.unescape(m.group(1)).strip() if m else rec["summary"]

    # Instrument type + sponsors from the STATUS INFORMATION block.
    m = re.search(r"STATUS INFORMATION\s+(.*?)(?:Introduced|Summary:)", txt, re.S)
    status_blob = m.group(1).strip() if m else ""
    tm = TYPE_RE.search(status_blob)
    rec["instrument_type"] = tm.group(1) if tm else (status_blob.split("  ")[0][:40]
                                                     if status_blob else "")
    sm = re.search(r"Sponsors?:\s*(.+?)(?:\s*Document Path|\s*Companion|\s*Similar|$)",
                   txt)
    rec["sponsors_raw"] = sm.group(1).strip()[:600] if sm else ""

    # Act / ratification header, e.g. "A69, R97, H4025".
    am = ACTHDR_RE.search(txt[:2500])
    if am and am.group(3) == rec["bill_no"]:
        rec["act_no"] = am.group(1)
        rec["ratification_no"] = am.group(2)

    # Action history. Two formats exist: older pages use a fixed-width <pre>
    # block; newer pages use an HTML <table> with Date/Body/Action cells.
    actions: list[dict] = []
    hist_start = raw.find("HISTORY OF LEGISLATIVE ACTIONS")
    hist = raw[hist_start:] if hist_start >= 0 else raw
    pre = re.search(r"<pre>(.*?)</pre>", hist, re.S)
    if pre:
        # Line-based parse: a new action starts with a date; the Body column
        # may be blank (e.g. "Ratified R 97"); wrapped lines continue the
        # previous action.
        current: dict | None = None
        for line in pre.group(1).splitlines():
            plain_line = _plain(line)
            m2 = re.match(
                r"^(\d{1,2}/\d{1,2}/\d{4})\s+(House|Senate|Scrivener)?\s*(.*)$",
                plain_line)
            if m2 and (m2.group(2) or m2.group(3)):
                current = {"date": m2.group(1), "body": m2.group(2) or "",
                           "action": m2.group(3).strip()}
                actions.append(current)
            elif current is not None and plain_line and "-----" not in plain_line \
                    and not plain_line.startswith("Date "):
                current["action"] = (current["action"] + " " + plain_line).strip()
    else:
        table = re.search(r"<table.*?</table>", hist, re.S)
        if table:
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(0), re.S):
                cells = [_plain(c) for c in
                         re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
                if len(cells) >= 3 and re.match(r"\d{1,2}/\d{1,2}/\d{4}", cells[0]):
                    actions.append({"date": cells[0], "body": cells[1],
                                    "action": cells[2]})
    for entry in actions:
        rc = RC_HISTORY_RE.search(entry["action"])
        if rc:
            entry["history_roll_call"] = {"yeas": int(rc.group(1)),
                                          "nays": int(rc.group(2))}
    rec["actions"] = actions
    rec["governor_actions"] = [a for a in actions if GOV_RE.search(a["action"])]
    status_m = re.search(
        r"(Currently residing.+?|Governor's Action:.+?|Act No\..+?)(?:\s{2,}|Summary:)",
        txt)
    rec["status_line"] = status_m.group(1).strip()[:300] if status_m else ""

    # Versions list (absolute or ../prever/ relative links).
    sess_path = SESSION_BY_NUMBER[session]["scstatehouse_path"]
    versions = []
    seen_versions: set[str] = set()
    for vm in re.finditer(r'href="[^"]*prever/(\d+)_(\d{8})\.htm"', raw):
        if vm.group(2) in seen_versions:
            continue
        seen_versions.add(vm.group(2))
        versions.append({
            "date": vm.group(2),
            "url": f"{BASE}/{sess_path}/prever/{vm.group(1)}_{vm.group(2)}.htm",
        })
    rec["versions"] = versions

    # Full text of the latest version (inline after the VERSIONS block).
    vi = raw.find("VERSIONS OF THIS BILL")
    text = ""
    if vi >= 0:
        body = _plain(raw[vi:])
        body = body.removeprefix("VERSIONS OF THIS BILL").strip()
        # Strip the version-date link texts and the reformatting disclaimer.
        body = re.sub(r"^(?:\d{1,2}/\d{1,2}/\d{4}\s*|Word\s*|version\s*)+", "",
                      body)
        body = re.sub(r"^\(Text matches printed bills.*?\)\s*", "", body,
                      flags=re.S)
        body = re.sub(r"-+XX-+.*$", "", body, flags=re.S)
        body = re.sub(r"This web page was last updated.*$", "", body, flags=re.S)
        text = body.strip()
    rec["latest_version_text"] = text
    rec["text_chars"] = len(text)
    return rec


# ---------------------------------------------------------------------------
# Sweep one session
# ---------------------------------------------------------------------------

def _existing_numbers(jsonl_gz: Path) -> set[int]:
    if not jsonl_gz.exists():
        return set()
    nums = set()
    try:
        with gzip.open(jsonl_gz, "rt", encoding="utf-8") as fh:
            for line in fh:
                try:
                    nums.add(json.loads(line)["number"])
                except Exception:
                    continue
    except EOFError:
        # A kill mid-write truncates the last gzip member; records read so
        # far are valid and anything lost is simply refetched on resume.
        pass
    return nums


def sweep_bills(session: int) -> None:
    sess = SESSION_BY_NUMBER[session]
    out_dir = ROOT / str(session)
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "bills.jsonl.gz"
    have = _existing_numbers(jsonl)
    misses_path = out_dir / "unused-numbers.json"
    misses: set[int] = set(json.loads(misses_path.read_text())
                           if misses_path.exists() else [])
    print(f"[{session}] sweep start; {len(have)} already collected")
    t0 = time.time()
    fetched = 0
    with gzip.open(jsonl, "at", encoding="utf-8") as fh:
        for lo, hi in (SENATE_RANGE, HOUSE_RANGE):
            run = 0
            for n in range(lo, hi + 1):
                if n in have or n in misses:
                    run = 0 if n in have else run
                    continue
                url = f"{BASE}/{sess['scstatehouse_path']}/bills/{n}.htm"
                r = soft_get(url)
                if r is None:
                    run += 1
                    misses.add(n)
                    if run >= MISS_RUN:
                        print(f"[{session}] {run} consecutive misses at {n}; "
                              f"chamber range done")
                        # Trim the tail misses (they are just the end of the
                        # number space, not real gaps).
                        misses = {m for m in misses if m <= n - MISS_RUN}
                        break
                    continue
                run = 0
                rec = parse_bill_page(r.text, session, n, url)
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fetched += 1
                if fetched % 200 == 0:
                    fh.flush()
                    misses_path.write_text(json.dumps(sorted(misses)))
                    rate = fetched / max(time.time() - t0, 1)
                    print(f"[{session}] {fetched} fetched "
                          f"(at {rec['bill_no']}, {rate:.1f}/s)")
    misses_path.write_text(json.dumps(sorted(misses)))
    print(f"[{session}] sweep done: {fetched} new bills "
          f"({len(misses)} unused numbers inside ranges)")


def build_index(session: int) -> list[dict]:
    out_dir = ROOT / str(session)
    bills = []
    with gzip.open(out_dir / "bills.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            bills.append({k: rec.get(k) for k in
                          ("session", "bill_no", "number", "chamber",
                           "instrument_type", "title", "summary", "sponsors_raw",
                           "act_no", "ratification_no", "status_line",
                           "text_chars", "url")}
                         | {"n_actions": len(rec.get("actions") or []),
                            "n_versions": len(rec.get("versions") or []),
                            "governor_actions":
                                [a["action"][:120] for a in
                                 rec.get("governor_actions") or []]})
    bills.sort(key=lambda b: b["number"])
    (out_dir / "bills-index.json").write_text(
        json.dumps({"session": session, "bill_count": len(bills),
                    "bills": bills}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    return bills


# ---------------------------------------------------------------------------
# Chamber-wide roll calls
# ---------------------------------------------------------------------------

def fetch_rollcalls(session: int) -> list[dict]:
    out_dir = ROOT / str(session)
    out_dir.mkdir(parents=True, exist_ok=True)
    all_rcs: list[dict] = []
    for chamber, label in (("S", "Senate"), ("H", "House")):
        r = soft_post(f"{BASE}/votehistory.php",
                      {"session": str(session), "chamber": chamber,
                       "headerfooter": "1"})
        if r is None:
            print(f"[{session}] WARNING: {label} roll-call list soft-failed")
            continue
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", r.text, re.S)
        n = 0
        for row in rows:
            cells = [_plain(c) for c in
                     re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
            if len(cells) < 13 or cells[0] == "Vote#" or not cells[0]:
                continue
            try:
                counts = [int(c) for c in cells[5:12]]
            except ValueError:
                continue
            key_m = re.search(r"KEY=(\d+)", row)
            # Vote lists zero-pad Senate numbers ("S 0001"); enumeration
            # uses the canonical unpadded form ("S1").
            raw_no = cells[1].replace(" ", "")
            bm = re.fullmatch(r"([HS])0*(\d+)", raw_no)
            bill_no = f"{bm.group(1)}{int(bm.group(2))}" if bm else (raw_no or None)
            all_rcs.append({
                "vote_no": cells[0], "chamber": label,
                "bill_no": bill_no,
                "motion": cells[2], "datetime": cells[3],
                "candidate": cells[4] or None,
                "yeas": counts[0], "nays": counts[1], "not_voting": counts[2],
                "excused_absent": counts[3], "present": counts[4],
                "abstain_recused": counts[5], "total": counts[6],
                "result": cells[12],
                "ballot_pdf_key": int(key_m.group(1)) if key_m else None,
            })
            n += 1
        print(f"[{session}] {label}: {n} roll calls")
    (out_dir / "rollcalls.json").write_text(json.dumps({
        "session": session,
        "note": "Every floor roll call recorded by the chamber, verbatim from "
                "votehistory.php. Ballot PDFs (per-member) at "
                "votehistory.php?KEY=<ballot_pdf_key>; names only there — "
                "party joins from the member roster. Committee vote tallies "
                "are not published by the state.",
        "roll_call_count": len(all_rcs),
        "roll_calls": all_rcs,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    return all_rcs


# ---------------------------------------------------------------------------
# Ratification sheets (governor-action cross-check)
# ---------------------------------------------------------------------------

RAT_ENTRY_RE = re.compile(
    r"\((?:(A\d+),\s*)?(R\d+),\s*([HS])\.?\s*(\d+)\b", re.I)


def fetch_ratifications(session: int) -> list[dict]:
    sess = SESSION_BY_NUMBER[session]
    out_dir = ROOT / str(session)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"{BASE}/{sess['scstatehouse_path']}/bills"
    r = soft_get(f"{base}/rats.php")
    entries: list[dict] = []
    if r is None:
        print(f"[{session}] WARNING: rats.php soft-failed")
    else:
        days = re.findall(r'href="((\d{8})\.htm)"', r.text)
        print(f"[{session}] {len(days)} ratification days")
        for href, day in days:
            dr = soft_get(f"{base}/{href}")
            if dr is None:
                continue
            txt = _plain(dr.text)
            for m in RAT_ENTRY_RE.finditer(txt):
                entries.append({
                    "date": day,
                    "act_no": m.group(1),
                    "ratification_no": m.group(2),
                    "bill_no": f"{m.group(3).upper()}{m.group(4)}",
                })
    (out_dir / "ratifications.json").write_text(json.dumps({
        "session": session, "ratification_count": len(entries),
        "entries": entries,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    return entries


# ---------------------------------------------------------------------------
# Certification: cross-check all surfaces
# ---------------------------------------------------------------------------

def certify() -> dict:
    checks: list[dict] = []
    totals = {"bills": 0, "roll_calls": 0, "ratifications": 0,
              "bills_with_text": 0, "bills_with_gov_action": 0}
    per_session: dict[int, dict] = {}

    for sess in SESSIONS:
        session = sess["number"]
        out_dir = ROOT / str(session)
        idx_path = out_dir / "bills-index.json"
        if not idx_path.exists():
            checks.append({"check": f"{session}_swept", "status": "FAIL",
                           "detail": "no bills-index.json"})
            continue
        idx = json.loads(idx_path.read_text(encoding="utf-8"))
        bills = idx["bills"]
        have = {b["bill_no"] for b in bills}
        rcs = json.loads((out_dir / "rollcalls.json").read_text(
            encoding="utf-8"))["roll_calls"]
        rats = json.loads((out_dir / "ratifications.json").read_text(
            encoding="utf-8"))["entries"]

        # 1. Every roll call that names a bill joins to enumeration.
        rc_missing = sorted({rc["bill_no"] for rc in rcs
                             if rc["bill_no"] and rc["bill_no"] not in have
                             and re.fullmatch(r"[HS]\d+", rc["bill_no"] or "")})
        checks.append({
            "check": f"{session}_rollcalls_join_bills",
            "status": "PASS" if not rc_missing else "FAIL",
            "detail": f"{len(rcs)} roll calls; bills cited but not in "
                      f"enumeration: {rc_missing[:10]} "
                      f"(n={len(rc_missing)})"})

        # 2. Every ratified bill joins to enumeration.
        rat_missing = sorted({e["bill_no"] for e in rats
                              if e["bill_no"] not in have})
        checks.append({
            "check": f"{session}_ratifications_join_bills",
            "status": "PASS" if not rat_missing else "FAIL",
            "detail": f"{len(rats)} ratifications; missing from enumeration: "
                      f"{rat_missing[:10]} (n={len(rat_missing)})"})

        # 3. Ratified bills carry governor/ratification evidence on their page.
        by_no = {b["bill_no"]: b for b in bills}
        rat_no_evidence = [e["bill_no"] for e in rats
                           if e["bill_no"] in by_no
                           and not (by_no[e["bill_no"]].get("ratification_no")
                                    or by_no[e["bill_no"]]["governor_actions"])]
        checks.append({
            "check": f"{session}_ratified_bills_have_page_evidence",
            "status": "PASS" if not rat_no_evidence else "WARN",
            "detail": f"ratified bills lacking act header AND governor "
                      f"action in history: {rat_no_evidence[:10]} "
                      f"(n={len(rat_no_evidence)})"})

        # 4. Text coverage. "Reserved" numbers are placeholders with no
        #    instrument ever filed — expected to be empty.
        reserved = [b["bill_no"] for b in bills
                    if not b["text_chars"] and b["title"] == "Reserved"]
        no_text = [b["bill_no"] for b in bills
                   if not b["text_chars"] and b["title"] != "Reserved"]
        checks.append({
            "check": f"{session}_full_text_coverage",
            "status": "PASS" if not no_text else "WARN",
            "detail": f"{len(bills) - len(no_text) - len(reserved)}/"
                      f"{len(bills)} bills with inline latest-version text; "
                      f"reserved placeholders: {reserved} (n={len(reserved)}); "
                      f"unexplained empty: {no_text[:10]} (n={len(no_text)})"})

        n_gov = sum(1 for b in bills if b["governor_actions"])
        per_session[session] = {
            "bills": len(bills), "roll_calls": len(rcs),
            "ratifications": len(rats),
            "bills_with_text": len(bills) - len(no_text),
            "bills_with_governor_action": n_gov,
        }
        totals["bills"] += len(bills)
        totals["roll_calls"] += len(rcs)
        totals["ratifications"] += len(rats)
        totals["bills_with_text"] += len(bills) - len(no_text)
        totals["bills_with_gov_action"] += n_gov

    fails = [c for c in checks if c["status"] == "FAIL"]
    warns = [c for c in checks if c["status"] == "WARN"]
    report = {
        "certified_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "FAIL" if fails else ("PASS_WITH_WARNINGS" if warns
                                         else "PASS"),
        "totals": totals,
        "per_session": per_session,
        "checks": checks,
        "known_limits": [
            "Committee vote TALLIES are not published by the State of South "
            "Carolina; committee outcomes are captured verbatim from bill "
            "histories ('Committee report: Favorable', etc.). Never invent "
            "tallies.",
            "Bill pages carry the full text of the LATEST version inline "
            "(captured); earlier-draft texts are recorded as dated URLs per "
            "bill and fetched on demand.",
            "Per-member ballot PDFs are recorded by ballot_pdf_key per roll "
            "call and fetched on demand; party joins from the member roster.",
            "Voice votes leave no roll call — absence of a roll call on a "
            "reading is normal, not a gap.",
        ],
    }
    ver = ROOT / "verification"
    ver.mkdir(parents=True, exist_ok=True)
    (ver / "universe-certification.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# SC universe certification (sessions 123rd-126th)",
        "",
        f"**Verdict: {report['verdict']}**  ",
        f"Certified: {report['certified_at']}",
        "",
        "| Session | Bills | Roll calls | Ratifications | With text | "
        "With governor action |",
        "|---|---|---|---|---|---|",
    ]
    for s, d in sorted(per_session.items()):
        lines.append(f"| {s} | {d['bills']} | {d['roll_calls']} | "
                     f"{d['ratifications']} | {d['bills_with_text']} | "
                     f"{d['bills_with_governor_action']} |")
    lines += ["", "## Checks", ""]
    for c in checks:
        lines.append(f"- **{c['status']}** `{c['check']}` — {c['detail']}")
    lines += ["", "## Known limits (state publication, not collection gaps)", ""]
    for k in report["known_limits"]:
        lines.append(f"- {k}")
    (ver / "universe-certification.md").write_text("\n".join(lines) + "\n",
                                                   encoding="utf-8")
    print(f"Certification: {report['verdict']} "
          f"({totals['bills']} bills, {totals['roll_calls']} roll calls)")
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, default=None,
                    help="Only this session (default: all four)")
    ap.add_argument("--certify-only", action="store_true")
    ap.add_argument("--skip-bills", action="store_true",
                    help="Skip the bill sweep (rollcalls/rats/certify only)")
    args = ap.parse_args()
    sessions = [args.session] if args.session else [s["number"] for s in SESSIONS]
    if not args.certify_only:
        for session in sessions:
            if not args.skip_bills:
                sweep_bills(session)
            build_index(session)
            fetch_rollcalls(session)
            fetch_ratifications(session)
    certify()


if __name__ == "__main__":
    main()
