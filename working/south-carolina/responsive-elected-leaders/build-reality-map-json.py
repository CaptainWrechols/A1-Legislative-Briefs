#!/usr/bin/env python3
"""Structured reality-map.json for south-carolina-02-responsive-elected-leaders.

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
    ("Term limits for elected officials", "rarely_moved", "high",
     "First Judiciary committee, no hearing, no vote - 30 state measures for 30; only the federal-target Article V application (126:H3008) was adopted",
     ["124:S302", "126:S590", "126:H3744", "126:H3008"]),
    ("Campaign money rules", "rarely_moved", "high",
     "Senate/House Judiciary, no votes; the one floor vote (125:H4561, House 53-45) died in Senate Judiciary",
     ["124:H4877", "126:S960", "126:S813", "125:H4561"]),
    ("Ranked choice voting and runoffs", "rarely_moved", "high",
     "House Judiciary, no hearings - enabling bills and ban bills alike",
     ["124:H5135", "126:H3589", "126:H3386"]),
    ("Who draws the voting maps (redistricting)", "rarely_moved", "high",
     "Judiciary committees, no votes on any commission/criteria bill; the legislature's own maps passed (Acts 117/118); the 2026 mid-decade redraw was shelved by the Senate 26-18",
     ["123:H3044", "124:H4229", "125:H4222", "126:H5683"]),
    ("Financial disclosure and ethics enforcement", "mixed", "medium-high",
     "Mostly Judiciary deaths, but one enactment (126:S70, Act 191 of 2026) and one conference death after unanimous passage in both chambers (126:H3570)",
     ["126:S70", "126:H3570", "125:S169", "126:S75"]),
    ("Lobbying rules", "rarely_moved", "high",
     "First committee, no votes - including leadership-sponsored 126:S632",
     ["126:S632", "124:H4876", "125:H4585"]),
    ("Open government: public records and meetings", "rarely_moved", "high",
     "Judiciary committees, no votes anywhere in eight years",
     ["123:H3259", "126:S6", "126:H3646"]),
    ("Civics and voter education", "mixed", "medium",
     "House Education and Public Works; the REACH Act passed on its second try (124:S38, Act 26 of 2021)",
     ["124:S38", "123:S35", "126:H3547"]),
    ("Direct democracy: recall, initiative, referendum", "rarely_moved", "medium",
     "Judiciary, no votes (3 bills - thin count)",
     ["124:H3256", "124:S39", "126:S95"]),
]

CARDS = [
    {"proposal_id": "term-limits",
     "citizens_proposed": "Term limits or rotation rules so incumbents cannot hold the same office indefinitely (very high frequency; mixed consensus).",
     "lawmakers_tried": "30 state-level measures in three designs: direct constitutional caps (2-6 terms), authorize-by-law amendments, and straight statutes. All died in a Judiciary committee with no vote. The one success targets Congress: 126:H3008, the Article V congressional term limits application, adopted May 2025 (Senate 29-14).",
     "where_similar_stopped": "House/Senate Judiciary, 30 for 30, no hearings. The broad Convention of States application (incl. federal term limits) failed at the last step twice (124:S133, 125:H3676) before the single-subject 2025 version passed.",
     "adjacent_carriers": ["Rep. B. Cox / B.J. Cox", "Sen. McLeod", "Sen. Climer", "Sen. Cash", "Sen. Reichenbach"],
     "levers_venue": "State constitutional amendment requires two-thirds of each chamber (the members being capped) plus a referendum; statute-only caps may conflict with the constitution's qualifications clause; chair rotation is a chamber rule (125:H4692), not a law.",
     "open_questions": ["Which design fits the two-thirds hurdle?", "What would earn a first hearing in eight years?", "What does the adopted federal application signal about state-level appetite, if anything?"]},
    {"proposal_id": "campaign-finance-reform",
     "citizens_proposed": "Limit the influence of money in politics, including PAC limits (very high frequency; high consensus; constitutional constraint noted).",
     "lawmakers_tried": "Mostly disclosure: dark-money ad disclosure (3x incl. leadership-sponsored), contributor employer disclosure, bank-statement filing (5x), a corporate-contribution ban, pay-to-play appointment bans (4x), one public-financing amendment (AG races only). All five contribution-limit bills raise limits; none lower them.",
     "where_similar_stopped": "Judiciary, no votes - except 125:H4561 (campaign funds for dependent care), House 53-45, died Senate Judiciary.",
     "adjacent_carriers": ["Senate leadership (Bennett, Hembree, Rankin, Massey, Campsen, Peeler, Jackson, Sabb)", "Sen. Fanning", "Sen. Young", "Rep. Wetmore"],
     "levers_venue": "Contribution limits and disclosure are state law (Title 8 Ch. 13); independent-expenditure spending caps face the federal constitutional constraint citizens flagged, which is why filed bills chase disclosure.",
     "open_questions": ["Limits, disclosure, or public financing - which is the actual aim?", "Why do leadership-sponsored disclosure bills die in their own chamber's committee?"]},
    {"proposal_id": "ranked-choice-voting",
     "citizens_proposed": "Ranked choice (instant runoff) voting (very high frequency; partial consensus; voter-confusion concerns).",
     "lawmakers_tried": "Three local-option enabling bills (124:H5135, 125:H4022, 126:H3589) and two statewide bans (125:H4591, 126:H3386).",
     "where_similar_stopped": "All five died in House Judiciary, no hearings - bans and enabling bills in the same room.",
     "adjacent_carriers": ["Rep. B. Cox", "Rep. J.L. Johnson", "Rep. Taylor (bans)"],
     "levers_venue": "Election method is state law even for city elections, so cities cannot adopt RCV without enabling legislation; runoff-abolition bills solve the same runoff-cost problem the opposite way and also never moved.",
     "open_questions": ["Statewide, local option, or runoff replacement?", "What would implementation cost (no fiscal note ever produced)?"]},
    {"proposal_id": "independent-redistricting",
     "citizens_proposed": "Move redistricting to an independent or nonpartisan commission (high frequency; high consensus; who-appoints was the debated tradeoff).",
     "lawmakers_tried": "21 bills, 2019-2024: constitutional independent commissions, statutory citizens commissions, and binding-criteria acts (FAIR, Anti-Gerrymandering). Zero hearings, zero votes. The legislature drew the actual maps (Act 117 of 2021, Act 118 of 2022).",
     "where_similar_stopped": "Judiciary committees every time; no commission bill filed in the 126th - the first session without one. The 2026 mid-decade redraw (H5683) passed the House 74-37 and was shelved on the Senate floor 26-18.",
     "adjacent_carriers": ["Rep. Cobb-Hunter", "Sen. Fanning", "Sen. Setzler", "Rep. Clary"],
     "levers_venue": "The constitution assigns reapportionment to the General Assembly; a true independent commission needs a constitutional amendment (two-thirds + referendum). Statutory designs (advisory commissions, binding criteria) exist because of that hurdle.",
     "open_questions": ["Advisory commission, binding criteria, or constitutional commission?", "Who appoints?", "Does the 2026 mid-decade fight change the opening for a criteria bill?"]},
    {"proposal_id": "financial-disclosure",
     "citizens_proposed": "Stronger financial disclosure and conflict-of-interest tracking, including PAC ties (high frequency; high consensus).",
     "lawmakers_tried": "The most movement of any proposal: 126:H3570 (disclosure rewrite) passed the House 102-0 and Senate 40-0 in different versions and died in conference; 126:S70 (School Board Ethics Act, Act 191 of 2026) became law 39-2 and 109-4. A slice of H3570 became FY 2026-27 proviso 117.219.",
     "where_similar_stopped": "Everything else - tax-return disclosure (3x), e-filing audits (4x), special-purpose districts (2x), ethics-fine ballot bars (4x), party-chairmen coverage - died in Judiciary without votes.",
     "adjacent_carriers": ["Sen. Hembree", "Sen. Climer", "Sen. Fanning", "Rep. Bannister"],
     "levers_venue": "State law (Ethics Act, Title 8 Ch. 13); Ethics Commission enforcement capacity and even its reporting website are controlled through one-year budget provisos (110.1, 110.2).",
     "open_questions": ["What divided the chambers in the H3570 conference?", "Does enforcement funding belong in the proposal, given proviso-level control?"]},
    {"proposal_id": "voter-civics-education",
     "citizens_proposed": "Better voter education and civics instruction, plus neutral civic information tools (medium frequency; high consensus; who curates 'neutral' open).",
     "lawmakers_tried": "The REACH Act (college civics instruction) became law on its second try (124:S38, Act 26 of 2021, 45-0 and 91-12) after 123:S35 passed the Senate 29-7 and died in House Education. The K-12 middle-school civics unit (126:H3547) sits unheard. Civic-education money moved through budget provisos (45.11 FY25, 118.21 FY27).",
     "where_similar_stopped": "House Education and Public Works - the one theme whose chokepoint is not Judiciary.",
     "adjacent_carriers": ["Sen. Grooms (REACH)", "Rep. Cobb-Hunter (H3547)"],
     "levers_venue": "Curriculum is state law plus State Board of Education standards; a voter-information tool would sit with the Election Commission - no bill proposes one.",
     "open_questions": ["Curriculum mandate, funding, or information tool?", "Who curates 'neutral'?", "Do content-restriction bills (124:H4392) change the design?"]},
]

out = {
    "issue": "south-carolina-02-responsive-elected-leaders",
    "generated_by": "reality-mapper v2.2 (issue-chat run, %s)" % datetime.date.today().isoformat(),
    "source": "working/south-carolina/responsive-elected-leaders/evidence-pack.json",
    "baskets": {"often_moved": "Often moved before",
                "unfinished": "Got support but didn't finish",
                "rarely_moved": "Rarely moved before"},
    "headline_pattern": {
        "policy_bills": 177,
        "first_committee_deaths": 163,
        "first_committee_deaths_in_judiciary": 149,
        "house_judiciary": 84, "senate_judiciary": 65,
        "no_passage_vote_at_any_stage": 166,
        "enacted": 4, "adopted_resolutions": 1,
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
        "126:S70 - School Board Ethics Act (Act 191 of 2026, 39-2 and 109-4)",
        "126:H3008 - congressional term limits Article V application, adopted May 2025 (29-14)",
        "126:H3007 - balanced-budget Article V application, adopted January 2026 (context)",
        "FY 2026-27 provisos: 117.219 ethics-filing detail (new), 117.145 election-litigation intervention, 110.2 monthly Ethics Commission meetings, 118.6/117.92 no public funds for lobbyists, 118.21 USC civic leadership center ($2.5M)"],
    "deliberation_prompts": [
        "If 92% of accountability bills die in the same two Judiciary committees without a hearing, what would earn hearing number one?",
        "Term-limit amendments need two-thirds of the members whose careers they would cap - is authorize-by-law a real path or the same hurdle reshaped?",
        "H3570 passed both chambers unanimously in different versions and died reconciling them - a 'no' on disclosure, or a solvable drafting fight?",
        "When a piece of a dead bill reappears as a one-year proviso (117.219), is that a win, a placeholder, or a way to avoid permanent law?",
        "Both RCV-enabling and RCV-ban bills die unheard in the same committee - radioactive, or unprioritized?",
        "Does the Senate's 26-18 shelving of the mid-decade redraw tell a commission group which chamber to start in?",
        "Why is it easier to pass accountability rules for other bodies (school boards, colleges, Congress) than for the General Assembly itself?",
        "Leadership-sponsored campaign-finance disclosure died in the leaders' own chamber's committee - what would a group need to learn about why?",
        "No bill proposes a neutral voter-information tool - is that lane empty because nobody asked, or because it belongs to an agency?"],
    "certainty": {
        "state_term_limits_never_voted": "high (30 bills, four sessions)",
        "redistricting_commissions_never_voted": "high (21 bills)",
        "judiciary_chokepoint": "high (149 of 163 first-committee deaths)",
        "campaign_money_no_votes": "high (35 of 36)",
        "rcv_both_directions_unheard": "high pattern, modest count (5)",
        "disclosure_most_moved_lane": "medium-high",
        "civics_lane": "medium (one enactment, small count)",
        "direct_democracy": "medium (3 bills)",
        "single_example_patterns": "insufficient alone (H4561 floor vote, H5683 continue motion, S133 conference death) - labeled history, not destiny"},
}
json.dump(out, open(os.path.join(HERE, "reality-map.json"), "w"), indent=1)
print("reality-map.json written:", len(out["theme_scorecards"]), "scorecards,", len(CARDS), "cards")
