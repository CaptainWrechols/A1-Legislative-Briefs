"""Build one SC issue's complete collection artifacts from the universe sweep.

Prerequisite: ``python3 -m collectors.sc.universe`` has populated
``sources/south-carolina/_universe/`` (all bills + roll calls + ratifications
for the 123rd-126th sessions).

For the issue selected by ``ISSUE_CONFIG`` this runner produces the full
artifact set that ``collectors.sc.verify_completeness`` (full mode) gates on:

  sources/south-carolina/{slug}/pass1/bills.json        discovery (keep ALL hits)
  sources/south-carolina/{slug}/processed/bills-core.json  full records (no text)
  sources/south-carolina/{slug}/processed/bill-votes.json  roll calls per bill
  sources/south-carolina/{slug}/data-gaps.json           every gap, explicit
  working/south-carolina/{slug}/provisos/{year}/…        Part IB per enacted cycle
  working/south-carolina/{slug}/proviso-*.json|md        latest enacted cycle

Discovery = union of two routes, per the dual-source rule:

  1. **Server-side full-text search** (query.php) for every ``search_terms``
     entry in every session — this searches the *full bill text*, so bills
     whose titles hide their relevance are still caught.
  2. **Local title/summary scan of the entire universe** for the same terms —
     catches instruments the search engine tokenises differently.

Pass 1 rule: every hit from either route is kept; ``relevance_terms`` only set
a review flag. Votes are joined verbatim from the chamber-wide roll-call
lists. Nothing is invented.

Run (after the universe sweep):

    ISSUE_CONFIG=config/issues/south-carolina-<slug>.yaml \\
        python3 -m collectors.sc.collect_issue
"""

from __future__ import annotations

import gzip
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import issue_paths as ip  # noqa: E402

from . import BUDGET_CYCLES, SESSIONS  # noqa: E402
from . import proviso_fetch, proviso_sections, scstatehouse  # noqa: E402

UNIVERSE = Path("sources/south-carolina/_universe")
SEARCH_CACHE = UNIVERSE / "search-cache"


def _cached_search(term: str, session: int) -> dict | None:
    """fulltext_search with an on-disk cache keyed by (session, term).

    Searches are issue-independent, so reruns and overlapping term lists skip
    completed queries entirely.
    """
    SEARCH_CACHE.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
    path = SEARCH_CACHE / f"{session}-{safe}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    res = scstatehouse.fulltext_search(term, session, numrows=100)
    if res is not None:
        path.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return res


def _load_universe_bills(session: int) -> dict[str, dict]:
    bills: dict[str, dict] = {}
    path = UNIVERSE / str(session) / "bills.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            bills[rec["bill_no"]] = rec
    return bills


def _load_rollcalls(session: int) -> list[dict]:
    path = UNIVERSE / str(session) / "rollcalls.json"
    return json.loads(path.read_text(encoding="utf-8"))["roll_calls"]


