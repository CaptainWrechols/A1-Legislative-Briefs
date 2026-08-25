"""Ingest OpenStates *bulk* CSV downloads for South Carolina (no API, no limits).

Same zero-rate-limit pattern proven for New Hampshire (collectors/nh): OpenStates
publishes every session's bills/sponsors/abstracts/votes as a bulk CSV archive.
A free OpenStates account (instant, unlike LegiScan's manual key review) lets
you download the archives once from

    https://open.pluralpolicy.com/data/session-csv/

Download the four South Carolina archives (sessions 2019-2020, 2021-2022,
2023-2024, 2025-2026) and unzip each into one folder per session:

    <bulk_dir>/2019-2020/bills.csv, bill_sponsorships.csv, ...
    <bulk_dir>/2021-2022/...
    ...

Default ``<bulk_dir>`` is ``sources/south-carolina/_bulk/openstates`` (override
with ``SC_OPENSTATES_BULK_DIR``). File names may be plain (``bills.csv``) or
prefixed (``sc_2021-2022_bills.csv``); both are handled.

Role in the SC pipeline: **discovery cross-check and backfill** alongside the
primary scstatehouse.gov full-text search — the dual-source rule from Nevada.
Vote counts should still be read from scstatehouse.gov vote-history tables
(the official source); bulk votes are a cross-check only.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

DEFAULT_DIR = Path("sources/south-carolina/_bulk/openstates")


def bulk_dir() -> Path:
    return Path(os.environ.get("SC_OPENSTATES_BULK_DIR", str(DEFAULT_DIR)))


def available(session_identifier: str | None = None) -> bool:
    d = bulk_dir()
    if not d.exists():
        return False
    if session_identifier is None:
        return any(d.iterdir())
    return (d / session_identifier).exists() or bool(
        list(d.glob(f"*{session_identifier}*")))


def _find_file(session_dir: Path, kind: str) -> Path | None:
    """Locate e.g. the 'bills' CSV whether plain or sc_2021-2022_bills.csv."""
    if not session_dir.exists():
        return None
    exact = session_dir / f"{kind}.csv"
    if exact.exists():
        return exact
    matches = [p for p in session_dir.glob("*.csv") if p.stem.lower().endswith(kind)]
    return matches[0] if matches else None


def _read(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _col(row: dict, *names: str) -> str:
    """Case-insensitive column lookup with alias fallbacks."""
    lower = {k.lower(): v for k, v in row.items()}
    for n in names:
        if n.lower() in lower and lower[n.lower()] not in (None, ""):
            return lower[n.lower()]
    return ""


def _session_dir(session_identifier: str) -> Path | None:
    d = bulk_dir()
    exact = d / session_identifier
    if exact.exists():
        return exact
    globbed = list(d.glob(f"*{session_identifier}*"))
    return globbed[0] if globbed else None


def discover_session(session_identifier: str, search_terms: list[str],
                     rel_terms: list[str]) -> list[dict]:
    """Keyword-filter one session's bulk CSVs, joining sponsors + abstracts.

    Pass 1 rule: a bill is kept when any *search* term matches its
    title/abstract; ``relevance_terms`` only set the ``relevance_flag`` used
    for human review — nothing is dropped by relevance.
    """
    sdir = _session_dir(session_identifier)
    if sdir is None:
        return []
    bills = _read(_find_file(sdir, "bills"))
    sponsorships = _read(_find_file(sdir, "bill_sponsorships"))
    abstracts = _read(_find_file(sdir, "bill_abstracts"))

    sp_by_bill: dict[str, list[dict]] = {}
    for s in sponsorships:
        bid = _col(s, "bill_id", "bill", "id")
        sp_by_bill.setdefault(bid, []).append({
            "name": _col(s, "name"),
            "primary": _col(s, "primary", "classification"),
            "entity_type": _col(s, "entity_type"),
        })
    ab_by_bill: dict[str, str] = {}
    for a in abstracts:
        bid = _col(a, "bill_id", "bill", "id")
        ab_by_bill[bid] = (ab_by_bill.get(bid, "") + " " + _col(a, "abstract", "note")).strip()

    terms = [t.lower() for t in search_terms]
    rel = [t.lower() for t in (rel_terms or search_terms)]
    hits = []
    for b in bills:
        bid = _col(b, "id", "bill_id")
        identifier = _col(b, "identifier", "bill_identifier").replace(" ", "")
        title = _col(b, "title")
        abstract = ab_by_bill.get(bid, "")
        blob = f"{title} {abstract}".lower()
        matched = [t for t in terms if t in blob]
        if not matched:
            continue
        hits.append({
            "bill_no": identifier,
            "title": title,
            "abstract": abstract,
            "classification": _col(b, "classification"),
            "subject": _col(b, "subject"),
            "openstates_url": _col(b, "openstates_url", "url"),
            "sponsors": sp_by_bill.get(bid, []),
            "found_by_terms": matched,
            "relevance_flag": any(t in blob for t in rel),
        })
    return sorted(hits, key=lambda h: h["bill_no"])


if __name__ == "__main__":
    d = bulk_dir()
    print(f"Bulk dir: {d} (exists: {d.exists()})")
    if d.exists():
        for sub in sorted(p.name for p in d.iterdir() if p.is_dir()):
            print("  session:", sub)
    else:
        print("  Download SC session CSVs from "
              "https://open.pluralpolicy.com/data/session-csv/ (free account).")
