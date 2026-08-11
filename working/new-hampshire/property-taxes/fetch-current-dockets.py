#!/usr/bin/env python3
"""Pull full docket action histories for current-biennium bills from GenCourt SQL.

The `docket` table covers the current biennium (2025-2026), which is exactly
where pass1's general_status alone cannot distinguish killed / retained /
pending bills. Writes processed/bill-actions.json (one record per bill with
its dated action list, verbatim from the official docket).

Adapted for the property-taxes issue from the housing pipeline script.
Run from repo root:
  python3 working/new-hampshire/property-taxes/fetch-current-dockets.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import gencourt_sql as db  # noqa: E402

SRC = Path("sources/new-hampshire/property-taxes")
OUT = SRC / "processed" / "bill-actions.json"


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    sql_years = set(db.legislation_years())
    out = []
    for b in pass1["bills"]:
        year, bill_no = b["session_year"], b["bill_no"]
        if year not in sql_years:
            continue
        rows = db.docket_actions(bill_no, year)
        if not rows:
            # NH bills span a two-year biennium; a bill discovered via its
            # first-year record may have its docket keyed to the second year
            # (e.g. 2025 HB649's docket lives under 2026).
            for other in sorted(sql_years):
                if other == year:
                    continue
                rows = db.docket_actions(bill_no, other)
                if rows:
                    break
        out.append({
            "session_year": year,
            "bill_no": bill_no,
            "action_count": len(rows),
            "actions": [
                {"body": r["LegislativeBody"], "date": str(r["StatusDate"])[:10],
                 "description": r["Description"]}
                for r in rows
            ],
        })
        print(f"{year} {bill_no}: {len(rows)} actions; last: "
              f"{(out[-1]['actions'][-1]['description'][:70] if rows else '-')}")
        time.sleep(0.3)
    OUT.write_text(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "note": ("Official docket actions from the NH public SQL database "
                 "(current biennium only; the docket table does not cover "
                 "2020-2024). Verbatim; nothing inferred."),
        "bills": out,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(out)} bills)")


if __name__ == "__main__":
    main()
