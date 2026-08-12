#!/usr/bin/env python3
"""Assemble reality-map.json + .md for the NH property-taxes issue.

One reality card per constituent proposal (plus two threads the record itself
makes unavoidable: the statewide education property tax fight and the
municipal-aid/retirement-contribution thread). Counts (session snapshot,
theme scorecards) are computed directly from evidence-pack.json so the
programmatic fact-check passes by construction; the notes and card prose are
the human judgment layer, with every specific claim carried as a structured,
checkable claim object.

Run from repo root:
  python3 working/new-hampshire/property-taxes/build-reality-map.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")
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
    "Property tax relief: exemptions, credits, and deferrals": (
        "unfinished", "high",
        "The busiest relief thread and the one with real recent wins: veterans' credits and exemptions "
        "passed repeatedly (HB130 2020, HB1667 2022, HB1154 2024, HB99 2025, HB1494 2026), charitable-"
        "exemption law was rewritten (HB1055 2024), and SB83 (2025) built a state fund - financed by the "
        "new video lottery terminals - to reimburse towns for the elderly, disabled, blind, and deaf "
        "exemptions. What keeps dying is broad relief for ordinary homeowners: bills exempting or capping "
        "taxes for elderly homeowners (HB101, HB766, HB782, all 2025) and lower-income owners (HB1674 2026) "
        "were killed in the House, and the working-families refund program (SB95 2020) died on the Senate table."),
    "Assessment, abatement, and property tax administration": (
        "mixed", "high",
        "Administration moves quietly and often: the equalization-rate study (HB411 2021), the assessing "
        "certification board (HB1552 2022), the equalization manual in rules (HB285 2023), abatement rules "
        "(HB202 2024), abatement interest (SB317 2022), and LIHTC assessment (SB173 2025) all became law. "
        "Transparency bills aimed at taxpayers rather than assessors fare worse: more information on tax "
        "bills (SB252 2022), tax-change breakdowns (HB495 2025), revaluation notice (SB225 2025), and public "
        "notice of tax impacts (SB217 2025) were killed, and HB284 (2025) passed the House 198-160 before "
        "dying in the Senate - until HB138 (2025) put multi-year tax-impact notation on warrant articles "
        "and HB1807 (2026) extended it. Structural rewrites of assessment itself (cost-based value, HB1380 "
        "2026; the land value tax, HB1417 2026) died on the House floor."),
    "The statewide education property tax and school funding": (
        "unfinished", "high",
        "The record's center of gravity: 112 policy bills. Aid formulas moved through budget trailers and "
        "a few standalone laws (SB420 2022 created extraordinary need grants; HB2 2025 added fiscal capacity "
        "disparity aid), but every structural SWEPT bill died: repeal (HB649 2023), replacement with a local "
        "contribution (HB527 2025), full state collection with an equalized rate (HB669 2025, HB675 2025 - "
        "the latter passed one House vote 190-185 before dying), excess-SWEPT remittance (HB1686 2024, HB137 "
        "2025), and the donor-town negative-rate fix (HB1385 2026). The ConVal school-funding litigation "
        "shadows all of it, and the 2025 trailer answered with a declaration of legislative authority "
        "(141:389) rather than a formula settlement."),
    "State business taxes: BPT and BET": (
        "mixed", "high",
        "The cuts came through budget trailers (2021: BPT 7.7 to 7.6, BET 0.675 to 0.55) and one standalone "
        "law (HB1221 2022, BPT to 7.5). Every bill pushing the other way died in the House: rate restorations "
        "(HB623 2020, HB10 2021-22, HB1422 2024), the low-wage-employer surcharge (HB1478 2022, killed 304-40), "
        "and the 2025 bills raising the education trust fund's share (HB255, HB318) - after which the 2025 "
        "trailer cut that share from 41 to 39 percent. Full-repeal bills (HB1546, HB1629, both 2026) also died: "
        "the settled zone is lower rates, not zero and not restoration."),
    "The interest and dividends tax": (
        "rarely_moved", "high",
        "The tax was phased out (HB2 2021) and the repeal accelerated to January 1, 2025 (HB2 2023) - both "
        "inside budget trailers, never as a standalone law. Standalone bills on both sides died: faster-repeal "
        "bills (HB568 2022; HB100 2023-24, interim study) and adjustment bills (SB261 2023, killed 13-10; "
        "HB192 2024; HB1492 2024, interim study). Since the tax ended, no bill has proposed restoring it - "
        "the certified record contains no restoration attempt."),
    "Meals and rooms, gaming, and other existing revenue streams": (
        "mixed", "high",
        "Gaming expands and rates stand still. The meals and rooms rate was cut inside HB2 2021 (9 to 8.5 "
        "percent); the one bill to raise it back (HB1480 2026) and the cut-plus-share bill (HB1204 2022) died. "
        "The communications services tax repeal was filed four times (HB1500 2022 through HB417 2026) and "
        "always ended in interim study. Gaming is where new money actually arrived: keno statewide and local "
        "games of chance (HB737 2025), extended keno hours (HB591 2025 and HB2 2025), historic horse racing "
        "with host-community revenue (SB472 2024), and video lottery terminals (HB2 2025) - while online "
        "gambling (SB104 2023, SB168 2025) kept dying."),
    "New or broad-based taxes and constitutional tax limits": (
        "rarely_moved", "high",
        "Nothing on this front passed in seven years, in either direction. New-tax bills died fast (the "
        "electronics tax HB1492 2020, killed 320-11; the vacancy tax HB1707 2026; the luxury second-home "
        "assessment HB1786 2026, tabled 189-158). So did every constitutional ban: the income-tax ban (CACR1 "
        "2021) won a majority 202-171 but fell short of three-fifths, as did the sales-tax ban (CACR2 2021) "
        "the two-thirds-for-new-taxes amendment (CACR15 2024, failed 183-185), and the 2026 tax-law-adoption amendments (CACR10, 194-158; CACR12, 193-148 after passing the Senate 16-8 - majorities, not three-fifths). Even studying revenue "
        "options was killed on the floor twice in 2026 (HB1636, 284-76; HB491, 195-157)."),
    "Municipal revenue, state aid, and state budget mechanics": (
        "unfinished", "high",
        "The one big win rode a trailer: HB2 2021 created the meals-and-rooms municipal revenue fund after "
        "SB99 (2021) passed the Senate 24-0 and died on the table. The retirement-contribution state share - "
        "towns' most-filed ask - failed in every form except HB1221's one-time 7.5 percent payment (2022): "
        "HB1417 (2022) passed both chambers' floors and died at the Senate deadline, SB114 (2023) passed 23-0 "
        "then sat on the table, SB20 (2025) passed 23-0 and died at the deadline, and HB197 (2026) was killed "
        "172-159. Local-option revenue died every time (occupancy fees and room assessments in 2020, 2022, 2023, 2024, 2025, and 2026; the gaming-facility enterprise-value tax HB688 2025), and revenue "
        "sharing went from suspended (every budget) to repealed outright (HB2 2025)."),
    "Current use, timber, utility, and other property-tax bases": (
        "mixed", "medium",
        "Technical but consequential for small towns: the current-use formula (SB48 2021), renewable-PILOT "
        "agreements (HB64 2021), the timber tax (SB514 2024), power-generation assessing commissions (HB410 "
        "2022, SB225 2023, HB458 2024), and the utility-property/SWEPT treatment of generators (HB696 2025) "
        "all became law. The contested ground - changing current-use eligibility (HB1484 2024, HB1691 2026, "
        "SB504 2024) - keeps dying."),
    "School district and municipal consolidation or cooperation": (
        "often_moved", "medium",
        "The legislature is active here - but in the opposite direction from the constituent proposal. What "
        "passed makes it easier to leave or absorb districts: withdrawal procedure laws (HB530 2023, HB1374 "
        "2026), Derry's absorption of its cooperative district (HB1331 2026), and cost-apportionment rules "
        "(HB152 2021). No bill in the certified record proposes state incentives for consolidating services "
        "or regionalizing. Consolidation MANDATES were filed and failed: consolidating school administrative "
        "units died in 2025 (HB765, unanimous ITL committee report) and sits in interim study in 2026 "
        "(HB1804), and the school-building consolidation planning bill (HB1818 2026) died on the Senate "
        "table. The other active thread is unilateral-withdrawal expansion (HB1644 2026, interim study)."),
    "Tax caps and local budget limits": (
        "often_moved", "high",
        "A live, moving front: tax-cap and budget-cap laws passed in 2021 (SB52), 2024 (HB1105, SB383), 2025 (HB200, HB374, and SB105 - town budget caps), "
        "and 2026 (HB1300, which puts school-district tax cap questions on the 2026 and 2028 state ballots). "
        "Override-procedure fights cut both ways, and loosening bills (HB1278, HB1528, HB1383, all 2026) died "
        "while the cap-tightening side kept winning."),
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
        "id": "restore-interest-dividends-tax",
        "proposal": "Restore the interest and dividends tax",
        "tried": "No. Repeal fights, yes - restoration, never.",
        "where_it_died": "The tax ended January 1, 2025 (accelerated by HB2 2023, inside the budget trailer). No restoration bill has been filed since.",
        "venue": "House Ways and Means / Senate Ways and Means; the decisive moves were budget-trailer sections.",
        "narrative": (
            "The interest and dividends tax was phased out by the 2021 budget trailer and repealed two years "
            "early by the 2023 trailer - votes taken only on HB2 as a whole. While the tax still existed, "
            "adjustment bills died in both chambers: SB261 (2023) was killed on the Senate floor 13-10, HB192 "
            "(2024) was killed in the House, and HB1492 (2024) went to interim study, as did the "
            "faster-repeal bill HB100. Since the repeal took effect, the certified 2025-2026 record contains "
            "no bill to restore the tax; the proposal has no legislative vehicle and no sponsor on record."),
        "claims": [
            {"bill_key": "2023:SB261", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Inexpedient", "yeas": 13, "nays": 10}},
            {"bill_key": "2024:HB192", "disposition": "killed"},
            {"bill_key": "2024:HB1492", "disposition": "interim_study"},
            {"bill_key": "2024:HB100", "disposition": "interim_study"},
        ],
    },
    {
        "id": "diversify-tax-base",
        "proposal": "Diversify the tax base / add new revenue sources",
        "tried": "Yes, repeatedly - and killed every time; the one new revenue source that passed is gambling machines inside the 2025 budget trailer.",
        "where_it_died": "The House floor, overwhelmingly; even study bills die there.",
        "venue": "House Ways and Means; budget trailers for what actually passes.",
        "narrative": (
            "New-tax bills lose big: the electronics tax to fund education (HB1492 2020) was killed 320-11, "
            "the e-cigarette tax (HB1699 2020) passed one House vote 172-142 and died on the table, marijuana "
            "taxation went to interim study (HB722 2020), hemp taxation likewise (SB485 2026), and the vacancy "
            "tax (HB1707 2026) died. Even studying revenue options was killed on the floor in 2026 - HB1636 "
            "(a DRA revenue-options study) 284-76 and HB491 (alternative education funding) 195-157. The "
            "constitutional bans meant to lock the door also failed: the income-tax ban (CACR1 2021) drew a "
            "202-171 majority but fell short of three-fifths, the sales-tax ban (CACR2 2021) fell the same "
            "way at 201-170, CACR15 (2024, two-thirds for new taxes) failed 183-185, and the 2026 tax-law-adoption "
            "amendments repeated the pattern (CACR10 at 194-158; CACR12 at 193-148 after passing the Senate "
            "16-8). Both tobacco-tax raises also died (HB290 2025; HB1596 2026, killed 200-157). What actually "
            "diversified revenue was gambling: video lottery terminals arrived inside HB2 2025 (31 percent "
            "state take), while online-gambling bills (SB104 2023; SB168 2025) died in the Senate."),
        "claims": [
            {"bill_key": "2020:HB1492", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 320, "nays": 11}},
            {"bill_key": "2020:HB1699", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 172, "nays": 142}},
            {"bill_key": "2020:HB722", "disposition": "interim_study"},
            {"bill_key": "2026:SB485", "disposition": "interim_study"},
            {"bill_key": "2026:HB1707", "disposition": "killed"},
            {"bill_key": "2026:HB1636", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 284, "nays": 76}},
            {"bill_key": "2026:HB491", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 195, "nays": 157}},
            {"bill_key": "2021:CACR1", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 202, "nays": 171}},
            {"bill_key": "2021:CACR2", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 201, "nays": 170}},
            {"bill_key": "2024:CACR15", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 183, "nays": 185}},
            {"bill_key": "2023:SB104", "disposition": "killed"},
            {"bill_key": "2025:SB168", "disposition": "killed"},
            {"bill_key": "2025:HB290", "disposition": "killed"},
            {"bill_key": "2026:HB1596", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 200, "nays": 157}},
            {"bill_key": "2026:CACR10", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 194, "nays": 158}},
            {"bill_key": "2026:CACR12", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 193, "nays": 148}},
        ],
    },
    {
        "id": "restore-business-taxes",
        "proposal": "Stop cutting / restore state business taxes (BET, BPT, rooms & meals)",
        "tried": "Yes, every session - and killed every time, while the cuts kept passing through budget trailers.",
        "where_it_died": "The House floor (Ways and Means recommendations).",
        "venue": "House Ways and Means; the rate changes themselves ride HB2.",
        "narrative": (
            "Every rate cut of this period passed inside a budget trailer or a leadership bill: HB2 2021 cut "
            "the BPT to 7.6, the BET to 0.55, and the meals and rooms tax to 8.5 percent; HB1221 (2022) cut "
            "the BPT again to 7.5 while paying towns a one-time 7.5 percent of their retirement contributions "
            "- it passed the House 177-141. Every restoration bill died: HB623 (2020), HB10 (2021-22), the "
            "omnibus rate bill HB1422 (2024, interim study), and the 2025 bills to raise the education trust "
            "fund's business-tax share (HB255, HB318) - months before HB2 2025 cut that share from 41 to 39 "
            "percent. The surtax on large low-wage employers (HB1478 2022) was crushed 304-40, and the meals "
            "and rooms rate-raise (HB1480 2026) died too. The full-repeal counterattack also failed: HB1546 "
            "and HB1629 (2026) were both killed. The communications services tax repeal has been filed four "
            "times and sits in interim study each time."),
        "claims": [
            {"bill_key": "2022:HB1221", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 177, "nays": 141}},
            {"bill_key": "2020:HB623", "disposition": "killed"},
            {"bill_key": "2022:HB10", "disposition": "killed"},
            {"bill_key": "2024:HB1422", "disposition": "interim_study"},
            {"bill_key": "2025:HB255", "disposition": "killed"},
            {"bill_key": "2025:HB318", "disposition": "killed"},
            {"bill_key": "2022:HB1478", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 304, "nays": 40}},
            {"bill_key": "2026:HB1480", "disposition": "killed"},
            {"bill_key": "2026:HB1546", "disposition": "killed"},
            {"bill_key": "2026:HB1629", "disposition": "killed"},
            {"bill_key": "2026:HB417", "disposition": "interim_study"},
        ],
    },
    {
        "id": "homestead-exemption",
        "proposal": "Homestead exemption (tax primary homes less; second homes more)",
        "tried": "Yes - the enabling bill has been filed three times and has never reached a floor win; the second-home side reached the floor once and was tabled.",
        "where_it_died": "House Municipal and County Government committee recommendations, then the floor or interim study.",
        "venue": "House Municipal and County Government.",
        "narrative": (
            "The direct proposal - letting towns tax an owner-occupied home on less than its full value - has "
            "been filed three times: HB1387 (2022) was killed on the House floor, HB1034 (2024) went to "
            "interim study, and HB1648 (2026, 'exemptions for qualifying residences') went to interim study "
            "again. The mirror image (taxing non-primary residences more) fared worse: HB1580 (2026) was "
            "killed 284-55, and the luxury second-home assessment (HB1786 2026) was tabled 189-158 with the "
            "rescue motion failing 100-235. The older split-rate idea (HB1365 2022, different rates for "
            "residential and non-residential property; HB1467 2020) also died. What did pass sits next door: "
            "SB83 (2025) created a state fund reimbursing towns for the elderly, disabled, blind, and deaf "
            "exemptions - state-financed relief for specific groups rather than a general homestead split."),
        "claims": [
            {"bill_key": "2022:HB1387", "disposition": "killed"},
            {"bill_key": "2024:HB1034", "disposition": "interim_study"},
            {"bill_key": "2026:HB1648", "disposition": "interim_study"},
            {"bill_key": "2026:HB1580", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 284, "nays": 55}},
            {"bill_key": "2026:HB1786", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Table", "yeas": 189, "nays": 158}},
            {"bill_key": "2022:HB1365", "disposition": "killed"},
            {"bill_key": "2020:HB1467", "disposition": "killed"},
            {"bill_key": "2026:HB1417", "disposition": "killed"},
            {"bill_key": "2026:HB1380", "disposition": "killed"},
            {"bill_key": "2025:SB83", "disposition": "enacted"},
        ],
    },
    {
        "id": "regionalization-consolidation",
        "proposal": "Increase regionalization / consolidate services",
        "tried": "Consolidation mandates for school administrative units, yes - both failed; consolidation INCENTIVES, never. Most of the active legislation runs the other way, easing exits from cooperative districts.",
        "where_it_died": "The mandates died in House Education (HB765 2025, after a unanimous 18-0 ITL committee report; HB1804 2026, interim study); the incentives version was never filed (certified against the full 2020-2024 universe and the 2025-2026 database).",
        "venue": "House Education (cooperative school district and school administrative unit statutes).",
        "narrative": (
            "The certified record contains no bill offering state incentives for towns or districts to "
            "consolidate services. Mandatory consolidation was tried at the school-administrative-unit level "
            "and failed: HB765 (2025) drew a unanimous Inexpedient to Legislate committee report and died on a "
            "voice vote, its refile HB1804 (2026) sits in interim study, and the school-building consolidation "
            "planning bill (HB1818 2026) died on the Senate table. The cooperative-district legislation that "
            "moves is about separation and "
            "control: withdrawal procedures passed in 2023 (HB530) and again in 2026 (HB1374, House 179-161 "
            "on the conference report); Derry absorbed its cooperative school district by charter amendment "
            "(HB1331 2026, House 193-157); unilateral withdrawal went to interim study (HB1644 2026); and "
            "dissolution-of-cooperatives went to interim study in 2022 (HB1679). The one clearly pro-"
            "cooperation law is HB152 (2021), which rewrote how cooperative districts apportion costs among "
            "member towns - a fairness fix, not an incentive."),
        "claims": [
            {"bill_key": "2021:HB152", "disposition": "enacted"},
            {"bill_key": "2023:HB530", "disposition": "enacted"},
            {"bill_key": "2026:HB1374", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "CofC", "yeas": 179, "nays": 161}},
            {"bill_key": "2026:HB1331", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 193, "nays": 157}},
            {"bill_key": "2026:HB1644", "disposition": "interim_study"},
            {"bill_key": "2022:HB1679", "disposition": "interim_study"},
            {"bill_key": "2025:HB765", "disposition": "killed"},
            {"bill_key": "2026:HB1804", "disposition": "interim_study"},
            {"bill_key": "2026:HB1818", "disposition": "killed"},
        ],
    },
    {
        "id": "legislator-communication",
        "proposal": "Improve communication and public education by legislators",
        "tried": "Yes, in the tax-transparency form - and the 2025-2026 biennium finally produced laws.",
        "where_it_died": "Both chambers' floors, until 2025.",
        "venue": "House and Senate Municipal and County Government; Ways and Means for tax-bill content.",
        "narrative": (
            "Bills making tax information easier for residents to see kept dying: more information on "
            "property tax bills (SB252 2022, killed on the Senate floor 13-10), rebate-program notices on tax "
            "bills (HB99 2023), tax-change breakdowns mailed with bills (HB495 2025), revaluation notice "
            "(SB225 2025), public notice of historic tax rates and project tax impacts (SB217 2025), "
            "relief-program awareness (HB782 2025), and the education-funding transparency data system (SB583 "
            "2026, tabled); HB284 (2025) - tax impact statements on warrant articles - passed the House "
            "198-160 and was killed on the Senate floor. Its twin broke through the same year: HB138 (2025) "
            "put multi-year tax-impact notation on warrant articles into law (Chapter 144), HB1807 (2026) "
            "extended it - tax rate and tax impact information on warrant articles, House 185-150, Chapter "
            "312 - and SB600 now requires quarterly public reports on the general and education trust funds "
            "(Chapter 141). The pie-charts-and-QR-codes tax bill (HB1516 2026) and value-change notice "
            "(HB1581 2026) reached interim study; the municipal funds-received posting bill (SB532 2024) died "
            "between the chambers."),
        "claims": [
            {"bill_key": "2022:SB252", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Inexpedient", "yeas": 13, "nays": 10}},
            {"bill_key": "2023:HB99", "disposition": "killed"},
            {"bill_key": "2025:SB217", "disposition": "killed"},
            {"bill_key": "2025:HB782", "disposition": "killed"},
            {"bill_key": "2026:SB583", "disposition": "killed"},
            {"bill_key": "2026:HB1807", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 185, "nays": 150}},
            {"bill_key": "2026:SB600", "disposition": "enacted"},
            {"bill_key": "2026:HB1516", "disposition": "interim_study"},
            {"bill_key": "2024:SB532", "disposition": "killed"},
            {"bill_key": "2025:HB138", "disposition": "enacted"},
            {"bill_key": "2025:HB284", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 198, "nays": 160}},
            {"bill_key": "2025:HB495", "disposition": "killed"},
            {"bill_key": "2025:SB225", "disposition": "killed"},
            {"bill_key": "2026:HB1581", "disposition": "interim_study"},
        ],
    },
    {
        "id": "swept-education-funding",
        "proposal": "(Record thread) The statewide education property tax and school funding",
        "tried": "Structurally, every session; nothing structural has passed as a standalone bill.",
        "where_it_died": "The House floor, whichever direction the bill pushed.",
        "venue": "House Education Funding; budget trailers for what passes; the ConVal litigation in the background.",
        "narrative": (
            "Every structural SWEPT bill died: repeal (HB649 2023), replacement with a local revenue "
            "contribution (HB527 2025), a single equalized statewide rate (HB669 2025), raising SWEPT and "
            "remitting the excess (HB675 2025 - it passed one House vote 190-185 before being killed in "
            "January 2026), excess-remittance alone (HB1686 2024, tabled; HB137 2025), and the donor-town "
            "negative-rate fix (HB1385 2026). What passed rode trailers and a few aid bills: extraordinary "
            "need grants (SB420 2022), the $4,100 base and bigger differentiated aid (HB2 2023), fiscal "
            "capacity disparity aid (HB2 2025) - while the same 2025 trailer delayed the adequacy inflation "
            "adjustment and swept education trust fund surpluses over $20 million to the general fund. Both "
            "chambers also entertained declarations against the Claremont mandates (HCR3 2021, HCR11 2026, "
            "both died; HB2 2025 carried a softer declaration as section 141:389)."),
        "claims": [
            {"bill_key": "2023:HB649", "disposition": "killed"},
            {"bill_key": "2025:HB527", "disposition": "killed"},
            {"bill_key": "2025:HB669", "disposition": "killed"},
            {"bill_key": "2025:HB675", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 190, "nays": 185}},
            {"bill_key": "2024:HB1686", "disposition": "killed"},
            {"bill_key": "2025:HB137", "disposition": "killed"},
            {"bill_key": "2026:HB1385", "disposition": "killed"},
            {"bill_key": "2022:SB420", "disposition": "enacted"},
            {"bill_key": "2021:HCR3", "disposition": "killed"},
            {"bill_key": "2026:HCR11", "disposition": "killed"},
        ],
    },
    {
        "id": "municipal-aid-retirement",
        "proposal": "(Record thread) State aid to towns and the retirement-contribution share",
        "tried": "Every session; one one-time payment passed, the permanent version never has.",
        "where_it_died": "The Senate table and the Senate's end-of-year deadline, after unanimous or near-unanimous Senate support; the House floor in 2026.",
        "venue": "Senate Finance / House Finance.",
        "narrative": (
            "Restoring the state share of local employers' retirement contributions is the most-refiled "
            "municipal-relief idea in the record: HB497 (2020) died, HB1417 (2022) passed the House 186-159 "
            "and the Senate 22-2 before dying at the Senate deadline, SB114 (2023) passed 23-0 and sat on the "
            "table, SB20 (2025) passed 23-0 and died at the deadline, and HB197 (2026) was killed 172-159. "
            "The one enacted version is HB1221 (2022): a one-time payment equal to 7.5 percent of municipal "
            "contributions, attached to a BPT cut. The wider aid picture matches: SB99 (2021, bigger "
            "meals-and-rooms share) passed the Senate 24-0 and died on the table months before HB2 2021 "
            "rewrote the distribution; SB315 (2022, using those distributions to cut tax rates) died at the "
            "deadline; the local-option occupancy fee or room assessment died in every one of its six filings "
            "(2020, 2022, 2023, 2024, 2025, 2026 - the last killed 15-9 on the Senate floor); and revenue sharing "
            "was repealed outright by HB2 2025 after fifteen years of suspensions."),
        "claims": [
            {"bill_key": "2020:HB497", "disposition": "killed"},
            {"bill_key": "2022:HB1417", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 186, "nays": 159}},
            {"bill_key": "2023:SB114", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 23, "nays": 0}},
            {"bill_key": "2025:SB20", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 23, "nays": 0}},
            {"bill_key": "2026:HB197", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 172, "nays": 159}},
            {"bill_key": "2022:HB1221", "disposition": "enacted"},
            {"bill_key": "2021:SB99", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 24, "nays": 0}},
            {"bill_key": "2022:SB315", "disposition": "killed"},
            {"bill_key": "2024:HB1254", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Indefinitely Postpone", "yeas": 195, "nays": 171}},
            {"bill_key": "2025:HB544", "disposition": "killed"},
            {"bill_key": "2026:SB634", "disposition": "killed",
             "vote": {"body": "Senate", "motion_contains": "Inexpedient", "yeas": 15, "nays": 9}},
        ],
    },
]

# ---- recent enactments watchlist ----
watch_keys = [
    ("2025:SB83", "Elderly/disabled/blind/deaf exemption reimbursement fund + video lottery terminals"),
    ("2025:HB138", "Multi-year tax-impact notation on warrant articles"),
    ("2025:SB105", "Town budget caps enabled"),
    ("2025:SB4", "C-PACER commercial property assessment districts"),
    ("2025:HB268", "Board of tax and land appeals hearings"),
    ("2026:SB489", "Board of tax and land appeals appointment process"),
    ("2025:HB696", "Utility property tax and SWEPT treatment of electric generating facilities"),
    ("2025:HB374", "Local tax cap and budget law rewrite"),
    ("2025:HB200", "Local tax cap override procedure"),
    ("2025:HB99", "Disabled veterans property tax waiver"),
    ("2026:HB1300", "School district tax cap ballot questions (2026 and 2028)"),
    ("2026:HB1807", "Tax rate and tax impact information on warrant articles"),
    ("2026:HB1494", "Higher optional veterans', combat service, and surviving spouse credits"),
    ("2026:HB1374", "Cooperative school district withdrawal procedures"),
    ("2026:HB1331", "Derry cooperative school district absorption"),
    ("2026:HB1433", "Business child care tax credit"),
    ("2026:HB1756", "One-time filing for continuing property tax exemptions"),
    ("2026:SB600", "Quarterly general/education trust fund reports"),
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
        "House Ways and Means -> House floor: where every rate restoration, new tax, and revenue study dies (often by lopsided ITL votes).",
        "The Senate table and the Rule 3-23 deadline: where municipal-aid bills with unanimous Senate support quietly end (SB99 2021, SB114 2023, SB20 2025).",
        "The budget trailer: the only vehicle that has actually changed tax rates, education funding formulas, or municipal revenue flows in this period - with votes recorded only on the whole bill.",
        "Three-fifths supermajorities: constitutional tax bans win majorities and still fail (CACR1/CACR2 2021, CACR15 2024).",
    ],
    "veto_watch": [
        "SB63 (2023): private-community property owners' credit - vetoed.",
        "HB242 (2021): adequate education content - vetoed.",
        "HB1102 (2026): R&D credit cap increase - vetoed.",
        "HB1565 (2026): school building aid project-manager rider - vetoed.",
    ],
}

rm = {
    "issue": "new-hampshire-02-property-taxes",
    "generated_by": "reality-mapper v2.2 (NH property-taxes run)",
    "sessions": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "coverage_caveat": (
        "Discovery is certified against the complete OpenStates bulk universe for 2020-2024 (5,467 bills; "
        "every title swept with a wide-net tax/revenue vocabulary and every candidate human-reviewed - see "
        "certification-report.json) and against the official state database for 2025-2026 (the identical wide net swept all 2,234 current-biennium titles; see certification-current.json). Biennium-spanning "
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
md = ["# Reality map — Property Taxes and Revenue Needs in New Hampshire", ""]
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
