#!/usr/bin/env python3
"""Attach party affiliation to Pass 2 vote ballots using the legislator roster.

Does not call OpenStates. Requires:
  1. processed/bill-votes.json (from pass2_bills.py)
  2. pass2/legislator_roster.json (from pass2_party_roster.py)

  python collectors/pass2_attach_party.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import issue_paths as ip  # noqa: E402
from pass2_party_roster import build_lookup, match_party, now  # noqa: E402

PASS2 = ip.PASS2
PROCESSED = ip.PROCESSED
ROSTER_PATH = PASS2 / "legislator_roster.json"
VOTES_PATH = PROCESSED / "bill-votes.json"
SPONSORS_PATH = PROCESSED / "bill-sponsors.json"
SUMMARY_PATH = PROCESSED / "pass2-summary.json"
GAPS_PATH = PROCESSED / "data-gaps.json"


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    if not ROSTER_PATH.exists():
        raise SystemExit(f"Missing {ROSTER_PATH}. Run pass2_party_roster.py first.")
    if not VOTES_PATH.exists():
        raise SystemExit(f"Missing {VOTES_PATH}. Run pass2_bills.py first.")

    roster = load_json(ROSTER_PATH, {})
    members = roster.get("members") or []
    global_lookup = build_lookup(members)
    by_session: dict[str, dict] = {}
    for member in members:
        by_session.setdefault(str(member.get("session")), []).append(member)
    session_lookups = {sid: build_lookup(rows) for sid, rows in by_session.items()}

    votes = load_json(VOTES_PATH, [])
    total = 0
    filled = 0
    for vote in votes:
        session = str(vote.get("session") or "")
        lookup = session_lookups.get(session) or global_lookup
        for ballot in vote.get("ballots") or []:
            total += 1
            name = ballot.get("name") or ""
            party, source, matched_as = match_party(name, lookup)
            if not party:
                party, source, matched_as = match_party(name, global_lookup)
            if party:
                ballot["party"] = party
                ballot["party_source"] = source
                ballot["party_matched_as"] = matched_as
                filled += 1
            else:
                ballot.pop("party", None)
                ballot["party_source"] = None
                ballot["party_matched_as"] = None

    save_json(VOTES_PATH, votes)

    # Also enrich NELIS person sponsors when party missing.
    sponsors = load_json(SPONSORS_PATH, [])
    sponsor_filled = 0
    for sponsor in sponsors:
        if sponsor.get("party"):
            continue
        if sponsor.get("entity_type") == "organization":
            continue
        session = str(sponsor.get("session") or "")
        lookup = session_lookups.get(session) or global_lookup
        party, source, matched_as = match_party(sponsor.get("name") or "", lookup)
        if not party:
            party, source, matched_as = match_party(sponsor.get("name") or "", global_lookup)
        if party:
            sponsor["party"] = party
            sponsor["party_source"] = source
            sponsor["party_matched_as"] = matched_as
            sponsor_filled += 1
    save_json(SPONSORS_PATH, sponsors)

    gaps = [g for g in load_json(GAPS_PATH, []) if g.get("topic") != "voter_party"]
    unmatched_names = sorted(
        {
            ballot.get("name")
            for vote in votes
            for ballot in vote.get("ballots") or []
            if ballot.get("name") and not ballot.get("party")
        }
    )
    if unmatched_names:
        gaps.append(
            {
                "topic": "voter_party",
                "session": "multi",
                "result": "partial",
                "notes": (
                    f"{len(unmatched_names)} unique voter names still lack party after "
                    f"NELIS roster (+ Ballotpedia fallback): {', '.join(unmatched_names[:20])}"
                    + ("…" if len(unmatched_names) > 20 else "")
                ),
            }
        )
    else:
        gaps.append(
            {
                "topic": "voter_party",
                "session": "all",
                "result": "complete",
                "notes": "All roll-call voter names matched to a party via legislator roster",
            }
        )
    save_json(GAPS_PATH, gaps)

    summary = load_json(SUMMARY_PATH, {})
    summary["party_enrichment"] = {
        "updated_at": now(),
        "ballot_rows": total,
        "ballot_rows_with_party": filled,
        "coverage_pct": round(100.0 * filled / total, 1) if total else 0.0,
        "sponsor_rows_filled": sponsor_filled,
        "unmatched_unique_names": unmatched_names,
        "method": "nelis_legislator_directory_plus_ballotpedia_fallback",
    }
    save_json(SUMMARY_PATH, summary)

    print(
        f"Attached party to {filled}/{total} ballot rows "
        f"({summary['party_enrichment']['coverage_pct']}%). "
        f"Sponsors filled: {sponsor_filled}. Unmatched names: {len(unmatched_names)}"
    )
    if unmatched_names:
        for name in unmatched_names[:20]:
            print(f"  unmatched: {name}")


if __name__ == "__main__":
    main()
