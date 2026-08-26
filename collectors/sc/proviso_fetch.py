"""Fetch SC General Appropriations **Part IB** full text for a budget cycle.

The budget hub is https://www.scstatehouse.gov/budget.php; each fiscal year has
an index page (gab{bill}.php) linking one sub-index per version. Version
prefixes, in enactment order:

    wm = Ways & Means          hp = House-passed
    sf = Senate Finance        sp = Senate-passed
    hr = returned to House     cr = Conference Report
    ta = ratified / enacted ("as passed by the General Assembly")

For every version the Part IB full text is a single static HTML file:

    {BASE}/{session_path}/appropriations{year}/{prefix}p1b.htm

(e.g. .../appropriations2024/tap1b.htm — verified live for the enacted version
of every cycle 2019 and 2021→2026; FY2020-21 was never enacted, see
collectors.sc.BUDGET_CYCLES).

Fetched HTML is cached under sources/south-carolina/... so extraction is
reproducible without re-hitting the site.
"""

from __future__ import annotations

from pathlib import Path

from . import BUDGET_CYCLE_BY_YEAR, SESSION_BY_NUMBER
from .scstatehouse import BASE, soft_get

# Fallback order if the preferred version's file is missing: latest first.
VERSION_ORDER = ["ta", "cr", "hr", "sp", "sf", "hp", "wm"]
VERSION_LABELS = {
    "wm": "Ways & Means Committee",
    "hp": "Passed by the House",
    "sf": "Senate Finance Committee",
    "sp": "Passed by the Senate",
    "hr": "Returned to the House",
    "cr": "Conference Report",
    "ta": "Ratified / enacted (as passed by the General Assembly)",
}


def part1b_url(year: int, version: str) -> str:
    cycle = BUDGET_CYCLE_BY_YEAR[year]
    session_path = SESSION_BY_NUMBER[cycle["session"]]["scstatehouse_path"]
    return f"{BASE}/{session_path}/appropriations{year}/{version}p1b.htm"


def fetch_part1b(year: int, *, cache_dir: Path | None = None) -> dict | None:
    """Fetch (and cache) the best available Part IB text for one cycle.

    Tries the cycle's ``best_version`` first (``ta`` for enacted budgets),
    then falls back down VERSION_ORDER — soft-fail all the way, so a missing
    version never kills a run. Returns None only if every version fails.
    """
    cycle = BUDGET_CYCLE_BY_YEAR.get(year)
    if cycle is None:
        raise ValueError(f"No SC appropriations cycle registered for {year}")
    preferred = cycle.get("best_version", "ta")
    order = [preferred] + [v for v in VERSION_ORDER if v != preferred]
    for version in order:
        if cache_dir is not None:
            cached = cache_dir / f"part1b-{year}-{version}.htm"
            if cached.exists():
                return {
                    "year": year, "version": version,
                    "version_label": VERSION_LABELS[version],
                    "fiscal_year": cycle["fiscal_year"],
                    "bill_no": cycle["bill_no"],
                    "enacted": cycle["enacted"],
                    "source_url": part1b_url(year, version),
                    "html": cached.read_text(encoding="utf-8", errors="replace"),
                    "from_cache": True,
                }
        r = soft_get(part1b_url(year, version))
        if r is None or len(r.text) < 50_000:  # tiny page = error/redirect stub
            continue
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"part1b-{year}-{version}.htm").write_text(
                r.text, encoding="utf-8")
        return {
            "year": year, "version": version,
            "version_label": VERSION_LABELS[version],
            "fiscal_year": cycle["fiscal_year"],
            "bill_no": cycle["bill_no"],
            "enacted": cycle["enacted"],
            "source_url": part1b_url(year, version),
            "html": r.text,
            "from_cache": False,
        }
    return None


if __name__ == "__main__":
    import sys

    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    doc = fetch_part1b(year)
    if doc:
        print(f"FY {doc['fiscal_year']} {doc['bill_no']} version={doc['version']} "
              f"({doc['version_label']}): {len(doc['html'])} bytes from "
              f"{doc['source_url']}")
    else:
        print(f"FAILED: no Part IB version reachable for {year}")
