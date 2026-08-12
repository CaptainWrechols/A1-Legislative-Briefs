#!/usr/bin/env python3
"""Assemble reality-map.json + .md for the NH energy issue.

One reality card per constituent proposal (plus two threads the record itself
makes unavoidable: the Department of Energy reorganization / who-regulates
question and the nuclear-and-utility-owned-generation pivot). Counts (session
snapshot, theme scorecards) are computed directly from evidence-pack.json so
the programmatic fact-check passes by construction; the notes and card prose
are the human judgment layer, with every specific claim carried as a
structured, checkable claim object.

Run from repo root:
  python3 working/new-hampshire/energy/build-reality-map.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path("working/new-hampshire/energy")
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
    "Electric rates, bills, and ratepayer costs": (
        "rarely_moved", "high",
        "The proposal territory that moves least: 24 policy bills, 4 laws - and the rate-DESIGN bills all "
        "died. The record's main package, HB674 (2025: non-wire alternatives, time-of-use tariffs, "
        "multi-year rate settings), died on the House table; the condominium rate bills died four times "
        "(HB1430 2024; HB537, HB539 2025; HB1432 2026); the default-service reform bills died (HB159 "
        "2023-24; HB760 2025; HB1534 2026) until HB1733 (2026) reformed default-service reconciliation; "
        "and both transparency bills (HB1724, HB1745, 2026) died in committee. What passed is narrow: "
        "purchased-power agreements for default service (SB54 2023), the reconciliation law, the "
        "residential ratepayers advisory board (HB610 2026), and storm-cost securitization bonds (HB1539 "
        "2026). SB597 (2026), tying rate increases to inflation thresholds with performance metrics, sits "
        "in interim study."),
    "Net metering, community power, and local generation": (
        "often_moved", "high",
        "The record's biggest theme (62 policy bills, 19 laws) and its clearest success story - but the "
        "expansion celing held for years. Community power passed in steps: municipal hosts serving "
        "political subdivisions (HB315 2021), county aggregation (SB265 2022), plan approvals (HB385 "
        "2023), the municipal/county rewrite (HB1600 2024), plan refinements (SB590 2026), and "
        "inadvertent-enrollment protection (HB1742 2026). Low-income community solar carved its niche "
        "(SB270 2022; SB161 2023). The capacity-cap fights mostly lost: the 5-megawatt bills were vetoed "
        "in 2020 (SB159, override failing 207-130; HB466, 199-139) and 2023 (SB79, House 194-179 before "
        "the veto), and the 2025-2026 expansion bills died (SB228, killed 190-151; SB449, killed 181-158; "
        "SB106, postponed 172-152) - but the biennium still delivered storage-with-net-metering (HB1718), "
        "municipal terms (SB538), and plug-in solar systems (SB540), all 2026 laws."),
    "Renewable generation and the RPS: solar, wind, hydro, biomass": (
        "mixed", "high",
        "55 policy bills, 13 laws, and a reversal of direction inside the period. 2020's expansion bills "
        "were vetoed (SB124's RPS raise, 214-141 in the House before the veto); 2021-2022 passed the "
        "omnibus SB91, REC reforms (HB309), Burgess BioPower relief (SB271), and the offshore-wind "
        "machinery (SB268 power-purchase approvals; SB440's industry office). Then the turn: the Burgess "
        "rescue was vetoed in 2023 (HB142, override failing 194-159), the RPS phase-out bills reached "
        "interim study (HB509 2024; HB219 2026, after a 175-152 House win), the House adopted HCR4 "
        "rejecting all offshore wind in the Gulf of Maine (195-149), HB575's outright prohibition died "
        "only on the table, the offshore wind office became the 'office of energy innovation' (HB1465 "
        "2024; HB682 2025, House 206-163), and the 2025 trailer swept the renewable energy fund. The "
        "2026 laws are housekeeping (HB1535's class clarifications; SB599's fund amendments)."),
    "Utility regulation and governance: the PUC, the Department of Energy, and restructuring": (
        "often_moved", "high",
        "The best-passing theme (14 of 34 policy bills became law) - because the majority kept building "
        "its own machine. The Department of Energy was created inside the 2021 trailer (91:187), then "
        "implemented and adjusted by standalone laws nearly every year (HB1258 2022; HB219 2023; SB388 "
        "2024; SB108 2025; HB266 2026). Energy-policy statutes were rewritten twice (HB1623 2024, House "
        "184-168; HB504 2025, 204-165), the 10-year strategy updated (HB189 2025, 206-148), and HB690 "
        "(2025, House 200-155) ordered the state to study leaving ISO-New England. Accountability bills "
        "died: electing PUC commissioners (CACR30 2026), Eversource market-share limits (HB633 2023), "
        "retail-charge transparency (HB1724 2026), cost-allocation reform (HB1745 2026), performance "
        "incentives (SB499 2020; SB320 2024, interim study), and the PUC-role definition (HB535 2025). "
        "The exceptions: the residential ratepayers advisory board (HB610 2026) and off-grid providers "
        "(HB672 2025, House 185-151)."),
    "Grid infrastructure: transmission, storage, microgrids, reliability, and data": (
        "mixed", "high",
        "43 policy bills, 14 laws - planning and studies pass, hard investment rules die. Grid "
        "modernization got its law (SB166 2023) and advisory group (SB233 2025); integrated distribution "
        "planning passed (HB1431 2024) after four years of tries; microgrids got their study (HB558 "
        "2024) and then port electrification and microgrid development (SB589 2026); storm-cost "
        "securitization passed (HB1539 2026); and HB1723 (2026) ordered transformer-vulnerability "
        "assessments. Storage passed early as a framework (HB715 2020; HB289 2021 for siting) and "
        "stalled late as policy (SB540 2024, interim; HB761 2025 and HB1290 2026, dead). The energy "
        "data platform - the infrastructure behind smart rates - was built in statute (2021 trailer; "
        "HB1285 2022), never launched, and repealed (HB723, Chapter 28 of 2026) after the replacement "
        "bills died (SB165 2023-24; HB681 2025). Transmission-scale bills died at the Senate deadline "
        "(SB307 2024) and on the table (SB386 2024)."),
    "Energy efficiency, weatherization, and fuel assistance": (
        "unfinished", "high",
        "The NHSaves proposal's home theme: 41 policy bills, 9 laws, and a decade-defining 2021-2022 "
        "fight. After the PUC's late-2021 order slashed the utilities' three-year efficiency plan, "
        "HB549 (2022) rebuilt the system benefits charge by formula and passed the House 343-0 - "
        "settling the crisis by capping the growth path; SB113 (2023) then required legislative "
        "approval for future SBC increases. The efficiency-fund raids failed (SB122 was vetoed in 2020, "
        "212-140 in the House before the veto; HB1621 2022 and HB418 2023 died), but so did every "
        "weatherization expansion: the study committees died or stalled (SB269 2022, interim study "
        "182-152; HB1230 2024; HB599 2025), the consumption-reduction goals died (HB1261 2020 through "
        "HB175 2024), and the efficiency-authority bill sits in interim study (HB1748 2026). What "
        "passed: emergency fuel assistance in the 2022 price spike (HB2023, Senate 23-0 on the "
        "remainder), the Electric Assistance Program transfer (SB236 2025), C-PACER financing (SB4 "
        "2025, Senate 23-0; municipal districts SB440 2026), and state performance contracting (SB96 "
        "2023). The building-code half died: the 2021 energy code (HB96 2025, tabled 199-135) and the "
        "2024 IECC update (HB1180 2026)."),
    "Fuels: natural gas, propane, and heating oil": (
        "often_moved", "medium",
        "The smallest big theme (14 policy bills) with the highest pass rate (7 laws) - consumer "
        "protection passes, market restructuring never appears. Home heating oil and propane contract "
        "protections passed (HB1262 2026) after the 2024 versions stalled (HB1395, interim study; "
        "HB1491, killed); underground heating-oil tank removal passed (HB1620 2026); pipeline safety "
        "passed (HB1491 2022); the oil discharge cleanup fund was raised (HB658 2025); and the "
        "gas-ban-preemption report law (HB1148 2022) answered the fuel-restriction question. The "
        "study bills died: propane ancillary charges (HB81 2023), the Jones Act's effect on heating "
        "fuel (SB102 2023), and green hydrogen (SB167 2023)."),
    "Nuclear power": (
        "unfinished", "high",
        "A pivot theme: 10 policy bills, 2 laws, and momentum arriving late. The 2020 decommissioning "
        "and waste bills died on the table; HB543 (2022) created the nuclear study commission; HB1465 "
        "(2024) ordered nuclear-technology studies while renaming the offshore wind office the office "
        "of energy innovation; HCR2 (2025) declared advanced nuclear in the state's interest. Then the "
        "utility-ownership fight: letting electric utilities own advanced nuclear died between the "
        "chambers (HB710 2025), died in the Senate (SB447 2026), and was VETOED as HB221 (2026, no "
        "override recorded as of collection) - while HB1775 (2026, House 198-153), covering utility "
        "ownership of natural gas and nuclear generation, became law alongside SB591's broader "
        "utility-owned-generation authority."),
    "Electric vehicles and charging infrastructure": (
        "rarely_moved", "medium",
        "29 policy bills, 5 laws - and the money bills all died. The regulatory frame passed: charging-"
        "station regulation (SB52 2023, surviving a 183-188 tabling attempt), the renters' charging "
        "study (HB111 2023, surviving reconsideration 170-177), the EV/battery council (SB430 2024), "
        "and the weight-based EV registration fee schedule (HB1594 2026), which replaced the 2023 "
        "trailer's flat surcharge approach. Everything with an appropriation died: the EV and "
        "infrastructure fund (SB447 2022), charging-station funding (SB272 2025, killed 195-163), "
        "state-building charging (HB606 2023-24, interim study), curbside charging (SB628 2026, "
        "interim study), and every road-toll-alternative study (HB1464, SB191 2024)."),
    "Climate, emissions, and RGGI": (
        "rarely_moved", "high",
        "The one-way theme: 36 policy bills, 5 laws, and every affirmative climate bill dead. The "
        "climate action plan / greenhouse-gas goals bills died in 2020, 2021, 2022 (tabled), and 2023 "
        "(killed on the floor); carbon pricing died four ways (HB735 2020; the study commissions 2021-"
        "2025; proxy pricing HB1486 2024 and HB278 2025); the RGGI expansion (HB1496 2020) passed the "
        "House 180-101 and died on the Senate table, while the RGGI-repeal-direction bills also died "
        "(HB524 2023, failing 181-186) - until HB1738 (2026) redirected RGGI ratepayer benefits as "
        "law. The House adopted HR17 (2022, 178-159) opposing all carbon taxes and HCR1 (2025). What "
        "passed otherwise is defensive or peripheral: the forest carbon credit rules (HB1697 2024), "
        "the sequestration moratorium (HB123 2025), and the state-lands sequestration ban (HB1205 "
        "2026)."),
    "Energy taxation and host-community revenue": (
        "unfinished", "medium",
        "The overlap theme with the property-taxes packet, included here from the energy angle: 14 "
        "policy bills, 5 laws. The assessing-power-generation study commissions passed three times "
        "(HB410 2022; SB225 2023; HB458 2024) before HB696 (2025) standardized utility property taxes "
        "and SWEPT on electric generating facilities as law - its Senate twin (SB277) died at the "
        "Senate deadline the same year. The renewable-exemption bills mostly died (HB1210 2020 storage; "
        "HB1406 2020 and SB424/SB530 2020 solar; HB1002 2026 repeal attempt, dead on the table), while "
        "the PILT option for renewable generation passed (HB64 2021) and SB584 (2024, interim study) "
        "carried the utility-tax-on-renewables question."),
    "Energy facility siting and decommissioning": (
        "often_moved", "medium",
        "13 policy bills, 6 laws - the Site Evaluation Committee was remade inside the period. The 2021 "
        "trailer shrank it and attached it to the new department (91:227) and created the revision "
        "study (91:228); SB256 (2022) studied replacing it outright; SB429 (2022) amended its "
        "procedures; storage joined the 'energy facility' definition (HB289 2021); HB609 (2024) "
        "rewrote the siting process and SB451 (2024) added an expedited track. What died: the "
        "SEC-rules bills (HB1611 2022; HB176 2023-24), gas-facility decommissioning-cost requirements "
        "(HB1229 2020), and the fee cut (SB626 2020; HB624 2021-22, dead between the chambers with "
        "its hydro rider)."),
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
        "id": "expand-renewable-energy",
        "proposal": "Prioritize / expand renewable energy (solar, wind, geothermal, diversified sources)",
        "tried": "Yes, every session - and the direction reversed mid-period: 2019-2020's expansions were vetoed, 2021-2022 built machinery, 2023-2026 turned against offshore wind and the RPS while nuclear rose.",
        "where_it_died": "The Governor's desk in 2020; the House floor and table for the RPS and offshore wind after 2023; the 2025 budget trailer took the renewable energy fund.",
        "venue": "House Science, Technology and Energy; Senate Energy and Natural Resources; the budget trailers.",
        "narrative": (
            "The record splits into two eras. In 2020 the expansion agenda passed both chambers and died at "
            "the Governor's desk: the RPS raise (SB124) passed the House 214-141 and was vetoed; the "
            "net-metering expansions (SB159, HB466) were vetoed with overrides failing 207-130 and 199-139. "
            "2021-2022 built infrastructure on bipartisan terms: the omnibus renewable/utilities law (SB91), "
            "REC computation reform (HB309), Gulf of Maine offshore-wind power-purchase approvals (SB268), "
            "the offshore wind industry office (SB440), and Burgess BioPower relief (SB271). From 2023 the "
            "direction reversed: the second Burgess rescue passed the House 269-109 and was vetoed (override "
            "failing 194-159); the RPS phase-out reached interim study twice (HB509 2024; HB219 2026, after "
            "a 175-152 House vote); the House adopted HCR4 (195-149) rejecting ALL offshore wind off New "
            "Hampshire; HB575's outright prohibition died only on the table; HB1465 (2024) and HB682 (2025, "
            "House 206-163) renamed the offshore-wind machinery into an all-of-the-above 'office of energy "
            "innovation'; and the 2025 trailer swept the renewable energy fund into the general fund "
            "(141:140-142) while the rebate-to-ratepayers alternative (HB224) sat in interim study. "
            "Geothermal has never had a New Hampshire bill in either universe - the diversification the "
            "record actually pursued is nuclear (see the nuclear thread). The 2026 laws are maintenance: "
            "RPS class clarifications (HB1535) and renewable-energy-fund amendments (SB599)."),
        "claims": [
            {"bill_key": "2020:SB124", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 214, "nays": 141}},
            {"bill_key": "2020:SB159", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "Veto Override", "yeas": 207, "nays": 130}},
            {"bill_key": "2020:HB466", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "Veto Override", "yeas": 199, "nays": 139}},
            {"bill_key": "2021:SB91", "disposition": "enacted"},
            {"bill_key": "2021:HB309", "disposition": "enacted"},
            {"bill_key": "2022:SB268", "disposition": "enacted"},
            {"bill_key": "2022:SB440", "disposition": "enacted"},
            {"bill_key": "2022:SB271", "disposition": "enacted"},
            {"bill_key": "2023:HB142", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "Veto Override", "yeas": 194, "nays": 159}},
            {"bill_key": "2024:HB509", "disposition": "interim_study"},
            {"bill_key": "2026:HB219", "disposition": "interim_study",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 175, "nays": 152}},
            {"bill_key": "2025:HCR4", "disposition": "passed",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 195, "nays": 149}},
            {"bill_key": "2025:HB575", "disposition": "killed"},
            {"bill_key": "2024:HB1465", "disposition": "enacted"},
            {"bill_key": "2025:HB682", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 206, "nays": 163}},
            {"bill_key": "2026:HB224", "disposition": "interim_study"},
            {"bill_key": "2026:HB1535", "disposition": "enacted"},
            {"bill_key": "2026:SB599", "disposition": "enacted"},
        ],
    },
    {
        "id": "fund-nh-saves-weatherization",
        "proposal": "Fund / strengthen NH Saves weatherization & efficiency programs (including on-bill financing)",
        "tried": "The funding mechanism was fought over all period - and the outcome CAPPED it: after regulators cut the 2021 efficiency plan, the legislature locked the system benefits charge to a formula and required legislative approval for increases.",
        "where_it_died": "Expansion died in study committees and on the table; the cap passed the House 343-0; the raid bills died too.",
        "venue": "House Science, Technology and Energy; Senate Energy and Natural Resources; the PUC's 2021 efficiency order in the background.",
        "narrative": (
            "The NHSaves programs are funded by the system benefits charge (SBC) on electric bills, and the "
            "record is the fight over that charge. The 2020 expansion attempt (SB122, redirecting efficiency-"
            "fund money) passed the House 212-140 and was vetoed. After the PUC's late-2021 order slashed "
            "the utilities' three-year efficiency plan, HB549 (2022) rebuilt the SBC on a statutory formula "
            "and passed the House 343-0 - restoring the programs but capping their growth - and SB113 (2023) "
            "required legislative approval for any future increase; HB211 (2023) added an effectiveness "
            "report. The raids failed (HB1621 2022; HB418 2023), but so did every expansion: weatherization "
            "study committees stalled (SB269 2022, interim study after a 182-152 vote; HB1230 2024 and HB599 "
            "2025, dead), the energy-consumption-reduction goals died in four sessions (HB1261 2020 through "
            "HB175 2024), ratepayer-funded project financing died (HB1317 2020), and the efficiency-and-"
            "resource-development authority sits in interim study (HB1748 2026). On-bill financing has never "
            "had a standalone New Hampshire bill; the closest instruments that PASSED are property-based: "
            "C-PACER financing (SB4 2025, Senate 23-0), municipal clean-energy districts (SB440 2026, after "
            "HB342 died on a 154-195 concurrence), and state performance contracting (SB96 2023). The "
            "assistance side did move: emergency fuel assistance in the 2022 price spike (HB2023, Senate "
            "23-0 on the remainder), the Electric Assistance Program's transfer to the department (SB236 "
            "2025), and the 2023 trailer's benefits-cliff fuel-assistance study (79:581). The building-code "
            "half died: the 2021 energy code (HB96 2025, tabled 199-135) and the IECC 2024 update (HB1180 "
            "2026)."),
        "claims": [
            {"bill_key": "2020:SB122", "disposition": "vetoed",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 212, "nays": 140}},
            {"bill_key": "2022:HB549", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 343, "nays": 0}},
            {"bill_key": "2023:SB113", "disposition": "enacted"},
            {"bill_key": "2023:HB211", "disposition": "enacted"},
            {"bill_key": "2022:HB1621", "disposition": "killed"},
            {"bill_key": "2023:HB418", "disposition": "killed"},
            {"bill_key": "2022:SB269", "disposition": "interim_study",
             "vote": {"body": "House", "motion_contains": "Interim Study", "yeas": 182, "nays": 152}},
            {"bill_key": "2024:HB1230", "disposition": "killed"},
            {"bill_key": "2025:HB599", "disposition": "killed"},
            {"bill_key": "2020:HB1317", "disposition": "killed"},
            {"bill_key": "2026:HB1748", "disposition": "interim_study"},
            {"bill_key": "2025:SB4", "disposition": "enacted",
             "vote": {"body": "Senate", "motion_contains": "Ought to Pass", "yeas": 23, "nays": 0}},
            {"bill_key": "2026:SB440", "disposition": "enacted"},
            {"bill_key": "2025:HB342", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Concur", "yeas": 154, "nays": 195}},
            {"bill_key": "2023:SB96", "disposition": "enacted"},
            {"bill_key": "2022:HB2023", "disposition": "enacted",
             "vote": {"body": "Senate", "motion_contains": "Remainder", "yeas": 23, "nays": 0}},
            {"bill_key": "2025:SB236", "disposition": "enacted"},
            {"bill_key": "2025:HB96", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Table", "yeas": 199, "nays": 135}},
            {"bill_key": "2026:HB1180", "disposition": "killed"},
        ],
    },
    {
        "id": "eversource-puc-accountability",
        "proposal": "Greater transparency / accountability for Eversource; better regulation of the PUC",
        "tried": "The state rebuilt WHO regulates (the 2021 trailer's Department of Energy) - but nearly every bill aimed at utility or regulator accountability died.",
        "where_it_died": "House committees and the House table; the structural change came through the budget trailer, where votes are on the whole bill.",
        "venue": "House Science, Technology and Energy; the 2021 budget trailer; the PUC itself.",
        "narrative": (
            "The biggest regulatory change of the period was never voted on as a bill: the 2021 budget "
            "trailer created the Department of Energy (91:187), rebuilt the PUC as a smaller full-time "
            "tribunal with a one-year revolving-door ban (91:204, 91:206), kept the Office of the Consumer "
            "Advocate - the ratepayers' lawyer - independent (91:211), and made utilities fund their own "
            "regulation through assessments recovered in rates (91:243-245). The implementation laws passed "
            "steadily (HB1258 2022; HB219 2023; SB388 2024; SB108 2025; HB266 2026). The accountability "
            "bills aimed at Eversource and the regulators mostly died: the Eversource market-share and "
            "rate-increase bill (HB633 2023), electing PUC commissioners (CACR30 2026), retail-charge "
            "transparency (HB1724 2026), ratepayer cost-allocation reform (HB1745 2026), performance "
            "incentives and penalties (SB499 2020; SB320 2024, interim study), the PUC-role definition "
            "(HB535 2025), and the inflation-indexed rate threshold (SB597 2026, interim study). What "
            "passed: the residential ratepayers advisory board (HB610 2026), default-service reconciliation "
            "reform (HB1733 2026), off-grid provider authorization (HB672 2025, House 185-151), and HB690 "
            "(2025, House 200-155), ordering the department to study withdrawing from ISO-New England - "
            "the regional market where wholesale prices are set. The 2023 trailer funded that fight with "
            "the Regional Energy Advocacy Fund (79:123)."),
        "claims": [
            {"bill_key": "2022:HB1258", "disposition": "enacted"},
            {"bill_key": "2023:HB219", "disposition": "enacted"},
            {"bill_key": "2024:SB388", "disposition": "enacted"},
            {"bill_key": "2025:SB108", "disposition": "enacted"},
            {"bill_key": "2026:HB266", "disposition": "enacted"},
            {"bill_key": "2023:HB633", "disposition": "killed"},
            {"bill_key": "2026:CACR30", "disposition": "killed"},
            {"bill_key": "2026:HB1724", "disposition": "killed"},
            {"bill_key": "2026:HB1745", "disposition": "killed"},
            {"bill_key": "2020:SB499", "disposition": "killed"},
            {"bill_key": "2024:SB320", "disposition": "interim_study"},
            {"bill_key": "2025:HB535", "disposition": "killed"},
            {"bill_key": "2026:SB597", "disposition": "interim_study"},
            {"bill_key": "2026:HB610", "disposition": "enacted"},
            {"bill_key": "2026:HB1733", "disposition": "enacted"},
            {"bill_key": "2025:HB672", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "Concur", "yeas": 185, "nays": 151}},
            {"bill_key": "2025:HB690", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 200, "nays": 155}},
        ],
    },
    {
        "id": "local-renewables-grid-infrastructure",
        "proposal": "Incentivize renewables for cities, towns, and individuals and strengthen supporting grid infrastructure",
        "tried": "The municipal half is the record's biggest success - community power and municipal net metering passed in steps all period. The transmission half is studies and planning laws; the investment bills die.",
        "where_it_died": "Individual/large-generator expansions at the Governor's desk (2020, 2023) and on the House floor (2025-2026); transmission-scale bills at the Senate deadline and on the table.",
        "venue": "House Science, Technology and Energy; Senate Energy and Natural Resources.",
        "narrative": (
            "For cities and towns, this proposal largely happened: municipal hosts serving political "
            "subdivisions (HB315 2021), county aggregation (SB265 2022), streamlined plan approvals (HB385 "
            "2023), the municipal/county aggregation rewrite (HB1600 2024), plan refinements (SB590 2026), "
            "customer protection in aggregation (HB1742 2026), municipal net-metering terms (SB538 2026), "
            "and low-income community solar (SB270 2022; SB161 2023) all became law - the machinery behind "
            "the state's fast-growing community power movement. For individuals, the ceiling held longer: "
            "the capacity-cap raises were vetoed in 2020 (SB159; override 207-130) and 2023 (SB79, House "
            "194-179 before the veto), the 2025-2026 expansions died on the floor (SB228 killed 190-151; "
            "SB449 killed 181-158; SB106 postponed 172-152) - but plug-in solar (SB540) and storage-with-"
            "net-metering (HB1718) passed in 2026. The grid half moves as planning, not investment: grid "
            "modernization (SB166 2023) and its advisory group (SB233 2025), integrated distribution "
            "planning (HB1431 2024), the microgrid study (HB558 2024), port electrification and microgrids "
            "(SB589 2026), transformer-vulnerability assessment (HB1723 2026), and storm-cost "
            "securitization (HB1539 2026) all passed; the transmission-scale bills died (SB307 2024, at "
            "the Senate deadline; SB386 2024, on the table; HB1739 2026 for data-center infrastructure), "
            "and the distributed-energy investment bills died with them (SB230, HB460 2025; HB1741 2026)."),
        "claims": [
            {"bill_key": "2021:HB315", "disposition": "enacted"},
            {"bill_key": "2022:SB265", "disposition": "enacted"},
            {"bill_key": "2023:HB385", "disposition": "enacted"},
            {"bill_key": "2024:HB1600", "disposition": "enacted"},
            {"bill_key": "2026:SB590", "disposition": "enacted"},
            {"bill_key": "2026:HB1742", "disposition": "enacted"},
            {"bill_key": "2026:SB538", "disposition": "enacted"},
            {"bill_key": "2022:SB270", "disposition": "enacted"},
            {"bill_key": "2023:SB161", "disposition": "enacted"},
            {"bill_key": "2025:SB228", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 190, "nays": 151}},
            {"bill_key": "2026:SB449", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 181, "nays": 158}},
            {"bill_key": "2026:SB106", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "Indefinitely Postpone", "yeas": 172, "nays": 152}},
            {"bill_key": "2026:SB540", "disposition": "enacted"},
            {"bill_key": "2026:HB1718", "disposition": "enacted"},
            {"bill_key": "2023:SB166", "disposition": "enacted"},
            {"bill_key": "2025:SB233", "disposition": "enacted"},
            {"bill_key": "2024:HB1431", "disposition": "enacted"},
            {"bill_key": "2024:HB558", "disposition": "enacted"},
            {"bill_key": "2026:SB589", "disposition": "enacted"},
            {"bill_key": "2026:HB1723", "disposition": "enacted"},
            {"bill_key": "2026:HB1539", "disposition": "enacted"},
            {"bill_key": "2024:SB307", "disposition": "killed"},
            {"bill_key": "2024:SB386", "disposition": "killed"},
            {"bill_key": "2025:SB230", "disposition": "killed"},
            {"bill_key": "2026:HB1741", "disposition": "killed"},
        ],
    },
    {
        "id": "time-of-use-rates",
        "proposal": "Adopt time-of-use / variable-price electricity rates",
        "tried": "Yes - and the direct vehicle died on the House table in 2025; the enabling infrastructure (smart meters, the energy data platform) has been dying since 2020, and the data platform was repealed outright in 2026.",
        "where_it_died": "The House table (HB674) and House floor (the smart-meter bills); the data platform in a signed repeal law.",
        "venue": "House Science, Technology and Energy; the PUC's rate dockets in the background.",
        "narrative": (
            "The one bill squarely on this proposal - HB674 (2025), requiring non-wire alternatives review, "
            "time-of-use tariffs for customers with advanced meters, and multi-year rate settings - died on "
            "the House table. Its companion (HB692 2025, requiring utilities to adopt advanced meters) died "
            "the same way, which is the deeper problem: time-of-use pricing needs meters and data the state "
            "keeps declining to require. The smart-meter gateway bills were killed twice (HB631 2023-24, the "
            "second time 192-180 on the floor); the smart-meter disclosure bill died (HB1743 2026); and the "
            "multi-use energy data platform - built in statute by the 2021 trailer (91:292) and amended by "
            "HB1285 (2022) to give customers and suppliers usage-data access - was never launched, its "
            "replacement bills died (SB165 2023-24; HB681 2025), and it was repealed outright by HB723 "
            "(Chapter 28 of 2026, after a 201-160 House vote on the carryover record). The rate-structure "
            "studies died too: demand charges (HB382 2021-22), fixed-versus-usage cost allocation (HB1475 "
            "2026), and default-service procurement reform (HB1617 2024, interim study). What passed "
            "instead keeps the CURRENT structure working: purchased-power agreements for default service "
            "(SB54 2023) and default-service reconciliation reform (HB1733 2026). SB597 (2026) - rate "
            "increases tied to inflation thresholds with performance metrics - sits in interim study as "
            "the proposal's nearest live vehicle."),
        "claims": [
            {"bill_key": "2025:HB674", "disposition": "killed"},
            {"bill_key": "2025:HB692", "disposition": "killed"},
            {"bill_key": "2024:HB631", "disposition": "killed",
             "vote": {"body": "House", "motion_contains": "ITL", "yeas": 192, "nays": 180}},
            {"bill_key": "2026:HB1743", "disposition": "killed"},
            {"bill_key": "2022:HB1285", "disposition": "enacted"},
            {"bill_key": "2024:SB165", "disposition": "killed"},
            {"bill_key": "2025:HB681", "disposition": "killed"},
            {"bill_key": "2026:HB723", "disposition": "enacted"},
            {"bill_key": "2022:HB382", "disposition": "killed"},
            {"bill_key": "2026:HB1475", "disposition": "killed"},
            {"bill_key": "2024:HB1617", "disposition": "interim_study"},
            {"bill_key": "2023:SB54", "disposition": "enacted"},
            {"bill_key": "2026:HB1733", "disposition": "enacted"},
            {"bill_key": "2026:SB597", "disposition": "interim_study"},
        ],
    },
    {
        "id": "doe-reorganization-thread",
        "proposal": "(Record thread) The Department of Energy reorganization - who regulates energy",
        "tried": "The defining structural change of the period, made inside the 2021 budget trailer with votes only on the whole bill - then implemented by standalone laws every year since.",
        "where_it_died": "It did not - this is the machinery the majority built; the bills that died were the ones trying to constrain it.",
        "venue": "The 2021 budget trailer; House Science, Technology and Energy for the annual implementation laws.",
        "narrative": (
            "In 2021 New Hampshire moved most energy regulation out of the Public Utilities Commission into "
            "a new cabinet Department of Energy - the biggest restructuring since electric restructuring "
            "itself - entirely inside the budget trailer (91:187-293): the department (91:187), the smaller "
            "full-time PUC with staggered terms and a revolving-door ban (91:204, 91:206), the consumer "
            "advocate's attachment (91:211), utility-funded assessments recovered in rates (91:243-245), "
            "and the transfer of net metering, RPS, RGGI, siting support, and Dig Safe administration. The "
            "trailer passed the Senate 14-10 and the House 198-181 - votes on the whole budget bill, never "
            "on the energy sections. The implementation then ran through standalone laws: HB1258 (2022), "
            "HB219 (2023), SB388 (2024), SB108 (2025), and HB266 (2026), plus the policy restatements "
            "(HB1623 2024, House 184-168; HB504 2025, 204-165) and the 10-year strategy update (HB189 "
            "2025, 206-148). The 2023 trailer added the Regional Energy Advocacy Fund (79:123) and "
            "rewrote the assessment mechanics (79:119-122); the direction now runs through HB690's "
            "ISO-New England withdrawal study (2025, House 200-155)."),
        "claims": [
            {"bill_key": "2022:HB1258", "disposition": "enacted"},
            {"bill_key": "2023:HB219", "disposition": "enacted"},
            {"bill_key": "2024:SB388", "disposition": "enacted"},
            {"bill_key": "2025:SB108", "disposition": "enacted"},
            {"bill_key": "2026:HB266", "disposition": "enacted"},
            {"bill_key": "2024:HB1623", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 184, "nays": 168}},
            {"bill_key": "2025:HB504", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 204, "nays": 165}},
            {"bill_key": "2025:HB189", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTPA", "yeas": 206, "nays": 148}},
            {"bill_key": "2025:HB690", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 200, "nays": 155}},
        ],
    },
    {
        "id": "nuclear-pivot-thread",
        "proposal": "(Record thread) The nuclear pivot and utility-owned generation",
        "tried": "The record's late-arriving direction: studies in 2022-2024, a House declaration in 2025, and the utility-ownership fight ending in one veto and two laws in 2026.",
        "where_it_died": "The advanced-nuclear utility-ownership bills died between the chambers (2025), in the Senate (2026), and at the Governor's desk (HB221, 2026) - while the broader ownership laws passed.",
        "venue": "House Science, Technology and Energy; Senate Energy and Natural Resources; the Governor's desk.",
        "narrative": (
            "Nuclear entered the record as caution - the 2020 decommissioning and waste bills died on the "
            "table - and the House even asked Washington to build a national repository (HR16, 2022, "
            "adopted on the consent calendar). Then it became strategy: HB543 (2022) created the nuclear "
            "study commission; HB1465 (2024) ordered nuclear-technology studies while renaming the "
            "offshore-wind office the office of energy innovation; HCR2 (2025) declared advanced nuclear "
            "in the state's interest. The utility-ownership fight ran three times in one biennium: HB710 "
            "(2025) died between the chambers, SB447 (2026) died in the Senate, and HB221 (2026) passed "
            "both chambers and was vetoed (no override recorded as of collection) - yet the same session "
            "passed HB1775 (House 198-153), addressing utility ownership of natural gas and nuclear "
            "generation facilities, and SB591, allowing utility companies to own or build generation - a "
            "step back from restructuring's divestiture principle that HB1738 (2026) reinforced on the "
            "procurement side. This is the 'diversified sources' the legislature actually chose."),
        "claims": [
            {"bill_key": "2020:HB412", "disposition": "killed"},
            {"bill_key": "2020:HB704", "disposition": "killed"},
            {"bill_key": "2022:HR16", "disposition": "passed"},
            {"bill_key": "2022:HB543", "disposition": "enacted"},
            {"bill_key": "2024:HB1465", "disposition": "enacted"},
            {"bill_key": "2025:HCR2", "disposition": "passed"},
            {"bill_key": "2025:HB710", "disposition": "killed"},
            {"bill_key": "2026:SB447", "disposition": "killed"},
            {"bill_key": "2026:HB221", "disposition": "vetoed"},
            {"bill_key": "2026:HB1775", "disposition": "enacted",
             "vote": {"body": "House", "motion_contains": "OTP", "yeas": 198, "nays": 153}},
            {"bill_key": "2026:SB591", "disposition": "enacted"},
            {"bill_key": "2026:HB1738", "disposition": "enacted"},
        ],
    },
]

# ---- recent enactments watchlist ----
watch_keys = [
    ("2025:HB696", "Utility property tax and SWEPT standardized for electric generating facilities"),
    ("2025:HB690", "ISO-New England withdrawal and regional-strategy investigation"),
    ("2025:HB682", "Offshore wind office reorganized into the office of energy innovation"),
    ("2025:HB672", "Off-grid electricity providers authorized"),
    ("2025:SB236", "Electric Assistance Program transferred to the department of energy"),
    ("2025:SB232", "Net metering terms and conditions clarified"),
    ("2025:SB233", "Grid modernization advisory group restructured"),
    ("2025:SB4", "C-PACER commercial clean-energy financing"),
    ("2026:HB1733", "Default electric service rate reconciliation reform"),
    ("2026:HB1539", "Storm-cost recovery securitization bonds"),
    ("2026:HB610", "Residential ratepayers advisory board"),
    ("2026:HB723", "Multi-use energy data platform repealed"),
    ("2026:HB1775", "Utility ownership of natural gas and nuclear generation"),
    ("2026:SB591", "Utility companies may own or build generation facilities"),
    ("2026:HB1738", "RGGI ratepayer benefits redirected; energy procurement and nuclear options"),
    ("2026:SB538", "Municipal net metering eligibility terms extended"),
    ("2026:SB540", "Plug-in solar generation systems legalized"),
    ("2026:SB589", "Port electrification, microgrids, and energy-system cybersecurity"),
    ("2026:SB590", "Community power aggregation plans refined"),
    ("2026:HB1723", "Transformer vulnerability assessments (geomagnetic/electromagnetic)"),
    ("2026:HB1262", "Home heating oil and propane contract protections"),
    ("2026:HB1594", "Weight-based EV and plug-in-hybrid registration fees"),
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
        "The House table: 87 bills in this record were laid on the table and never taken back up - including the climate action plans, the 2020 net-metering wave, and HB674's time-of-use package.",
        "The Governor's desk: seven energy bills were vetoed and no override succeeded - four in 2020 alone (net metering twice, the RPS raise, the efficiency fund), Burgess BioPower in 2023 (override failing 194-159), and advanced nuclear in 2026 (HB221, no override recorded as of collection).",
        "The budget trailer: the Department of Energy's creation, the PUC restructuring, the EV registration surcharge, and the renewable energy fund sweep were all made inside HB2, with votes only on the whole bill.",
        "The Senate's end-of-year deadline (Rule 3-23): the utility-property-tax Senate bill (SB277, 2025) and the transmission-agreements bill (SB307, 2024) died there.",
    ],
    "veto_watch": [
        "SB159 (2020): net metering limits to 5 MW - vetoed, override failed 207-130.",
        "HB466 (2020): customer-generator capacity - vetoed, override failed 199-139.",
        "SB124 (2020): renewable portfolio standards raise - vetoed, override vote failed in the Senate 14-10.",
        "SB122 (2020): energy efficiency fund expenditures - vetoed, override vote failed in the Senate 14-10.",
        "HB142 (2023): Burgess BioPower operation - vetoed, override failed 194-159.",
        "SB79 (2023): customer-generator net metering participation - vetoed, override abandoned 0-23.",
        "HB221 (2026): utilities owning advanced nuclear resources - vetoed, no override action recorded as of collection.",
    ],
}

rm = {
    "issue": "new-hampshire-04-energy",
    "generated_by": "reality-mapper v2.2 (NH energy run)",
    "sessions": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
    "coverage_caveat": (
        "Discovery is certified against the complete OpenStates bulk universe for 2020-2024 (5,467 bills; "
        "every title swept with a wide-net energy vocabulary and every candidate human-reviewed - see "
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
md = ["# Reality map — Energy Cost, Sourcing, and Reliability in New Hampshire", ""]
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
