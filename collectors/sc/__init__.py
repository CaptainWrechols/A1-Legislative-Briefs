"""South Carolina collectors — isolated adapters for scstatehouse.gov + OpenStates.

Nothing in this package touches the Nevada/NELIS collectors or collectors/nh.
See docs/sc-data-sources.md for the proven data routes and
docs/sc-appropriations-proviso-workflow.md for the budget-proviso workflow.

Canonical registries live here so every module (and every issue config) agrees
on session numbers, scstatehouse path segments, OpenStates identifiers, and
General Appropriations cycles.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Sessions ("back to 2020" = the 123rd General Assembly onward, because 2020
# is the second year of the two-year 123rd session; bill numbers persist
# across a session's two years).
# ---------------------------------------------------------------------------
SESSIONS: list[dict] = [
    {
        "number": 123,
        "label": "123rd (2019-2020)",
        "years": [2019, 2020],
        "openstates_identifier": "2019-2020",
        "scstatehouse_path": "sess123_2019-2020",
    },
    {
        "number": 124,
        "label": "124th (2021-2022)",
        "years": [2021, 2022],
        "openstates_identifier": "2021-2022",
        "scstatehouse_path": "sess124_2021-2022",
    },
    {
        "number": 125,
        "label": "125th (2023-2024)",
        "years": [2023, 2024],
        "openstates_identifier": "2023-2024",
        "scstatehouse_path": "sess125_2023-2024",
    },
    {
        "number": 126,
        "label": "126th (2025-2026)",
        "years": [2025, 2026],
        "openstates_identifier": "2025-2026",
        "scstatehouse_path": "sess126_2025-2026",
    },
]

SESSION_BY_NUMBER = {s["number"]: s for s in SESSIONS}


def session_for_year(year: int) -> dict | None:
    for s in SESSIONS:
        if year in s["years"]:
            return s
    return None


# ---------------------------------------------------------------------------
# General Appropriations cycles (annual — unlike New Hampshire's biennial
# HB1/HB2). "year" is the calendar year of the appropriations directory on
# scstatehouse.gov (…/appropriations{year}/…); Part IB = policy provisos.
#
# Version prefixes on the budget index/text files, in enactment order:
#   wm = Ways & Means, hp = House-passed, sf = Senate Finance,
#   sp = Senate-passed, hr = House amendments returned, cr = Conference
#   Report, ta = ratified/enacted ("as passed by the General Assembly").
# Enacted Part IB full text: …/appropriations{year}/tap1b.htm (verified live
# for 2019 and 2021-2026; see docs/sc-data-sources.md).
# ---------------------------------------------------------------------------
BUDGET_CYCLES: list[dict] = [
    {
        "fiscal_year": "2020-2021",
        "year": 2020,
        "bill_no": "H5201",
        "session": 123,
        "enacted": False,
        "best_version": "sf",  # Senate Finance (Sept 2020) is the last version
        "note": (
            "COVID year: H.5201 died in committee; FY2020-21 ran on continuing "
            "resolution H.3411 plus CARES acts (H.5202, H.3210, H.4014). "
            "There is no enacted Part IB for this cycle."
        ),
    },
    {"fiscal_year": "2021-2022", "year": 2021, "bill_no": "H4100",
     "session": 124, "enacted": True, "best_version": "ta"},
    {"fiscal_year": "2022-2023", "year": 2022, "bill_no": "H5150",
     "session": 124, "enacted": True, "best_version": "ta"},
    {"fiscal_year": "2023-2024", "year": 2023, "bill_no": "H4300",
     "session": 125, "enacted": True, "best_version": "ta"},
    {"fiscal_year": "2024-2025", "year": 2024, "bill_no": "H5100",
     "session": 125, "enacted": True, "best_version": "ta"},
    {"fiscal_year": "2025-2026", "year": 2025, "bill_no": "H4025",
     "session": 126, "enacted": True, "best_version": "ta"},
    {"fiscal_year": "2026-2027", "year": 2026, "bill_no": "H5126",
     "session": 126, "enacted": True, "best_version": "ta"},
]

BUDGET_CYCLE_BY_YEAR = {c["year"]: c for c in BUDGET_CYCLES}
