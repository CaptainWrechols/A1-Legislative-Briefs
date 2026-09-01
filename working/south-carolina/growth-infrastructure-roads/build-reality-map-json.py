#!/usr/bin/env python3
"""Structured reality-map.json for south-carolina-01-growth-infrastructure-roads.

Companion to the narrative reality-map.md (same findings, machine form).
Reads evidence-pack.json for counts so numbers cannot drift.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
pack = json.load(open(os.path.join(HERE, "evidence-pack.json")))

themes = {t["theme"]: t for t in pack["themes"]}

SCORECARDS = [
    ("Local tools to pay for growth (penny taxes, tolls, local fees)", "mixed", "medium-high",
     "Finance/Ways and Means, no hearings on penny expansions or tolls; the one new tool (124:S152 Green Space penny, Act 166 of 2022) passed with leadership sponsorship; flexibility acts passed at the edges",
     ["124:S152", "126:S979", "125:S674", "123:S172", "126:H4589"]),
    ("Making developers pay (impact fees)", "rarely_moved", "high",
     "Ways and Means/Finance/Judiciary, no hearings in either direction for eight years; the one enacted impact-fee rule (FY 2021-22 proviso 117.96) blocked the fees for schools, one year only",
     ["125:H4659", "126:H5088", "125:H4981", "126:H3165"]),
    ("State road money (gas tax, road fees, infrastructure funds)", "mixed", "medium-high",
     "Ways and Means/Finance, no votes on any gas-fee freeze/repeal/suspension or the county-share increase; collection-tightening passed (124:H3505, Act 70)",
     ["124:H4092", "126:S1045", "126:H5331", "124:H3505"]),
    ("Fixing and maintaining existing roads", "rarely_moved", "high",
     "First committee for every bill; the money moved through budget provisos instead (86.1 yearly; $417.4M FY 2024-25, $200M FY 2025-26, $225M FY 2026-27; Road Buyback 84.18)",
     ["126:H5363", "125:H4610", "126:H4687"]),
    ("Who runs SCDOT (governance and accountability)", "mixed", "medium-high",
     "Judiciary, unheard in 2019 and 2024 - then the same design passed near-unanimously in 2026 with Senate leadership carrying it (126:S831, Act 177)",
     ["126:S831", "123:H3111", "125:H5045", "126:H5071"]),
    ("Road contracts and contractor accountability", "mixed", "medium",
     "Committee deaths and two regulation resolutions stranded on the 2020 calendar; edges passed (123:S401 Act 36, 126:H3768 Act 244); transparency lives in provisos (84.8 priority lists, 84.15 dashboard)",
     ["125:H5312", "123:S1069", "123:S401", "126:H3768"]),
    ("Transit, rail, and other ways to get around", "rarely_moved", "high",
     "House Education and Public Works / Senate Transportation, zero hearings on every transit bill; the freight-rail credit passed the House twice (106-3, 65-46) and died in Senate Finance twice",
     ["123:H3656", "125:H4013", "124:H4817", "125:H3737"]),
    ("Planning for growth (zoning, comprehensive plans, annexation)", "mixed", "medium-high",
     "Committee deaths both directions; one enactment (123:S259, Act 163 of 2020, resilience element); concurrency (126:S227) amended on the Senate floor in the final weeks and died without completing passage",
     ["123:S259", "126:S227", "126:H5742", "125:H4651"]),
    ("Water, sewer, and broadband infrastructure", "mixed", "medium",
     "RIA consolidation passed the House 112-0 and died in Senate Finance; broadband bills died in committee; small-cell preemption enacted (123:H4262, Act 179)",
     ["125:H3075", "123:H4262", "123:S1235"]),
]

CARDS = [
    {"proposal_id": "local-funding-tools",
     "citizens_proposed": "New or expanded local funding tools: penny sales taxes, impact fees, tolls, parking fees (high frequency; high consensus; transparency on use of funds the attached condition).",
     "lawmakers_tried": "Widening the existing referendum-gated pennies: transit eligibility filed all four sessions, penny stacking (124:H3129), 11-year reimposition (125:S116), grocery carve-outs; five I-95 toll bills; a local-option gas tax (123:S172). All died in first committee. Enacted: the County Green Space Sales Tax Act (124:S152, Act 166 of 2022, 43-1/41-3/67-28) - the one new local penny - plus flexibility acts (123:S217 Act 146, 124:S40 Act 89, 126:H4589 Act 203).",
     "where_similar_stopped": "Senate Finance, House Ways and Means, Senate Transportation - no hearings.",
     "adjacent_carriers": ["Sen. Davis", "Sen. Scott", "Sen. Hutto (tolls)", "Rep. Pendarvis"],
     "levers_venue": "Transportation penny + tolls: Title 4 Ch. 37 (referendum). Capital project penny: Title 4 Ch. 10. Interstate tolls also need federal approval. Every local tool is referendum-gated - the transparency condition is structurally present in ballot-question requirements.",
     "open_questions": ["New tool, or make the existing penny usable for transit/maintenance?", "Why does a preservation penny pass while transportation-penny expansions go unheard in the same committees?"]},
    {"proposal_id": "developer-pays-growth",
     "citizens_proposed": "Developers pay for the infrastructure their projects create demand for, via impact fees or proffers (very high frequency; high consensus; price pass-through the concern).",
     "lawmakers_tried": "Ten bills, both directions, on the 1999 Development Impact Fee Act: expand (residential-only 125:H4659, resurfacing as fundable cost 126:H5088, gentrification fee 124:H3460/126:H4008) and narrow (exclude maintenance/admin costs 125:H4981/S856/H5017, 126:H3165; exempt repeat buyers 126:H4672). Zero hearings either way.",
     "where_similar_stopped": "Ways and Means / Finance / Judiciary / Medical-Municipal - first committee, all ten. The one enacted impact-fee rule blocked the fees: FY 2021-22 proviso 117.96 (schools, one year, not renewed).",
     "adjacent_carriers": ["Rep. Bailey (narrowing)", "Rep. Pendarvis (gentrification fee)", "Sen. Davis (concurrency)"],
     "levers_venue": "Impact fees are already legal under Section 6-1-910 et seq. with strict conditions (capital improvements plan; no maintenance funding). Proffers would be new law. The concurrency bills (126:S227 - amended on the Senate floor April 2026, died) are the adjacent growth-pays design.",
     "open_questions": ["New authority, or easing the 1999 Act's constraints?", "How does the group answer the school-proviso precedent - the one legislative action on impact fees blocked them?"]},
    {"proposal_id": "multimodal-transport",
     "citizens_proposed": "Invest in public transit, rail, and multimodal transportation rather than roads alone (high frequency, 3 events; high consensus in cities; rural relevance questioned).",
     "lawmakers_tried": "Complete streets (123:H3656), multimodal feasibility reviews (124:H3051), transit-oriented development (123:H3655, 125:H4013), developer transit stops (123:H3828), four rail commissions/studies, the Charlotte connection study (123:S730), commuter rail along highways (125:H5347).",
     "where_similar_stopped": "First committee, zero hearings, four sessions - House Education and Public Works and Senate Transportation. The freight exception: the shortline railroad credit passed the House 106-3 (124:H4817) and 65-46 (125:H3737) and died in Senate Finance both times.",
     "adjacent_carriers": ["Rep. Pendarvis (7 of 11 core bills)", "Sen. Scott", "Rep. Stavrinakis (rail)", "Rep. Ligon (shortline)"],
     "levers_venue": "No dedicated state transit funding stream exists in this record; the filed design is local-option penny-funded transit plus state studies. SCDOT's Title 57 mandate is the road system - the complete-streets bills tried to change that mandate.",
     "open_questions": ["State money, state studies, or unlocking the local penny for transit?", "Does the twice-passed freight credit show what kind of rail argument moves the House?"]},
    {"proposal_id": "state-master-planning",
     "citizens_proposed": "State-level comprehensive or regional planning in place of fragmented county plans (very high frequency, all 4 events; mixed consensus - the home-rule tension runs through it).",
     "lawmakers_tried": "Nothing filed proposes state or regional master planning - the lever does not appear in the record. What exists: state rules layered on local plans (123:S259, Act 163 of 2020 - Office of Resilience + required resiliency element, 44-1/65-35), concurrency (125:H5562, 126:S227/H4050), community impact assessments (126:H4390), annexation controls (125:H4651, 126:H5742).",
     "where_similar_stopped": "Concurrency got the furthest: 126:S227 reported favorably, amended on the Senate floor April 29, 2026, died without completing passage. Everything else died in committee - including the developer-side bills pulling the opposite direction (Home Attainability, shot clocks, TDR).",
     "adjacent_carriers": ["Sen. Davis (concurrency)", "Rep. Hixon", "Sen. Jackson (Home Attainability)", "Rep. Bustos (annexation)"],
     "levers_venue": "Local comprehensive planning is Title 6 Ch. 29 (nine required elements). The resilience act shows the add-an-element path works; a state/regional planning body would be new law. The enacted small-cell act (123:H4262, Act 179) is the record's one state-over-local land-use preemption.",
     "open_questions": ["State planning, regional coordination, or state rules for local plans (the only path with an enactment)?", "How is the home-rule tension resolved when bills pulling both directions die in the same committees?"]},
    {"proposal_id": "fix-roads-first",
     "citizens_proposed": "Maintain and repair existing roads before spending on expansion (medium frequency; mixed consensus).",
     "lawmakers_tried": "Pavement preservation program (126:H5363, 'Fix Our Roads Accountability Act'), SCDOT must maintain transferred roads (125:H4610), pothole hotlines (124:H3871, 125:H3451), sheriff road-hazard reports (126:H4687). All died in first committee.",
     "where_similar_stopped": "Bills: first committee, every one. Money: moved through the budget - proviso 86.1 (yearly fix-it-first rule for CTC money), $417.4M FY 2024-25 (CTC $200M + bridges $100M + rural road safety $117.4M), $200M FY 2025-26 bridges, $225M FY 2026-27, Road Buyback Program (84.18, new FY 2026-27).",
     "adjacent_carriers": ["Rep. White (the 2026 four-bill package)", "Rep. J.L. Johnson (hotlines)", "Rep. Hixon"],
     "levers_venue": "Maintenance money is annual-budget territory; a statutory preservation program (H5363's design) would make it permanent. The buyback program shifts roads to counties, resurfaced first.",
     "open_questions": ["Permanent law (unheard) or the budget (where it moves)?", "Is the Road Buyback Program a fix-first tool or a cost shift to counties?"]},
    {"proposal_id": "no-new-taxes",
     "citizens_proposed": "Fund infrastructure without new taxes or fees (medium frequency; low consensus - a sharp split, conflicting with local-funding-tools and developer-pays).",
     "lawmakers_tried": "Ten measures against the gas user fee: freeze (124:H4091), repeal (124:H4092), 2022 suspensions (124:H5103, H5112), the 2026 wave (126:S1045 + five near-identical House resolutions). EV-fee repeals (124:H4945, 125:H3177).",
     "where_similar_stopped": "Ways and Means / Finance, no hearings - the same rooms that stop the new-tool bills. Neither side of the tax split has had a vote. The one increase bill (126:H5331, county gas-fee share) died there too; collection was tightened instead (124:H3505, Act 70, 106-4/42-2).",
     "adjacent_carriers": ["Rep. Haddon (freeze/repeal)", "multiple 2026 suspension sponsors"],
     "levers_venue": "The gas fee is Title 12 Ch. 28 statute; suspensions were joint resolutions. Every local tool in the record is referendum-gated - where this proposal and local-funding-tools structurally meet.",
     "open_questions": ["Is the referendum requirement the shared ground for the split citizens showed?", "Do the budget's one-time transfers ($400M+ FY 2024-25) count as 'no new taxes' in practice?"]},
    {"proposal_id": "contractor-accountability",
     "citizens_proposed": "Improve bidding for road and infrastructure contracts and hold contractors accountable for results (medium frequency; high consensus; seen as low-cost).",
     "lawmakers_tried": "Design-build pilots (125:H5312, 126:H3560), the 2020 SCDOT contractor performance-evaluation and disqualification regulation resolutions (123:S1069/S1070, stranded on the calendar at COVID), expenditure-report certification (124:H4090), DBE goals (123:S385/H4401/H4823), the P3 framework (124:H3559).",
     "where_similar_stopped": "Committee or calendar; no floor votes. Edges passed: utility-relocation costs (123:S401, Act 36 of 2019, extended by 126:H3768, Act 244 of 2026) and contractor licensing (125:H4115, Act 69).",
     "adjacent_carriers": ["Rep. Brewer (design-build, Act 36 extension)", "Rep. Haddon"],
     "levers_venue": "SCDOT procurement sits in Title 57 + agency regulation (legislature reviews by joint resolution). The accountability tools that exist are one-year provisos: published priority lists with methodology (84.8/84.9) and the Programmed Project Viewer dashboard upgrade with forecast-vs-actual costs (84.18 FY 2024-25 onward).",
     "open_questions": ["Bidding method, performance consequences, or public visibility (already moving as provisos)?", "Should the one-year transparency provisos become statute?"]},
]

out = {
    "issue": "south-carolina-01-growth-infrastructure-roads",
    "generated_by": "reality-mapper v2.2 (issue-chat run, %s)" % datetime.date.today().isoformat(),
    "source": "working/south-carolina/growth-infrastructure-roads/evidence-pack.json",
    "baskets": {"often_moved": "Often moved before",
                "unfinished": "Got support but didn't finish",
                "rarely_moved": "Rarely moved before"},
    "headline_pattern": {
        "policy_bills": pack["inventory"]["policy_set"],
        "enacted": pack["inventory"]["dispositions_policy"]["Enacted"],
        "first_committee_deaths": pack["inventory"]["first_committee_deaths_policy"],
        "money_committee_deaths": pack["inventory"]["chokepoint_committees"]["House Ways and Means"]
                                  + pack["inventory"]["chokepoint_committees"]["Senate Finance"],
        "house_ways_and_means": pack["inventory"]["chokepoint_committees"]["House Ways and Means"],
        "senate_finance": pack["inventory"]["chokepoint_committees"]["Senate Finance"],
        "house_education_public_works": pack["inventory"]["chokepoint_committees"]["House Education and Public Works"],
        "floor_vote_failures": 0,
        "note": "Counts from evidence-pack.json inventory; policy set = core + adjacent."},
    "session_snapshot": pack["sessions"],
    "theme_scorecards": [
        {"theme": name, "bills": themes[name]["bills"],
         "enacted_or_adopted": themes[name]["enacted_or_adopted"],
         "basket": basket, "certainty": certainty,
         "typical_stop": stop, "examples": examples}
        for name, basket, certainty, stop, examples in SCORECARDS],
    "people_signals": pack["people_signals"],
    "high_support_non_enactments_top": pack["high_support_non_enactments"],
    "proposal_reality_cards": CARDS,
    "recent_enactments_watchlist": [
        "126:S831 - SCDOT Modernization Act (Act 177 of 2026, Senate 37-1, House 114-0, conference 112-2/43-0): governor appoints the secretary; commission duties devolve",
        "126:H3768 - Act 244 of 2026 (103-0/44-0): utility-relocation rule extended to 2032 + NEPA-assignment consent",
        "126:H4589 - Act 203 of 2026 (81-18/40-2/91-14): school-buildings penny opened to more counties",
        "126:S399 - Act 222 of 2026 (44-0/107-0): transit-facility trespass",
        "FY 2026-27 provisos: Road Buyback Program (84.18, new), $175M CTC Acceleration + $50M Bridge Modernization (118.21), CTC fix-it-first renewed (86.1), priority lists + dashboard renewed (84.8, 84.15)"],
    "deliberation_prompts": [
        "The money committees stop 42% of this set without hearings. What would earn a first hearing for a penny-tax expansion or impact-fee bill - and does the Green Space penny's path transfer?",
        "The one new local tool passed funds green space, not roads. Why did the same legislature never hear a transit-penny clarification?",
        "Impact-fee bills died in both directions for eight years; the one enacted impact-fee rule blocked the fees for schools. Is the 1999 Act's maintenance exclusion the real fight?",
        "Fix-first moves as one-time budget money and one-year rules, never as permanent law. Feature (annual control) or problem (no guarantee)?",
        "SCDOT governance passed 114-0 once leadership carried it, after dying unheard in 2019 and 2024. What does that path say about the other unheard structural bills?",
        "The freight-rail credit passed the House twice and died in Senate Finance twice; no passenger-transit bill ever got a hearing. How would a group learn what the Senate Finance objection is?",
        "Nothing proposes state or regional planning; concurrency died at the last step in 2026. Is S227's near-miss the opening?",
        "No-new-taxes and local-funding-tools conflict - but every local tool is referendum-gated. Is 'voters decide per county' the reconcilable core?",
        "Contract transparency exists as one-year provisos. Should a proposal make the dashboard and priority-list rules statute, and what is lost if they lapse?"],
    "certainty": {
        "money_committee_chokepoint": "high (58 of 138 first-committee deaths; 86% first-committee death rate)",
        "impact_fee_bills_never_voted": "high (10 bills, both directions, three sessions)",
        "transit_rail_never_heard": "high (11 core bills, four sessions)",
        "gas_fee_bills_never_voted": "high (10 measures, two sessions)",
        "no_state_planning_bill_exists": "high (absence verified against title scan + full-text discovery)",
        "fix_first_via_budget": "high on the money trail (verbatim proviso figures); reasons not in the record",
        "scdot_governance_path": "high on facts; single-case pattern for inference",
        "shortline_two_passages": "high on facts; two instances - history, not destiny",
        "green_space_only_new_tool": "high within 2019-2026 scope"},
}
json.dump(out, open(os.path.join(HERE, "reality-map.json"), "w"), indent=1)
print("reality-map.json written:", len(out["theme_scorecards"]), "scorecards,", len(CARDS), "cards")
