#!/usr/bin/env python3
"""Curate Part IB budget provisos for south-carolina-04-slow-wage-growth.

The term-matched sets in provisos/{year}/proviso-relevant.json are broad
(566-674 provisos per cycle). This script encodes the hand review: the
provisos that actually bear on wages and workforce pathways, verified by
reading caption + text, with the FY 2020-21 no-enacted-Part-IB gap stated
explicitly.

Output: working/south-carolina/slow-wage-growth/proviso-curated.json
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "proviso-curated.json")

# caption -> plain note (why it matters for this issue)
NOTES = {
    "GP: Lead Apprenticeship Agency": "Names the technical college board (through Apprenticeship Carolina) the lead agency for all registered apprenticeships in the state. This designation exists only as a one-year budget rule, not permanent law.",
    "TEC: Critical Statewide Workforce Needs": "Directs technical college STEM/workforce money to the fields with the most unmet employer demand, set with the Commerce and workforce agencies.",
    "TEC: SC Workforce Competitiveness Initiative": "Funds a public-awareness campaign about manufacturing and related careers.",
    "TEC: IDD Workforce Pilot": "A pilot program helping people with intellectual and developmental disabilities into the workforce.",
    "TEC: Dual Enrollment Courses": "Sets rules for technical college dual-enrollment courses.",
    "TEC: Denmark Technical College": "Targeted support for Denmark Technical College.",
    "SDE-EIA: Career Cluster Industry Partnerships": "Grants to industry groups running certified career and technology education programs (automotive, construction, healthcare, and more).",
    "SDE-EIA: Career and Technology Education": "Funds career and technology education in schools.",
    "SDE: SC Future Makers and Tallo": "Funds a platform connecting students to South Carolina employers.",
    "GP: Employee Compensation": "The annual state-employee pay raise is set here, inside the budget, not in a standalone pay law.",
    "LEA lottery funding (SC WINS line)": "Lottery money funds the SC Workforce Industry Needs Scholarship for technical college students each year.",
}

# (fiscal_year, bill_no, [(proviso, caption, extra)]) — extra holds verbatim
# figures pulled from the proviso text where the brief may cite them.
SELECTION = [
    ("2020-2021", "H5201", None,
     "No enacted Part IB this cycle: H5201 died in committee during COVID; the state ran on continuing resolution H3411 plus CARES acts."),
    ("2021-2022", "H4100", [
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("1A.33", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.58", "SDE-EIA: Career and Technology Education", None),
        ("3.5", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $17,000,000"),
        ("117.169", "GP: Employee Compensation", "State employee base pay raised 2.5%"),
    ], None),
    ("2022-2023", "H5150", [
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("1A.33", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.57", "SDE-EIA: Career and Technology Education", None),
        ("3.5", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $17,000,000"),
        ("117.149", "GP: Employee Compensation", "State employee base pay raised 3%"),
    ], None),
    ("2023-2024", "H4300", [
        ("117.165", "GP: Lead Apprenticeship Agency", "First appearance of the lead-agency designation"),
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("1A.28", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.51", "SDE-EIA: Career and Technology Education", None),
        ("3.6", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $93,739,407"),
        ("117.144", "GP: Employee Compensation", "State employee raise: $2,500 (making $50,000 or less) or 5% (making more)"),
    ], None),
    ("2024-2025", "H5100", [
        ("117.163", "GP: Lead Apprenticeship Agency", None),
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("25.9", "TEC: IDD Workforce Pilot", None),
        ("1.102", "SDE: SC Future Makers and Tallo", None),
        ("1A.28", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.51", "SDE-EIA: Career and Technology Education", None),
        ("3.6", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $78,651,047"),
        ("117.142", "GP: Employee Compensation", "State employee raise: $1,125 (making $50,000 or less) or 2.25% (making more)"),
    ], None),
    ("2025-2026", "H4025", [
        ("117.159", "GP: Lead Apprenticeship Agency", None),
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("25.10", "TEC: SC Workforce Competitiveness Initiative", None),
        ("25.8", "TEC: IDD Workforce Pilot", None),
        ("25.12", "TEC: Denmark Technical College", None),
        ("25.14", "TEC: Dual Enrollment Courses", None),
        ("1.98", "SDE: SC Future Makers and Tallo", None),
        ("1A.28", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.51", "SDE-EIA: Career and Technology Education", None),
        ("3.7", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $54,324,046"),
        ("117.141", "GP: Employee Compensation", "State employee base pay raised 2%"),
    ], None),
    ("2026-2027", "H5126", [
        ("117.155", "GP: Lead Apprenticeship Agency", None),
        ("25.4", "TEC: Critical Statewide Workforce Needs", None),
        ("25.8", "TEC: SC Workforce Competitiveness Initiative", None),
        ("25.7", "TEC: IDD Workforce Pilot", None),
        ("25.9", "TEC: Denmark Technical College", None),
        ("25.10", "TEC: Dual Enrollment Courses", None),
        ("1.94", "SDE: SC Future Makers and Tallo", None),
        ("1A.27", "SDE-EIA: Career Cluster Industry Partnerships", None),
        ("1A.50", "SDE-EIA: Career and Technology Education", None),
        ("3.8", "LEA lottery funding (SC WINS line)", "SC WINS scholarships: $24,717,545"),
        ("117.138", "GP: Employee Compensation", "State employee base pay raised 2%"),
    ], None),
]

# captions as they appear in the source files (LEA line differs per year)
LEA_RE = re.compile(r"LEA: .*Lottery Funding")


def main():
    cycles = []
    for entry in SELECTION:
        fy, bill_no = entry[0], entry[1]
        picks, gap_note = entry[2], entry[3]
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
            src_caption = pv["caption"]
            if caption != "LEA lottery funding (SC WINS line)" and src_caption != caption:
                raise SystemExit("caption mismatch %s %s: %r vs %r" % (fy, pid, caption, src_caption))
            if caption == "LEA lottery funding (SC WINS line)" and not LEA_RE.match(src_caption):
                raise SystemExit("LEA caption mismatch %s %s: %r" % (fy, pid, src_caption))
            rows.append({
                "proviso": pid,
                "caption": src_caption,
                "display_caption": caption,
                "why_relevant": NOTES[caption],
                "verbatim_figure": extra,
            })
        cycles.append({"fiscal_year": fy, "bill_no": bill_no, "enacted": True,
                       "provisos": rows})
    out = {
        "issue": "south-carolina-04-slow-wage-growth",
        "note": ("Hand-curated wage/workforce provisos from Part IB of each enacted "
                 "appropriations act (term-matched candidate sets in provisos/{year}/). "
                 "Budget provisos are one-year rules enacted inside the annual budget bill; "
                 "votes attach to the whole appropriations bill (or a named amendment), never "
                 "to one proviso. FY 2020-21 had no enacted Part IB (COVID continuing "
                 "resolution) — stated explicitly per the workflow's none-found rule."),
        "cycles": cycles,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    n = sum(len(c["provisos"]) for c in cycles)
    print("curated", n, "provisos across", len(cycles), "cycles")


if __name__ == "__main__":
    main()
