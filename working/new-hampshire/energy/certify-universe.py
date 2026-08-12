#!/usr/bin/env python3
"""Certify the energy set against the complete 2020-2024 bill universe.

The OpenStates bulk CSVs (sources/new-hampshire/_bulk/openstates/{year}/) are
a full mirror of the official GenCourt docket - every bill filed in each
session. This script proves the collected set left nothing out:

1. UNIVERSE SWEEP - scans EVERY bill title in all five sessions against a
   deliberately over-broad energy vocabulary (much wider than the issue's
   search terms) and lists any bill that matches but is NOT in the collected
   set, for human review. An empty (or fully-dispositioned) review list is
   the certification.
2. SET CROSS-CHECK - every collected 2020-2024 bill (including any manual
   supplement) must exist in the universe; anything else would mean a bad
   bill number.
3. VOTE CROSS-CHECK - for every collected 2020-2024 bill, compares the
   authoritative SQL roll-call count with the bulk votes.csv count and lists
   mismatches (bulk votes are a mirror; SQL remains authoritative).

Writes working/new-hampshire/energy/certification-report.json
plus a human-readable .md (via annotate-certification.py). Run from repo
root after collection. Adapted from the public-education pipeline.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BULK = Path("sources/new-hampshire/_bulk/openstates")
SRC = Path("sources/new-hampshire/energy")
W = Path("working/new-hampshire/energy")
YEARS = [2020, 2021, 2022, 2023, 2024]

# Deliberately over-broad: recall >> precision. \benerg\w*, \belectric\w*, and
# \butilit\w* alone catch every energy/energetic/electricity/electrical/
# electrician/utility/utilities title; \bpower\b, \bgas\b, \bcarbon\b,
# \bgenerat\w*, and \bfuel\w* re-open the very traps the search terms avoided
# (powers and duties, tear gas, future generations) - here the human review
# absorbs the volume. Word-boundary regexes where substrings would explode
# (wind vs. window/Windham, oil vs. soil/toilet, meter vs. perimeter).
WIDE_NET = [
    r"\benerg\w*", r"\belectric\w*", r"\butilit\w*",
    r"\brenewabl\w*", r"\bsolar\b", r"\bwind\b", r"\bfuel\w*",
    r"\bpipeline\w*", r"\bkilowatt\w*", r"\bmegawatt\w*", r"\bthermal\b",
    r"\bhydro\w*", r"\bweatheriz\w*", r"\bRGGI\b", r"\beversource\b",
    r"\bgrid\w*", r"\bratepayer\w*", r"\bnuclear\b", r"\bpropane\b",
    r"\bbiomass\b", r"\bbiodiesel\b", r"\bethanol\b", r"\btransmission\w*",
    r"\bmeter(s|ing|ed)?\b", r"\boffshore\b", r"\bphotovoltaic\w*",
    r"\bgeothermal\b", r"\bbiopower\b", r"\bnatural gas\b", r"\bgas\b",
    r"\bcarbon\b", r"\bemission\w*", r"\bclimate\b", r"\bgreenhouse\b",
    r"\bkerosene\b", r"\bheating\b", r"\bcoal\b", r"\bpower\b",
    r"\bgenerat\w*", r"\breactor\w*", r"\bturbine\w*",
    r"\bsite evaluation committee\b", r"\bdecommission\w*",
    r"\baggregat\w*", r"\bstove\w*", r"\bboiler\w*", r"\bfurnace\w*",
    r"\bwoodstove\w*", r"\bwood pellet\w*", r"\bpetroleum\b", r"\bdiesel\b",
    r"\bgasoline\b", r"\b\boil\b", r"\bcharging station\w*",
]
NET = re.compile("|".join(WIDE_NET), re.I)


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def universe() -> dict[tuple[int, str], str]:
    out: dict[tuple[int, str], str] = {}
    for y in YEARS:
        f = next((BULK / str(y)).glob("*_bills.csv"))
        for r in read_csv(f):
            ident = (r.get("identifier") or "").replace(" ", "")
            out[(y, ident)] = r.get("title") or ""
    return out


def main() -> None:
    uni = universe()
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    collected = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}
    old_collected = {k for k in collected if k[0] in YEARS}

    # 1) universe sweep
    review = []
    for (y, ident), title in sorted(uni.items()):
        if (y, ident) in collected:
            continue
        if NET.search(title or ""):
            review.append({"session_year": y, "bill_no": ident, "title": title})

    # 2) set cross-check
    ghosts = sorted(f"{y}:{b}" for (y, b) in old_collected if (y, b) not in uni)

    # 3) vote cross-check
    votes = {(v["session_year"], v["bill_no"]): v["roll_call_count"]
             for v in json.loads((SRC / "processed" / "bill-votes.json").read_text())["bills"]}
    bulk_votes: dict[tuple[int, str], int] = {}
    for y in YEARS:
        vf = next((BULK / str(y)).glob("*_votes.csv"), None)
        bf = next((BULK / str(y)).glob("*_bills.csv"))
        bid_to_ident = {r["id"]: (r.get("identifier") or "").replace(" ", "")
                        for r in read_csv(bf)}
        if vf:
            for r in read_csv(vf):
                ident = bid_to_ident.get(r.get("bill_id") or "")
                if ident:
                    bulk_votes[(y, ident)] = bulk_votes.get((y, ident), 0) + 1
    vote_mismatches = []
    for k in sorted(old_collected):
        sql_n, bulk_n = votes.get(k, 0), bulk_votes.get(k, 0)
        if bulk_n > sql_n:
            vote_mismatches.append({"bill": f"{k[0]}:{k[1]}",
                                    "sql_roll_calls": sql_n, "bulk_votes": bulk_n})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_bills": len(uni),
        "universe_by_year": {y: sum(1 for k in uni if k[0] == y) for y in YEARS},
        "collected_2020_2024": len(old_collected),
        "wide_net_patterns": len(WIDE_NET),
        "review_candidates_not_in_set": review,
        "collected_bills_not_in_universe": ghosts,
        "bulk_vote_rows_exceeding_sql": vote_mismatches,
    }
    (W / "certification-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Universe: {len(uni)} bills {report['universe_by_year']}")
    print(f"Collected 2020-2024: {len(old_collected)}")
    print(f"Wide-net candidates NOT in set (need human review): {len(review)}")
    print(f"Collected bills missing from universe (should be 0): {len(ghosts)} {ghosts[:5]}")
    print(f"Bills where bulk shows more votes than SQL (should be 0): {len(vote_mismatches)} {vote_mismatches[:5]}")


if __name__ == "__main__":
    main()
