#!/usr/bin/env python3
"""Curate Part IB budget provisos for south-carolina-01-growth-infrastructure-roads.

The term-matched sets in provisos/{year}/proviso-relevant.json are broad
(246-305 provisos per cycle). This script encodes the hand review: the
provisos that actually bear on roads, growth, local infrastructure funding,
and SCDOT accountability, verified by reading caption + text, with the
FY 2020-21 no-enacted-Part-IB gap stated explicitly.

Output: working/south-carolina/growth-infrastructure-roads/proviso-curated.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "proviso-curated.json")

# caption -> plain note (why it matters for this issue)
NOTES = {
    "GP: School Construction Development Impact Fee Assessment Prohibition":
        "Barred local governments from charging development impact fees on new school construction, on pain of losing state aid - a one-year limit on the impact-fee tool that appeared only in this budget and was not renewed.",
    "CTC: Increased Funding":
        "Requires that the extra gas-tax money Act 40 of 2017 sends to County Transportation Committees be spent exclusively on repairs, maintenance, and improvements to the state highway system - a renewed-every-year fix-it-first rule for the county road boards.",
    "DOT: Preventative Maintenance Credit":
        "Authorized SCDOT to transfer part of the gas user fee to cover the Act 40 preventative-maintenance tax credit for drivers. This authorization appeared every enacted budget from FY 2021-22 through FY 2024-25 and stopped appearing in FY 2025-26.",
    "SR: Nonrecurring Revenue":
        "The budget's one-time money list - where the big single-year infrastructure sums ride.",
    "SR: Homestead Exemption Fund":
        "A one-time $600 million sweep from the Homestead Exemption Fund whose priority list put $200,000,000 into a CTC Acceleration Fund for county road boards, $100,000,000 into a Bridge Acceleration Fund, and $117,401,000 into a Rural Road Safety Program - the largest one-year roads package in this record.",
    "DOT: Programmed Project Viewer Dashboard":
        "Directs SCDOT to upgrade its public Programmed Project Viewer dashboard - project status, forecast versus actual cost, completion dates, and an on-time/on-budget list - with quarterly reports to the budget chairmen. A transparency rule aimed at exactly the project-accountability question citizens raised.",
    "DOT: Project Priority List":
        "Requires SCDOT to publish its project priority lists - and the engineering directives explaining the ranking methodology - in a conspicuous, publicly accessible place on its website.",
    "DOT: Road Buyback Program":
        "New this year: directs SCDOT to identify state roads that no longer serve a statewide purpose and negotiate transferring them to counties and cities, with buyback funds paying for resurfacing and transition costs - the state shrinking its road inventory by paying locals to take roads back.",
}

# (fiscal_year, bill_no, [(proviso, caption, verbatim_figure)], gap_note)
SELECTION = [
    ("2020-2021", "H5201", None,
     "No enacted Part IB this cycle: H5201 died in committee during COVID; the state ran on continuing resolution H3411 plus CARES acts."),
    ("2021-2022", "H4100", [
        ("117.96", "GP: School Construction Development Impact Fee Assessment Prohibition",
         "One-year rule; not renewed in any later budget"),
        ("86.1", "CTC: Increased Funding", "First budget in scope with the Act 40 fix-it-first rule"),
        ("84.12", "DOT: Preventative Maintenance Credit", None),
        ("118.18", "SR: Nonrecurring Revenue",
         "State Ports Authority intermodal container transfer facility and waterborne cargo infrastructure: $200,000,000"),
    ], None),
    ("2022-2023", "H5150", [
        ("118.19", "SR: Nonrecurring Revenue",
         "Department of Transportation, Rural Interstate Funding: $133,636,230"),
        ("86.1", "CTC: Increased Funding", None),
        ("84.12", "DOT: Preventative Maintenance Credit", None),
    ], None),
    ("2023-2024", "H4300", [
        ("84.9", "DOT: Project Priority List", None),
        ("86.1", "CTC: Increased Funding", None),
        ("84.12", "DOT: Preventative Maintenance Credit", None),
    ], None),
    ("2024-2025", "H5100", [
        ("118.22", "SR: Homestead Exemption Fund",
         "CTC Acceleration Fund $200,000,000; Bridge Acceleration Fund $100,000,000; Rural Road Safety Program $117,401,000"),
        ("84.18", "DOT: Programmed Project Viewer Dashboard", "First appearance of the dashboard-upgrade directive"),
        ("86.1", "CTC: Increased Funding", None),
    ], None),
    ("2025-2026", "H4025", [
        ("118.22", "SR: Nonrecurring Revenue",
         "Department of Transportation, Bridge Modernization: $200,000,000"),
        ("84.16", "DOT: Programmed Project Viewer Dashboard", None),
    ], None),
    ("2026-2027", "H5126", [
        ("84.18", "DOT: Road Buyback Program", "New for FY 2026-27"),
        ("118.21", "SR: Nonrecurring Revenue",
         "CTC Acceleration $175,000,000; Department of Transportation Bridge Modernization: $50,000,000"),
        ("86.1", "CTC: Increased Funding", None),
    ], None),
]


def main():
    cycles = []
    for fy, bill_no, picks, gap_note in SELECTION:
        if picks is None:
            cycles.append({"fiscal_year": fy, "bill_no": bill_no,
                           "enacted": False, "provisos": [], "note": gap_note})
            continue
        year = fy.split("-")[0]
        src = json.load(open(os.path.join(HERE, "provisos", year, "proviso-relevant.json")))
        by_id = {pv["proviso"]: pv for pv in src["provisos"]}
        rows = []
        for pid, caption, extra in picks:
            pv = by_id.get(pid)
            if pv is None:
                raise SystemExit("proviso %s not found for %s" % (pid, fy))
            if pv["caption"] != caption:
                raise SystemExit("caption mismatch %s %s: %r vs %r" % (fy, pid, caption, pv["caption"]))
            rows.append({
                "proviso": pid,
                "caption": pv["caption"],
                "why_relevant": NOTES[caption],
                "verbatim_figure": extra,
            })
        cycles.append({"fiscal_year": fy, "bill_no": bill_no, "enacted": True,
                       "provisos": rows})
    out = {
        "issue": "south-carolina-01-growth-infrastructure-roads",
        "note": ("Hand-curated roads/growth/infrastructure provisos from Part IB of each "
                 "enacted appropriations act (term-matched candidate sets in provisos/{year}/). "
                 "Budget provisos are one-year rules enacted inside the annual budget bill; "
                 "votes attach to the whole appropriations bill (or a named amendment), never "
                 "to one proviso. Dollar figures are verbatim from the enacted Part IB text. "
                 "FY 2020-21 had no enacted Part IB (COVID continuing resolution) - stated "
                 "explicitly per the workflow's none-found rule."),
        "cycles": cycles,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    n = sum(len(c["provisos"]) for c in cycles)
    print("curated", n, "provisos across", len(cycles), "cycles")


if __name__ == "__main__":
    main()