def discover(cfg: dict) -> tuple[list[dict], list[dict]]:
    """Return (pass1 bills, gaps) for the issue across all sessions."""
    terms = [str(t) for t in cfg.get("search_terms") or []]
    rel = [str(t).lower() for t in cfg.get("relevance_terms") or terms]
    gaps: list[dict] = []
    found: dict[tuple[int, str], dict] = {}

    for sess in SESSIONS:
        session = sess["number"]
        universe = _load_universe_bills(session)

        # Route 1: server-side full-text search (full bill language).
        for term in terms:
            res = _cached_search(term, session)
            if res is None:
                gaps.append({"gap": "search_soft_fail", "session": session,
                             "term": term,
                             "detail": "query.php soft-failed; rerun to close"})
                continue
            for hit in res["hits"]:
                key = (session, hit["bill_no"])
                rec = found.get(key)
                if rec is None:
                    u = universe.get(hit["bill_no"])
                    if u is None:
                        # Search cites a bill enumeration lacks -> serious.
                        gaps.append({"gap": "search_hit_not_in_universe",
                                     "session": session,
                                     "bill_no": hit["bill_no"], "term": term})
                        continue
                    rec = found[key] = {
                        "session": session,
                        "bill_no": u["bill_no"],
                        "title": u["title"],
                        "summary": u["summary"],
                        "instrument_type": u["instrument_type"],
                        "sponsors_raw": u["sponsors_raw"],
                        "status_line": u["status_line"],
                        "act_no": u.get("act_no"),
                        "ratification_no": u.get("ratification_no"),
                        "url": u["url"],
                        "sources": ["scstatehouse_fulltext_search"],
                        "found_by_terms": [],
                    }
                if term not in rec["found_by_terms"]:
                    rec["found_by_terms"].append(term)
            print(f"  [{session}] '{term}': {res['total_matches']} matches",
                  flush=True)

        # Routes 2+3: local scans over the whole universe — titles/summaries
        # AND the full latest-version text held on disk. The local full-text
        # scan is the fast, reproducible twin of the server search (which
        # additionally covers earlier versions and acts as the cross-check).
        lowered = [t.lower() for t in terms]
        for bill_no, u in universe.items():
            blob = f"{u['title']} {u['summary']}".lower()
            text_blob = (u.get("latest_version_text") or "").lower()
            matched = [t for t, tl in zip(terms, lowered)
                       if tl in blob or tl in text_blob]
            if not matched:
                continue
            key = (session, bill_no)
            rec = found.get(key)
            if rec is None:
                rec = found[key] = {
                    "session": session,
                    "bill_no": u["bill_no"],
                    "title": u["title"],
                    "summary": u["summary"],
                    "instrument_type": u["instrument_type"],
                    "sponsors_raw": u["sponsors_raw"],
                    "status_line": u["status_line"],
                    "act_no": u.get("act_no"),
                    "ratification_no": u.get("ratification_no"),
                    "url": u["url"],
                    "sources": [],
                    "found_by_terms": [],
                }
            if "universe_local_scan" not in rec["sources"]:
                rec["sources"].append("universe_local_scan")
            for t in matched:
                if t not in rec["found_by_terms"]:
                    rec["found_by_terms"].append(t)

    bills = sorted(found.values(),
                   key=lambda b: (b["session"], b["bill_no"][0],
                                  int(b["bill_no"][1:])))
    for b in bills:
        blob = f"{b['title']} {b['summary']}".lower()
        b["relevance_flag"] = any(t in blob for t in rel)
    return bills, gaps


def build_votes(bills: list[dict]) -> dict:
    by_session: dict[int, list[dict]] = {}
    rows = []
    for b in bills:
        session = b["session"]
        if session not in by_session:
            by_session[session] = _load_rollcalls(session)
        rcs = [rc for rc in by_session[session]
               if rc["bill_no"] == b["bill_no"]]
        rows.append({
            "session": session,
            "bill_no": b["bill_no"],
            "roll_call_count": len(rcs),
            "roll_calls": rcs,
        })
    return {
        "note": "Roll calls verbatim from the chamber-wide vote lists "
                "(votehistory.php). Zero roll calls is a real answer (voice "
                "votes / died in committee), never invented. Per-member "
                "ballots via votehistory.php?KEY=<ballot_pdf_key>; party "
                "joins from the member roster.",
        "bills": rows,
    }


def build_core(bills: list[dict]) -> dict:
    by_session: dict[int, dict[str, dict]] = {}
    out = []
    for b in bills:
        session = b["session"]
        if session not in by_session:
            by_session[session] = _load_universe_bills(session)
        u = by_session[session][b["bill_no"]]
        core = {k: u.get(k) for k in
                ("session", "bill_no", "number", "chamber", "instrument_type",
                 "title", "summary", "sponsors_raw", "act_no",
                 "ratification_no", "status_line", "actions",
                 "governor_actions", "versions", "text_chars", "url")}
        core["found_by_terms"] = b["found_by_terms"]
        core["relevance_flag"] = b["relevance_flag"]
        core["sources"] = b["sources"]
        out.append(core)
    return {"note": "Full per-bill records from the universe sweep "
                    "(sources/south-carolina/_universe); latest-version full "
                    "text lives in the universe JSONL, keyed by session + "
                    "bill_no.",
            "bills": out}


