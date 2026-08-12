#!/usr/bin/env python3
"""Add the 2025-2026 universe-certification catches to the collected set.

These bills matched the current-biennium certification sweep's wide net over
the complete SQL legislation table and were judged energy-relevant on human
review, but had escaped the keyword search (their titles use vocabulary the
seed terms missed: 'community customer generators' with no electric/energy
word in the title). Tagged source 'supplement:universe-certification-current'
so re-collections preserve them. Votes come from SQL as always.

Run from repo root after the collection, before certify-current-biennium.py.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import gencourt_sql as db  # noqa: E402

SRC = Path("sources/new-hampshire/energy")

ADDS = [
    # net-metering / community generator thread (no electric/energy word)
    (2025, "SB228"),
]


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    core = json.loads((SRC / "processed" / "bills-core.json").read_text())
    votes = json.loads((SRC / "processed" / "bill-votes.json").read_text())
    have = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}

    added = 0
    for year, bill in ADDS:
        if (year, bill) in have:
            print(f"{year} {bill}: already in set")
            continue
        rows = db.query(
            "SELECT sessionyear, CondensedBillNo, LSRTitle FROM legislation "
            "WHERE sessionyear = %s AND REPLACE(CondensedBillNo, ' ', '') = %s",
            (year, bill))
        assert rows, f"{year} {bill} not in the SQL legislation table!"
        title = rows[0]["LSRTitle"]
        rec = {"session_year": year, "bill_no": bill, "title": title,
               "found_by_terms": [],
               "sources": ["supplement:universe-certification-current"],
               "discovery_source": ("universe certification sweep over the SQL "
                                    "legislation table (wide-net title match, human-reviewed)")}
        pass1["bills"].append(rec)
        core["bills"].append(dict(rec))
        summaries = db.rollcall_summaries(bill, year)
        vrec = {"session_year": year, "bill_no": bill,
                "roll_calls": summaries, "roll_call_count": len(summaries)}
        if summaries:
            vrec["ballots"] = db.rollcall_ballots(bill, year)
        votes["bills"].append(vrec)
        added += 1
        print(f"{year} {bill}: added; rolls={len(summaries)}; {title[:70]}")
        time.sleep(0.3)

    for doc, name in ((pass1, "pass1/bills.json"), (core, "processed/bills-core.json"),
                      (votes, "processed/bill-votes.json")):
        doc["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
        if "count" in doc:
            doc["count"] = len(doc["bills"])
        (SRC / name).write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(f"Added {added} certification bills; set now {len(pass1['bills'])}.")


if __name__ == "__main__":
    main()
