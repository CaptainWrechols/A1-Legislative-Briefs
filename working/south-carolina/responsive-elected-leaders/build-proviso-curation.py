#!/usr/bin/env python3
"""Curate Part IB budget provisos for south-carolina-02-responsive-elected-leaders.

The term-matched sets in provisos/{year}/proviso-relevant.json are broad
(191-234 provisos per cycle). This script encodes the hand review: the
provisos that actually bear on ethics enforcement, election-law power,
lobbying restrictions, and civic education, verified by reading caption +
text, with the FY 2020-21 no-enacted-Part-IB gap stated explicitly.

Output: working/south-carolina/responsive-elected-leaders/proviso-curated.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "proviso-curated.json")

# caption -> plain note (why it matters for this issue)
NOTES = {
    "GP: Ethics Filing": "New this year: officials who report income paid by the state budget on their statement of economic interests must name the specific government body that paid them. A disclosure tightening enacted as a one-year budget rule in the same year the H3570 disclosure bill died in conference.",
    "GP: Actions on Election Law": "Gives the Senate President and House Speaker an unconditional right to intervene in any lawsuit challenging an election law or how an election is run. This litigation power exists only as a one-year budget rule, renewed every cycle.",
    "ETHICS: Ethics Commission Website Changes": "The State Ethics Commission cannot change its public disclosure and accountability reporting system without the approval of the House and Senate Ethics Committees - the legislature keeps veto power over the watchdog's own website.",
    "ETHICS: Commission Meeting": "Requires the State Ethics Commission to meet at least monthly and post notice 24 hours ahead on its website.",
    "SR: Prohibits Public Funded Lobbyists": "Bars every state agency and institution from using general-fund money to employ or contract lobbyists, certified through the State Ethics Commission.",
    "GP: Prohibits Local Government Fund Public Funded Lobbyists": "Bars counties, cities, and their associations from using Local Government Fund money to pay employees for lobbying.",
    "ELECT: November 2020 Election Investigation Report": "One-time rule: the Election Commission had to report to the General Assembly the number of election-fraud investigations from the November 2020 election and post the report publicly.",
    "CU-PSA: Feasibility Study": "Funded a Clemson feasibility study for a Center for Civic Engagement to cultivate civic engagement and leadership.",
    "SR: Nonrecurring Revenue (USC civic leadership line)": "One-time money list that includes $2,500,000 for a Center for American Civic Leadership and Public Discourse at USC - civic-education funding placed in the budget, not a standalone law.",
}

# (fiscal_year, bill_no, [(proviso, caption, extra)], gap_note)
SELECTION = [
    ("2020-2021", "H5201", None,
     "No enacted Part IB this cycle: H5201 died in committee during COVID; the state ran on continuing resolution H3411 plus CARES acts."),
    ("2021-2022", "H4100", [
        ("117.191", "GP: Actions on Election Law", "First appearance of the litigation-intervention rule"),
        ("110.1", "ETHICS: Ethics Commission Website Changes", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.95", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
        ("102.14", "ELECT: November 2020 Election Investigation Report", None),
    ], None),
    ("2022-2023", "H5150", [
        ("117.160", "GP: Actions on Election Law", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.94", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
    ], None),
    ("2023-2024", "H4300", [
        ("117.152", "GP: Actions on Election Law", None),
        ("110.1", "ETHICS: Ethics Commission Website Changes", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.94", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
    ], None),
    ("2024-2025", "H5100", [
        ("117.150", "GP: Actions on Election Law", None),
        ("110.1", "ETHICS: Ethics Commission Website Changes", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.93", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
        ("45.11", "CU-PSA: Feasibility Study", "Center for Civic Engagement feasibility study"),
    ], None),
    ("2025-2026", "H4025", [
        ("117.148", "GP: Actions on Election Law", None),
        ("110.1", "ETHICS: Ethics Commission Website Changes", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.93", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
    ], None),
    ("2026-2027", "H5126", [
        ("117.219", "GP: Ethics Filing", "New for FY 2026-27"),
        ("117.145", "GP: Actions on Election Law", None),
        ("110.2", "ETHICS: Commission Meeting", None),
        ("118.6", "SR: Prohibits Public Funded Lobbyists", None),
        ("117.92", "GP: Prohibits Local Government Fund Public Funded Lobbyists", None),
        ("118.21", "SR: Nonrecurring Revenue (USC civic leadership line)", "USC Center for American Civic Leadership and Public Discourse: $2,500,000"),
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
            src_caption = pv["caption"]
            if caption.startswith("SR: Nonrecurring Revenue"):
                if src_caption != "SR: Nonrecurring Revenue":
                    raise SystemExit("caption mismatch %s %s: %r" % (fy, pid, src_caption))
            elif src_caption != caption:
                raise SystemExit("caption mismatch %s %s: %r vs %r" % (fy, pid, caption, src_caption))
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
        "issue": "south-carolina-02-responsive-elected-leaders",
        "note": ("Hand-curated ethics/elections/lobbying/civics provisos from Part IB of each "
                 "enacted appropriations act (term-matched candidate sets in provisos/{year}/). "
                 "Budget provisos are one-year rules enacted inside the annual budget bill; "
                 "votes attach to the whole appropriations bill (or a named amendment), never "
                 "to one proviso. FY 2020-21 had no enacted Part IB (COVID continuing "
                 "resolution) - stated explicitly per the workflow's none-found rule."),
        "cycles": cycles,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    n = sum(len(c["provisos"]) for c in cycles)
    print("curated", n, "provisos across", len(cycles), "cycles")


if __name__ == "__main__":
    main()