def build_provisos(cfg: dict) -> None:
    terms = [str(t) for t in (cfg.get("relevance_terms") or [])]
    for prop in cfg.get("constituent_proposals") or []:
        terms += [str(t) for t in (prop.get("match_terms") or [])]
    omni = (cfg.get("omnibus_bills") or [{}])[0]
    cache = UNIVERSE / "part1b-cache"
    shared_root = UNIVERSE / "part1b"
    latest_enacted = None
    for cyc in omni.get("cycles") or []:
        if not cyc.get("enacted"):
            continue
        year = cyc["year"]
        doc = proviso_fetch.fetch_part1b(year, cache_dir=cache)
        if doc is None:
            print(f"  provisos {year}: FETCH FAILED (record a gap)")
            continue
        provisos = proviso_sections.extract_provisos(doc["html"])
        relevant = proviso_sections.match_provisos(provisos, terms)
        meta = {k: doc[k] for k in ("fiscal_year", "year", "bill_no",
                                    "version", "version_label", "enacted",
                                    "source_url")}
        # Full proviso set is issue-independent: write it ONCE under the
        # shared universe tree; per issue keep the relevant subset plus a
        # pointer record (so every issue directory is self-describing).
        shared = shared_root / str(year)
        if not (shared / "proviso-sections.json").exists():
            proviso_sections.write_outputs(provisos, [], shared, dict(meta))
            (shared / "proviso-relevant.json").unlink(missing_ok=True)
        out_dir = ip.WORKING / "provisos" / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "proviso-sections.json").write_text(json.dumps({
            **meta,
            "proviso_count": len(provisos),
            "full_sections_at": str(shared / "proviso-sections.json"),
            "note": "Full proviso set stored once, shared across issues; "
                    "this issue's matched subset is proviso-relevant.json.",
        }, indent=1), encoding="utf-8")
        (out_dir / "proviso-relevant.json").write_text(json.dumps({
            **meta,
            "issue_slug": ip.ISSUE_SLUG,
            "matched_with": "relevance_terms + constituent_proposals.match_terms",
            "relevant_proviso_count": len(relevant),
            "provisos": relevant,
        }, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"  provisos {year}: {len(provisos)} total, "
              f"{len(relevant)} relevant", flush=True)
        latest_enacted = (provisos, relevant, meta)
    if latest_enacted:
        provisos, relevant, meta = latest_enacted
        proviso_sections.write_outputs(provisos, relevant, ip.WORKING, {
            **meta, "issue_slug": ip.ISSUE_SLUG,
            "matched_with": "relevance_terms + constituent_proposals.match_terms",
        })


def main() -> None:
    cfg = ip.load_config()
    print(f"Collecting issue: {ip.ISSUE_SLUG}")

    bills, gaps = discover(cfg)
    print(f"  pass1: {len(bills)} bills discovered")
    ip.PASS1.mkdir(parents=True, exist_ok=True)
    (ip.PASS1 / "bills.json").write_text(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "issue": cfg["issue_id"],
        "note": "Pass 1 keep-all discovery: union of scstatehouse full-text "
                "search and universe title/summary scan. relevance_flag is a "
                "review flag only; nothing was dropped.",
        "bill_count": len(bills),
        "bills": bills,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    ip.PROCESSED.mkdir(parents=True, exist_ok=True)
    core = build_core(bills)
    (ip.PROCESSED / "bills-core.json").write_text(
        json.dumps(core, indent=1, ensure_ascii=False), encoding="utf-8")
    votes = build_votes(bills)
    n_rc = sum(r["roll_call_count"] for r in votes["bills"])
    print(f"  votes: {n_rc} roll calls across {len(votes['bills'])} bills")
    (ip.PROCESSED / "bill-votes.json").write_text(
        json.dumps(votes, indent=1, ensure_ascii=False), encoding="utf-8")

    # Explicit gaps: the optional external mirror is not on disk.
    from . import openstates_bulk
    if not openstates_bulk.available():
        gaps.append({
            "gap": "openstates_bulk_not_downloaded",
            "sessions": [s["number"] for s in SESSIONS],
            "detail": "Optional external cross-check mirror (OpenStates bulk "
                      "CSVs) not on disk; completeness is certified from "
                      "official surfaces (enumeration + chamber vote lists + "
                      "ratification sheets + full-text search joins). To add "
                      "the mirror: download session CSVs from "
                      "open.pluralpolicy.com/data/session-csv into "
                      "sources/south-carolina/_bulk/openstates/.",
        })
    (ip.SOURCES / "data-gaps.json").write_text(
        json.dumps({"gaps": gaps}, indent=1), encoding="utf-8")

    build_provisos(cfg)
    print(f"Done: {ip.SOURCES}")


if __name__ == "__main__":
    main()
