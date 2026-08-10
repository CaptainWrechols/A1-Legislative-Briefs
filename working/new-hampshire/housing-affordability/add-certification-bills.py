#!/usr/bin/env python3
"""Add the universe-certification catches to the collected set.

These bills matched the certification sweep's wide net over the complete
OpenStates bulk universe and were judged housing-relevant on human review,
but had escaped both the keyword search (their titles use vocabulary like
'tenancy'/'lease'/'residential units' that the seed terms missed) and the
earlier index supplement. Tagged source 'supplement:universe-certification'
so re-collections preserve them. Votes come from SQL as always.

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

SRC = Path("sources/new-hampshire/housing-affordability")
BULK = Path("sources/new-hampshire/_bulk/openstates")

ADDS = [
    (2020, "HB143"), (2020, "HB311"), (2020, "HB1276"), (2020, "HB1439"),
    (2020, "HB1450"), (2020, "HB1588"), (2020, "SB152"), (2020, "SB482"),
    (2020, "SB562"), (2020, "SB710"),
    (2021, "HB227"), (2021, "HB341"), (2021, "HB588"), (2021, "HB616"),
    (2022, "HB227"), (2022, "HB1133"), (2022, "HB1136"), (2022, "HB1177"),
    (2022, "HB1068"), (2022, "HB1408"), (2022, "SB244"), (2022, "SB338"),
    (2022, "SB359"),
    (2023, "HB117"), (2023, "HB236"), (2023, "HB310"), (2023, "HB340"),
    (2023, "SB78"),
    (2024, "HB1053"), (2024, "HB1101"), (2024, "HB1115"), (2024, "HB1215"),
    (2024, "HB1284"), (2024, "HB1483"), (2024, "HB1521"), (2024, "HB1140"),
    (2024, "CACR16"), (2024, "SB413"),
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
