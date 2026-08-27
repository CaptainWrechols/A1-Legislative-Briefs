#!/usr/bin/env python3
"""Curate Part IB budget provisos for south-carolina-03-rising-cost-of-living.

The term-matched sets in provisos/{year}/proviso-relevant.json are broad
(434-564 provisos per cycle). This script encodes the hand review: the
provisos that actually bear on utility oversight, personal-finance
education, tax relief, and housing costs, verified by reading caption +
text, with the FY 2020-21 no-enacted-Part-IB gap stated explicitly.

Notable: no proviso in any cycle funds or directs personal-finance /
financial-literacy instruction EXCEPT FY 2022-23 proviso 1.101, which
ordered the State Board of Education to write the half-credit personal
finance graduation requirement into regulation — the regulation (Document
5130, amending R.43-234) took effect May 26, 2023 and applies beginning
with the 2023-24 freshman class.

Output: working/south-carolina/rising-cost-of-living/proviso-curated.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "proviso-curated.json")

# caption -> plain note (why it matters for this issue)
NOTES = {
    "SDE: Graduation Requirements": "Ordered the State Board of Education to write a required half-credit in personal finance into the high school graduation regulation — the route by which the citizens' financial-education idea actually became policy after the S16 bill died in conference. One-time proviso; the regulation (Document 5130) took effect May 26, 2023.",
    "GP: Tax Rate": "Suspends the income tax law's phase-in trigger subsections (Section 12-6-510(B)(2) and (3)) for the year, so the rate table applies as written instead of waiting on revenue triggers — the budget's lever for accelerating the income tax cut.",
    "GP: Homestead Exemption": "An extra $25,000 homestead exemption for seniors and disabled homeowners who already qualify under Section 12-37-250, on top of the standing $50,000 — with the state reimbursing local governments. A one-year property-tax cut that exists only in the budget.",
    "GP: Property Tax Bill Payments - Third-Party Authorization": "Lets anyone pay someone else's property tax bill without proof of authorization (no ownership rights conferred).",
    "GP: Homestead Exemption Fund": "Suspends subsection (C) of the Homestead Exemption Fund statute (Section 11-11-156) for the year — a recurring budget-side adjustment to how the school-operating property-tax relief fund's rules run.",
    "GP: Personal Property Tax Relief Fund": "Backstops counties that swapped vehicle/personal property taxes for a local sales tax: if the 2% sales tax falls short, the state Trust Fund for Tax Relief covers the gap.",
    "SR: Tax Relief Reserve Fund": "Creates a reserve fund, separate from the General Fund, that may only be used to provide tax relief to businesses and individuals as provided by law.",
    "SR: Homestead Exemption Fund": "Moved $600 million of accumulated Homestead Exemption Fund balance into the budget as nonrecurring revenue, suspending the fund's use restrictions for the year.",
    "DOR: Manufacturing Property Tax Reduction": "Denies utilities (including solar farms) the manufacturing property tax reduction percentage for the year — keeping utility property fully on local tax rolls.",
    "PSC: Santee Cooper Funds Held by Public Service Commission": "Keeps the money transferred for reforming Santee Cooper available to the Public Service Commission, including hiring outside experts.",
    "PSC: Santee Cooper Billing": "Lets the Public Service Commission bill Santee Cooper for the cost of overseeing it under the 2021 reform law (Act 90) — the oversight regime's funding lives here, in the budget.",
    "GP: Funds Transferred to Santee Cooper": "Distributed the money held from the Santee Cooper sale-evaluation process (Act 95 of 2019): $2 million to the Office of Regulatory Staff, $1 million to the Public Service Commission, the balance to Santee Cooper, all for reform work.",
    "ORS: Natural Gas Rate Stabilization Act Study": "Ordered the state utility watchdog to study whether the Natural Gas Rate Stabilization Act — the mechanism letting gas utilities adjust rates yearly outside full rate cases — actually serves ratepayers, reporting by December 31, 2021.",
    "ORS: Energy Efficient Manufactured Homes": "Kept the energy-efficient manufactured homes purchase incentive running for another year.",
    "ORS: Energy Office": "Authorizes the state Energy Office to administer federal Infrastructure Investment and Jobs Act and Inflation Reduction Act programs (including household energy money) and carry the funds forward.",
    "HFDA: Federal Rental Assistance Administrative Fee Carry Forward": "Lets the state housing authority carry forward federal rental-assistance administrative fees to keep running assistance programs.",
    "HFDA: SC Housing Statewide Assessment": "Paid for the comprehensive statewide housing needs assessment ($100,000, Darla Moore School of Business) — the state's housing-cost evidence base.",
    "HFDA: Workforce Housing": "Funds the 'Made it Home!' program at the state housing authority: new construction of affordable single-family homes with down-payment assistance.",
}

# (fiscal_year, bill_no, [(proviso, caption, extra)], gap_note)
SELECTION = [
    ("2020-2021", "H5201", None,
     "No enacted Part IB this cycle: H5201 died in committee during COVID; the state ran on continuing resolution H3411 plus CARES acts."),
    ("2021-2022", "H4100", [
        ("73.9", "ORS: Natural Gas Rate Stabilization Act Study", None),
        ("73.5", "ORS: Energy Efficient Manufactured Homes", None),
        ("117.172", "GP: Funds Transferred to Santee Cooper", "$2,000,000 to ORS; $1,000,000 to the PSC; balance to Santee Cooper"),
        ("117.186", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
        ("42.1", "HFDA: Federal Rental Assistance Administrative Fee Carry Forward", None),
    ], None),
    ("2022-2023", "H5150", [
        ("1.101", "SDE: Graduation Requirements", "Half-credit personal finance graduation requirement ordered into regulation"),
        ("72.2", "PSC: Santee Cooper Funds Held by Public Service Commission", None),
        ("42.6", "HFDA: SC Housing Statewide Assessment", "$100,000 statewide housing needs assessment"),
        ("117.158", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
    ], None),
    ("2023-2024", "H4300", [
        ("72.4", "PSC: Santee Cooper Billing", "First appearance of the PSC-bills-Santee-Cooper oversight funding"),
        ("72.2", "PSC: Santee Cooper Funds Held by Public Service Commission", None),
        ("109.16", "DOR: Manufacturing Property Tax Reduction", None),
        ("42.6", "HFDA: SC Housing Statewide Assessment", None),
        ("117.151", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
    ], None),
    ("2024-2025", "H5100", [
        ("72.3", "PSC: Santee Cooper Billing", None),
        ("73.9", "ORS: Energy Office", None),
        ("109.16", "DOR: Manufacturing Property Tax Reduction", None),
        ("118.22", "SR: Homestead Exemption Fund", "$600,000,000 of fund balance used as nonrecurring revenue"),
        ("117.149", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
    ], None),
    ("2025-2026", "H4025", [
        ("117.208", "GP: Tax Rate", "Puts the tax-cut law's 6% top income tax rate into effect for the year"),
        ("72.3", "PSC: Santee Cooper Billing", None),
        ("73.7", "ORS: Energy Office", None),
        ("109.14", "DOR: Manufacturing Property Tax Reduction", None),
        ("117.147", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
    ], None),
    ("2026-2027", "H5126", [
        ("117.220", "GP: Homestead Exemption", "Extra $25,000 homestead exemption for qualifying seniors/disabled homeowners, state-reimbursed"),
        ("117.191", "GP: Tax Rate", None),
        ("117.222", "GP: Property Tax Bill Payments - Third-Party Authorization", None),
        ("42.7", "HFDA: Workforce Housing", "'Made it Home!' affordable single-family construction program"),
        ("72.3", "PSC: Santee Cooper Billing", None),
        ("109.14", "DOR: Manufacturing Property Tax Reduction", None),
        ("117.144", "GP: Homestead Exemption Fund", None),
        ("117.37", "GP: Personal Property Tax Relief Fund", None),
        ("118.9", "SR: Tax Relief Reserve Fund", None),
    ], None),
]


def main():
    cycles = []
    for fy, bill_no, picks, gap_note in SELECTION:
        if picks is None:
            cycles.append({"fiscal_year": fy, "bill_no": bill_no,
                           "enacted": False, "provisos": [],
                           "note": gap_note})
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
                "display_caption": caption,
                "why_relevant": NOTES[caption],
                "verbatim_figure": extra,
            })
        cycles.append({"fiscal_year": fy, "bill_no": bill_no, "enacted": True,
                       "provisos": rows})
    out = {
        "issue": "south-carolina-03-rising-cost-of-living",
        "note": ("Hand-curated cost-of-living provisos (utility oversight, personal-finance "
                 "education, tax relief, housing) from Part IB of each enacted appropriations "
                 "act (term-matched candidate sets in provisos/{year}/). Budget provisos are "
                 "one-year rules enacted inside the annual budget bill; votes attach to the "
                 "whole appropriations bill (or a named amendment), never to one proviso. "
                 "FY 2020-21 had no enacted Part IB (COVID continuing resolution) — stated "
                 "explicitly per the workflow's none-found rule. Financial-education provisos: "
                 "none found in any cycle except FY 2022-23 proviso 1.101 (the graduation-"
                 "requirement order) — an explicit none-found for the other six cycles."),
        "cycles": cycles,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    n = sum(len(c["provisos"]) for c in cycles)
    print("curated", n, "provisos across", len(cycles), "cycles")


if __name__ == "__main__":
    main()
