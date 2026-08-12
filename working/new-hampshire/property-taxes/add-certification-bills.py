#!/usr/bin/env python3
"""Add the universe-certification catches to the collected set.

These bills matched the certification sweep's wide net over the complete
OpenStates bulk universe and were judged property-tax/revenue-relevant on
human review, but had escaped the keyword search (their titles use vocabulary
the seed terms missed: 'occupancy fee', 'assessments' vs 'assessing',
'communications service tax' singular, 'payments in lieu of taxes' plural,
'omnibus legislation on state taxes', budget caps, differential rates, and
similar). Tagged source 'supplement:universe-certification' so re-collections
preserve them. Votes come from SQL as always.

Run from repo root after the bulk collection.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import gencourt_sql as db  # noqa: E402

SRC = Path("sources/new-hampshire/property-taxes")
BULK = Path("sources/new-hampshire/_bulk/openstates")

ADDS = [
    # local-option / municipal revenue
    (2020, "HB1160"), (2022, "SB338"), (2023, "SB262"), (2024, "HB1254"),
    (2021, "SB53"), (2020, "SB484"), (2022, "SB251"), (2023, "HB576"),
    # property tax administration / assessment / appeals
    (2020, "HB1311"), (2021, "HB383"), (2022, "SB312"), (2023, "HB403"),
    (2023, "HB99"), (2024, "HB1456"), (2024, "HB1651"), (2021, "HB528"),
    # rates, exemptions, and bases
    (2022, "HB1365"), (2023, "HB80"), (2023, "HB174"), (2024, "CACR18"),
    (2024, "SB586"),
    # state taxes and revenue streams
    (2021, "SB13"), (2021, "SB3"), (2020, "SB93"), (2020, "HB680"),
    (2023, "HB510"), (2020, "HB1477"), (2020, "SB663"), (2024, "SB433"),
    (2024, "SB472"),
    # school funding / budget caps / state-aid transparency
    (2022, "HB1393"), (2023, "HB365"), (2024, "HB1570"), (2024, "SB532"),
]


def universe_titles() -> dict:
    out = {}
    for y in (2020, 2021, 2022, 2023, 2024):
        f = next((BULK / str(y)).glob("*_bills.csv"))
        for r in csv.DictReader(f.open(encoding="utf-8-sig")):
            out[(y, r["identifier"].replace(" ", ""))] = r["title"]
    return out


def main() -> None:
    titles = universe_titles()
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    core = json.loads((SRC / "processed" / "bills-core.json").read_text())
    votes = json.loads((SRC / "processed" / "bill-votes.json").read_text())
    have = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}

    added = 0
    for year, bill in ADDS:
        if (year, bill) in have:
            print(f"{year} {bill}: already in set")
            continue
        title = titles.get((year, bill))
        assert title, f"{year} {bill} not in universe!"
        rec = {"session_year": year, "bill_no": bill, "title": title,
               "found_by_terms": [], "sources": ["supplement:universe-certification"],
               "discovery_source": ("universe certification sweep over the OpenStates "
                                    "bulk CSVs (wide-net title match, human-reviewed)")}
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
