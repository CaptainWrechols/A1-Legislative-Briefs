#!/usr/bin/env python3
"""Build the consolidated, hand-curated HB2 education analysis for this issue.

Reads the collector's per-cycle outputs (working/.../hb2/{year}/) and writes
the issue-level files the mission requires:

  working/new-hampshire/public-education/hb2-sections.json
  working/new-hampshire/public-education/hb2-sections.md

The keep/drop decisions and plain-language summaries below are the human
curation pass over the term-matched candidates (recall-first matching produced
false positives like "student" inside licensing sections and "learning" in
health-program text). Three sections the term matcher missed were added by
hand after a full-text sweep for education headings (91:322's SWEPT cut,
79:139's episode-of-treatment definition, 79:45's advanced-manufacturing-
education repeal); they are flagged ``hand_added``. The property-taxes packet
curated the education-FUNDING sections first; this pass re-curates for the
education scope, where the policy sections (the divisive-concepts sections,
the DEI prohibition, testing, special education, EFAs, the cell-phone policy)
are core. Vote counts are on the whole HB2 trailer only - never attributed to
a single section.

Run from repo root:
  python3 working/new-hampshire/public-education/build-hb2-analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/public-education")

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

HAND_ADDED = {"91:322", "79:139", "79:45"}

# cite -> (category, plain-language summary). Categories:
#   core     = directly changes what schools must teach or may do, how much
#              state school aid exists, or a major education program's law
#   adjacent = education administration, appropriations detail, and mechanics
#              that shape schools indirectly
KEEP = {
    2021: {
        "91:431": ("core", "Created the education freedom account (EFA) program (new RSA 194-F): state adequacy money follows a student out of public school to private, religious, or home education expenses, paid from the education trust fund through a scholarship organization - the biggest school-choice change of the period."),
        "91:432": ("core", "Amended the compulsory-attendance statute so participation in the EFA program satisfies a child's school-attendance duty - the conforming change that makes the program legal schooling."),
        "91:298": ("core", "The 'divisive concepts' teaching ban as enacted: no public school pupil shall be taught or compelled to express belief in a list of concepts about the superiority or inferiority of any group (new RSA 193:40) - the classroom-content restriction later struck down in part by a federal court and repealed in the 2025 trailer's DEI rewrite's shadow."),
        "91:297": ("core", "The companion civil-rights half of the teaching ban: a new 'right to freedom from discrimination in public workplaces and education' under the human rights commission (RSA 354-A:29 and following), giving the banned-concepts rule an enforcement path including teacher-license discipline."),
        "91:322": ("core", "Cut the statewide education property tax (SWEPT) for fiscal year 2023: the rate is set to raise $263 million instead of the usual $363 million target - a one-year, $100 million cut in the local school tax the state counts as its aid."),
        "91:323": ("core", "Guaranteed no municipality's total education grant would fall because of the SWEPT cut: the state makes up any decrease with a supplemental payment."),
        "91:53": ("core", "Created relief funding (RSA 198:40-e): an extra $600 per free-and-reduced-price-meal pupil in districts where at least 48 percent of pupils qualify, layered onto adequacy aid for the poorest districts."),
        "91:55": ("core", "Moved $35 million of education trust fund surplus into a restricted account to pay the new relief funding in fiscal years 2022 and 2023."),
        "91:51": ("core", "Let districts use their higher pre-pandemic or pandemic-year enrollment count for fiscal 2022 aid, so pandemic enrollment drops would not cut adequacy grants."),
        "91:52": ("core", "Kept free-and-reduced-meal counts (and the aid tied to them) from collapsing in fiscal 2023 if pandemic conditions continued - a conditional hold-harmless for differentiated aid."),
        "91:315": ("core", "Made full-day kindergarten adequacy grants a standing charge on the education trust fund every year, ending the keno-revenue-dependent formula."),
        "91:320": ("core", "Appropriated $30 million from the education trust fund for school building aid on new projects - the first new-project money after a decade-long moratorium era."),
        "91:311": ("core", "Rewrote the dual and concurrent enrollment program (RSA 188-E:25-29): high school students earn community-college credit in STEM and career courses with the state paying tuition - the main high-school-to-career bridge program."),
        "91:96": ("adjacent", "Conforming change to the education tax credit scholarship statute for the interest-and-dividends repeal: individuals' I&D-tax credits for scholarship-organization donations end with the tax in 2027 (later 2025)."),
        "91:97": ("adjacent", "Companion conforming change to the scholarship-organization award rules for the same repeal."),
        "91:50": ("adjacent", "Let the department of education accept private gifts and grants for department purposes with Governor and Council approval for the biennium."),
        "91:54": ("adjacent", "Let a school district call a special meeting to decide how to budget any adjustment in its education aid."),
        "91:58": ("adjacent", "Directed the education department to certify compliance with the federal ARPA 'maintenance of equity' rule protecting high-poverty districts' shares of state aid."),
        "91:59": ("adjacent", "Appropriated $3 million from the education trust fund for a statewide student data collection and reporting system - the state's education-data infrastructure."),
        "91:60": ("adjacent", "Rewrote what the education trust fund may pay for - adequacy grants, the homeowners' property tax relief program, and the new education freedom accounts among them."),
        "91:61": ("adjacent", "Transferred $1 million a year from the education trust fund to the public school infrastructure fund in each year of the biennium."),
        "91:62": ("adjacent", "Rewrote the public school infrastructure fund statute (RSA 198:15-y) - the school security and infrastructure account funded by state surpluses."),
        "91:63": ("adjacent", "Repealed the scheduled sunset of the public school infrastructure fund, making the fund permanent."),
        "91:313": ("adjacent", "Extended annual school building aid lease grants to more kinds of district lease arrangements, including space leased from other districts and municipalities."),
        "91:314": ("adjacent", "Required the department of education to maintain a 10-year school facilities plan ranking potential school building aid projects."),
        "91:316": ("adjacent", "Appropriated $1.9 million to top up fiscal 2021 kindergarten and adequacy grant payments."),
        "91:318": ("adjacent", "Rewrote how vacancies on cooperative and area school planning committees and school boards are filled - district governance mechanics."),
        "91:398": ("adjacent", "Folded the department of education into the children's mental health system of care plan - schools as a delivery point for children's behavioral health."),
        "91:425": ("adjacent", "Let the Medicaid-to-schools program accept extra federal money mid-biennium with fiscal committee approval - the funding stream for school-based health services."),
        "91:112": ("adjacent", "Rewrote the meals and rooms tax distribution, fixing the education trust fund's share of that revenue while creating the municipal revenue fund (the tax mechanics live in the property-taxes packet)."),
    },
    2023: {
        "79:150": ("core", "Rewrote the cost of an adequate education (RSA 198:40-a): base per-pupil aid rises to $4,100 with larger add-ons for free-and-reduced-lunch pupils, special education, and English learners - the formula rewrite the whole 2023 education budget turned on."),
        "79:151": ("core", "Re-enacted the annual adjustment: adequacy aid amounts rise 2 percent automatically every year starting July 2024."),
        "79:153": ("core", "Rewrote extraordinary need grants for 2023 - extra aid scaled to a town's equalized property value per pupil, targeting the towns with the weakest tax bases."),
        "79:154": ("core", "Set the 2025-and-after version of extraordinary need grants, extending the property-poor-town aid formula."),
        "79:156": ("core", "Rewrote how each municipality's total education grant is determined, including hold-harmless rules so no town's grant falls below prior levels while the new formula phases in."),
        "79:157": ("core", "Raised chartered public school per-pupil funding: adequacy amounts plus an additional grant, with the amount indexed going forward - the charter funding statute's biggest rewrite of the period."),
        "79:141": ("core", "Changed special education state aid so districts are reimbursed for costs above 3.5 times the state average per-pupil cost - the 'catastrophic aid' threshold that decides when the state steps in."),
        "79:143": ("core", "Shifted liability for certain court-ordered placements of children with disabilities, defining when the state rather than the school district pays."),
        "79:158": ("core", "Repealed the third-grade reading accountability data requirement from the statewide assessment statute (RSA 193-C) - a piece of the testing regime removed."),
        "79:191": ("core", "Fixed the education trust fund's share of the business profits tax at 41 percent of revenue - replacing the old 'increase attributable to' formula with a straight statutory split."),
        "79:192": ("core", "Fixed the education trust fund's share of the business enterprise tax at 41 percent of revenue, the same straight split."),
        "79:62": ("core", "Created the commission on New Hampshire civics inside the department of education - the body charged with building the state's civics-education program."),
        "79:80": ("core", "Created the computer science educator program (new RSA 200-O): tuition-reimbursement incentives for teachers earning computer science credentials - the trailer's main classroom-technology investment."),
        "79:65": ("core", "Created an educator recruitment program: stipends and grants for academic residencies and alternative certification pathways, aimed at the teacher shortage."),
        "79:3": ("core", "Extended the dual and concurrent enrollment program to career and technical education center students in grades 10 through 12."),
        "79:4": ("core", "Doubled the funded dual/concurrent enrollment courses per student (from 2 to 4 in each of grades 10, 11, and 12)."),
        "79:605": ("core", "Created the career and technical education incentive grant to pay transportation costs that keep sending-district students out of regional CTE centers."),
        "79:63": ("adjacent", "Appropriated $1 million to the civics commission, including a New Hampshire civics textbook project."),
        "79:66": ("adjacent", "Let discretionary federal ARPA/ESSER money fund the educator recruitment stipends."),
        "79:79": ("adjacent", "Created a computer science and STEM administrator position in the department of education."),
        "79:81": ("adjacent", "Appropriated $500,000 for computer science professional development credentials for certified educators."),
        "79:83": ("adjacent", "Put $10 million from the education trust fund into the public school infrastructure fund for school construction and safety projects."),
        "79:137": ("adjacent", "Reduced the education trust fund appropriation earmarked for education freedom accounts by $10 million in each year of the biennium, an accounting true-up to actual enrollment."),
        "79:138": ("adjacent", "Re-enacted the education trust fund statute, restating everything the fund may pay for - adequacy grants, homeowners' property tax relief, EFAs, court-ordered placements, and school building aid among them."),
        "79:139": ("adjacent", "Defined 'episode of treatment' placements for children placed by DHHS in facilities - the definition the special-education payment sections hang on."),
        "79:142": ("adjacent", "Gave the state board of education rulemaking authority for paying episode-of-treatment costs."),
        "79:144": ("adjacent", "Appropriated $9.2 million from the education trust fund for court-ordered placement costs."),
        "79:146": ("adjacent", "Rewrote the career and technical education renovation-funding statute the CTE center projects run through."),
        "79:147": ("adjacent", "Appropriated $12.5 million from the education trust fund for the Sugar River Valley career and technical education renovation project."),
        "79:148": ("adjacent", "Appropriated $7.6 million from the education trust fund for the Winnisquam regional CTE renovation project."),
        "79:159": ("adjacent", "Amended the 2021 maintenance-of-equity provision so any such aid distributes as an education grant to districts and charter schools."),
        "79:201": ("adjacent", "Extended the Medicaid-to-schools supplemental-funding authority through the 2025 biennium."),
        "79:264": ("adjacent", "Appropriated $315,700 from the education trust fund for new full-day kindergarten adequacy grants."),
        "79:383": ("adjacent", "Appropriated $150,000 to contract with the National Student Clearinghouse to track every district's graduates into college and careers - an outcomes-measurement investment."),
        "79:385": ("adjacent", "Required annual reporting on the math learning communities program partnering community colleges with high schools."),
        "79:386": ("adjacent", "Appropriated $200,000 a year to continue the math learning communities program."),
        "79:439": ("adjacent", "Charged a study committee with examining how expanded free-and-reduced-price-meal eligibility (SNAP categorical eligibility, Medicaid data) changes the pupil counts that drive state education aid."),
        "79:468": ("adjacent", "Created a commission to study hospitality and tourism education - the industry-pathways study that also arrived as a standalone bill (SB37)."),
        "79:601": ("adjacent", "Appropriated $500,000 for grants to adult education programs - the second-chance diploma track."),
        "79:606": ("adjacent", "Appropriated $4 million for the CTE transportation incentive grant program."),
        "79:609": ("adjacent", "Findings on children's mental health: schools named as the daily front line of the behavioral-health crisis."),
        "79:610": ("adjacent", "Appropriated $900,000 for the multi-tiered system of supports for behavior (MTSS-B) framework in schools."),
        "79:45": ("adjacent", "Repealed the advanced manufacturing education advisory council and partnership statutes (RSA 188-E:21-24) - a CTE-adjacent program taken off the books."),
    },
    2025: {
        "141:322": ("core", "Prohibited diversity, equity, and inclusion programs in public schools (new RSA 186:71 and following): no DEI offices, officers, trainings, or DEI-based hiring or contracting in schools, with enforcement through the department of education - the 2025 trailer's biggest education-policy section."),
        "141:321": ("core", "The statewide companion: the same DEI prohibition applied to every state agency and political subdivision (new RSA 21-I:112 and following), which reaches school districts as public employers."),
        "141:389": ("core", "Declared the legislature's position on the Claremont school-funding rulings - asserting that defining and funding an adequate education is the legislature's prerogative - while the ConVal litigation over adequacy amounts and the SWEPT remains in the courts."),
        "141:16": ("core", "Made the education freedom account expansion's effective date contingent on program participation certification - the mechanics attached to 2025's removal of the EFA income cap (2025, 75) that opened the program to every family."),
        "141:223": ("core", "Delayed the annual 2 percent inflation adjustment of per-pupil adequacy aid to July 2026 - a pause in the automatic growth of state school aid."),
        "141:224": ("core", "Re-enacted the extraordinary need grant formula - the extra aid tied to a town's equalized property value per pupil."),
        "141:225": ("core", "Created fiscal capacity disparity aid: up to $1,250 extra per pupil for municipalities with less than $1 million of equalized property value per pupil, phasing out by $1.6 million - aid aimed squarely at property-poor towns."),
        "141:226": ("core", "Rewrote how each municipality's education grant is computed to fold in the new fiscal capacity disparity aid."),
        "141:80": ("core", "Capped the education trust fund's balance: any surplus over $20 million at the close of a biennium is swept into the general fund - money that once stayed dedicated to schools."),
        "141:132": ("core", "Cut the education trust fund's share of the business profits tax from 41 percent to 39 percent, keeping more business tax revenue in the general fund."),
        "141:133": ("core", "Cut the education trust fund's share of the business enterprise tax from 41 percent to 39 percent."),
        "141:228": ("core", "Rewrote the required civics instruction statute (RSA 189:11): the locally developed civics competency assessment and the naturalization-test requirement for graduation - the testing piece of the civics program."),
        "141:275": ("core", "Ordered an independent, nationally recognized audit of the state's special education program approval and monitoring system - the oversight response to exploding special-education costs."),
        "141:276": ("core", "Restructured special education state aid administration and reimbursement - the catastrophic-cost aid that shields local budgets."),
        "141:278": ("core", "Rewrote the funding rule for statewide special education programs."),
        "141:455": ("core", "Required every school board and charter school to adopt a policy governing student cell phones and other personal electronic devices in school - the statewide 'bell-to-bell' phone-policy mandate, with exceptions for IEPs, 504 plans, and medical needs."),
        "141:17": ("adjacent", "Let an EFA student leave the program and re-enroll in public school on notice to the scholarship organization - exit mechanics for the expanded program."),
        "141:302": ("adjacent", "Let unused EFA funds roll over quarter-to-quarter and year-to-year until withdrawal or graduation."),
        "141:79": ("adjacent", "Amended the education trust fund's purpose list, including how court-ordered placement costs are paid."),
        "141:81": ("adjacent", "Rewrote the chartered public school tuition payment schedule (30/40/30 percent installments on enrollment counts)."),
        "141:82": ("adjacent", "Set special payment rules for the Virtual Learning Academy Charter School based on estimated full-time enrollment."),
        "141:83": ("adjacent", "Moved the final determination of education grants to October 1 and guaranteed each municipality at least 95 percent of its estimated grant."),
        "141:134": ("adjacent", "Rewrote the tobacco tax split: 39 percent of tobacco revenue to the education trust fund, the rest to the general fund."),
        "141:135": ("adjacent", "Rewrote the real estate transfer tax split: 39 percent to the education trust fund, the rest to the general fund."),
        "141:229": ("adjacent", "Extended the 2023 computer science professional-development appropriations' availability."),
        "141:274": ("adjacent", "Let the public school infrastructure commission approve fund expenditures without fiscal committee sign-off."),
        "141:307": ("adjacent", "Added a statewide termination trigger to the Medicaid-to-schools program if federal or state policy conflicts with parental control of children's medical services."),
        "141:398": ("adjacent", "Restated the adult education program statute as the adult high school education program for residents 16 and older."),
        "141:399": ("adjacent", "Appropriated $400,000 a year from the education trust fund for adult high school education programs."),
        "141:400": ("adjacent", "Narrowed the student-privacy statute's protected 'workforce information' definition (RSA 189:68) - part of the student-data layer."),
        "141:401": ("adjacent", "Made the education and revenue departments jointly maintain school accounting standards - the books behind local school budgets and tax rates."),
        "141:403": ("adjacent", "Appropriated $1.5 million a year from the education trust fund for statewide student learning platforms - the state's classroom-technology line."),
    },
}

# Term-matched candidates reviewed and excluded, with the reason (audit trail).
EXCLUDED = {
    2021: {
        "91:45": "Controlled drug prescription health and safety program; health regulation ('school' appears in exemption text).",
        "91:67": "Film and digital media bureau repeal; economic-development housekeeping.",
        "91:74": "Water and wastewater state aid grant freeze; municipal infrastructure (property-taxes packet).",
        "91:99": "Interest and dividends tax repeal; state tax structure (analyzed in the property-taxes packet; the education angle is the trust-fund plumbing kept above).",
        "91:109": "Business enterprise tax rate cut; state tax structure (property-taxes packet).",
        "91:110": "Business profits tax rate cut; state tax structure (property-taxes packet).",
        "91:114": "Cross-reference correction in the education trust fund statute; companion detail to 91:112.",
        "91:126": "Adult parole board; corrections.",
        "91:162": "College tuition savings plan commission; higher-education program governance.",
        "91:163": "Governor's scholarship program and fund; postsecondary scholarships.",
        "91:178": "Speech-language pathology licensing compact; occupational licensing ('school' in practice-setting lists).",
        "91:179": "Speech-language pathology initial licensure; occupational licensing.",
        "91:192": "Executive branch organization list; agency housekeeping.",
        "91:199": "Council on resources and development membership; land-use governance.",
        "91:201": "Offshore wind commission cross-reference; energy policy.",
        "91:263": "Utility regulation duties; energy policy.",
        "91:281": "Electric restructuring principles; energy policy.",
        "91:295": "Tax expenditure report mechanics; tax administration (property-taxes packet).",
        "91:330": "Sununu youth services center closure committee; juvenile justice facilities.",
        "91:331": "DHHS closed-loop referral system limit; health IT policy ('school' in referral-network lists).",
        "91:369": "National guard scholarship fund reference removal; military benefits.",
        "91:385": "Department of safety appropriation; public safety.",
        "91:395": "State mental health plan child-welfare reporting; health-system planning.",
        "91:420": "Graduate medical education payments; Medicaid hospital funding, not schools.",
        "91:464": "Granite State paid family leave plan; employment benefits.",
    },
    2023: {
        "79:7": "Retirement system 'employee' definition; pension mechanics.",
        "79:12": "Corrections unclassified positions; personnel.",
        "79:68": "Retirement benefits commission; pension policy.",
        "79:73": "Pulp and paper industry stabilization grants; economic development.",
        "79:199": "Graduate medical education payments; Medicaid hospital funding.",
        "79:243": "Business and economic affairs bureaus; agency organization.",
        "79:244": "Workforce development bureau; adult workforce programs.",
        "79:245": "Workforce development director; adult workforce programs.",
        "79:273": "Auctioneer rulemaking; occupational licensing.",
        "79:293": "Electrician licensing; occupational licensing.",
        "79:327": "Real estate appraiser examinations; occupational licensing.",
        "79:377": "Military postsecondary educational assistance; veterans' higher-education benefits.",
        "79:429": "DHHS feasibility study appropriation; health facilities.",
        "79:444": "Family resource centers; family-services funding.",
        "79:459": "Retirement system reduction age; pension policy.",
        "79:512": "Wastewater state aid appropriation; municipal infrastructure (property-taxes packet).",
        "79:534": "DHHS organizational section; health administration.",
        "79:552": "Home visiting program; maternal-child health.",
        "79:557": "Licensed nursing assistant reimbursement; health workforce.",
        "79:588": "Foster care college tuition waiver; higher-education benefit.",
        "79:589": "First-responder career development; public-safety workforce.",
        "79:598": "Early childhood mental health consultation pilot; pre-K health services.",
        "79:599": "Appropriation for the same pilot; pre-K health services.",
    },
    2025: {
        "141:35": "Workforce innovation fund; adult workforce development.",
        "141:49": "Graduate medical education payments; Medicaid hospital funding.",
        "141:91": "Workers' compensation hearings; labor law.",
        "141:112": "Wastewater aid repeal; municipal infrastructure (property-taxes packet).",
        "141:153": "Esthetician qualifications; occupational licensing ('student' in apprentice text).",
        "141:155": "Cosmetology school operating rules; occupational licensing.",
        "141:158": "Pesticide registration; agriculture regulation.",
        "141:196": "Child advocate educational outreach; oversight-office communications, not school instruction.",
        "141:234": "Motor vehicle title fees; transportation.",
        "141:259": "Maternal depression screening coverage; health insurance.",
        "141:262": "Women's health care sections; health policy.",
        "141:279": "Excellence in higher education endowment trust fund; postsecondary.",
        "141:280": "Companion higher-education trust fund section; postsecondary.",
        "141:293": "Opioid abatement commission; health governance.",
        "141:299": "Alcohol and drug abuse commission rename; health governance.",
        "141:328": "Surplus-triggered contingent appropriation; general budget mechanics (property-taxes packet).",
        "141:379": "Department of environmental services appropriation; municipal infrastructure.",
        "141:402": "Deputy education commissioner's IT-supervision duties; department housekeeping.",
        "141:405": "Advance deposit account wagering; gambling revenue (property-taxes packet).",
        "141:408": "First-responder career development program; public-safety workforce.",
        "141:410": "Home and community-based behavioral health services; health programs.",
        "141:420": "Long-term managed care study committee; health policy.",
        "141:424": "Public-private health care initiative; health policy.",
        "141:425": "Rural residency training appropriation; health workforce.",
        "141:431": "DHHS organizational section; health administration.",
        "141:442": "Retirement earnable compensation definition; pension policy.",
        "141:453": "Department of education building maintenance appropriation; agency facilities housekeeping.",
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
        "issue": "new-hampshire-03-public-education",
        "note": (
            "Hand-curated K-12 education analysis of HB2, New Hampshire's "
            "omnibus budget policy trailer, for the 2021, 2023, and 2025 "
            "budget cycles. Candidates came from relevance-term matching over "
            "every extracted section (see working/.../hb2/{year}/); a human "
            "pass kept the education sections, added three sections the "
            "matcher missed (flagged hand_added), and logged every "
            "exclusion. Roll-call votes are recorded on HB2 AS A WHOLE - a "
            "vote for or against the trailer is never a vote on one section, "
            "and must not be presented as one."
        ),
        "cycles": cycles,
    }
    (W / "hb2-sections.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# HB2 (budget policy trailer) — public-education sections, 2021 / 2023 / 2025",
        "",
        "New Hampshire passes its two-year budget in two bills: HB1 (the money)",
        "and HB2, a policy 'trailer' that bundles dozens to hundreds of legal",
        "changes into one bill. The state's biggest education changes of this",
        "period — the education freedom account program, the divisive-concepts",
        "teaching ban, the $4,100 adequacy rewrite, the special-education aid",
        "restructurings, the DEI prohibition, and the statewide cell-phone",
        "policy mandate — were all made inside HB2, not as standalone bills.",
        "This file is the hand-reviewed, section-level education analysis for",
        "the three budget cycles in scope.",
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
            f"{len(c['relevant_sections'])} education-relevant after review; "
            f"{c['whole_bill_roll_call_count']} floor roll calls on the whole bill.*",
            "",
            "Final passage (whole bill): " + "; ".join(
                f"{v['body']} {v['yeas']}–{v['nays']} ({v['motion']}, {v['date']})"
                for v in c["whole_bill_final_votes"]) + ".",
            "",
        ]
        for cat, label in (("core", "Core education sections"),
                           ("adjacent", "Adjacent (administration and funding-mechanics) sections")):
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
