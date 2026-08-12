#!/usr/bin/env python3
"""Term calibration for the public-education issue config.

Counts, for every candidate search term, how many bills it would sweep in
(a) the OpenStates bulk CSVs (2020-2024, titles+abstracts, substring match —
the same matching the collector uses) and (b) the GenCourt SQL ``legislation``
table (2025-2026, LSRTitle LIKE '%term%').  Also reports the union set size so
the frozen term list's total curation load is known BEFORE collection.

Run from repo root:  python3 working/new-hampshire/public-education/calibrate-terms.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, "collectors")
from nh import gencourt_sql as db  # noqa: E402

BULK = Path("sources/new-hampshire/_bulk/openstates")
YEARS = ["2020", "2021", "2022", "2023", "2024"]

CANDIDATES = [
    # compound-phrase core vocabulary (the task's seed list)
    "school district", "charter school", "chartered public school",
    "education freedom", "special education", "curriculum", "school board",
    "teacher", "pupil", "kindergarten", "school building", "student",
    "tuition", "adequate education", "school meals", "IEP",
    "career and technical",
    # funding thread (shared with the property-taxes packet)
    "school funding", "education funding", "statewide education", "adequacy",
    "education trust fund", "school building aid", "state aid",
    # governance / structure
    "school administrative unit", "cooperative school", "school attendance",
    "open enrollment", "home education", "nonpublic school", "public school",
    "school choice", "superintendent", "school nurse", "paraprofessional",
    "school year", "school age", "school employee", "school personnel",
    "school property", "school safety", "school bus", "school meal",
    "school lunch", "school breakfast", "school calendar", "school health",
    # instruction / outcomes
    "literacy", "graduation", "diploma", "dropout", "truancy",
    "statewide assessment", "competency", "proficiency", "civics",
    "computer science", "sex education", "reading instruction",
    "learning disabilit", "dyslexia", "remote instruction", "remote learning",
    "extended learning", "career pathways", "workforce development",
    "education program", "educational program", "educational institution",
    "department of education", "state board of education", "school psychologist",
    "instructional", "classroom", "educator",
    # traps to demonstrate volume (NOT for the config)
    "education", "school", "board", "assessment", "college", "university",
]


def bulk_counts() -> tuple[dict, dict]:
    per_term: dict[str, int] = {t: 0 for t in CANDIDATES}
    matched_bills: dict[str, set] = {t: set() for t in CANDIDATES}
    for y in YEARS:
        d = BULK / y
        bills_csv = next(iter(d.glob("*bills.csv")), None)
        abs_csv = next(iter(d.glob("*bill_abstracts.csv")), None)
        ab: dict[str, str] = {}
        if abs_csv and abs_csv.exists():
            with abs_csv.open(encoding="utf-8-sig", newline="") as fh:
                for r in csv.DictReader(fh):
                    bid = r.get("bill_id") or r.get("id") or ""
                    ab[bid] = (ab.get(bid, "") + " " + (r.get("abstract") or "")).strip()
        with bills_csv.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                bid = r.get("id") or ""
                blob = f"{r.get('title','')} {ab.get(bid,'')}".lower()
                key = f"{y}:{(r.get('identifier') or '').replace(' ','')}"
                for t in CANDIDATES:
                    if t.lower() in blob:
                        per_term[t] += 1
                        matched_bills[t].add(key)
    return per_term, matched_bills


def sql_counts() -> tuple[dict, dict]:
    years = db.legislation_years()
    per_term: dict[str, int] = {}
    matched: dict[str, set] = {}
    rows = db.query(
        "SELECT sessionyear, CondensedBillNo, LSRTitle FROM legislation "
        "WHERE sessionyear IN (%s, %s)", tuple(years))
    for t in CANDIDATES:
        tl = t.lower()
        hits = {f"{r['sessionyear']}:{r['CondensedBillNo']}"
                for r in rows if tl in (r["LSRTitle"] or "").lower()}
        per_term[t] = len(hits)
        matched[t] = hits
    return per_term, matched


def main() -> None:
    bc, bm = bulk_counts()
    sc, sm = sql_counts()
    print(f"{'term':38} {'bulk20-24':>9} {'sql25-26':>9} {'total':>7}")
    for t in CANDIDATES:
        print(f"{t:38} {bc[t]:9d} {sc[t]:9d} {bc[t]+sc[t]:7d}")
    print()
    # Union sizes for the trap terms vs everything else
    traps = {"education", "school", "board", "assessment", "college", "university"}
    keep = [t for t in CANDIDATES if t not in traps]
    union_keep = set().union(*(bm[t] | sm[t] for t in keep))
    union_all = set().union(*(bm[t] | sm[t] for t in CANDIDATES))
    print(f"union of non-trap terms: {len(union_keep)} bills")
    print(f"union incl. bare traps:  {len(union_all)} bills")


if __name__ == "__main__":
    main()
