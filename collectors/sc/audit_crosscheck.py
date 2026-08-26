"""Independent audit of the SC universe data via endpoints NOT used to build it.

The universe was built from bill-page enumeration + chamber-wide vote lists +
ratification sheets. This audit re-derives facts from two *different* official
endpoints and reconciles:

1. **Per-bill vote-history endpoint** (``votehistory.php?type=BILL&…``) — for
   a random sample of bills per session (bills with roll calls and bills
   without), the roll calls returned by the per-bill endpoint must match the
   chamber-wide lists exactly (vote number, yeas, nays, result). A bill with
   no roll calls must come back empty from both.
2. **Official Act Lists** (``listofacts.php?Y=<year>``) — every act listed for
   2019-2026 must join to an enumerated bill that carries ratification/act
   evidence on its own page.

Output: sources/south-carolina/_universe/verification/audit-crosscheck.{json,md}

Run:  python3 -m collectors.sc.audit_crosscheck [--sample-per-session 20]
"""

from __future__ import annotations

import argparse
import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

from . import SESSIONS
from .scstatehouse import BASE, _plain, soft_get, vote_history

UNIVERSE = Path("sources/south-carolina/_universe")

# listofacts rows link the act's bill: billsearch.php?billnumbers=N&session=S
_ACT_ROW_RE = re.compile(
    r'href="/billsearch\.php\?billnumbers=(\d+)&(?:amp;)?session=(\d+)&(?:amp;)?summary=B"[^>]*>(\d+)<')


def audit_votes(sample_per_session: int, rng: random.Random) -> list[dict]:
    checks: list[dict] = []
    for sess in SESSIONS:
        session = sess["number"]
        rcs = json.loads((UNIVERSE / str(session) / "rollcalls.json")
                         .read_text(encoding="utf-8"))["roll_calls"]
        idx = json.loads((UNIVERSE / str(session) / "bills-index.json")
                         .read_text(encoding="utf-8"))["bills"]
        by_bill: dict[str, list[dict]] = {}
        for rc in rcs:
            if rc["bill_no"]:
                by_bill.setdefault(rc["bill_no"], []).append(rc)
        with_votes = sorted(by_bill)
        without_votes = [b["bill_no"] for b in idx
                         if b["bill_no"] not in by_bill
                         and b["title"] != "Reserved"]
        n_with = min(sample_per_session * 3 // 5, len(with_votes))
        n_without = min(sample_per_session - n_with, len(without_votes))
        sample = (rng.sample(with_votes, n_with)
                  + rng.sample(without_votes, n_without))
        mismatches: list[dict] = []
        for bill_no in sample:
            per_bill = vote_history(session, bill_no[1:])
            if per_bill is None:
                mismatches.append({"bill": bill_no, "problem": "fetch_failed"})
                continue
            a = sorted((rc["vote_no"], rc["yeas"], rc["nays"], rc["result"])
                       for rc in per_bill)
            b = sorted((rc["vote_no"], rc["yeas"], rc["nays"], rc["result"])
                       for rc in by_bill.get(bill_no, []))
            if a != b:
                mismatches.append({"bill": bill_no,
                                   "per_bill_endpoint": a, "chamber_list": b})
        checks.append({
            "check": f"{session}_per_bill_vote_endpoint_sample",
            "status": "PASS" if not mismatches else "FAIL",
            "detail": f"sampled {len(sample)} bills ({n_with} with roll "
                      f"calls, {n_without} without); mismatches="
                      f"{mismatches[:3]} (n={len(mismatches)})",
        })
        print(checks[-1]["status"], checks[-1]["check"], "-",
              checks[-1]["detail"][:120], flush=True)
    return checks


def audit_acts() -> list[dict]:
    checks: list[dict] = []
    by_session_bills: dict[int, dict[str, dict]] = {}
    for sess in SESSIONS:
        idx = json.loads((UNIVERSE / str(sess["number"]) / "bills-index.json")
                         .read_text(encoding="utf-8"))["bills"]
        by_session_bills[sess["number"]] = {b["bill_no"]: b for b in idx}

    for year in range(2019, 2027):
        r = soft_get(f"{BASE}/listofacts.php?Y={year}")
        if r is None:
            checks.append({"check": f"acts_{year}", "status": "FAIL",
                           "detail": "listofacts.php soft-failed"})
            continue
        rows = _ACT_ROW_RE.findall(r.text)
        missing, no_evidence = [], []
        for numstr, session_str, act_no in rows:
            session = int(session_str)
            if session not in by_session_bills:
                continue  # pre-2019 acts listed on overlap pages
            number = int(numstr)
            bill_no = f"{'S' if number < 3000 else 'H'}{number}"
            b = by_session_bills[session].get(bill_no)
            if b is None:
                missing.append(f"{session}:{bill_no} (Act {act_no})")
            elif not (b.get("ratification_no") or b.get("act_no")
                      or b["governor_actions"]):
                no_evidence.append(f"{session}:{bill_no} (Act {act_no})")
        status = "PASS" if not missing and not no_evidence else "FAIL"
        checks.append({
            "check": f"acts_{year}_join_universe",
            "status": status,
            "detail": f"{len(rows)} act rows; not in enumeration: "
                      f"{missing[:5]} (n={len(missing)}); no page evidence: "
                      f"{no_evidence[:5]} (n={len(no_evidence)})",
        })
        print(status, checks[-1]["check"], "-", checks[-1]["detail"][:120],
              flush=True)
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-per-session", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260826)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    checks = audit_votes(args.sample_per_session, rng) + audit_acts()
    fails = [c for c in checks if c["status"] == "FAIL"]
    report = {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "verdict": "FAIL" if fails else "PASS",
        "seed": args.seed,
        "note": "Audit endpoints (per-bill vote history, yearly Act Lists) "
                "were NOT used to build the universe; agreement is an "
                "independent confirmation.",
        "checks": checks,
    }
    ver = UNIVERSE / "verification"
    ver.mkdir(parents=True, exist_ok=True)
    (ver / "audit-crosscheck.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# SC universe audit — independent endpoint reconciliation",
        "",
        f"**Verdict: {report['verdict']}**  ",
        f"Audited: {report['audited_at']} (sample seed {args.seed})",
        "",
        report["note"],
        "",
        "## Checks",
        "",
    ]
    for c in checks:
        lines.append(f"- **{c['status']}** `{c['check']}` — {c['detail']}")
    (ver / "audit-crosscheck.md").write_text("\n".join(lines) + "\n",
                                             encoding="utf-8")
    print(f"Audit verdict: {report['verdict']}")


if __name__ == "__main__":
    main()
