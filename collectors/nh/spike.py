"""Smoke-test the NH data routes and write sample artifacts.

Run from the repo root:

    python -m collectors.nh.spike

It proves each source end to end and drops small, inspectable samples under
``sources/new-hampshire/_spike/`` so a human can confirm the foundation works
before any large collection:

  * HB2 floor roll-call summaries for each budget cycle (SQL)
  * HB2 2025 full section extraction (website full text + hb2_sections)

Nothing here writes citizen-facing prose and no vote counts are invented --
counts come straight from the public database.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import fortiweb, gencourt_sql, gencourt_web, hb2_sections

OUT = Path("sources/new-hampshire/_spike")
BUDGET_CYCLES = (2021, 2023, 2025)


def _save(name: str, data) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(f"  wrote {OUT / name}")


def sql_samples() -> None:
    print("SQL: HB2 roll-call summaries per budget cycle")
    summary = {}
    for yr in BUDGET_CYCLES:
        rows = gencourt_sql.rollcall_summaries("HB2", yr)
        summary[yr] = {
            "roll_call_count": len(rows),
            "sample": rows[:3],
        }
        print(f"  HB2 {yr}: {len(rows)} floor roll calls")
    _save("hb2-rollcalls-by-cycle.json", summary)


def hb2_2025_sections() -> None:
    print("Website: HB2 2025 full text + section extraction")
    legislation_id = gencourt_sql.resolve_legislation_id("HB2", 2025)
    print(f"  HB2 2025 legislationID = {legislation_id}")
    s = fortiweb.new_session()
    version_html = gencourt_web.fetch_version_text(s, legislation_id, version_index=0)
    (OUT / "raw").mkdir(parents=True, exist_ok=True)
    (OUT / "raw" / "hb2-2025-introduced.html").write_text(version_html, encoding="utf-8")
    sections = hb2_sections.extract_sections(version_html)
    print(f"  extracted {len(sections)} sections")
    hb2_sections.write_outputs(
        sections,
        OUT / "hb2-2025",
        {
            "bill_no": "HB2",
            "session_year": 2025,
            "version_label": "Introduced",
            "source_url": f"{gencourt_web.BILLINFO}?id={legislation_id}&inflect=2",
        },
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sql_samples()
    hb2_2025_sections()
    print("Spike complete.")


if __name__ == "__main__":
    main()
