#!/usr/bin/env python3
"""Build the consolidated, hand-curated HB2 tax/revenue analysis for this issue.

Reads the collector's per-cycle outputs (working/.../hb2/{year}/) and writes
the issue-level files the mission requires:

  working/new-hampshire/property-taxes/hb2-sections.json
  working/new-hampshire/property-taxes/hb2-sections.md

The keep/drop decisions and plain-language summaries below are the human
curation pass over the term-matched candidates (recall-first matching produced
false positives like "revenue" inside agency fund mechanics and "assessment"
in education testing). Three sections the term matcher missed were added by
hand after a full-text sweep for the rate statutes (91:89 interest-and-
dividends schedule, 91:103-104 meals-and-rooms rate cut); they are flagged
``hand_added``. Vote counts are on the whole HB2 trailer only - never
attributed to a single section.

Run from repo root:
  python3 working/new-hampshire/property-taxes/build-hb2-analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")

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

HAND_ADDED = {"91:89", "91:103", "91:104"}

# cite -> (category, plain-language summary). Categories:
#   core     = directly changes a tax rate, a tax's structure, or a major
#              state-to-local revenue flow
#   adjacent = tax administration, tax credits, or education/municipal funding
#              mechanics that shape local tax pressure indirectly
KEEP = {
    2021: {
        "91:89": ("core", "Began phasing out the interest and dividends tax: the 5 percent rate drops to 4 percent in 2023, 3 percent in 2024, 2 percent in 2025, and 1 percent in 2026 - the schedule the full repeal rides on."),
        "91:99": ("core", "Repealed the interest and dividends tax (RSA 77) outright, effective January 1, 2027 - the end point of the phase-out schedule. (The 2023 trailer later moved this date up to 2025.)"),
        "91:103": ("core", "Cut the meals and rooms tax rate from 9 percent to 8.5 percent, effective October 2021 - the tax's first rate cut; its revenue feeds the general fund, the education trust fund, and the towns' share."),
        "91:109": ("core", "Cut the business enterprise tax rate from 0.675 percent to 0.55 percent for tax periods ending on or after December 31, 2022, and repealed the earlier revenue-trigger contingencies."),
        "91:110": ("core", "Cut the business profits tax rate from 7.7 percent to 7.6 percent for tax periods ending on or after December 31, 2022, deleting the contingency that could have raised it back to 7.9 percent."),
        "91:112": ("core", "Rewrote how meals and rooms tax money is shared: created the dedicated meals and rooms municipal revenue fund, with the towns' share (after administration and the education trust fund's cut) distributed to every city and town by population - the change that pushed the local share toward the statutory 30 percent."),
        "91:48": ("core", "Suspended revenue sharing with cities and towns (RSA 31-A) for another biennium - the general-fund aid stream that had been suspended in every budget since 2010."),
        "91:320": ("core", "Appropriated $30 million from the education trust fund for school building aid on new projects - construction costs that otherwise land on local property taxes."),
        "91:322": ("core", "Cut the statewide education property tax (SWEPT) for fiscal year 2023: the commissioner sets the rate to raise $263 million instead of the usual $363 million target - a one-year, $100 million property-tax reduction."),
        "91:323": ("core", "Guaranteed that no municipality's total education grant would fall because of the SWEPT cut: the state makes up any decrease with a supplemental payment."),
        "91:26": ("adjacent", "Capped how fast county payments to the state for long-term care can grow (2 percent a year for the biennium) - the reimbursement stream counties raise through county property taxes."),
        "91:51": ("adjacent", "Let districts use their higher pre-pandemic or pandemic-year enrollment count for fiscal 2022 aid, so pandemic enrollment drops would not cut adequacy grants."),
        "91:55": ("adjacent", "Moved $35 million of education trust fund surplus into a restricted account to fund additional school relief aid in fiscal years 2022 and 2023."),
        "91:60": ("adjacent", "Rewrote what the education trust fund may pay for - adequacy grants, the low and moderate income homeowners' property tax relief program, and the new education freedom accounts among them."),
        "91:61": ("adjacent", "Transferred $1 million a year from the education trust fund to the public school infrastructure fund in each year of the biennium."),
        "91:69": ("adjacent", "Suspended the earmark that sends a slice of meals and rooms revenue to the state's travel and tourism division for the biennium."),
        "91:74": ("adjacent", "Froze new state aid grants for local water, wastewater, and landfill infrastructure projects for the biennium (existing commitments kept) - deferring a municipal aid stream."),
        "91:87": ("adjacent", "Raised the cap on the rainy day fund (revenue stabilization reserve) to 10 percent of general fund revenue, letting the state bank more surplus."),
        "91:106": ("adjacent", "Raised the business enterprise tax filing thresholds to $250,000 of receipts or tax base, dropping the smallest businesses out of the filing pool."),
        "91:115": ("adjacent", "Limited how much overpaid business profits tax can be carried forward as a credit (to 500 percent of the current year's tax), with the rest refunded."),
        "91:116": ("adjacent", "Applied the same 500 percent carry-forward limit and refund rule to business enterprise tax overpayments."),
        "91:117": ("adjacent", "Created a commission to study limiting the business tax credit carry-over - including whether unused credit refunds could be redirected to other uses."),
        "91:295": ("adjacent", "Updated the annual tax expenditure report statute - the report that tells lawmakers what each tax credit and exemption costs in forgone revenue."),
        "91:313": ("adjacent", "Extended annual school building aid lease grants to more kinds of district lease arrangements."),
        "91:315": ("adjacent", "Made full-day kindergarten adequacy grants a standing charge on the education trust fund every year, ending the keno-revenue-dependent formula."),
        "91:316": ("adjacent", "Appropriated $1.9 million to top up fiscal 2021 kindergarten and adequacy grant payments."),
        "91:332": ("adjacent", "Let municipalities accept and spend federal American Rescue Plan money as 'unanticipated revenue' without a town-meeting vote."),
        "91:431": ("adjacent", "Created the education freedom account (EFA) program - per-pupil adequacy money following students out of public schools, paid from the education trust fund; the fund's biggest new draw."),
        "91:469": ("adjacent", "Created a business enterprise tax credit worth 50 percent of premiums an employer pays into the new Granite State paid family leave plan."),
    },
    2023: {
        "79:85": ("core", "Rewrote the interest and dividends tax schedule to end at 3 percent in 2024: the previous 2 percent (2025) and 1 percent (2026) steps were deleted so the tax stops a full two years early."),
        "79:86": ("core", "Moved the final interest-and-dividends return filing rules from 2027 to 2025 to match the accelerated repeal."),
        "79:88": ("core", "Changed the repeal's effective date: the interest and dividends tax now ends January 1, 2025 instead of 2027."),
        "79:109": ("core", "Suspended revenue sharing with cities and towns (RSA 31-A) for the 2024-2025 biennium - again."),
        "79:150": ("core", "Rewrote the cost of an adequate education: base per-pupil aid rises to $4,100 with larger add-ons for free-and-reduced-lunch, special education, and English learners - the state share that offsets local school property taxes."),
        "79:153": ("core", "Rewrote extraordinary need grants for 2023 - extra aid scaled to a town's equalized property value per pupil, targeting the towns with the weakest tax bases."),
        "79:154": ("core", "Set the 2025-and-after version of extraordinary need grants, extending the property-poor-town aid formula."),
        "79:156": ("core", "Rewrote how each municipality's total education grant is determined, including hold-harmless rules so no town's grant falls below prior levels while the new formula phases in."),
        "79:191": ("core", "Fixed the education trust fund's share of the business profits tax at 41 percent of revenue - replacing the old 'increase attributable to' formula with a straight statutory split."),
        "79:192": ("core", "Fixed the education trust fund's share of the business enterprise tax at 41 percent of revenue, the same straight split."),
        "79:83": ("core", "Put $10 million from the education trust fund into the public school infrastructure fund for school construction and safety projects."),
        "79:67": ("adjacent", "Restated the Board of Tax and Land Appeals as a 3-member body of tax-law experts - the state board that hears property tax abatement appeals."),
        "79:137": ("adjacent", "Reduced the education trust fund appropriation earmarked for education freedom accounts by $10 million in each year of the biennium, an accounting true-up to actual enrollment."),
        "79:138": ("adjacent", "Re-enacted the education trust fund statute, restating everything the fund may pay for - adequacy grants, homeowners' property tax relief, EFAs, court-ordered placements, and school building aid among them."),
        "79:141": ("adjacent", "Changed special education state aid so districts are reimbursed for costs above 3.5 times the state average per-pupil cost - catastrophic costs that otherwise hit local budgets."),
        "79:143": ("adjacent", "Shifted liability for certain court-ordered placements of children with disabilities, defining when the state rather than the school district pays."),
        "79:144": ("adjacent", "Appropriated $9.2 million from the education trust fund for court-ordered placement costs."),
        "79:147": ("adjacent", "Appropriated $12.5 million from the education trust fund for the Sugar River Valley career and technical education renovation project."),
        "79:148": ("adjacent", "Appropriated $7.6 million from the education trust fund for the Winnisquam regional CTE renovation project."),
        "79:248": ("adjacent", "Updated the population-estimate process that determines each town's share of the meals and rooms tax distribution."),
        "79:264": ("adjacent", "Appropriated $315,700 from the education trust fund for new full-day kindergarten adequacy grants."),
        "79:266": ("adjacent", "Converted the assessing certification board into an advisory board inside the office of professional licensure - the body that certifies the assessors who set property values (companion sections 79:267-269 carry the details)."),
        "79:349": ("adjacent", "Extended the Department of Revenue Administration's revenue information management system account - the tax-collection IT system funded from the extra revenue it captures."),
        "79:512": ("adjacent", "Appropriated $15 million in each of fiscal 2026 and 2027 for payments to communities for wastewater projects - state aid the 2025 trailer would later repeal before it was paid."),
        "79:583": ("adjacent", "Created a study commission on the recent charitable gaming law changes, including the newly authorized historic horse racing machines - the fastest-growing state gaming revenue stream."),
    },
    2025: {
        "141:111": ("core", "Repealed RSA 31-A, revenue sharing with cities and towns, outright - the municipal aid statute suspended in every budget since 2010 is now off the books entirely."),
        "141:112": ("core", "Repealed the 2023 budget's $30 million in wastewater state aid payments to communities before the money went out."),
        "141:132": ("core", "Cut the education trust fund's share of the business profits tax from 41 percent to 39 percent, keeping more business tax revenue in the general fund."),
        "141:133": ("core", "Cut the education trust fund's share of the business enterprise tax from 41 percent to 39 percent."),
        "141:134": ("core", "Rewrote the tobacco tax split: 39 percent of tobacco revenue to the education trust fund, the rest to the general fund."),
        "141:135": ("core", "Rewrote the real estate transfer tax split: 39 percent to the education trust fund, the rest to the general fund."),
        "141:80": ("core", "Capped the education trust fund's balance: any surplus over $20 million at the close of a biennium is swept into the general fund."),
        "141:223": ("core", "Delayed the annual 2 percent inflation adjustment of per-pupil adequacy aid to July 2026 - a pause in the automatic growth of state school aid."),
        "141:224": ("core", "Re-enacted the extraordinary need grant formula - the extra aid tied to a town's equalized property value per pupil."),
        "141:225": ("core", "Created fiscal capacity disparity aid: up to $1,250 extra per pupil for municipalities with less than $1 million of equalized property value per pupil, phasing out by $1.6 million - aid aimed squarely at property-poor towns."),
        "141:226": ("core", "Rewrote how each municipality's education grant is computed to fold in the new fiscal capacity disparity aid."),
        "141:26": ("core", "Legalized video lottery terminals (slot-machine-style VLTs) at licensed charitable gaming facilities: the state collects 31 percent of gross machine revenue, split 75 percent to the general fund and 25 percent to the lottery's special fund - the budget's biggest new revenue source."),
        "141:358": ("core", "Created a tax amnesty program: back taxes paid during the amnesty window owe no penalties and only half the usual interest - a one-time revenue catch-up."),
        "141:389": ("core", "Declared the legislature's position on the Claremont school-funding rulings - asserting that defining and funding an adequate education is the legislature's prerogative, while the statewide education property tax and adequacy formula remain under active court challenge."),
        "141:79": ("adjacent", "Amended the education trust fund's purpose list, including how court-ordered placement costs are paid."),
        "141:83": ("adjacent", "Moved the final determination of education grants to October 1 and guaranteed each municipality at least 95 percent of its estimated grant."),
        "141:139": ("adjacent", "Authorized drawing down the rainy day fund to cover a fiscal 2025 general-fund deficit, if the audit finds one."),
        "141:187": ("adjacent", "Created a 'granite patron of the arts' business profits tax credit for half of donations to the new state arts fund."),
        "141:188": ("adjacent", "Let unused granite patron of the arts credits apply against the business enterprise tax."),
        "141:276": ("adjacent", "Restructured special education state aid administration and reimbursement - the catastrophic-cost aid that shields local budgets."),
        "141:278": ("adjacent", "Rewrote the funding rule for statewide special education programs."),
        "141:320": ("adjacent", "Ordered the governor to raise general fund revenues or cut appropriations by a combined $16 million per year for the biennium, on top of the budget's line items."),
        "141:328": ("adjacent", "Made an extra appropriation contingent on fiscal 2026 revenues beating the plan - surplus-triggered spending rather than committed dollars."),
        "141:340": ("adjacent", "Adjusted the Board of Tax and Land Appeals quorum rules - the board that hears property tax appeals, now also backstopping the housing appeals board."),
        "141:351": ("adjacent", "Charged a study committee with weighing a state film office and an accompanying tax credit - a potential new tax expenditure."),
        "141:359": ("adjacent", "Appropriated $50,000 to the Department of Revenue Administration to run the tax amnesty program."),
        "141:379": ("adjacent", "Appropriated $2.5 million in each of fiscal 2026 and 2027 for payments to communities - the much smaller replacement for the repealed $30 million wastewater aid."),
        "141:399": ("adjacent", "Appropriated $400,000 a year from the education trust fund for adult high school education programs."),
        "141:401": ("adjacent", "Made the education and revenue departments jointly maintain school accounting standards - the books behind local school tax rates."),
        "141:403": ("adjacent", "Appropriated $1.5 million a year from the education trust fund for statewide student learning platforms."),
        "141:404": ("adjacent", "Removed the 11 a.m.-to-1 a.m. window on keno games, letting licensees run keno all business hours - keno revenue funds kindergarten aid."),
        "141:405": ("adjacent", "Authorized advance deposit account wagering on horse racing, with the tax on wagers flowing partly to the education trust fund."),
    },
}

# Term-matched candidates reviewed and excluded, with the reason (audit trail).
EXCLUDED = {
    2021: {
        "91:4": "Graphic services revolving fund; agency internal-services accounting ('revenue' false positive).",
        "91:9": "State employee health plan cost sharing; personnel policy.",
        "91:16": "Retirement system medical benefit contingency; pension administration.",
        "91:29": "Granite Advantage health care trust fund sources; Medicaid financing, not state tax structure.",
        "91:34": "DHHS program eligibility guardrail; 'revenues' appears in budget-process boilerplate.",
        "91:35": "Federal-match reporting rule for DHHS; budget process mechanics.",
        "91:49": "Liquor commission merchant-card processing operations.",
        "91:58": "Federal ARPA maintenance-of-equity compliance mechanics for school aid.",
        "91:59": "$3 million education-department IT appropriation (student data system); departmental IT, though charged to the education trust fund.",
        "91:62": "Public school infrastructure fund statute restatement; companion detail to the kept transfer (91:61).",
        "91:81": "Office of professional licensure fee-setting authority; occupational licensing.",
        "91:90": "Conforming cross-reference deletion for the I&D repeal; the substantive change is in 91:89 and 91:99.",
        "91:91": "Conforming cross-reference deletion for the I&D repeal (financial disclosure forms).",
        "91:92": "Conforming cross-reference deletion for the I&D repeal (late-filing penalties).",
        "91:93": "Conforming cross-reference deletion for the I&D repeal (understatement penalties).",
        "91:94": "Conforming cross-reference deletion for the I&D repeal (electronic filing).",
        "91:95": "Conforming cross-reference deletion for the I&D repeal (tax expenditure report list).",
        "91:96": "Conforming change removing individuals' I&D credit from the education tax credit statute in 2027.",
        "91:97": "Conforming change to scholarship-organization rules for the same credit.",
        "91:98": "Electric rate reduction bonds; utility financing ('taxation' in bond-exemption boilerplate).",
        "91:100": "Final-return mechanics for the repealed I&D tax; companion detail to 91:99.",
        "91:113": "Treasury accounting subparagraph for the new meals-and-rooms municipal fund; companion detail to 91:112.",
        "91:114": "Cross-reference correction in the education trust fund statute; companion detail to 91:112.",
        "91:118": "Sunset repeal of the business tax credit carry-over study commission; companion to 91:117.",
        "91:162": "College tuition savings plan commission; program governance.",
        "91:178": "Speech-language pathology licensing; term match inside unrelated text.",
        "91:187": "Creates the Department of Energy; agency reorganization.",
        "91:192": "Executive branch department list housekeeping.",
        "91:195": "Office of Planning and Development creation; agency reorganization (its housing role is covered in the housing packet).",
        "91:243": "Public utilities commission assessments on utilities; utility regulation funding.",
        "91:245": "Utility recovery of assessment costs; utility regulation.",
        "91:252": "Utility investigation expense rules; utility regulation.",
        "91:253": "Utility penalty provisions; utility regulation.",
        "91:263": "Utility oversight duties; utility regulation.",
        "91:270": "Telecommunications regulation; term match inside unrelated text.",
        "91:281": "Electric restructuring principles; energy policy.",
        "91:311": "Dual and concurrent enrollment program; higher-education programming.",
        "91:318": "School planning committee vacancy rules; local governance housekeeping.",
        "91:331": "DHHS closed-loop referral system limit; health IT policy.",
        "91:366": "National guard enlistment incentive program; military benefits.",
        "91:369": "National guard scholarship reference removal; military benefits.",
        "91:410": "DHHS loan repayment program lapse extension ('restricted revenue' accounting).",
        "91:412": "Medicaid services appropriation lapse extension; accounting.",
        "91:416": "Nursing facility payment lapse extension; accounting.",
        "91:428": "Lottery commission headquarters mortgage payoff; facilities financing, not revenue structure.",
        "91:435": "Woodsville fire district audit requirement; single-district accountability rider.",
        "91:438": "COVID-19 micro enterprise relief fund; pandemic grant program.",
        "91:440": "Live venue purpose statement; 'tax bases' appears in findings prose only.",
        "91:441": "Council on the arts policy declaration.",
        "91:457": "Broadband matching grant initiative; infrastructure program.",
        "91:464": "Granite State paid family leave plan itself; the tax piece (its BET credit) is kept as 91:469.",
    },
    2023: {
        "79:12": "Corrections unclassified positions; personnel.",
        "79:99": "Oversize vehicle permit fee revolving fund; transportation fees.",
        "79:102": "Prime wetlands hearing exemption for DOT projects; environmental permitting.",
        "79:105": "Aeronautics credit-card convenience fee; transportation fees.",
        "79:119": "Public utilities commission assessment mechanics; utility regulation.",
        "79:122": "Small-utility exemption from PUC assessment; utility regulation.",
        "79:142": "Special education rulemaking subparagraph; companion detail to the kept aid changes (79:141).",
        "79:158": "Third-grade reading data repeal; education testing ('assessment' false positive).",
        "79:159": "Federal ARPA maintenance-of-equity mechanics; companion to the 2021 provision, excluded on the same ground.",
        "79:202": "Medicaid appropriation lapse extension; accounting.",
        "79:267": "Assessing certification advisory board membership details; companion to kept 79:266.",
        "79:268": "Assessing certification rulemaking transfer; companion to kept 79:266.",
        "79:269": "Assessing certification statute repeals; companion to kept 79:266.",
        "79:276": "Auctioneer license revenue disposition; occupational licensing.",
        "79:338": "Professional bondsmen fees; occupational licensing.",
        "79:375": "National guard enlistment incentive fund; military benefits.",
        "79:402": "Granite Advantage program evaluation commission; health policy.",
        "79:404": "High risk pool funding mechanics; health insurance.",
        "79:405": "Granite Advantage 'remainder amount' definition; health financing.",
        "79:408": "Alcohol fund transfer repeals; health financing.",
        "79:432": "Cyanobacteria mitigation purpose statement; environmental program.",
        "79:456": "State officer compensation review; personnel ('assessing' in consultant boilerplate).",
        "79:462": "Housing Champion program; housing policy, covered in the housing-affordability packet.",
        "79:471": "Liquor profits share to the alcohol treatment fund; spending allocation within health policy.",
        "79:474": "Electric vehicle findings prose.",
        "79:475": "Electric vehicle registration surcharge; highway fund revenue (transportation), excluded consistently with the toll/road-fee category.",
        "79:584": "Charitable gaming study appropriation; companion dollar detail to kept 79:583.",
        "79:606": "Career and technical education transportation grant program; education programming.",
    },
    2025: {
        "141:2": "Fish and game conservation programs; wildlife policy.",
        "141:19": "Voluntary gambling self-exclusion database; companion consumer-protection detail to the VLT authorization (141:26).",
        "141:20": "Lottery and gaming commission rename/structure; companion to 141:26.",
        "141:21": "High-stakes tournament definitions; companion gaming-regulation detail.",
        "141:23": "High-stakes tournament authorization; companion gaming-regulation detail.",
        "141:25": "Games of chance prize rules; companion gaming-regulation detail.",
        "141:27": "Opioid abatement fund enforcement overtime; public-safety spending.",
        "141:45": "Opioid-fund shelter appropriation; homelessness services (covered in the housing packet).",
        "141:51": "Medicaid appropriation lapse extension; accounting.",
        "141:82": "Virtual charter school payment timing; education finance mechanics specific to one school.",
        "141:116": "Dam easement acceptance for $1; property management.",
        "141:171": "Dam registration fees; program fees.",
        "141:173": "Automotive oil fee increase for the hazardous waste cleanup fund; environmental program fee.",
        "141:181": "Sununu Youth Services Center possession; state property management ('revenue' false positive).",
        "141:186": "Granite patron of the arts fund creation; companion detail to the kept tax credits (141:187-188).",
        "141:240": "Vanity plate fee to driver training fund; transportation fees.",
        "141:244": "Motor vehicle air pollution abatement definitions; transportation.",
        "141:253": "Vehicle inspection statute repeals; transportation.",
        "141:262": "Perinatal health insurance coverage; health policy.",
        "141:266": "Ten-year transportation plan funding; transportation.",
        "141:267": "Fish and game gifts and raffles; wildlife funding.",
        "141:269": "Pheasant license revenues; wildlife funding.",
        "141:270": "Fish food sales account transfer; wildlife funding.",
        "141:271": "Fish food account repeals; wildlife funding.",
        "141:276-notused": None,
        "141:293": "Opioid abatement commission membership; health governance.",
        "141:294": "Opioid abatement commission duties; health governance.",
        "141:296": "Liquor profits to the renamed addiction fund; health financing.",
        "141:297": "Addiction fund rename; health financing.",
        "141:299": "Governor's addiction commission rename; health governance.",
        "141:300": "Council for responsible gambling repeal; gaming governance housekeeping.",
        "141:302": "Education freedom account rollover mechanics; education-choice program detail.",
        "141:305": "Granite Advantage trust fund restatement; health financing.",
        "141:322": "DEI prohibition in public schools; education policy ('assessment' false positive).",
        "141:325": "State payment and procurement card fund; treasury operations.",
        "141:333": "Reduction-in-force notice rules; personnel.",
        "141:357": "Sale of the Sununu Youth Services Center; state property management.",
        "141:384": "License plate inventory fund; transportation operations.",
        "141:398": "Adult education program restatement; companion detail to the kept appropriation (141:399).",
        "141:442": "Retirement system earnable compensation definition; pension policy.",
    },
}
EXCLUDED[2025].pop("141:276-notused")


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
        "issue": "new-hampshire-02-property-taxes",
        "note": (
            "Hand-curated tax-and-revenue analysis of HB2, New Hampshire's "
            "omnibus budget policy trailer, for the 2021, 2023, and 2025 "
            "budget cycles. Candidates came from relevance-term matching over "
            "every extracted section (see working/.../hb2/{year}/); a human "
            "pass kept the tax/revenue sections, added three rate sections "
            "the matcher missed (flagged hand_added), and logged every "
            "exclusion. Roll-call votes are recorded on HB2 AS A WHOLE - a "
            "vote for or against the trailer is never a vote on one section, "
            "and must not be presented as one."
        ),
        "cycles": cycles,
    }
    (W / "hb2-sections.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# HB2 (budget policy trailer) — tax and revenue sections, 2021 / 2023 / 2025",
        "",
        "New Hampshire passes its two-year budget in two bills: HB1 (the money)",
        "and HB2, a policy 'trailer' that bundles dozens to hundreds of legal",
        "changes into one bill. The state's biggest tax changes of this period —",
        "the business tax rate cuts, the interest-and-dividends repeal, the",
        "education funding rewrites, and the fate of municipal revenue sharing —",
        "were all made inside HB2, not as standalone bills. This file is the",
        "hand-reviewed, section-level tax/revenue analysis for the three budget",
        "cycles in scope.",
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
            f"{len(c['relevant_sections'])} tax/revenue-relevant after review; "
            f"{c['whole_bill_roll_call_count']} floor roll calls on the whole bill.*",
            "",
            "Final passage (whole bill): " + "; ".join(
                f"{v['body']} {v['yeas']}–{v['nays']} ({v['motion']}, {v['date']})"
                for v in c["whole_bill_final_votes"]) + ".",
            "",
        ]
        for cat, label in (("core", "Core tax and revenue sections"),
                           ("adjacent", "Adjacent (tax-administration and funding-mechanics) sections")):
            subset = [s for s in c["relevant_sections"] if s["category"] == cat]
            if not subset:
                continue
            lines += [f"### {label}", ""]
            for s in subset:
                rsas = f" *(affects {', '.join(s['affected_rsas'][:4])})*" if s["affected_rsas"] else ""
                flag = " *(hand-added; missed by term matching)*" if s.get("hand_added") else ""
                lines += [f"- **{s['cite']} — {s['heading']}.** {s['plain_language']}{rsas}{flag}"]
            lines += [""]
        lines += ["### Reviewed and excluded (false positives and companions)", ""]
        for e in c["excluded_candidates"]:
            lines += [f"- {e['cite']}: {e['reason']}"]
        lines += [""]
    (W / "hb2-sections.md").write_text("\n".join(lines), encoding="utf-8")
    print("Wrote hb2-sections.json and hb2-sections.md "
          f"({sum(len(c['relevant_sections']) for c in cycles)} kept sections)")


if __name__ == "__main__":
    main()
