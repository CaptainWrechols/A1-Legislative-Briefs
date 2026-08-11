#!/usr/bin/env python3
"""Complete the sponsor layer for 2020-2024 bills from the OpenStates bulk
sponsorship files (the housing packet's sponsor recipe).

For every collected 2020-2024 bill that has no sponsor list yet (or only the
short os_sponsors capture from discovery), attach the full sponsorship rows
from <bulk>/{year}/*_bill_sponsorships.csv. New Hampshire lists the prime
sponsor first; where the bulk file carries no primary flag, the first-listed
sponsor is marked prime with ``prime_inferred: true``. Party labels are not in
the bulk files and stay null (the evidence pack documents this limit).

Rewrites pass1/bills.json and processed/bills-core.json in place.
Run from repo root after collection.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

BULK = Path("sources/new-hampshire/_bulk/openstates")
SRC = Path("sources/new-hampshire/property-taxes")
YEARS = (2020, 2021, 2022, 2023, 2024)


def read_csv(p: Path) -> list[dict]:
    with p.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def bulk_sponsors() -> dict[tuple[int, str], list[dict]]:
    out: dict[tuple[int, str], list[dict]] = {}
    for y in YEARS:
        bf = next((BULK / str(y)).glob("*_bills.csv"))
        id2ident = {r["id"]: (r.get("identifier") or "").replace(" ", "")
                    for r in read_csv(bf)}
        sf = next((BULK / str(y)).glob("*_bill_sponsorships.csv"), None)
        if not sf:
            continue
        for r in read_csv(sf):
            ident = id2ident.get(r.get("bill_id") or "")
            if not ident:
                continue
            flag = (r.get("primary") or r.get("classification") or "").strip().lower()
            out.setdefault((y, ident), []).append({
                "name": (r.get("name") or "").strip(),
                "party": None,
                "prime": flag in ("true", "primary", "1"),
                "prime_inferred": False,
                "source": "openstates_bulk_sponsorships",
            })
    # first-listed = prime where no flag is present at all
    for key, sp in out.items():
        if sp and not any(s["prime"] for s in sp):
            sp[0]["prime"] = True
            sp[0]["prime_inferred"] = True
    return out


def normalize_existing(sp: list[dict]) -> list[dict] | None:
    """Normalize a discovery-time os_sponsors capture ({name, primary,
    entity_type}) into the standard shape, with first-listed prime inference
    when no flag is present."""
    if not sp or "prime" in sp[0]:
        return None  # already normalized (or SQL shape)
    out = [{
        "name": (s.get("name") or "").strip(),
        "party": None,
        "prime": str(s.get("primary")).strip().lower() in ("true", "primary", "1"),
        "prime_inferred": False,
        "source": "openstates_bulk_sponsorships",
    } for s in sp]
    if out and not any(s["prime"] for s in out):
        out[0]["prime"] = True
        out[0]["prime_inferred"] = True
    return out


def main() -> None:
    sponsors = bulk_sponsors()
    attached = normalized = 0
    for name in ("pass1/bills.json", "processed/bills-core.json"):
        doc = json.loads((SRC / name).read_text())
        for b in doc["bills"]:
            key = (b["session_year"], b["bill_no"])
            if key[0] not in YEARS:
                continue
            if b.get("sponsors"):
                norm = normalize_existing(b["sponsors"])
                if norm:
                    b["sponsors"] = norm
                    normalized += 1
                continue
            sp = sponsors.get(key)
            if sp:
                b["sponsors"] = sp
                attached += 1
        (SRC / name).write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(f"Attached bulk sponsor lists to {attached} bill records; normalized "
          f"{normalized} discovery-time captures (first-listed prime inferred "
          f"where unflagged). Counts cover pass1 + bills-core together.")


if __name__ == "__main__":
    main()
