"""Ingest OpenStates *bulk* CSV downloads from local files (no API, no limits).

This is the zero-rate-limit path for older NH sessions. OpenStates publishes
every session's bills/sponsors/votes as a **bulk CSV archive** (a free, instant
account is required to download it -- unlike LegiScan there is no human review).
You download the per-session archives once and drop them in a folder; this
module reads them locally, so collection makes **no API calls at all** and there
is nothing to rate-limit.

Expected layout (one folder per session; file names may be plain or prefixed
like ``nh_2021_bills.csv`` -- both are handled):

    <bulk_dir>/2020/bills.csv, bill_sponsorships.csv, bill_abstracts.csv, votes.csv
    <bulk_dir>/2021/...
    ...

Default ``<bulk_dir>`` is ``sources/new-hampshire/_bulk/openstates`` (override
with ``NH_OPENSTATES_BULK_DIR``). Get the files from
https://open.pluralpolicy.com/data/session-csv/ (Bill & Vote CSV, per session).

The CSV schema is OpenStates' "experimental" bulk format
(`bills`, `bill_abstracts`, `bill_actions`, `bill_sponsorships`,
`bill_versions`, `bill_version_links`, `votes`, `vote_counts`, `vote_people`,
`vote_sources`). Column detection here is tolerant (case-insensitive, common
aliases) so minor schema drift does not break ingestion. Votes are still taken
from the authoritative GenCourt SQL database; the bulk votes are only a
cross-check.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

DEFAULT_DIR = Path("sources/new-hampshire/_bulk/openstates")


def bulk_dir() -> Path:
    return Path(os.environ.get("NH_OPENSTATES_BULK_DIR", str(DEFAULT_DIR)))


def available(session_label: str | None = None) -> bool:
    d = bulk_dir()
    if not d.exists():
        return False
    if session_label is None:
        return any(d.iterdir())
    return (d / session_label).exists() or bool(list(d.glob(f"*{session_label}*")))


def _find_file(session_dir: Path, kind: str) -> Path | None:
    """Locate e.g. the 'bills' CSV whether it's bills.csv or nh_2021_bills.csv."""
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


def _session_dir(session_label: str) -> Path | None:
    d = bulk_dir()
    exact = d / session_label
    if exact.exists():
        return exact
    globbed = list(d.glob(f"*{session_label}*"))
    return globbed[0] if globbed else None


def discover_session(session_label: str, search_terms: list[str],
                     rel_terms: list[str]) -> list[dict]:
    """Filter one session's bulk CSVs to issue-relevant bills, with sponsors
    and abstracts joined in.
    """
    sdir = _session_dir(session_label)
    if sdir is None:
        return []
    bills = _read(_find_file(sdir, "bills"))
    sponsorships = _read(_find_file(sdir, "bill_sponsorships"))
    abstracts = _read(_find_file(sdir, "bill_abstracts"))

    # Index sponsors/abstracts by the bill's OCD id.
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
        if not matched or not any(t in blob for t in rel):
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
        })
    return sorted(hits, key=lambda h: h["bill_no"])


if __name__ == "__main__":
    d = bulk_dir()
    print(f"Bulk dir: {d} (exists: {d.exists()})")
    if d.exists():
        for sub in sorted(p.name for p in d.iterdir() if p.is_dir()):
            print("  session:", sub)
