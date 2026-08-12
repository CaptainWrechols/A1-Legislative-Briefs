#!/usr/bin/env python3
"""Assemble reality-map.json + .md for the NH public-education issue.

One reality card per constituent proposal (plus two threads the record itself
makes unavoidable: the education freedom account / school-choice expansion and
the parental-rights / classroom-content fight). Counts (session snapshot,
theme scorecards) are computed directly from evidence-pack.json so the
programmatic fact-check passes by construction; the notes and card prose are
the human judgment layer, with every specific claim carried as a structured,
checkable claim object.

Run from repo root:
  python3 working/new-hampshire/public-education/build-reality-map.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path("working/new-hampshire/public-education")
pack = json.loads((W / "evidence-pack.json").read_text())
bills = {b["bill_key"]: b for b in pack["bills"]}
policy = [b for b in pack["bills"] if b["relevance"] != "context"
          and b["disposition"] != "carryover_duplicate"]

# ---- session snapshot (computed) ----
snap = defaultdict(Counter)
for b in policy:
    snap[str(b["session_year"])]["in_set"] += 1
    snap[str(b["session_year"])][b["disposition"]] += 1
session_snapshot = {y: dict(c) for y, c in sorted(snap.items())}

# ---- theme scorecards: counts computed; basket/note hand-written ----
SCORECARD_NOTES = {
    "School funding: adequacy, SWEPT, and the education trust fund": (
        "rarely_moved", "high",
        "The hardest ground in the record: 84 policy bills, 9 laws - and every structural rewrite died. Full "
        "state funding of adequacy (HB678 2020; HB1799 2026, killed 185-159), SWEPT repeal or replacement "
        "(HB649 2023; HB527, HB669 2025), excess-SWEPT remittance (HB1686 2024; HB137 2025; HB675 2025, which "
        "passed one House vote 190-185 before dying), and the foundation opportunity budget (HB1680 2022, "
        "HB1586 2024, HB772 2026 - interim study every time) all failed. What passed came through budget "
        "trailers ($4,100 base and extraordinary need in 2023; fiscal capacity disparity aid in 2025) plus two "
        "standalone laws: SB420 (2022), which created extraordinary need grants, and HB1815 (2026), the "
        "biennium's education financing law, passed 188-162 and 16-8. The ConVal litigation shadows all of it; "
        "the legislature answered with a declaration of authority (HB2 2025, 141:389), and the bills to repeal "
        "that declaration (HB1456) or ask the justices for guidance (HR28) died in 2026."),
    "Special education: services, costs, and rights": (
        "often_moved", "high",
        "The record's quiet success story: 30 of 64 policy bills became law, the highest rate of any big "
        "theme. Rights and process laws passed steadily - burden of proof on districts (HB581 2021), the "
        "advocate's office (SB381 2022), services to age 22 (SB394 2022), ADR (SB135 2023; HB532 2025), "
        "expedited hearings (HB753 2025), complaint tracking (HB76 2025), parent communication (SB340 2024). "
        "The COST side moved late: the 2023 trailer set the 3.5x catastrophic threshold, the 2025 trailer "
        "ordered an independent program audit, SB292 (2025) and HB1563 (2026) rewrote the aid formula - and "
        "SB57 (2025) created exactly what the Community Conversations proposed, a commission to study special "
        "education costs. The bills that died were the money bills: catastrophic-aid raises (HB717 2025, "
        "HB773 2026), higher per-pupil amounts (SB584 2026, killed 16-8), and cost-data publication (HB1548, "
        "interim study)."),
    "School choice: EFAs, charter schools, tuitioning, and open enrollment": (
        "often_moved", "high",
        "The busiest theme (146 policy bills) and the majority's signature project. Education freedom "
        "accounts arrived inside the 2021 trailer after the standalone bills stalled, survived two repeal "
        "attempts in 2022 (HB1683, killed 189-166; SB432, 14-9), and went universal when SB295 (2025) removed "
        "the income cap - while HB115, the House version, was vetoed over an unrelated amendment and its "
        "override abandoned 1-347. Open enrollment broke through in 2025: intra-district transfers (SB97), "
        "open-enrollment funding (HB771), contracting with any approved nonpublic school (HB768), then "
        "cross-district course access (HB1817, 2026). What keeps dying is oversight of the choice programs: "
        "EFA academic accountability (HB1716, killed 194-166), assessment data (HB1610 2024), reporting "
        "(HB1513, HB1578, SB576), administration transfers to the department (five tries), and provider "
        "review - none has passed."),
    "Testing, accountability, and measures of student success": (
        "mixed", "high",
        "The grid's 'better measures' proposal has been legislated at the edges, never at the core. What "
        "passed narrows or reorganizes the existing regime: HB1160 (2024) limited statewide assessments to "
        "academic areas, SB266 (2024) consolidated assessment administration, the 2023 trailer repealed "
        "third-grade reading accountability data, HB1066 (2024) repealed the FAFSA graduation requirement - "
        "and SB378 (2024) created the performance-based accountability task force, the one direct move toward "
        "different measures. The civics competency assessment (HB320, 2021) is the period's only new required "
        "measure. Alternatives died: proficiency-based aid (HB1675 2024), testing exceptions (HB399 2023), "
        "proficiency-exam attendance waivers (HB1402 2024, interim study), graduation-requirement rewrites "
        "(HB1692 2024; HB1183 2026), assessment-score incentive grants (2022, 2023, 2025), and the "
        "standards-review commissions (HB371 2023; HB1571 2026, tabled in the Senate)."),
    "Curriculum, instruction, and classroom content": (
        "mixed", "high",
        "Two very different threads share this theme. Skills mandates pass: cursive and multiplication "
        "tables (HB170 2023), elementary literacy development (HB1015 2024), dyslexia screening (HB377 "
        "2023), civics instruction (HB1367 2022; SB216 2023), health/PE/finance-literacy studies (HB1263 "
        "2022), the adequate-education content rewrite (HB1671 2022). The content-control fights mostly die "
        "outside the budget: the divisive-concepts ban rode the 2021 trailer (91:298) after HB544 was tabled, "
        "and every later version - repeal (HB1576, SB298 2022), amendment (HB1090 2022; HB61 2023; HB1162 "
        "2024), intent requirements (HB50 2025), rewrite (SB100 2025; HB1792 2026) - failed; the "
        "school-materials bills failed five ways (HB1419 killed; SB523 dead on a 187-193 division; HB1311 "
        "and SB33 dead between the chambers; HB324 and SB434 vetoed); and the one content law enacted "
        "without the trailer was the World Economic Forum materials ban (HB1448, 2026), which became law "
        "without the Governor's signature."),
    "Teachers and school staff: certification, pay, and background checks": (
        "mixed", "high",
        "Background checks and credential discipline pass almost every year: teaching-credential checks "
        "(HB1234 2022), assault/drug disqualifications (HB1311 2022), substitute checks (SB352 2022), "
        "revoked-educator bans (SB136 2023), renewal checks (HB1795 2026), universal personnel checks "
        "(HB1827 2026), plus the educator code of ethics' new responsibility to parents (HB235 2025). "
        "Recruitment moved once the trailer led: the 2023 trailer's educator recruitment program was "
        "followed by the rural and underserved area incentive law (HB1079, 2024). What never passed is pay "
        "and pipeline support as policy: the teacher salary floor (SB219 2023), loan forgiveness (HB623 "
        "2023-24), new-teacher induction (HB1608 2024), and the teacher bill of rights (HB1669 2026) all "
        "died or sit in interim study."),
    "School governance: boards, districts, budgets, and consolidation": (
        "often_moved", "high",
        "A live front that moved hard in 2025-2026, mostly toward state and voter control of district "
        "spending: education department intervention in financially distressed districts (HB1816), monitoring "
        "reports to school boards (HB1514), independent audits (SB586), SAU budget adoption (HB564), the "
        "school-district tax cap ballot questions (HB1300), and budget-ballot information (HB557). On "
        "consolidation the legislature studies but does not mandate: SB57 (2025) and SB574 (2026) created "
        "SAU-structure studies, while mandatory SAU consolidation died twice (HB765 2025, on a unanimous "
        "18-0 committee report; HB1804 2026, interim study) and the separation bills advanced - cooperative "
        "withdrawal procedures (HB530 2023; HB1374 2026), Derry's absorption of its district (HB1331 2026), "
        "and unilateral-withdrawal study (HB1644 2026)."),
    "Students: discipline, safety, health, meals, and wellbeing": (
        "mixed", "high",
        "The widest theme (145 policy bills). Safety and health infrastructure passes: school safety "
        "coordination (SB109 2023), bullying rewrites (HB108 2025; HB131 2026), seclusion elimination "
        "(SB179 2023), trauma kits (SB429 2026), emergency map databases (HB1503 2026), sports-injury "
        "plans (HB763 2025). School meals split by design: meal-shaming and meal-debt bills died for five "
        "years (HB1127 2020 through HB703 2025, killed 202-173) until HB143 (2025) made districts provide "
        "meals during school hours with reimbursement - but every eligibility expansion (HB1212, HB572 "
        "2024; SB205 2025; HB665 2026, killed 189-158; SB204, killed 183-161) failed. The culture-war "
        "student bills split: the women's-sports law passed (HB1205 2024, 189-182 and 13-10), the mask-"
        "policy ban passed on its second try (HB361 2025), and the gender-procedures law carried "
        "school provisions (HB619 2024)."),
    "School buildings, facilities, and transportation": (
        "unfinished", "medium",
        "School building aid keeps almost passing: the facility condition assessment became law (HB365 "
        "2023) and charter eligibility for building aid became law (HB354 2024), but the money and process "
        "bills died - appropriations (HB176 2020; HB541 2023-24), nonlapsing funds (HB295 2026), priority "
        "rewrites (HB1104, HB366 2026), and the owner's-project-manager requirement, which passed both "
        "chambers in different forms twice (SB209 2025; SB513 2026) and then rode HB1565 (2026) into a "
        "veto. Water safety advanced (lead limits, HB1421 2022; filling stations, SB233 2022, HB466 2023); "
        "the electric-bus pilot and most transportation-cost bills did not."),
    "Career and technical education and workforce pathways": (
        "often_moved", "high",
        "The record's highest hit rate: 17 of 25 policy bills became law. Dual and concurrent enrollment "
        "grew in 2021 and 2023 trailers and standalone laws (SB421 2022; HB193 2025; HB1202 2026); CTE "
        "transportation was funded (HB364 2023, plus the trailer's $4 million incentive grants); regional "
        "CTE agreements were rewritten (SB99 2025, House 206-167); alternate CTE-instructor certification "
        "passed (HB354 2025); construction-funding planning advanced (SB441 2024); and SB491 (2026) let "
        "education freedom account funds pay for CTE. The stalled edge is money at scale: the 2026 "
        "dual-enrollment appropriation died (HB716), as did CTE lab fees (SB294) and the hospitality-"
        "education study (SB37 2023) - though the trailer carried a version of that study anyway."),
    "Parental rights, transparency, and school information": (
        "unfinished", "high",
        "Five years of near misses, then a breakthrough biennium. The parental bill of rights failed in "
        "2022 (HB1431, dead between the chambers), 2023 (HB10 tabled; SB272 indefinitely postponed 195-190), "
        "and twice more in 2025 (SB72, SB96) - and then HB10 (2025) became law (Chapter 74), followed by "
        "mandatory school-employee disclosure to parents (SB430 2026, after SB341's 2024 version was "
        "postponed 185-176), parental notification of health matters and curricula (HB1312 2024, passed the "
        "House 186-185), medical-transport consent (HB231 2025), and school financial transparency laws "
        "(HB1265 2024; HB1514, SB586 2026). The constitutional versions (CACR17, CACR25 2024; CACR24 2026) "
        "and the curriculum-posting mandates (HB1434 2022; HB1643 2024) still died, and two notification "
        "bills were vetoed (HB446 2025; HB1267 2026)."),
    "Technology in schools: devices, data privacy, and online learning": (
        "unfinished", "medium",
        "The smallest theme (14 policy bills) - and the one where the budget trailer did the only decisive "
        "work. The statewide cell-phone policy mandate passed inside HB2 2025 (141:455) after BOTH "
        "standalone vehicles failed: HB781 was vetoed (override abandoned 28-322) and SB206 died in a "
        "conference committee. The 2026 adjustment bills (HB1055 state-board rulemaking; HB1129 laptop "
        "exceptions) died too. Around devices, almost nothing passes: the online tutoring appropriation "
        "died at the Senate deadline (SB117 2025), screen-time and recess bills died (SB578 2026, in "
        "conference; HB1507 2026), media-literacy study was tabled (HB1087 2024), the student-data bill "
        "died in conference (HB1695 2024), and the educational-technology right to repair died (HB1071 "
        "2024). The laws are narrow: social-media credential limits (SB213 2023), Summer EBT data sharing "
        "(HB1727 2026), and the unique pupil ID system (HB1626 2022)."),
}

theme_scorecards = []
pack_themes = {t["theme"]: t for t in pack["themes"]}
for theme, (basket, certainty, note) in SCORECARD_NOTES.items():
    pt = pack_themes[theme]
    examples = pt["bill_keys"][:6]
    theme_scorecards.append({
        "theme": theme,
        "bills": pt["bills"],
        "enacted": pt["enacted"],
        "basket": basket,
        "certainty": certainty,
        "note": note,
        "example_bills": examples,
    })

# ---- topic reality cards (per constituent proposal + two record threads) ----
cards = [
    {
        "id": "increase-state-funding-swept",
        "proposal": "Increase state funding / SWEPT / distribution of funds to high-need districts",
        "tried": "Yes, every session - the targeted-aid half keeps passing (mostly through budget trailers); every structural rewrite of SWEPT or full state funding has died.",
        "where_it_died": "The House floor for the structural bills; interim study for the foundation-opportunity design; the budget trailer for what actually passed.",
        "venue": "House Education Funding (a standing committee created for this fight); Senate Education; the budget trailer; the ConVal litigation in the background.",
        "narrative": (
            "Distribution to high-need districts is the half that moves: SB420 (2022) created extraordinary "
            "need grants tied to town property wealth (Senate 21-1, House 261-71), the 2023 trailer raised "
            "base adequacy to $4,100 with bigger poverty add-ons, the 2025 trailer added fiscal capacity "
            "disparity aid of up to $1,250 per pupil - and HB1815 (2026), the education financing law, passed "
            "188-162 and 16-8. Raising the state's overall share is the half that fails: full state funding "
            "died in 2020 (HB678) and again in 2026 (HB1799, killed 185-159); every SWEPT restructuring died "
            "(repeal HB649 2023; local-contribution replacement HB527 2025; the equalized statewide rate "
            "HB669 2025; HB675 2025 passed one House vote 190-185 before being killed); the foundation "
            "opportunity budget went to interim study three times (HB1680 2022, HB1586 2024, HB772 2026); and "
            "even studying alternatives was killed 195-157 (HB491, 2026). The same 2025 trailer that added "
            "disparity aid also delayed the 2 percent adequacy inflation adjustment, swept trust-fund "
            "surpluses over $20 million to the general fund, and declared the legislature's authority over "
            "school funding (141:389) while ConVal is argued - the repeal of that declaration (HB1456) and "
            "the request for an opinion of the justices (HR28) both died in 2026."),
        "claims": [
            {"bill_key": "2022:SB420", "disposition": "enacted",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 21, "nays": 1}},
            {"bill_key": "2026:HB1815", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 188, "nays": 162}},
            {"bill_key": "2020:HB678", "disposition": "killed"},
            {"bill_key": "2026:HB1799", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 185, "nays": 159}},
            {"bill_key": "2023:HB649", "disposition": "killed"},
            {"bill_key": "2025:HB527", "disposition": "killed"},
            {"bill_key": "2025:HB669", "disposition": "killed"},
            {"bill_key": "2025:HB675", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 190, "nays": 185}},
            {"bill_key": "2022:HB1680", "disposition": "interim_study"},
            {"bill_key": "2024:HB1586", "disposition": "interim_study"},
            {"bill_key": "2026:HB772", "disposition": "interim_study"},
            {"bill_key": "2026:HB491", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 195, "nays": 157}},
            {"bill_key": "2026:HB1456", "disposition": "killed"},
            {"bill_key": "2026:HR28", "disposition": "killed"},
        ],
    },
    {
        "id": "diversify-revenue-sources",
        "proposal": "Diversify state revenue sources (income tax, business taxes, interest & dividends and other revenue)",
        "tried": "For education specifically, yes - and every attempt died, while the budget trailers moved the education trust fund's revenue the other way.",
        "where_it_died": "The House floor, usually by lopsided margins; the tax bills' full record is in the property-taxes packet.",
        "venue": "House Ways and Means for the taxes; House Education Funding for the education-revenue studies; the budget trailer for what actually changed.",
        "narrative": (
            "Every bill tying new or restored revenue to schools died. Extending the interest and dividends "
            "tax to capital gains for adequacy funding (HB686, 2020) and the electronics tax dedicated to "
            "education (HB1492, 2020) were killed; raising the education trust fund's business-tax shares "
            "(HB255 and HB318, 2025) died months before the 2025 trailer cut those shares from 41 to 39 "
            "percent; the broader reallocation bill (HB503, 2025) was crushed 345-27; state school-funding "
            "bonds (HB1714, 2026) died; and the 2026 SWEPT-and-revenues package (HB1708) died in committee. "
            "Even the study bills failed: alternative education funding to reduce property-tax reliance was "
            "killed on the House floor 195-157 (HB491), and the revenue-raising study (HB1579) sits in "
            "interim study alongside three SWEPT study bills (HB734, HB1787, HB1800). What the trailers did "
            "instead was subtract: the 39 percent shares, the $20 million trust-fund surplus sweep, and the "
            "adequacy-adjustment delay all moved money away from the dedicated education stream. The full "
            "income/sales/business-tax record lives in the property-taxes packet; from the education side, "
            "no diversification proposal has ever reached a floor win."),
        "claims": [
            {"bill_key": "2020:HB686", "disposition": "killed"},
            {"bill_key": "2020:HB1492", "disposition": "killed"},
            {"bill_key": "2025:HB255", "disposition": "killed"},
            {"bill_key": "2025:HB318", "disposition": "killed"},
            {"bill_key": "2025:HB503", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 345, "nays": 27}},
            {"bill_key": "2026:HB1714", "disposition": "killed"},
            {"bill_key": "2026:HB1708", "disposition": "killed"},
            {"bill_key": "2026:HB491", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 195, "nays": 157}},
            {"bill_key": "2026:HB1579", "disposition": "interim_study"},
            {"bill_key": "2026:HB734", "disposition": "interim_study"},
            {"bill_key": "2026:HB1787", "disposition": "interim_study"},
            {"bill_key": "2026:HB1800", "disposition": "interim_study"},
        ],
    },
    {
        "id": "better-measures-student-success",
        "proposal": "Identify better measures of student success",
        "tried": "Yes - the legislature keeps adjusting the measurement regime, and in 2024 created a task force for exactly this question; the replacement-measure bills themselves keep dying.",
        "where_it_died": "The House floor and the House table for alternatives; the Senate table for the 2026 standards review.",
        "venue": "House and Senate Education; the statewide assessment statute (RSA 193-C).",
        "narrative": (
            "The direct answer to this proposal is SB378 (2024): the performance-based school accountability "
            "system task force, now law. Around it, what passed narrows the existing regime rather than "
            "replacing it: HB1160 (2024) limited statewide assessments to academic areas, SB266 (2024) "
            "consolidated assessment administration in the department, the 2023 trailer repealed third-grade "
            "reading accountability data, and HB1066 (2024) repealed the FAFSA graduation requirement. The "
            "one new required measure is the civics competency assessment for graduation (HB320, 2021, House "
            "208-141). Everything that would substitute a different metric died: statewide assessment report "
            "rewrites (HB1323 2020, killed 187-139; HB323 2021-22), a graduation testing exception (HB399 "
            "2023, tabled), the proficiency-exam attendance waiver (HB1402 2024, interim study), "
            "proficiency-adjusted aid (HB1675 2024), assessment-score incentive grants (three versions, 2022 "
            "through 2025), graduation-requirement rewrites (HB1692 2024; HB1183 2026), the school-standards "
            "commissions (HB371 2023, tabled; HB1212 2026), and the 2026 statewide standards review (HB1571), "
            "which passed the House and died on the Senate table."),
        "claims": [
            {"bill_key": "2024:SB378", "disposition": "enacted"},
            {"bill_key": "2024:HB1160", "disposition": "enacted"},
            {"bill_key": "2024:SB266", "disposition": "enacted"},
            {"bill_key": "2024:HB1066", "disposition": "enacted"},
            {"bill_key": "2021:HB320", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 208, "nays": 141}},
            {"bill_key": "2020:HB1323", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 187, "nays": 139}},
            {"bill_key": "2023:HB399", "disposition": "killed"},
            {"bill_key": "2024:HB1402", "disposition": "interim_study"},
            {"bill_key": "2024:HB1675", "disposition": "killed"},
            {"bill_key": "2024:HB1692", "disposition": "killed"},
            {"bill_key": "2026:HB1183", "disposition": "killed"},
            {"bill_key": "2023:HB371", "disposition": "killed"},
            {"bill_key": "2026:HB1571", "disposition": "killed"},
        ],
    },
    {
        "id": "special-education-cost-commission",
        "proposal": "Create a commission to study special education costs",
        "tried": "Yes - and it exists: SB57 (2025) created the commission to study the costs of special education. The aid-formula rewrites passed with it; the aid-increase bills died.",
        "where_it_died": "Nowhere - this is the one proposal already enacted in its own words; the surrounding money bills died on both floors.",
        "venue": "Senate Education; House Education Policy; the special education statutes (RSA 186-C).",
        "narrative": (
            "This proposal is law. SB57 (2025) established a commission to study the costs of special "
            "education (alongside a school-administrative-unit study committee), after HB1176 (2024) - a "
            "commission to study special education funding - had gone to interim study. The refile that "
            "duplicated the commission (HB431, 2026) was killed on the Senate floor, and the bill directing "
            "the commission to consider centralized service locations (HB1221, 2026) was killed in the "
            "House. The cost machinery itself moved in parallel: the 2023 trailer set the 3.5x catastrophic "
            "threshold and shifted court-ordered placement liability (enacted standalone as HB1511, 2024), "
            "SB292 (2025) rewrote special-education aid, HB1563 (2026) rewrote the formula and its "
            "administration, the 2025 trailer ordered an independent audit of program approval and "
            "monitoring, and HB1099 (2026) created a study of residential-placement education costs. What "
            "keeps dying is more money and more disclosure: catastrophic-aid increases (HB717 2025; HB773 "
            "2026), higher per-pupil special-education funding (SB584 2026, killed 16-8; HB1557 2026, killed "
            "184-157), trust-fund catastrophic funding (HB742 2026, interim study), and statewide cost-data "
            "publication (HB1548 2026, interim study). The House also adopted HCR10 (2024), urging Congress "
            "to fully fund federal special education aid."),
        "claims": [
            {"bill_key": "2025:SB57", "disposition": "enacted"},
            {"bill_key": "2024:HB1176", "disposition": "interim_study"},
            {"bill_key": "2026:HB431", "disposition": "killed"},
            {"bill_key": "2026:HB1221", "disposition": "killed"},
            {"bill_key": "2024:HB1511", "disposition": "enacted"},
            {"bill_key": "2025:SB292", "disposition": "enacted"},
            {"bill_key": "2026:HB1563", "disposition": "enacted"},
            {"bill_key": "2026:HB1099", "disposition": "enacted"},
            {"bill_key": "2025:HB717", "disposition": "killed"},
            {"bill_key": "2026:HB773", "disposition": "killed"},
            {"bill_key": "2026:SB584", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Inexpedient", "yeas": 16, "nays": 8}},
            {"bill_key": "2026:HB1557", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 184, "nays": 157}},
            {"bill_key": "2026:HB742", "disposition": "interim_study"},
            {"bill_key": "2026:HB1548", "disposition": "interim_study"},
            {"bill_key": "2024:HCR10", "disposition": "passed"},
        ],
    },
    {
        "id": "career-pathways-business-partnerships",
        "proposal": "Offer more career pathways and opportunities to partner with businesses",
        "tried": "Yes - and it passes more reliably than anything else in the education record: 17 of 25 CTE policy bills became law.",
        "where_it_died": "Almost nowhere; the deaths are appropriations (the 2026 dual-enrollment funding) and fees (CTE lab fees).",
        "venue": "House and Senate Education; the CTE statutes (RSA 188-E); budget trailers for the money.",
        "narrative": (
            "This is the legislature's most bipartisan education ground. Dual and concurrent enrollment - "
            "high schoolers earning community-college credit - was rebuilt in the 2021 trailer, extended to "
            "CTE students (SB421, 2022), doubled per grade in the 2023 trailer, and adjusted again in laws "
            "of 2025 (HB193) and 2026 (HB1202). CTE-center transportation, the barrier the Community "
            "Conversations named, was funded by HB364 (2023) plus the trailer's $4 million incentive-grant "
            "program. Regional CTE agreements were rewritten (SB99, 2025, House 206-167), the advisory "
            "council was restructured (SB195, 2025), industry-professional certification pathways opened "
            "(HB354, 2025), donations to CTE programs were extended (SB98, 2025), classroom-space "
            "reallocation passed (HB484, 2025), construction-funding planning advanced (SB441, 2024), and "
            "SB491 (2026) let education freedom account funds pay for CTE courses. The stalls are narrow: "
            "the 2026 dual-enrollment appropriation died (HB716), CTE lab-fee funding was tabled (SB294, "
            "2025), the 2024 dual-enrollment expansion died (HB420), and the hospitality-education study "
            "(SB37, 2023) was killed as a standalone - though the 2023 trailer carried a version of it "
            "anyway."),
        "claims": [
            {"bill_key": "2022:SB421", "disposition": "enacted"},
            {"bill_key": "2025:HB193", "disposition": "enacted"},
            {"bill_key": "2026:HB1202", "disposition": "enacted"},
            {"bill_key": "2023:HB364", "disposition": "enacted"},
            {"bill_key": "2025:SB99", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 206, "nays": 167}},
            {"bill_key": "2025:SB195", "disposition": "enacted"},
            {"bill_key": "2025:HB354", "disposition": "enacted"},
            {"bill_key": "2025:SB98", "disposition": "enacted"},
            {"bill_key": "2025:HB484", "disposition": "enacted"},
            {"bill_key": "2024:SB441", "disposition": "enacted"},
            {"bill_key": "2026:SB491", "disposition": "enacted"},
            {"bill_key": "2026:HB716", "disposition": "killed"},
            {"bill_key": "2025:SB294", "disposition": "killed"},
            {"bill_key": "2024:HB420", "disposition": "killed"},
            {"bill_key": "2023:SB37", "disposition": "killed"},
        ],
    },
    {
        "id": "technology-in-schools",
        "proposal": "Review the use of technology in school",
        "tried": "The device half, yes - the statewide cell-phone policy mandate passed inside the 2025 budget trailer after both standalone bills failed. The screen-time and review half has never passed.",
        "where_it_died": "Vetoes and conference committees for the phone bills; the House floor and table for everything else.",
        "venue": "House and Senate Education; the budget trailer for what passed.",
        "narrative": (
            "The one enacted answer rode HB2 2025 (141:455): every school board and charter school must "
            "adopt a policy governing student cell phones and personal devices, with IEP and medical "
            "exceptions. Both standalone vehicles died first - HB781 was vetoed and its override abandoned "
            "28-322, and SB206 died in a conference committee that never agreed. The 2026 follow-ups (state "
            "board rulemaking over phone policies, HB1055; superintendent laptop exceptions, HB1129) were "
            "killed. Beyond devices, the review this proposal asks for has no vehicle: the media-literacy "
            "study commission was tabled (HB1087, 2024), the screen-time-adjacent play-based curriculum and "
            "recess bills died (SB578, 2026, in conference; HB1507, 2026), the online-tutoring appropriation "
            "died at the Senate deadline (SB117, 2025), the educational-technology right to repair died "
            "(HB1071, 2024), and the student data protection bill died in a conference committee (HB1695, "
            "2024). The enacted layer is narrow and specific: schools cannot demand students' social-media "
            "credentials (SB213, 2023), student data may flow to the Summer EBT meals program (HB1727, "
            "2026), and the unique pupil ID system was rebuilt (HB1626, 2022)."),
        "claims": [
            {"bill_key": "2025:HB781", "disposition": "vetoed"},
            {"bill_key": "2025:SB206", "disposition": "killed"},
            {"bill_key": "2026:HB1055", "disposition": "killed"},
            {"bill_key": "2026:HB1129", "disposition": "killed"},
            {"bill_key": "2024:HB1087", "disposition": "killed"},
            {"bill_key": "2026:SB578", "disposition": "killed"},
            {"bill_key": "2026:HB1507", "disposition": "killed"},
            {"bill_key": "2025:SB117", "disposition": "killed"},
            {"bill_key": "2024:HB1071", "disposition": "killed"},
            {"bill_key": "2024:HB1695", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 192, "nays": 173}},
            {"bill_key": "2023:SB213", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 201, "nays": 175}},
            {"bill_key": "2026:HB1727", "disposition": "enacted"},
            {"bill_key": "2022:HB1626", "disposition": "enacted"},
        ],
    },
    {
        "id": "school-choice-efa",
        "proposal": "(Record thread) Education freedom accounts and school choice",
        "tried": "The record's largest thread - 146 policy bills - and the majority's signature project; the oversight side has never passed.",
        "where_it_died": "Repeals and accountability bills die on both floors; the expansions pass, twice through budget trailers.",
        "venue": "House Education Policy; Senate Education; budget trailers for the program's creation and mechanics.",
        "narrative": (
            "Education freedom accounts were created inside the 2021 trailer (91:431) after the standalone "
            "bills stalled - SB130 passed its Senate votes 14-10 and was left on the table. Repeal died in "
            "2022 (HB1683, killed 189-166; SB432, 14-9 in the Senate), eligibility widened in 2023 (HB367, "
            "House 187-184), and SB295 (2025) removed the income cap entirely (Senate 16-8, House 188-176), "
            "while the House version (HB115) was vetoed over an unrelated amendment and its override "
            "abandoned 1-347. Open enrollment followed the same arc in 2025-2026: intra-district transfers "
            "(SB97, House 199-165), open-enrollment funding (HB771, House 205-169), contracting with any "
            "approved nonpublic school (HB768), and cross-district course access (HB1817, 2026, House "
            "179-156) all became law, while the universal versions (HB741, interim study; SB101, tabled "
            "after a 168-184 floor loss; HB709, killed by the Senate) fell short. The oversight ledger is "
            "one-sided: the EFA performance audit law (HB1135, 2022) passed, but academic accountability "
            "(HB1716, killed 194-166), assessment data (HB1610, 2024), reporting-and-transparency bills "
            "(HB1513, HB1578, SB576, 2026), five department-administration transfers, and every "
            "provider-review bill died."),
        "claims": [
            {"bill_key": "2021:SB130", "disposition": "killed"},
            {"bill_key": "2022:HB1683", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 189, "nays": 166}},
            {"bill_key": "2022:SB432", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Inexpedient", "yeas": 14, "nays": 9}},
            {"bill_key": "2023:HB367", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 187, "nays": 184}},
            {"bill_key": "2025:SB295", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 188, "nays": 176}},
            {"bill_key": "2025:HB115", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "Veto Override", "yeas": 1, "nays": 347}},
            {"bill_key": "2025:SB97", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 199, "nays": 165}},
            {"bill_key": "2025:HB771", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 205, "nays": 169}},
            {"bill_key": "2025:HB768", "disposition": "enacted"},
            {"bill_key": "2026:HB1817", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 179, "nays": 156}},
            {"bill_key": "2026:HB741", "disposition": "interim_study"},
            {"bill_key": "2026:HB709", "disposition": "killed"},
            {"bill_key": "2022:HB1135", "disposition": "enacted"},
            {"bill_key": "2026:HB1716", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 194, "nays": 166}},
        ],
    },
    {
        "id": "parental-rights-content",
        "proposal": "(Record thread) Parental rights and classroom content",
        "tried": "Every session, in every form - failed for five years by one-vote margins and vetoes, then broke through in 2025-2026.",
        "where_it_died": "Conference committees, the House table, and the Governor's desk - until HB10 (2025).",
        "venue": "House Education Policy; Senate Education; the Governor's desk repeatedly.",
        "narrative": (
            "The parental bill of rights failed in 2022 (HB1431, conference report rejected 171-176), 2023 "
            "(HB10 tabled after a 189-195 floor loss; SB272 indefinitely postponed 195-190), and twice more "
            "in 2025 (SB72, SB96) - then HB10 (2025) became law as Chapter 74 (House 212-161), followed by "
            "mandatory school-employee disclosure to parents (SB430, 2026) after the 2024 version (SB341) "
            "was postponed 185-176. Parental notification of health matters and curricula passed the House "
            "by a single vote (HB1312, 2024, 186-185); medical-transport consent (HB231, 2025) and the "
            "educator code's responsibility to parents (HB235, 2025) followed. The content-control side "
            "split: the divisive-concepts ban lives where the 2021 trailer put it (91:298) - repeal, "
            "amendment, and rewrite bills failed in every session since, including SB100 (2025) and HB1792 "
            "(2026, concurrence failed 127-222) - and the 2025 trailer added the DEI prohibition in public "
            "schools (141:322). The school-materials bills failed five ways: killed (HB1419, 2024), dead on "
            "a 187-193 division (SB523, 2024), dead between the chambers (HB1311, 2024; SB33, 2026), and "
            "vetoed (HB324, 2025, override failing 183-167; SB434, 2026, no override recorded as of "
            "collection). The constitutional amendments (CACR17, CACR25, CACR24) all died in committee or "
            "on the floor."),
        "claims": [
            {"bill_key": "2022:HB1431", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "CofC", "yeas": 171, "nays": 176}},
            {"bill_key": "2023:HB10", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 189, "nays": 195}},
            {"bill_key": "2023:SB272", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Indefinitely Postpone", "yeas": 195, "nays": 190}},
            {"bill_key": "2025:HB10", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 212, "nays": 161}},
            {"bill_key": "2025:SB72", "disposition": "killed"},
            {"bill_key": "2025:SB96", "disposition": "killed"},
            {"bill_key": "2026:SB430", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 193, "nays": 163}},
            {"bill_key": "2024:SB341", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Indefinitely Postpone", "yeas": 185, "nays": 176}},
            {"bill_key": "2024:HB1312", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 186, "nays": 185}},
            {"bill_key": "2025:HB231", "disposition": "enacted"},
            {"bill_key": "2025:HB235", "disposition": "enacted"},
            {"bill_key": "2025:SB100", "disposition": "killed"},
            {"bill_key": "2026:HB1792", "disposition": "killed"},
            {"bill_key": "2024:HB1419", "disposition": "killed"},
            {"bill_key": "2024:SB523", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 14, "nays": 10}},
            {"bill_key": "2024:HB1311", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 194, "nays": 180}},
            {"bill_key": "2026:SB33", "disposition": "killed"},
            {"bill_key": "2025:HB324", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "Veto Override", "yeas": 183, "nays": 167}},
            {"bill_key": "2026:SB434", "disposition": "vetoed"},
        ],
    },
]

# ---- recent enactments watchlist ----
watch_keys = [
    ("2025:SB295", "EFA income cap removed - universal eligibility"),
    ("2026:HB1815", "Education financing rewrite (the biennium's main standalone funding law)"),
    ("2026:HB1563", "Special education aid formula and administration rewrite"),
    ("2025:SB292", "Special education aid to districts"),
    ("2025:SB57", "SAU-reduction study committee + special education cost commission"),
    ("2026:SB574", "Commission on SAU efficiency and structure"),
    ("2025:HB10", "Parental bill of rights (Chapter 74)"),
    ("2026:SB430", "Mandatory school-employee disclosure to parents"),
    ("2026:HB1374", "Cooperative school district withdrawal procedures"),
    ("2026:HB1331", "Derry cooperative school district absorption"),
    ("2026:HB1817", "Cross-district curricular course access"),
    ("2025:HB771", "Open enrollment school funding"),
    ("2025:SB97", "Intra-district public school transfers"),
    ("2024:HB1205", "Women's school sports restriction"),
    ("2025:HB143", "School meals during school hours with reimbursement"),
    ("2026:HB1727", "Student data sharing for Summer EBT"),
    ("2026:SB586", "Independent audits for charter schools, SAUs, and unaudited districts"),
    ("2026:HB1816", "Education department intervention in district financial emergencies"),
    ("2025:HB557", "School budget ballot information"),
    ("2026:SB491", "EFA funds usable for career and technical education"),
]
watchlist = {
    "note": "Laws from the 2025-2026 biennium that set the terrain the proposals would land on.",
    "laws": [{"bill_key": k, "what": w, "citation": bills[k]["stage"]} for k, w in watch_keys],
}

# ---- high-support non-enactments (verbatim from the pack) ----
high_support = pack["high_support_non_enactments"]

# ---- people and process ----
people = {
    "frequent_primary_sponsors": pack["people_signals"]["frequent_primary_sponsors"],
    "cross_party_sponsorship": {
        "count": pack["people_signals"]["cross_party_count"],
        "note": ("Bills whose sponsor list includes both major parties. Party labels exist only for "
                 "2025-2026 sponsors, so this understates the true number."),
    },
    "chokepoints": [
        "The House floor's Inexpedient to Legislate motion: where school-funding rewrites, meal expansions, and choice-oversight bills die - often after passing committee.",
        "Conference committees and concurrence votes: the parental-rights, school-materials, cell-phone, and bullying/open-enrollment packages all passed both chambers in different forms and died between them at least once.",
        "The Governor's desk: eighteen education bills were vetoed in this record, and no override succeeded - several fell short with clear majorities (HB324 183-167; HB319 182-173; HB446 181-170).",
        "The budget trailer: the EFA program, the divisive-concepts ban, the adequacy formula rewrites, the DEI prohibition, and the cell-phone mandate all became law inside HB2, with votes only on the whole bill.",
    ],
    "veto_watch": [
        "HB242 (2021): adequate-education content - vetoed, override failed 165-182.",
        "HB324 (2025): school materials - vetoed, override failed 183-167.",
        "HB115 (2025): universal EFA (House version) - vetoed, override abandoned 1-347 (SB295 carried the policy).",
        "HB781 (2025): cell-phone-free education - vetoed, override abandoned 28-322 (the trailer carried the policy).",
        "SB434 (2026): school materials again - vetoed, no override action recorded as of collection.",
        "HB1358 (2026): all-charter transition study - vetoed, no override action recorded as of collection.",
        "HB1610 (2026): district retention of year-end funds - vetoed, no override action recorded as of collection.",
        "HB1565 (2026): school building aid project-manager rider - vetoed, no override action recorded as of collection.",
    ],
}

rm = {
    "issue": "new-hampshire-03-public-education",
    "generated_by": "reality-mapper v2.2 (NH public-education run)",
    "sessions": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "coverage_caveat": (
        "Discovery is certified against the complete OpenStates bulk universe for 2020-2024 (5,467 bills; "
        "every title swept with a wide-net education vocabulary and every candidate human-reviewed - see "
        "certification-report.json) and against the official state database for 2025-2026 (the identical wide "
        "net swept all 2,234 current-biennium titles; see certification-current.json). Biennium-spanning "
        "bills are counted once, in their decision year. Party labels exist for 2025-2026 sponsors and for "
        "roll-call ballots; 2020-2024 sponsor party labels are absent, so cross-party counts understate."),
    "session_snapshot": session_snapshot,
    "theme_scorecards": theme_scorecards,
    "topic_reality_cards": cards,
    "recent_enactments_watchlist": watchlist,
    "high_support_non_enactments": high_support,
    "people_and_process": people,
}
(W / "reality-map.json").write_text(json.dumps(rm, indent=2), encoding="utf-8")

# ---- markdown skim ----
md = ["# Reality map — Public Education in New Hampshire", ""]
md += [rm["coverage_caveat"], ""]
md += ["## Reality cards", ""]
for c in cards:
    md += [f"### {c['proposal']}", "", f"*Tried?* {c['tried']}", "",
           f"*Where it died:* {c['where_it_died']}", "", c["narrative"], ""]
md += ["## Theme scorecards", ""]
for t in theme_scorecards:
    md += [f"- **{t['theme']}** — {t['bills']} bills, {t['enacted']} laws, basket {t['basket']}: {t['note'][:180]}..."]
md += ["", "## Chokepoints", ""]
for c in people["chokepoints"]:
    md += [f"- {c}"]
(W / "reality-map.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"Wrote reality-map.json ({len(cards)} cards, {len(theme_scorecards)} scorecards) and reality-map.md")
