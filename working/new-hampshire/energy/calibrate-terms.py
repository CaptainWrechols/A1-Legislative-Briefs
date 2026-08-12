#!/usr/bin/env python3
"""Term calibration for the energy issue config.

Counts, for every candidate search term, how many bills it would sweep in
(a) the OpenStates bulk CSVs (2020-2024, titles+abstracts, substring match —
the same matching the collector uses) and (b) the GenCourt SQL ``legislation``
table (2025-2026, LSRTitle LIKE '%term%').  Also reports the union set size so
the frozen term list's total curation load is known BEFORE collection.

Adapted from working/new-hampshire/public-education/calibrate-terms.py.
Energy-specific substring traps under test (SQL LIKE matches substrings):
  * "power"  — powers and duties, power of attorney, horsepower
  * "wind"   — Windham, winding, windfall
  * "oil"    — soil, boiler, oversight ("recoil" unlikely but cheap to test)
  * "gas"    — gasoline is fine, but check volume
  * "meter"  — perimeter, parameter, kilometer
  * "rate"   — crime rate, tax rate, graduation rate, corporate
  * "solar" / "grid" — believed safe, verify
  * bare "energy", "electric", "utility" — may be affordable here (unlike
    bare "school"/"education" in the education packet) — measure first.

Run from repo root:  python3 working/new-hampshire/energy/calibrate-terms.py
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
    # bare high-value words (affordability under test)
    "energy", "electric", "electricity", "utility", "utilities",
    # compound-phrase core vocabulary (the task's seed list)
    "renewable energy", "net energy metering", "net metering",
    "electric grid", "transmission", "electric rate", "electric vehicle",
    "default service", "community power", "aggregation", "smart meter",
    "time-of-use", "peak demand", "public utilities commission",
    "ratepayer", "energy efficiency", "weatherization",
    "system benefits charge", "renewable portfolio", "offshore wind",
    "hydroelectric", "geothermal", "biomass", "nuclear", "natural gas",
    "propane", "heating fuel", "fuel assistance", "energy facility",
    "site evaluation committee", "energy storage", "solar", "grid",
    # additional candidates worth measuring
    "renewable", "kilowatt", "megawatt", "energy conservation",
    "energy policy", "power plant", "power purchase", "electrical",
    "distributed energy", "microgrid", "hydropower", "wood heat",
    "thermal", "pipeline", "fuel oil", "biodiesel", "clean energy",
    "department of energy", "consumer advocate", "burial of utility",
    "decommissioning", "low-income", "rate reduction",
    # traps to demonstrate volume (NOT for the config unless proven cheap)
    "power", "wind", "oil", "gas", "meter", "rate", "fuel",
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
    traps = {"power", "wind", "oil", "gas", "meter", "rate", "fuel"}
    keep = [t for t in CANDIDATES if t not in traps]
    union_keep = set().union(*(bm[t] | sm[t] for t in keep))
    union_all = set().union(*(bm[t] | sm[t] for t in CANDIDATES))
    print(f"union of non-trap terms: {len(union_keep)} bills")
    print(f"union incl. bare traps:  {len(union_all)} bills")


if __name__ == "__main__":
    main()
