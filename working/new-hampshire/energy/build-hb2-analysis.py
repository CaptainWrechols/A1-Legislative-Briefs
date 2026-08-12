#!/usr/bin/env python3
"""Build the consolidated, hand-curated HB2 energy analysis for this issue.

Reads the collector's per-cycle outputs (working/.../hb2/{year}/) and writes
the issue-level files the mission requires:

  working/new-hampshire/energy/hb2-sections.json
  working/new-hampshire/energy/hb2-sections.md

The keep/drop decisions and plain-language summaries below are the human
curation pass over the term-matched candidates (recall-first matching produced
false positives like 'transmission' in workers-compensation and budget-process
text, 'utility' in speech-language licensing, and 'generating' revenue). One
section the term matcher missed was added by hand after a full-text sweep
(91:275, the Dig Safe rulemaking companion between the matched 91:274 and
91:276); it is flagged ``hand_added``.

REVERSAL NOTE: the property-taxes and public-education packets both EXCLUDED
the energy and utility sections of these trailers with documented reasons
(2021: the Department of Energy creation 91:187, electric rate reduction
bonds 91:98, PUC assessments 91:243-263, restructuring principles 91:281,
offshore wind 91:201; 2023: PUC assessment mechanics 79:119/122, the EV
sections 79:474-475). This pass re-curates for the energy scope, where those
sections are the core; conversely the education and tax sections those
packets kept are excluded here. Vote counts are on the whole HB2 trailer
only - never attributed to a single section.

Run from repo root:
  python3 working/new-hampshire/energy/build-hb2-analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/energy")

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

HAND_ADDED = {"91:275"}

# cite -> (category, plain-language summary). Categories:
#   core     = directly changes who regulates energy, what ratepayers pay,
#              what gets built, or a major energy program's law
#   adjacent = conforming reference changes, administrative machinery, and
#              appropriations detail that shape the energy system indirectly
KEEP = {
    2021: {
        # ---- the Department of Energy reorganization (the trailer's energy headline) ----
        "91:187": ("core", "Created the Department of Energy (new RSA 12-P): a cabinet agency absorbing most Public Utilities Commission staff and functions plus the old Office of Strategic Initiatives' energy programs - the biggest restructuring of New Hampshire energy regulation since electric restructuring, moving policy, ratepayer advocacy support, and program administration out of the utility tribunal."),
        "91:189": ("adjacent", "The companion repeals: struck the Office of Strategic Initiatives' energy-planning statutes (including its offshore wind industry office) whose functions moved into the new department."),
        "91:188": ("adjacent", "Let the Governor appoint an interim energy commissioner ahead of the department's full stand-up."),
        "91:192": ("adjacent", "Added the Department of Energy to the executive-branch organization statute."),
        "91:193": ("adjacent", "Established the department's unclassified leadership positions (commissioner, deputy, division directors)."),
        "91:194": ("adjacent", "Re-established the slimmed-down Public Utilities Commission's unclassified positions after the staff transfer."),
        "91:200": ("adjacent", "Renamed statutory references from the old offices to the Department of Energy."),
        "91:201": ("adjacent", "Moved the 10-year state energy strategy and the offshore wind commission references from the Office of Strategic Initiatives to the new department."),
        "91:202": ("adjacent", "Moved the least-cost energy planning policy reference to the new department."),
        "91:451": ("adjacent", "Transferred a business-systems position into the Department of Energy."),
        "91:11": ("adjacent", "Let the Department of Administrative Services suspend, for the biennium, its executive-order obligations to identify energy-efficiency projects in state facilities and to track state buildings' and vehicles' energy use, fossil-fuel consumption, and greenhouse-gas emissions."),
        # ---- the restructured PUC ----
        "91:204": ("core", "Rewrote the Public Utilities Commission itself: three full-time commissioners on staggered six-year terms, nominated through a screening process - the leaner adjudicative tribunal left after the department split."),
        "91:206": ("core", "Barred PUC commissioners from taking employment with any utility the commission regulates for one year after leaving office - a revolving-door restriction on the state's utility regulators."),
        "91:205": ("adjacent", "Repealed the old PUC organizational provisions superseded by the rewrite."),
        "91:207": ("adjacent", "Set the two-commissioner quorum rule for the restructured commission."),
        "91:208": ("adjacent", "Let parties request that the full commission hear a case."),
        "91:209": ("adjacent", "Repealed superseded PUC hearing-officer provisions."),
        "91:210": ("adjacent", "Authorized the restructured commission's own staff (general counsel and hearings personnel)."),
        "91:213": ("adjacent", "Repealed superseded PUC staffing statutes."),
        "91:214": ("adjacent", "Split complaint-handling between the new department and the commission."),
        "91:246": ("adjacent", "Conforming split of complaint and proceeding jurisdiction between the department and the commission."),
        "91:247": ("adjacent", "Rewrote who may complain against a public utility and where the complaint goes."),
        "91:248": ("adjacent", "Routed customer complaints to the department, with adjudication before the commission."),
        "91:249": ("adjacent", "Conforming change to commission proceeding rules."),
        "91:250": ("adjacent", "Conforming change to commission proceeding rules."),
        "91:251": ("adjacent", "Repealed a superseded proceedings provision."),
        "91:252": ("adjacent", "Assigned investigation expenses of department and commission proceedings to the utilities investigated (rate-case expense mechanics)."),
        "91:253": ("adjacent", "Conforming change to the civil-penalty statute for utilities, enforceable through the new department."),
        # ---- who pays for regulation: the utility assessments ----
        "91:242": ("core", "Rewrote how the state charges utilities for their own regulation: the expenses of the commission and the new department are assessed against the utilities they regulate."),
        "91:243": ("core", "The assessment formula itself: each public utility is assessed its share of regulatory costs based on gross revenue from New Hampshire customers - the funding backbone for both agencies, which flows into rates."),
        "91:244": ("adjacent", "Certification and collection mechanics for the utility assessment."),
        "91:245": ("adjacent", "Let utilities recover the assessment costs in rates (default service and delivery charges) - the section that passes regulatory costs to ratepayers."),
        # ---- consumer advocate ----
        "91:211": ("core", "Kept the Office of the Consumer Advocate - the ratepayers' lawyer in utility cases - independent, administratively attached to the new Department of Energy rather than the commission."),
        "91:212": ("adjacent", "Companion attachment and staffing provisions for the consumer advocate's office."),
        # ---- programs and boards moved or rebuilt ----
        "91:215": ("adjacent", "Reconstituted the electric vehicle charging stations infrastructure commission's membership around the new department."),
        "91:216": ("adjacent", "Rewrote that commission's duties: planning the build-out of EV charging infrastructure along state corridors."),
        "91:217": ("adjacent", "Moved custody of funds collected under electric utility restructuring orders (rate-settlement money) to the new department's oversight."),
        "91:218": ("adjacent", "Moved the commercial property assessed clean energy (C-PACE) districts' technical standards from the PUC to the department - the financing tool for building-efficiency retrofits."),
        "91:220": ("adjacent", "Reconstituted the Energy Efficiency and Sustainable Energy (EESE) board - the standing stakeholder board on efficiency and clean-energy policy - around the new department."),
        "91:221": ("adjacent", "Put the new department on the state building code review board, where the energy code lives."),
        "91:222": ("adjacent", "Reconstituted the nuclear decommissioning financing committee (the body assuring Seabrook's decommissioning money) with the new department."),
        "91:223": ("adjacent", "Moved the atomic-development law-and-regulation study duty to the department."),
        "91:224": ("adjacent", "Moved the simplified residential energy code compliance form's rulemaking to the building code review board with department input."),
        "91:225": ("adjacent", "Conforming reorganization of the nuclear decommissioning financing committee."),
        "91:226": ("adjacent", "Conforming change to decommissioning reports and public hearings for nuclear generating facilities."),
        "91:229": ("adjacent", "Moved the minimum energy efficiency standards for products (appliance standards) to the department."),
        "91:230": ("adjacent", "Companion reference change for the appliance efficiency standards."),
        # ---- siting ----
        "91:227": ("core", "Restructured the Site Evaluation Committee - the body that approves or rejects large energy facilities like transmission lines and wind plants - shrinking it and attaching it administratively to the new department."),
        "91:228": ("core", "Created a study committee on further revisions to the Site Evaluation Committee - the opening move in the siting-reform fight that continued all period."),
        # ---- gas, net metering, renewables ----
        "91:231": ("adjacent", "Conforming change to when gas companies (including pipeline operators) are regulated as public utilities."),
        "91:232": ("adjacent", "Added a department definition to the Limited Electrical Energy Producers Act - the net-metering statute's framework."),
        "91:233": ("adjacent", "Conforming reference change moving net energy metering administration to the department."),
        "91:234": ("core", "Rewrote the group-host net metering rules (RSA 362-A:9, XIV): how a customer-generator hosts a group of customers and how hosts register and report - the mechanics that community solar projects run on."),
        "91:235": ("adjacent", "Repealed a superseded net-metering provision."),
        "91:236": ("adjacent", "Conforming reference changes to the electric renewable energy classes."),
        "91:237": ("adjacent", "Conforming reference change to the renewable energy classes."),
        "91:238": ("adjacent", "Moved renewable energy certificate administration to the department."),
        "91:239": ("adjacent", "Moved renewable portfolio standard information collection to the department."),
        "91:240": ("core", "Rewrote the renewable energy fund statute (RSA 362-F:10): the alternative-compliance-payment money that funds rebates and low-income solar programs is continually appropriated to the new department."),
        "91:241": ("adjacent", "Conforming reference changes across the renewable portfolio standard."),
        # ---- utility regulation machinery moved to the department ----
        "91:254": ("adjacent", "Moved public-utility affiliate oversight to the department."),
        "91:255": ("adjacent", "Conforming reference changes for utility service-equipment regulation."),
        "91:256": ("adjacent", "Conforming change to units-of-service rules for utility equipment."),
        "91:257": ("adjacent", "Conforming change assigning service-equipment oversight to the department."),
        "91:258": ("adjacent", "Streamlined licenses for new attachments on existing utility poles and conduits over public waters and lands (license by notification)."),
        "91:259": ("adjacent", "Companion hearing-and-order rules for those public-waters utility licenses."),
        "91:260": ("adjacent", "Conforming reference changes for utility property-rights proceedings."),
        "91:261": ("adjacent", "Conforming change to the extent of regulatory power over utilities."),
        "91:262": ("adjacent", "Split supervisory power over utilities between the department and the commission."),
        "91:263": ("adjacent", "Rewrote the general duties statute for utility oversight between the two agencies."),
        "91:264": ("adjacent", "Moved investigation of non-jurisdictional utilities and violation orders to the department."),
        "91:265": ("adjacent", "Utility reports now filed with the department."),
        "91:266": ("adjacent", "Companion utility reporting change."),
        "91:267": ("adjacent", "Moved utility service-territory jurisdiction to the department."),
        "91:271": ("adjacent", "Moved pole attachment regulation (the rates and terms for wires on utility poles) to the commission with department participation."),
        "91:272": ("adjacent", "Repealed superseded utility-regulation provisions."),
        "91:273": ("adjacent", "Moved utility accident investigation to the department."),
        "91:274": ("adjacent", "Added the department to the underground utility damage prevention (Dig Safe) law's definitions."),
        "91:275": ("adjacent", "Moved Dig Safe rulemaking from the commission to the department - the excavation-safety rules protecting buried gas and electric lines."),
        "91:276": ("adjacent", "Conforming change to Dig Safe civil penalties."),
        "91:278": ("adjacent", "Moved the renewable energy and energy efficiency project loan programs (business finance authority lending) to the department."),
        # ---- restructuring policy and markets ----
        "91:279": ("adjacent", "Conforming change to the electric utility restructuring purpose statute."),
        "91:280": ("adjacent", "Added a department definition to the restructuring chapter."),
        "91:281": ("core", "Amended the electric utility restructuring policy principles (RSA 374-F:3) and their implementation - the ground rules of New Hampshire's competitive electricity market, including how energy efficiency programs and the system benefits charge are administered."),
        "91:282": ("core", "Rewrote the restructuring chapter's ratepayer-protection provisions - who watches that restructuring savings reach customers."),
        "91:283": ("adjacent", "Conforming change to the restructuring oversight committee's reporting."),
        "91:284": ("adjacent", "Moved competitive electricity supplier registration and regional-activities participation to the department."),
        "91:289": ("adjacent", "Conforming change to rate-fixing procedures and federal Energy Policy Act standards review."),
        "91:290": ("adjacent", "Conforming change to utility advertising-contract rules (RSA 378:24)."),
        "91:291": ("adjacent", "Conforming change to rate filing, inspection, and temporary-rate procedures."),
        # ---- offshore wind, storage, data, RGGI ----
        "91:285": ("core", "Moved the offshore wind and port development commission under the new department's leadership - the state's standing body on Gulf of Maine offshore wind."),
        "91:286": ("adjacent", "Renamed the office of offshore wind industry development under the department."),
        "91:287": ("adjacent", "Conforming definitions change for the multi-use energy data chapter (RSA 374-H)."),
        "91:288": ("core", "Turned the energy storage docket into a department investigation: how storage projects get paid for avoided transmission and distribution costs - the grid-modernization question behind peak-demand costs."),
        "91:292": ("core", "Rewrote the multi-use energy data platform statute (RSA 378:50-52): the shared platform giving customers and competitive suppliers access to electric and gas usage data - the infrastructure that time-of-use rates and smart-meter programs depend on."),
        "91:293": ("core", "Moved the Regional Greenhouse Gas Initiative energy efficiency fund to the department and re-enacted how RGGI auction proceeds are used - most consumer proceeds rebated on electric bills, with a set-aside funding low-income energy efficiency programs."),
        # ---- rate reduction bonds ----
        "91:98": ("core", "Extended electric rate reduction bond authority to 2027 (RSA 369-B:5): the securitization tool that let utilities refinance stranded costs - the statute later used for storm-cost and divestiture financing that ratepayers repay on their bills."),
    },
    2023: {
        "79:110": ("core", "Amended electric utility restructuring implementation (RSA 374-F:4): how the system benefits charge's energy efficiency component is set and reviewed - the ratepayer charge that funds the NHSaves efficiency programs."),
        "79:111": ("adjacent", "Conforming change to the disclosure rules for electric service energy sources and environmental characteristics."),
        "79:112": ("core", "Amended the renewable energy fund statute (RSA 362-F:10) - the alternative-compliance-payment fund behind solar rebates and low-income clean-energy grants."),
        "79:113": ("adjacent", "Conforming change to renewable portfolio standard information collection."),
        "79:114": ("adjacent", "Phase-in rules for existing electricity supply contract load under the renewable portfolio standard."),
        "79:115": ("adjacent", "Conforming change to the energy commissioner's duties."),
        "79:116": ("adjacent", "Moved Office of the Consumer Advocate budget provisions within the PUC statute."),
        "79:117": ("adjacent", "Companion consumer-advocate budget provision."),
        "79:118": ("adjacent", "Gave the Office of the Consumer Advocate authority to transfer funds between expenditure classes - budget flexibility for the ratepayers' advocate."),
        "79:119": ("core", "Rewrote the public utilities assessment (RSA 363-A): how the costs of the Department of Energy and PUC are assessed against regulated utilities - the mechanics of who pays for utility regulation."),
        "79:120": ("adjacent", "Certification mechanics for the utility assessment."),
        "79:121": ("adjacent", "Collection mechanics for the assessment."),
        "79:122": ("adjacent", "Exempted the smallest utilities (under $150,000 of annual revenue) from the regulatory assessment."),
        "79:123": ("core", "Created the Regional Energy Advocacy Fund with a $250,000 appropriation: money for the state to advocate in regional (ISO-New England and federal) energy proceedings, where wholesale prices are actually set."),
        "79:125": ("adjacent", "Restated the Department of Energy's leadership structure (commissioner, deputy, directors, general counsel)."),
        "79:474": ("adjacent", "Legislative findings on electric vehicles: EVs pay no gas tax, so the trailer's registration-fee sections frame road funding as the issue."),
        "79:475": ("core", "Created the electric vehicle registration surcharge (RSA 261:141-b): $100 a year for battery-electrics and $50 for plug-in hybrids in lieu of gas taxes - the state's first EV-specific charge."),
        "79:517": ("core", "Appropriated $10,000 for New Hampshire's share of the 11-state regional fisheries effort alongside offshore wind development - the state's seat at the table as Gulf of Maine wind advances."),
        "79:518": ("core", "Appropriated $30,000 for three years of state membership in the Business Network for Offshore Wind - the supply-chain and industry-development side of offshore wind."),
        "79:581": ("core", "Ordered the Department of Energy to study a graduated, proportional low-income home energy assistance program for households that earn too much for existing fuel assistance - the benefits-cliff study on heating help."),
    },
    2025: {
        "141:140": ("core", "Swept every uncommitted dollar of the renewable energy fund into the general fund on July 1, 2025 - a one-time raid on the fund that pays solar rebates and low-income clean-energy grants."),
        "141:141": ("core", "Rewrote the renewable energy fund statute so that money in the fund at the start of each budget period is diverted to the general fund before programs are funded - the ongoing version of the sweep."),
        "141:142": ("core", "The 2027 prospective restatement of the same renewable energy fund diversion - locking the general-fund-first rule into the statute going forward."),
        "141:118": ("adjacent", "Updated the Air Resources Council's industry seats - the 'steam power' seat becomes an 'electric generating industry' seat - the air-permitting council that hears power-plant permit appeals."),
    },
}

# cite -> reason. Every term-matched candidate not kept above must appear here.
EXCLUDED = {
    2021: {
        "91:5": "Division of plant and property reorganization; state facilities management ('energy' in building-management text).",
        "91:45": "Controlled drug prescription health program; 'transmission' of prescription data.",
        "91:60": "Education trust fund statute; school finance ('utility' false positive; kept by the education and property-taxes packets).",
        "91:62": "Public school infrastructure fund; school facilities ('energy' in building-systems text; education packet's section).",
        "91:76": "Office of professional licensure reorganization; occupational licensing ('electric' in electrologists).",
        "91:130": "Workers' compensation hearings; 'transmission' of records.",
        "91:178": "Speech-language pathology licensing; 'utility' false positive.",
        "91:190": "Publications revolving fund renumbering; agency accounting (Office of Strategic Initiatives reorganization residue, no energy content).",
        "91:191": "Municipal and regional training fund renumbering; agency accounting (same reorganization residue).",
        "91:195": "Office of Planning and Development creation; land-use and development planning (its housing role is covered in the housing packet).",
        "91:219": "Enhanced 911 commission membership; telecommunications governance (conforming swap from the same reorganization).",
        "91:268": "Telephone utility service territories; telecommunications regulation (moved in the same reorganization; not energy).",
        "91:269": "Shared tenant telephone services; telecommunications regulation.",
        "91:270": "Competitive telecommunications provider regulation and affordable telephone service; telecommunications.",
        "91:277": "Telephone number conservation and area code policy; telecommunications.",
        "91:457": "Broadband matching grant initiative; telecommunications infrastructure ('utility' pole text).",
        "91:466": "Family and medical leave insurance purchasing pool; insurance ('transmission' false positive).",
    },
    2023: {
        "79:138": "Education trust fund restatement; school finance ('utility' false positive; the education packet's section).",
        "79:248": "Meals and rooms tax population estimates; tax administration ('energy' false positive in office-of-planning text).",
        "79:291": "Electricians; definitions - occupational licensing for the electrical trades (consistent with the siblings' electrician-licensing exclusions).",
        "79:292": "Electricians; inspectors - occupational licensing.",
        "79:293": "Electricians; licensing requirements - occupational licensing.",
        "79:294": "Electrician licensing repeals - occupational licensing.",
        "79:302": "Mechanical licensing board (fire control, gas fitters); occupational licensing for the heating trades ('propane' in trade definitions).",
        "79:346": "Budget trailer transmission to the legislature; budget-process boilerplate ('transmission' false positive).",
        "79:353": "Food waste disposal rules; solid-waste policy ('generating' food waste).",
        "79:462": "Housing Champion designation program; housing policy ('electric' in infrastructure-grant text; covered by the housing packet).",
        "79:514": "Drinking water transmission main appropriation (Nashua-Litchfield); water infrastructure ('transmission'/'ratepayer' false positives).",
    },
    2025: {
        "141:95": "Workers' compensation hearings; 'transmission' of records.",
        "141:145": "Electricians; inspectors - occupational licensing for the electrical trades.",
        "141:169": "Weights and measures device licensing fees; consumer-protection metrology (fuel-dispenser fees, not energy policy).",
        "141:171": "Dam registration fees; water-management program fees (hydro dams pay them, but the section is fee mechanics).",
        "141:176": "Solid waste management fund; waste policy ('energy' false positive).",
        "141:234": "Motor vehicle title and registration fees; transportation ('utility' vehicle class text).",
        "141:253": "Vehicle inspection statute repeals (including the emissions-inspection program); transportation program administration, consistent with the siblings' exclusion.",
        "141:254": "Companion directive to the department of environmental services on the inspection repeal; transportation.",
        "141:255": "Contingency clause for the inspection repeal; transportation.",
        "141:299": "Alcohol and drug abuse commission; health governance ('transmission' false positive).",
        "141:378": "Drinking water and groundwater trust fund appropriation; water infrastructure ('utility'/'ratepayer' false positives).",
        "141:389": "Legislative declaration on public-education funding authority; education policy ('energy' false positive in text; the education packet's core section).",
    },
}


def main() -> None:
    cycles = []
    for year in (2021, 2023, 2025):
        secs = json.loads((W / "hb2" / str(year) / "hb2-sections.json").read_text())
        idx = {s.get("chapter_cite") or str(s["section"]): s for s in secs["sections"]}
        chap = WHOLE_BILL_VOTES[year]["chapter"]

        def get(cite):
            return idx.get(cite) or idx.get(cite.split(":")[1])

        # coverage check: every term-matched candidate is kept or excluded
        rel = json.loads((W / "hb2" / str(year) / "hb2-relevant.json").read_text())
        cand = {(s.get("chapter_cite") or f"{chap}:{s['section']}") for s in rel["sections"]}
        covered = set(KEEP[year]) | set(EXCLUDED[year])
        missing = sorted(cand - covered)
        assert not missing, f"HB2 {year}: candidates without review: {missing}"

        kept = []
        for cite, (cat, plain) in KEEP[year].items():
            s = get(cite)
            assert s, f"HB2 {year}: kept section {cite} not found in extraction"
            heading = s["heading"]
            for pre in (f"{cite} ", cite.split(":")[1] + " "):
                if heading.startswith(pre):
                    heading = heading[len(pre):]
            rec = {
                "cite": cite,
                "heading": heading,
                "category": cat,
                "plain_language": plain,
                "affected_rsas": s["affected_rsas"],
            }
            if cite in HAND_ADDED:
                rec["hand_added"] = True
            kept.append(rec)
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
        "issue": "new-hampshire-04-energy",
        "note": (
            "Hand-curated energy analysis of HB2, New Hampshire's omnibus "
            "budget policy trailer, for the 2021, 2023, and 2025 budget "
            "cycles. Candidates came from relevance-term matching over every "
            "extracted section (see working/.../hb2/{year}/); a human pass "
            "kept the energy sections, added one section the matcher missed "
            "(flagged hand_added), and logged every exclusion. This analysis "
            "REVERSES the sibling packets' curation: the energy and utility "
            "sections they excluded with documented reasons are the core "
            "here, and their education/tax sections are excluded. Roll-call "
            "votes are recorded on HB2 AS A WHOLE - a vote for or against "
            "the trailer is never a vote on one section, and must not be "
            "presented as one."
        ),
        "cycles": cycles,
    }
    (W / "hb2-sections.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# HB2 (budget policy trailer) — energy sections, 2021 / 2023 / 2025",
        "",
        "New Hampshire passes its two-year budget in two bills: HB1 (the money)",
        "and HB2, a policy 'trailer' that bundles dozens to hundreds of legal",
        "changes into one bill. The state's biggest energy-governance change of",
        "this period — the creation of the Department of Energy and the",
        "restructuring of the Public Utilities Commission — was made inside the",
        "2021 trailer, not as a standalone bill; the 2023 trailer set the EV",
        "registration surcharge and the regional energy advocacy fund; the 2025",
        "trailer swept and permanently diverted the renewable energy fund.",
        "This file is the hand-reviewed, section-level energy analysis for the",
        "three budget cycles in scope.",
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
            f"{len(c['relevant_sections'])} energy-relevant after review; "
            f"{c['whole_bill_roll_call_count']} floor roll calls on the whole bill.*",
            "",
            "Final passage (whole bill): " + "; ".join(
                f"{v['body']} {v['yeas']}–{v['nays']} ({v['motion']}, {v['date']})"
                for v in c["whole_bill_final_votes"]) + ".",
            "",
        ]
        for cat, label in (("core", "Core energy sections"),
                           ("adjacent", "Adjacent (conforming and machinery) sections")):
            subset = [s for s in c["relevant_sections"] if s["category"] == cat]
            if not subset:
                continue
            lines += [f"### {label}", ""]
            for s in subset:
                rsas = f" *(affects {', '.join(s['affected_rsas'][:4])})*" if s["affected_rsas"] else ""
                flag = " *(hand-added; missed by term matching)*" if s.get("hand_added") else ""
                lines += [f"- **{s['cite']} — {s['heading']}.** {s['plain_language']}{rsas}{flag}"]
            lines += [""]
        lines += ["### Reviewed and excluded (false positives and other packets' sections)", ""]
        for e in c["excluded_candidates"]:
            lines += [f"- {e['cite']}: {e['reason']}"]
        lines += [""]
    (W / "hb2-sections.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote hb2-sections.json and hb2-sections.md "
          f"({sum(len(c['relevant_sections']) for c in cycles)} kept sections)")


if __name__ == "__main__":
    main()
