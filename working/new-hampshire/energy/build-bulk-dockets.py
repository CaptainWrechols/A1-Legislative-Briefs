#!/usr/bin/env python3
"""Extract official docket actions for every 2020-2024 bill in the set from
the OpenStates bulk CSVs (bill_actions.csv mirrors the GenCourt docket).

Writes working/.../bulk-dockets.json: {year:bill: [{date, org, description}]}.
build-dispositions.py stages 2020-2024 bills from these (complete and local).

Adapted for the energy issue from the housing pipeline script.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

BULK = Path("sources/new-hampshire/_bulk/openstates")
SRC = Path("sources/new-hampshire/energy")
W = Path("working/new-hampshire/energy")


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    want = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]
            if b["session_year"] <= 2024}
    # NH numbering is continuous within a biennium, so a first-year bill that
    # carried over appears in the next year's CSV under the same number. When
    # that second-year record is NOT separately in the set, append its actions
    # to the first-year record so the biennium docket is complete (e.g. 2021
    # SB128 passed the Senate in 2021 and died in the House in 2022).
    continuation = {(y + 1, b): (y, b) for (y, b) in want
                    if y in (2021, 2023) and (y + 1, b) not in want}
    out: dict[str, list] = {}
    for y in (2020, 2021, 2022, 2023, 2024):
        bf = next((BULK / str(y)).glob("*_bills.csv"))
        id2ident = {r["id"]: r["identifier"].replace(" ", "")
                    for r in csv.DictReader(bf.open(encoding="utf-8-sig"))}
        af = next((BULK / str(y)).glob("*_bill_actions.csv"))
        for r in csv.DictReader(af.open(encoding="utf-8-sig")):
            ident = id2ident.get(r.get("bill_id") or "")
            if not ident:
                continue
            if (y, ident) in want:
                key_year = y
            elif (y, ident) in continuation:
                key_year = continuation[(y, ident)][0]
            else:
                continue
            org = r.get("organization__name") or r.get("organization_id") or ""
            if org.startswith("ocd-organization/3b8"):
                org = "House"
            elif org.startswith("ocd-organization/c95"):
                org = "Senate"
            desc = r.get("description") or ""
            if org.startswith("ocd-"):
                # fall back to journal cites in the docket text
                if " HJ " in desc or " HC " in desc:
                    org = "House"
                elif " SJ " in desc or " SC " in desc:
                    org = "Senate"
            out.setdefault(f"{key_year}:{ident}", []).append({
                "date": (r.get("date") or "")[:10],
                "organization": org,
                "description": desc,
            })
    for k in out:
        out[k].sort(key=lambda a: a["date"])
    covered = len(out)
    (W / "bulk-dockets.json").write_text(json.dumps({
        "note": ("Official docket actions per bill, from the OpenStates bulk "
                 "CSVs (a mirror of the GenCourt docket). Chronological order. "
                 "Used for disposition staging of 2020-2024 bills."),
        "bills": out,
    }, indent=2), encoding="utf-8")
    missing = sorted(f"{y}:{b}" for (y, b) in want if f"{y}:{b}" not in out)
    print(f"Dockets for {covered}/{len(want)} 2020-2024 bills; missing: {missing}")


if __name__ == "__main__":
    main()
