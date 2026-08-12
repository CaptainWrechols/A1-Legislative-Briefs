#!/usr/bin/env python3
"""Add the universe-certification catches to the collected set.

These bills matched the certification sweep's wide net over the complete
OpenStates bulk universe and were judged K-12-education-relevant on human
review, but had escaped the keyword search (their titles use vocabulary the
seed terms missed: 'adequate public education' - which the substring
'adequate education' does NOT match, 'in schools' phrasings with no compound
term, 'women's school sports', the foundation opportunity budget, 'eligibility
to teach', menstrual-products and school-materials bills, Medicaid to schools,
school counseling, and similar). Tagged source
'supplement:universe-certification' so re-collections preserve them. Votes
come from SQL as always.

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

SRC = Path("sources/new-hampshire/public-education")
BULK = Path("sources/new-hampshire/_bulk/openstates")

ADDS = [
    # ---- 2020 ----
    # curriculum / content / civics
    (2020, "HB1148"), (2020, "HB1306"), (2020, "HB1635"), (2020, "SB727"),
    (2020, "SB515"),
    # school assignment, records, credits, and governance
    (2020, "HB1328"), (2020, "HB1329"), (2020, "HB1369"), (2020, "HB1412"),
    (2020, "SJR1"), (2020, "HB1231"),
    # pupil safety, health, meals, wellbeing
    (2020, "HB1337"), (2020, "HB1512"), (2020, "HB1549"), (2020, "HB1682"),
    (2020, "HB1686"), (2020, "SB684"), (2020, "SB171"), (2020, "SB533"),
    (2020, "SB556"), (2020, "SB599"), (2020, "SB624"), (2020, "SB711"),
    (2020, "HB1373"), (2020, "HB1470"),
    # special education / teachers / funding
    (2020, "SB582"), (2020, "SB585"), (2020, "HB1492"),
    # ---- 2021 ----
    (2021, "HB182"), (2021, "HB198"), (2021, "HB267"), (2021, "HB276"),
    (2021, "HB432"), (2021, "HB609"), (2021, "HB69"), (2021, "HB96"),
    (2021, "SB108"), (2021, "SB20"), (2021, "HB504"), (2021, "HB500"),
    # ---- 2022 ----
    (2022, "HB1035"), (2022, "HB1072"), (2022, "HB1125"), (2022, "HB1131"),
    (2022, "HB1132"), (2022, "HB1196"), (2022, "HB1236"), (2022, "HB1244"),
    (2022, "HB1398"), (2022, "HB1421"), (2022, "HB1561"), (2022, "HB1576"),
    (2022, "HB1603"), (2022, "HB1605"), (2022, "HB1632"), (2022, "HB1638"),
    (2022, "HB1639"), (2022, "HB1653"), (2022, "HB1657"), (2022, "HB1661"),
    (2022, "HB1680"), (2022, "HB198"), (2022, "HB267"), (2022, "HB276"),
    (2022, "SB233"), (2022, "SB263"), (2022, "SB298"), (2022, "SB304"),
    (2022, "SB351"), (2022, "SB353"), (2022, "SB452"), (2022, "HB504"),
    # ---- 2023 ----
    (2023, "HB104"), (2023, "HB129"), (2023, "HB267"), (2023, "HB309"),
    (2023, "HB32"), (2023, "HB437"), (2023, "HB439"), (2023, "HB466"),
    (2023, "HB487"), (2023, "HB505"), (2023, "HB529"), (2023, "HB561"),
    (2023, "HB627"), (2023, "HB638"), (2023, "HB649"), (2023, "HB569"),
    (2023, "HB420"), (2023, "SB151"), (2023, "SB179"), (2023, "SB37"),
    (2023, "SB39"), (2023, "HB539"),
    # ---- 2024 ----
    (2024, "CACR17"), (2024, "CACR25"), (2024, "HB1019"), (2024, "HB1048"),
    (2024, "HB1071"), (2024, "HB1084"), (2024, "HB1088"), (2024, "HB1093"),
    (2024, "HB1205"), (2024, "HB1247"), (2024, "HB1269"), (2024, "HB1287"),
    (2024, "HB1378"), (2024, "HB1419"), (2024, "HB1458"),
    (2024, "HB1471"), (2024, "HB1511"), (2024, "HB1563"), (2024, "HB1586"),
    (2024, "HB1639"), (2024, "HB1678"), (2024, "HB1691"), (2024, "HB185"),
    (2024, "HB267"), (2024, "HB420"), (2024, "HB437"), (2024, "HB439"),
    (2024, "HB468"), (2024, "HB505"), (2024, "HB529"), (2024, "HB569"),
    (2024, "HB627"), (2024, "HB638"), (2024, "HR30"), (2024, "SB151"),
    (2024, "SB338"), (2024, "SB343"), (2024, "SB378"), (2024, "SB443"),
    (2024, "SB444"), (2024, "SB524"), (2024, "SB532"), (2024, "SB565"),
    (2024, "SB593"),
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
