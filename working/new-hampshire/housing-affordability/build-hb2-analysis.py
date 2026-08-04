#!/usr/bin/env python3
"""Build the consolidated, hand-curated HB2 housing analysis for this issue.

Reads the collector's per-cycle outputs (working/.../hb2/{year}/) and writes
the issue-level files the mission requires:

  working/new-hampshire/housing-affordability/hb2-sections.json
  working/new-hampshire/housing-affordability/hb2-sections.md

The keep/drop decisions and plain-language summaries below are the human
curation pass over the term-matched candidates (recall-first matching produced
false positives like "rent" inside the rooms-and-meals tax and "housing the
SYSC" as a verb). Vote counts are on the whole HB2 trailer only - never
attributed to a single section.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/build-hb2-analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")

WHOLE_BILL_VOTES = {
    2021: {"chapter": 91,
           "final_votes": [
               {"body": "Senate", "date": "2021-06-24", "motion": "Conference Committee Report", "yeas": 14, "nays": 10},
               {"body": "House", "date": "2021-06-24", "motion": "Adopt Conference Committee Report", "yeas": 198, "nays": 181}],
           "roll_call_count": 42},
    2023: {"chapter": 79,
           "final_votes": [
               {"body": "House", "date": "2023-06-08", "motion": "Concur (with Senate changes)", "yeas": 326, "nays": 53}],
           "roll_call_count": 17},
    2025: {"chapter": 141,
           "final_votes": [
               {"body": "Senate", "date": "2025-06-26", "motion": "Conference Committee Report", "yeas": 16, "nays": 8},
               {"body": "House", "date": "2025-06-26", "motion": "Adopt Conference Committee Report", "yeas": 184, "nays": 183}],
           "roll_call_count": 45},
}

# cite -> (category, plain-language summary). Categories:
#   core     = directly a housing-affordability policy or dollar item
#   adjacent = touches housing but is mainly another policy area
KEEP = {
    2021: {
        "91:23": ("adjacent", "Suspended the state's congregate housing and congregate services programs for older adults (Medicaid waiver services) for the 2022-2023 budget years - a service cut, not an expansion."),
        "91:117": ("adjacent", "Created a study commission on business tax credit carry-overs that was told to examine letting companies put unused credit refunds into affordable housing development."),
        "91:195": ("adjacent", "Created the Office of Planning and Development inside the Department of Business and Economic Affairs - the state office that helps cities and towns with land use planning and housing data."),
        "91:240": ("adjacent", "Directed part of the state's renewable energy fund toward community solar projects that serve manufactured-housing communities and multi-family rental housing."),
        "91:376": ("core", "Put $25 million into the state's Affordable Housing Fund (run by New Hampshire Housing) to finance or match funding for affordable housing projects."),
        "91:408": ("core", "Put $6 million into transitional housing beds - raising the rates paid for the beds and funding new ones for patients leaving New Hampshire Hospital and people with complex behavioral health needs."),
    },
    2023: {
        "79:39": ("core", "Wrote the InvestNH fund and program into law - a standing fund that makes grants and loans to speed up municipal approvals and support housing construction. (InvestNH began in 2022 with federal money; this made it permanent in statute.)"),
        "79:43": ("core", "Put another $25 million into the Affordable Housing Fund, non-lapsing, for financing or matching funds for affordable housing."),
        "79:196": ("adjacent", "Restored $1.5 million for the congregate housing and congregate services programs for older adults that the 2021 budget had suspended."),
        "79:239": ("adjacent", "Within a package of Medicaid rate increases, raised the housing reimbursement rates paid on behalf of people receiving community mental health services."),
        "79:301": ("core", "Repealed the Board of Manufactured Housing (RSA 205-A:25-31) effective September 1, 2023 - the state board where manufactured-home park residents and park owners could resolve disputes without going to court. A separate bill to restructure the board (SB203) died between the chambers the same year."),
        "79:371": ("core", "Created a land use review docket in the superior court - a dedicated court track for appeals of local planning and zoning decisions, intended to speed up housing-related land disputes."),
        "79:462": ("core", "Created the New Hampshire Housing Champion program: cities and towns that volunteer to adopt housing-friendly regulations, train land boards, and invest in water/sewer capacity earn a designation that unlocks state grants. This enacted the substance of SB145, which had passed the Senate 21-3 as a standalone bill."),
        "79:464": ("core", "Created the state staff positions to run the Housing Champion program."),
        "79:465": ("core", "Set up the dedicated-fund accounting so Housing Champion money stays in its own fund."),
        "79:466": ("core", "Funded the Housing Champion program: $5 million for the grant fund plus $250,000 for administration."),
        "79:545": ("core", "Extended the 2021 budget's $6 million transitional-housing-beds appropriation so it would not expire until mid-2025."),
        "79:564": ("core", "Put $8 million into raising the rates the state pays homeless shelter programs, plus $2 million for shelter assistance including cold-weather shelter and hotel placements."),
        "79:579": ("adjacent", "Ordered New Hampshire Housing to study a graduated, proportional rental assistance voucher for people who do not qualify for existing programs, reporting by November 2023."),
    },
    2025: {
        "141:31": ("adjacent", "Reorganized the state planning office into a Division of Planning and Community Development that administers the state's planning, broadband, and housing programs."),
        "141:45": ("core", "Directed $5 million a year for two years from the opioid abatement trust fund to year-round emergency shelter for people with opioid use disorder, with services aimed at recovery and permanent housing."),
        "141:56": ("adjacent", "Funded congregate housing and congregate services for older adults at $350,000 a year for two years."),
        "141:212": ("core", "Created the Partners in Housing program: state funding for workforce housing built on city-, town-, or county-owned land that is transferred to developers, with at least 20 percent of units meeting workforce-housing rules."),
        "141:213": ("core", "Let municipalities fast-track site plan review for residential projects on state-listed surplus properties, and let solely residential workforce-housing projects use the quicker 'minor site plan review' where a town has adopted it."),
        "141:214": ("core", "Extended the Housing Champion fund's purpose to also pay for compiling the list of municipal and county property suitable for residential development."),
        "141:335": ("core", "Shrank the Housing Appeals Board - the state board that hears appeals of local zoning and planning decisions - from 3 members to 2."),
        "141:336": ("core", "Attached the Housing Appeals Board to the Board of Tax and Land Appeals for budget and administration, with shared staff."),
        "141:337": ("core", "Changed Housing Appeals Board members from fixed terms to serving 'at the pleasure of' the governor and Executive Council, who also pick the chair."),
        "141:338": ("core", "Set a tie-breaker rule for the now 2-member Housing Appeals Board: a member of the Board of Tax and Land Appeals casts the deciding vote."),
        "141:340": ("adjacent", "Adjusted the Board of Tax and Land Appeals quorum rules to fit its new role backing up the Housing Appeals Board."),
        "141:355": ("core", "Extended the 2023 Housing Champion appropriation ($5 million) so it would not lapse until mid-2026."),
        "141:418": ("core", "Ordered the state to renew and fully implement a Medicaid benefit paying for supportive housing services, with progress reports to the legislature in 2025 and 2026."),
    },
}

# Term-matched candidates reviewed and excluded, with the reason (audit trail).
EXCLUDED = {
    2021: {
        "91:5": "State plant/property management reorganization; no housing content (matched ' rent' inside unrelated text).",
        "91:8": "Consolidation of HR/payroll functions; no housing content.",
        "91:19": "Sale of the former Laconia State School property; the section text sets sale terms and does not address housing.",
        "91:60": "Education trust fund mechanics; mentions the existing low/moderate-income homeowners property tax relief only in passing.",
        "91:103": "Rooms and meals tax rate cut; 'rent' here is hotel-room occupancy, not residential housing.",
        "91:114": "Education trust fund reference change; same as 91:60.",
        "91:122": "Wildlife damage/posting of land; 'dwelling' and 'tenant' appear in a hunting-law context.",
        "91:178": "Speech-language pathology licensing; term match inside unrelated text.",
        "91:183": "Hearing aid dealer registration; term match inside unrelated text.",
        "91:187": "Creates the Department of Energy; 'land use' appears in an energy-siting context.",
        "91:199": "Council on Resources and Development membership housekeeping.",
        "91:220": "Energy efficiency board membership housekeeping.",
        "91:269": "'Shared tenant services' is a telecommunications term, not residential tenancy.",
        "91:278": "Utility energy-efficiency loan programs; tenants appear only as loan-program participants.",
        "91:302": "Animal records database; term match inside unrelated text.",
        "91:303": "Dog and cat transfer certificates; 'shelter' is animal shelter.",
        "91:369": "National Guard scholarship reference removal; term match inside unrelated text.",
        "91:378": "OHRV trail grants; term match inside unrelated text.",
        "91:76": "Professional-licensing office reorganization; the Board of Manufactured Housing appears only in a list of boards being re-homed administratively.",
    },
    2023: {
        "79:103": "Telecom use of highway rights-of-way; 'zoning' appears in an infrastructure context.",
        "79:138": "Education trust fund rewrite; homeowners property tax relief mentioned only in passing.",
        "79:348": "Public works definition housekeeping.",
        "79:415": "Medicaid doula coverage; term match inside unrelated text.",
        "79:505": "OHRV trail grants; term match inside unrelated text.",
        "79:568": "Long-term-care system of care; housing appears only as part of aging-services planning.",
        "79:583": "Charitable gaming study commission; term match inside unrelated text.",
    },
    2025: {
        "141:129": "State surplus distribution accounting; no housing content.",
        "141:180": "Court fee schedule rewrite; landlord/tenant filings appear only in a list of court fee categories being restructured.",
        "141:181": "Sununu Youth Services Center transfer; 'housing' is used as a verb ('property currently housing the SYSC').",
        "141:189": "OHRV trail grants; term match inside unrelated text.",
        "141:209": "Select board authority to rent out town property; municipal property management, not residential housing policy.",
        "141:324": "Office building (One Granite Place) appropriation; 'rent' is state office rent.",
        "141:335-357 note": None,  # placeholder removed below
        "141:357": "Sale of the Sununu Youth Services Center; 'housing' is used as a verb.",
        "141:370": "Court-related committee membership; term match inside unrelated text.",
    },
}
EXCLUDED[2025].pop("141:335-357 note")


def main() -> None:
    cycles = []
    for year in (2021, 2023, 2025):
        secs = json.loads((W / "hb2" / str(year) / "hb2-sections.json").read_text())
        idx = {s.get("chapter_cite") or str(s["section"]): s for s in secs["sections"]}
        # 2025 sections are keyed by bare number with text prefixed 141:N
        def get(cite):
            return idx.get(cite) or idx.get(cite.split(":")[1])
        kept = []
        for cite, (cat, plain) in KEEP[year].items():
            s = get(cite)
            kept.append({
                "cite": cite if ":" in cite else f"{WHOLE_BILL_VOTES[year]['chapter']}:{cite}",
                "heading": s["heading"].replace(f"{cite} ", "", 1),
                "category": cat,
                "plain_language": plain,
                "affected_rsas": s["affected_rsas"],
            })
        kept.sort(key=lambda r: int(r["cite"].split(":")[1]))
        excluded = [{"cite": c, "reason": r} for c, r in sorted(
            EXCLUDED[year].items(), key=lambda kv: int(kv[0].split(":")[1]))]
        meta = WHOLE_BILL_VOTES[year]
        cycles.append({
            "session_year": year,
            "bill_no": "HB2",
            "chapter": meta["chapter"],
            "laws_citation": f"Laws of {year}, Chapter {meta['chapter']}",
            "total_sections_extracted": secs["section_count"],
            "source": secs.get("source"),
            "source_url": secs.get("source_url") or secs.get("url"),
            "whole_bill_roll_call_count": meta["roll_call_count"],
            "whole_bill_final_votes": meta["final_votes"],
            "relevant_sections": kept,
            "excluded_candidates": excluded,
        })

    out = {
        "issue": "new-hampshire-01-housing-affordability",
        "note": (
            "Hand-curated housing analysis of HB2, New Hampshire's omnibus "
            "budget policy trailer, for the 2021, 2023, and 2025 budget "
            "cycles. Candidates came from relevance-term matching over every "
            "extracted section (see working/.../hb2/{year}/); a human pass "
            "kept the housing sections and logged every exclusion. Roll-call "
            "votes are recorded on HB2 AS A WHOLE - a vote for or against the "
            "trailer is never a vote on one section, and must not be "
            "presented as one."
        ),
        "cycles": cycles,
    }
    (W / "hb2-sections.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# HB2 (budget policy trailer) — housing sections, 2021 / 2023 / 2025",
        "",
        "New Hampshire passes its two-year budget in two bills: HB1 (the money)",
        "and HB2, a policy 'trailer' that bundles dozens to hundreds of legal",
        "changes into one bill. Housing policy that never moved as a standalone",
        "bill often becomes law inside HB2. This file is the hand-reviewed,",
        "section-level housing analysis for the three budget cycles in scope.",
        "",
        "**Votes are on the whole trailer.** Every roll call below was cast on",
        "HB2 as a package. A lawmaker's vote on HB2 says nothing certain about",
        "any single section.",
        "",
    ]
    for c in cycles:
        lines += [
            f"## HB2 {c['session_year']} — {c['laws_citation']}",
            "",
            f"*{c['total_sections_extracted']} sections extracted; "
            f"{len(c['relevant_sections'])} housing-relevant after review; "
            f"{c['whole_bill_roll_call_count']} floor roll calls on the whole bill.*",
            "",
            "Final passage (whole bill): " + "; ".join(
                f"{v['body']} {v['yeas']}–{v['nays']} ({v['motion']}, {v['date']})"
                for v in c["whole_bill_final_votes"]) + ".",
            "",
        ]
        for cat, label in (("core", "Core housing sections"),
                           ("adjacent", "Adjacent (housing-touching) sections")):
            subset = [s for s in c["relevant_sections"] if s["category"] == cat]
            if not subset:
                continue
            lines += [f"### {label}", ""]
            for s in subset:
                rsas = f" *(affects {', '.join(s['affected_rsas'][:4])})*" if s["affected_rsas"] else ""
                lines += [f"- **{s['cite']} — {s['heading']}.** {s['plain_language']}{rsas}"]
            lines += [""]
        lines += ["### Reviewed and excluded (false positives)", ""]
        for e in c["excluded_candidates"]:
            lines += [f"- {e['cite']}: {e['reason']}"]
        lines += [""]
    (W / "hb2-sections.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote hb2-sections.json and hb2-sections.md "
          f"({sum(len(c['relevant_sections']) for c in cycles)} kept sections)")


if __name__ == "__main__":
    main()
