#!/usr/bin/env python3
"""Evidence Curator build for south-carolina-01-growth-infrastructure-roads.

Combines curation-map.json (hand-reviewed set) with the prebuilt processed
artifacts (bills-core, bill-votes) into the evidence pack the Reality Mapper
and writers consume. Universe-sourced bills (the sales-tax/annexation/
hospitality adds) take their records and roll calls from
sources/south-carolina/_universe/. No scraping; local files only.

Outputs:
  working/south-carolina/growth-infrastructure-roads/evidence-pack.json
  working/south-carolina/growth-infrastructure-roads/evidence-pack.md
"""
import datetime
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "sources/south-carolina/growth-infrastructure-roads")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")

SESSION_LABEL = {123: "123rd (2019-2020)", 124: "124th (2021-2022)",
                 125: "125th (2023-2024)", 126: "126th (2025-2026)"}

PROPOSALS = [
    {"id": "local-funding-tools",
     "title": "New/expanded local funding tools (penny sales tax, impact fees, tolls, parking fees)"},
    {"id": "developer-pays-growth",
     "title": "Make developers pay for growth (impact fees / proffers)"},
    {"id": "multimodal-transport",
     "title": "Public transit, rail, and multimodal options beyond roads"},
    {"id": "state-master-planning",
     "title": "State comprehensive/regional planning instead of fragmented county plans"},
    {"id": "fix-roads-first",
     "title": "Maintain existing roads before building new capacity"},
    {"id": "no-new-taxes",
     "title": "Oppose new taxes or fees for infrastructure"},
    {"id": "contractor-accountability",
     "title": "Improve the bidding process and hold contractors accountable"},
]

# Hand-reviewed crosswalk (bill keys verified in the curation map).
CROSSWALK = {
    "local-funding-tools": {
        "matched_bills": ["123:S594", "123:S611", "123:H4389", "124:H3535", "124:S437",
                          "125:S290", "125:S562", "125:H4059", "125:H5188", "125:S1113",
                          "126:S979", "125:S116", "124:H3129", "124:S152", "123:S178",
                          "123:H3739", "123:S780", "125:S499", "125:S674", "123:S172",
                          "124:H3483"],
        "near_miss_bills": ["123:S449", "126:S298", "126:H3911", "126:S1006", "126:H5744",
                            "125:S792", "126:H4589", "123:S217", "123:H3132", "123:H4674",
                            "123:S629", "123:H4597", "124:S40"],
        "coverage": "one_new_tool_enacted_everything_else_unheard",
        "note": ("The tools citizens named already exist in some form: counties can levy a "
                 "transportation penny tax (with tolls) by referendum under Title 4 Chapter 37, "
                 "and a capital project penny under Chapter 10. What the record holds is attempts "
                 "to widen those tools - letting the penny fund transit explicitly (filed in all "
                 "four sessions), stacking pennies (H3129), longer reimposition (S116), grocery "
                 "exemptions - and every one died in Finance or Ways and Means without a vote. "
                 "The one NEW local tool that passed is the County Green Space Sales Tax Act "
                 "(S152, Act 166 of 2022; Senate 43-1 and 41-3, House 67-28) - a preservation "
                 "penny, not a roads penny. Tolls went nowhere: five bills to toll I-95 (four "
                 "targeting the Lake Marion crossing) died in Senate Transportation or House "
                 "Education and Public Works. The local-option gas tax (S172, one cent for beach "
                 "renourishment) died in Finance. Around the edges, flexibility passed: tourism "
                 "taxes can now fund flooding and drainage repairs (S217, Act 146 of 2020), paid "
                 "beach parking got state rules (S40, Act 89 of 2021), and the school-buildings "
                 "penny was opened to more counties (H4589, Act 203 of 2026, House 81-18). The "
                 "SCDOT Modernization Act (126:S831, Act 177 of 2026) then rewrote the state "
                 "toll framework itself: usage charges may only be placed on new-capacity "
                 "'choice lanes', never on existing free lanes."),
    },
    "developer-pays-growth": {
        "matched_bills": ["124:H3460", "126:H4008", "124:H4943", "125:H4659", "125:H4981",
                          "125:S856", "125:H5017", "126:H3165", "126:H4672", "126:H5088"],
        "near_miss_bills": ["125:H5562", "126:S227", "126:H4050", "123:H3828"],
        "coverage": "attempts_both_directions_zero_votes",
        "note": ("South Carolina has had a Development Impact Fee Act since 1999 (Section "
                 "6-1-910 et seq.), so the fight is over its shape. Ten bills in three sessions "
                 "pulled in both directions: expanding the tool (residential-only fees H4659, "
                 "adding road resurfacing as a fundable cost H5088, a gentrification-fund fee on "
                 "developers H3460/H4008) and narrowing it for the building industry (excluding "
                 "maintenance and administrative costs, H4981/S856/H5017/H3165; exempting "
                 "repeat in-district buyers, H4672). Not one impact-fee bill received a hearing "
                 "or a vote in eight years - all died in Ways and Means, Finance, or a Medical/"
                 "Municipal committee. The only impact-fee rule that became law in this record "
                 "ran the other way: FY 2021-22 budget proviso 117.96 barred impact fees on new "
                 "school construction for one year (not renewed). The concurrency bills "
                 "(development waits for infrastructure) are the adjacent lane: S227 got the "
                 "furthest of anything in this proposal's orbit - reported favorably and amended "
                 "on the Senate floor in April 2026, then died without completing passage."),
    },
    "multimodal-transport": {
        "matched_bills": ["123:H3656", "124:H3051", "123:H3655", "125:H4013", "123:H3828",
                          "123:S216", "123:H3189", "124:H3937", "126:H4122", "123:S730",
                          "125:H5347"],
        "near_miss_bills": ["124:H4817", "125:H3737", "125:S269", "126:S399", "123:H3654",
                            "126:H4057"],
        "coverage": "zero_hearings_on_transit_two_house_passages_on_rail_credit",
        "note": ("Every transit and rail bill died in its first committee: complete streets "
                 "(H3656), SCDOT feasibility reviews with bus lanes (H3051), transit-oriented "
                 "development agencies (H3655, H4013), the developer-provided transit stop act "
                 "(H3828), commuter/high-speed rail commissions (S216, H3189, H3937, H4122, "
                 "S730), and the commuter-rail-along-highways study (H5347). The one measure "
                 "with floor movement is freight, not passengers: the Shortline Railroad "
                 "Modernization Act tax credit passed the House twice - 106-3 in 2022 and 65-46 "
                 "in 2023 - and died in Senate Finance both times. What was enacted is "
                 "peripheral: a transit-facility trespass misdemeanor (S399, Act 222 of 2026, "
                 "44-0 and 107-0) and the EV-charging/electrification framework (S304, Act 46 "
                 "of 2021). Note the county-penny transit clarifications counted under "
                 "local-funding-tools - the two proposals meet there."),
    },
    "state-master-planning": {
        "matched_bills": ["123:S259", "123:H4731", "125:H5562", "126:S227", "126:H4050",
                          "126:H4390", "126:H5742", "125:H4651"],
        "near_miss_bills": ["124:S528", "124:H3863", "125:S4", "126:S4", "123:H4482",
                            "123:S757", "123:H4598", "123:S833", "123:H4721", "125:H4652",
                            "126:H3215", "125:H4996", "126:H4146", "126:S288", "126:S530",
                            "126:H4293", "124:H5196", "125:H3236", "126:H4726"],
        "coverage": "one_enactment_rest_in_committee",
        "note": ("Nothing filed proposes state-level master planning in place of county plans - "
                 "the lever citizens described does not appear in this record. What exists is "
                 "state rules layered onto the existing local comprehensive-plan system: the "
                 "Disaster Relief and Resilience Act (S259, Act 163 of 2020; Senate 44-1, House "
                 "65-35) created a state Office of Resilience with a statewide resilience plan "
                 "and added a required resiliency element to every local comprehensive plan - "
                 "the record's one enacted statewide-planning layer. The concurrency design "
                 "(infrastructure keeps pace before development is approved: H5562, S227, "
                 "H4050) is the closest thing to the growth-management idea; S227 was amended "
                 "on the Senate floor in the 2026 session's final weeks and died there. The "
                 "annexation fights (county standing to challenge annexations H4651, county "
                 "power to block annexation until an infrastructure impact study H5742) carry "
                 "the same infrastructure-first logic and also died in Judiciary. The developer-"
                 "side bills run opposite: permitting shot-clocks, third-party inspectors, and "
                 "housing-impact analyses to loosen local control."),
    },
    "fix-roads-first": {
        "matched_bills": ["126:H5363", "125:H4610", "124:H3871", "125:H3451", "126:H4687",
                          "125:H3516", "123:H3358"],
        "near_miss_bills": ["126:H4971", "124:S1043", "126:H5331", "125:H5348", "126:H3357"],
        "coverage": "bills_unheard_money_moved_through_budget",
        "note": ("The maintenance-first idea has moved through money, not law. Every "
                 "maintenance-accountability bill died in first committee: the Fix Our Roads "
                 "Accountability Act's statewide pavement preservation program (H5363, 2026), "
                 "the rule that SCDOT must maintain roads it takes over (H4610), pothole-damage "
                 "hotlines (H3871, H3451), and sheriff road-hazard reports (H4687). The budget "
                 "is where fix-it-first is real: an every-year proviso (86.1) requires the Act "
                 "40 increase to County Transportation Committees be spent exclusively on "
                 "repairs, maintenance, and improvements; and the one-time money lists put "
                 "$200,000,000 into a CTC Acceleration Fund plus $100,000,000 into bridges in "
                 "FY 2024-25, $200,000,000 into Bridge Modernization in FY 2025-26, and "
                 "$175,000,000 CTC plus $50,000,000 bridges in FY 2026-27. FY 2026-27 also "
                 "created a Road Buyback Program (proviso 84.18): the state paying counties to "
                 "take back state roads, resurfaced first. And one piece passed as permanent "
                 "law inside the SCDOT Modernization Act (126:S831, Act 177 of 2026): the "
                 "Pothole Mitigation Program (new Section 57-5-1800) - public pothole "
                 "reporting by phone, website, or a free mobile app, a seven-day repair "
                 "requirement, and $15,000,000 a year for full-depth repair of repeat "
                 "potholes - plus a rewritten county 'C'-funds rule (a thirty-three percent "
                 "state-highway share, the rest at the county committee's discretion)."),
    },
    "no-new-taxes": {
        "matched_bills": ["124:H4091", "124:H4092", "124:H5103", "124:H5112", "126:S1045",
                          "126:H5398", "126:H5419", "126:H5422", "126:H5443", "126:H5475"],
        "near_miss_bills": ["126:H5331", "124:H4945", "125:H3177", "123:H5150", "124:S148",
                            "124:H3505"],
        "coverage": "suspension_and_repeal_bills_all_died_in_committee",
        "note": ("The other side of the funding split is fully represented: ten measures to "
                 "freeze, repeal, or suspend the gas user fee - the 2017 Act 40 increase - were "
                 "filed across the 124th and 126th sessions (four in the 2022 price spike, six "
                 "in 2026, five of those near-identical suspension resolutions). Every one died "
                 "in Ways and Means or Finance without a vote. Two bills would have repealed "
                 "the road-use fee on electric vehicles (H4945, H3177) - also unheard. The one "
                 "gas-tax bill pointing the other way, H5331 (2026), would more than double the "
                 "county share of the gas fee for local roads; it died in Ways and Means too. "
                 "Meanwhile the fee machinery was quietly tightened, not loosened: Act 70 of "
                 "2021 (H3505, 106-4 and 42-2) closed the titling gap in the road-funding "
                 "infrastructure maintenance fee."),
    },
    "contractor-accountability": {
        "matched_bills": ["125:H5312", "126:H3560", "123:S1069", "123:S1070", "124:H4090",
                          "123:S385", "123:H4401", "123:H4823"],
        "near_miss_bills": ["124:H3559", "123:S401", "123:H3799", "126:H3768", "125:H5315",
                            "126:H3845", "125:H3119", "126:H3344", "125:H4115"],
        "coverage": "bills_unheard_transparency_moved_through_budget",
        "note": ("The bidding-process bills never moved: SCDOT design-build pilots (H5312, "
                 "H3560) died in Ways and Means and Education and Public Works, and the 2020 "
                 "joint resolutions approving SCDOT's contractor performance-evaluation and "
                 "disqualification regulations (S1069, S1070) were placed on the Senate "
                 "calendar and never taken up when COVID ended the session. SCDOT expenditure-"
                 "report certification (H4090) and disadvantaged-business contracting bills "
                 "(S385, H4401, H4823) died in committee. But the bidding method itself then "
                 "passed inside the SCDOT Modernization Act (126:S831, Act 177 of 2026): "
                 "phased design-build contracting (new Section 57-5-1710) and construction-"
                 "manager/general-contractor authority (57-5-1720), plus public-private "
                 "partnership agreements capped at sixty years (57-3-205) and an independent "
                 "external performance audit of SCDOT every four years. What else passed sits "
                 "at the edges: who pays to relocate water and sewer lines in road projects "
                 "(S401, Act 36 of 2019, 38-0 and 108-0; extended to 2032 by H3768, Act 244 "
                 "of 2026) and a contractor-licensing rewrite (H4115, Act 69 of 2023). The "
                 "transparency tools citizens described exist as budget provisos: SCDOT must "
                 "publish its project priority lists with ranking methodology (84.8/84.9, "
                 "renewed yearly) and upgrade its public Programmed Project Viewer dashboard "
                 "with forecast-versus-actual costs and an on-time/on-budget list (84.18 "
                 "FY 2024-25 onward)."),
    },
}

DATA_LIMITS = [
    "The set is keyword-discovered from official full-text search plus a title/summary scan of the certified universe; it is a curated selection, not a proven-complete universe of growth and infrastructure bills. Nine bills were hand-added from the certified universe because the Pass 1 search terms did not cover 'sales tax', 'annexation', or 'hospitality tax' phrasings.",
    "South Carolina publishes committee outcomes in bill histories but never committee vote tallies; no committee vote counts exist anywhere in this record and none may be implied.",
    "Party labels are not attached to sponsors or floor votes in this pack: the roster/ballot join was not fetched for this brief, so the brief makes no party claims.",
    "Floor roll-call counts are verbatim from the chamber vote-history tables; motions to table, to adopt amendments, or to carry over are procedural, and only passage/reading/adoption votes are used as support signals.",
    "Local County Transportation Committee membership bills routinely pass one chamber and finish through the county legislative delegation; their one-chamber passage is not a support signal for statewide policy.",
    "For non-enacted 126th-session (2025-2026) bills, disposition is 'did not pass' as of the collection date (2026-08-25), after the regular session's final regular calendar.",
    "FY 2020-21 has no enacted Part IB proviso set (COVID continuing resolution), so budget-proviso coverage runs FY 2021-22 through FY 2026-27. Proviso dollar figures are verbatim from the enacted Part IB text.",
    "The seven Phase 2 constituent proposals are Forum process input from Community Conversations (labels [P-...]), not verified facts.",
    "The 2017 gas-tax act (Act 40) and the 1999 Development Impact Fee Act predate this record's 2019 start; they appear as background context, not as collected bills.",
]

# Stage overrides for bills whose histories the generic classifier cannot
# describe accurately (verified against full action lists).
STAGE_OVERRIDES = {
    (126, "H5071"): ("Did not pass (session ended)",
                     "Reported out of House Ways and Means; recommitted after floor debate stalled - the Senate's S831 passed instead"),
    (126, "S227"):  ("Did not pass (session ended)",
                     "Reported favorably and amended on the Senate floor in the session's final weeks; never completed passage"),
    (126, "S288"):  ("Did not pass (session ended)",
                     "Favorable Judiciary committee report; died on the Senate calendar"),
    (123, "H4369"): ("Did not pass",
                     "Passed the House 107-0; favorable Senate committee report, then recommitted to Senate Transportation"),
    (123, "S780"):  ("Did not pass",
                     "Placed directly on the Senate calendar; never taken up"),
    (123, "S1069"): ("Did not pass",
                     "Placed on the Senate calendar; never taken up before COVID ended the session"),
    (123, "S1070"): ("Did not pass",
                     "Placed on the Senate calendar; never taken up before COVID ended the session"),
    (123, "H3775"): ("Did not pass",
                     "Recalled from Judiciary and recommitted to Ways and Means; no further action"),
    (126, "H3845"): ("Did not pass (session ended)",
                     "Recalled from one committee and recommitted to another; no further action"),
    (124, "H4817"): ("Did not pass",
                     "Passed the House 106-3; died in Senate Finance"),
    (125, "H3737"): ("Did not pass",
                     "Passed the House 65-46; died in Senate Finance"),
    (125, "H3075"): ("Did not pass",
                     "Passed the House 112-0; died in Senate Finance"),
}

PASSAGE_RE = re.compile(
    r"passage of bill|3rd reading|third reading|2nd reading|second reading|ratif"
    r"|adopt concurrent resolution|adopt the resolution|conference report"
    r"|concur in senate amendments|concur in house amendments", re.I)
PROCEDURAL_RE = re.compile(r"\btable\b|amendment number|adopt amendment|to continue|rule \d|adjourn|special order|reconsider|recall|order of the day|waive|suspend|free conference", re.I)


def parse_sponsors(raw):
    if not raw:
        return []
    s = raw.replace("Reps.", "").replace("Rep.", "").replace("Senators", "").replace("Senator", "")
    return [p.strip() for p in re.split(r",| and ", s) if p.strip()]


def _committee(actions):
    for a in actions:
        m = re.match(r"Referred to Committee on (.+?)(?:\s*\(|$)", a["action"])
        if m:
            return m.group(1).strip()
    return None


def classify(b):
    """Return (disposition, stage_plain)."""
    key = (b["session"], b["bill_no"])
    if key in STAGE_OVERRIDES:
        return STAGE_OVERRIDES[key]
    acts = [a["action"] for a in b["actions"]]
    joined = " || ".join(acts)
    if b.get("act_no"):
        return ("Enacted", "Became law (Act %s)" % b["act_no"].lstrip("A"))
    if b.get("governor_actions"):
        gov = " ".join(g.get("action", "") for g in b["governor_actions"]).lower()
        if "veto" in gov:
            return ("Vetoed", "Passed both chambers; vetoed by the governor")
    sess = b["session"]
    died = "Did not pass" if sess < 126 else "Did not pass (session ended)"
    origin = "House" if b["chamber"] == "H" else "Senate"
    second = "Senate" if origin == "House" else "House"
    if re.search(r"[Cc]onference committee appointed", joined):
        return (died, "Passed both chambers; died in conference")
    second_acts = [a for a in b["actions"] if a["body"] == second]
    crossed = any(re.search(r"Introduced and read first time|Introduced \(|Referred to Committee|Referred to .*Delegation|Referred to delegation",
                            a["action"]) for a in second_acts)
    if crossed:
        if any("Second Reading Failed" in a["action"] for a in second_acts):
            return (died, "Passed the %s; failed on the %s floor" % (origin, second))
        committee = _committee(second_acts)
        if committee:
            return (died, "Passed the %s; died in %s %s Committee" %
                    (origin, second, committee))
        if any(re.search(r"Referred to .*[Dd]elegation", a["action"]) for a in second_acts):
            return (died, "Passed the %s; died with the county delegation in the %s" % (origin, second))
        return (died, "Passed the %s; died in the %s" % (origin, second))
    origin_acts = [a for a in b["actions"] if a["body"] == origin]
    committee = _committee(origin_acts)
    if re.search(r"Read second time", joined):
        return (died, "Advanced in its own chamber; never finished passage there")
    if re.search(r"Committee report", joined):
        where = ("%s %s Committee" % (origin, committee)) if committee else "committee"
        return (died, "Reported out of %s; died before a floor vote" % where)
    if committee:
        return (died, "Died in its first committee (%s %s)" % (origin, committee))
    return (died, "Died without committee referral action")


def vote_snapshot(roll_calls):
    """Passage/adoption-type floor votes per chamber (verbatim counts)."""
    keep = []
    for rc in roll_calls:
        motion = rc["motion"]
        if PASSAGE_RE.search(motion) and not PROCEDURAL_RE.search(motion):
            keep.append({
                "chamber": rc["chamber"], "motion": rc["motion"],
                "yeas": rc["yeas"], "nays": rc["nays"], "result": rc["result"],
                "datetime": rc["datetime"], "ballot_pdf_key": rc["ballot_pdf_key"],
            })
    return keep


def load_universe(session, bill_nos):
    out = {}
    with gzip.open(os.path.join(UNIVERSE, str(session), "bills.jsonl.gz"), "rt") as f:
        for line in f:
            b = json.loads(line)
            if b["bill_no"] in bill_nos:
                b.setdefault("act_no", None)
                b.setdefault("ratification_no", None)
                out[(session, b["bill_no"])] = b
    rcs = json.load(open(os.path.join(UNIVERSE, str(session), "rollcalls.json")))["roll_calls"]
    votes = {}
    for r in rcs:
        if r["bill_no"] in bill_nos:
            votes.setdefault((session, r["bill_no"]), []).append(r)
    return out, votes


def main():
    curation = json.load(open(os.path.join(HERE, "curation-map.json")))
    core = {(b["session"], b["bill_no"]): b
            for b in json.load(open(os.path.join(SRC, "processed/bills-core.json")))["bills"]}
    votes = {(v["session"], v["bill_no"]): v["roll_calls"]
             for v in json.load(open(os.path.join(SRC, "processed/bill-votes.json")))["bills"]}

    uni_keys = {}
    for row in curation["bills"]:
        if row.get("source") == "universe":
            uni_keys.setdefault(row["session"], set()).add(row["bill_no"])
    for sess, bns in uni_keys.items():
        ub, uv = load_universe(sess, bns)
        core.update(ub)
        votes.update(uv)

    bills = []
    for row in curation["bills"]:
        key = (row["session"], row["bill_no"])
        b = core[key]
        rcs = sorted(votes.get(key, []), key=lambda r: r["datetime"])
        disposition, stage = classify(b)
        snaps = vote_snapshot(rcs)
        best = None
        for s in snaps:
            if s["result"] == "Passed":
                pct = s["yeas"] / (s["yeas"] + s["nays"]) if (s["yeas"] + s["nays"]) else None
                if best is None or (pct or 0) > (best["yes_pct"] or 0):
                    best = {"chamber": s["chamber"], "yeas": s["yeas"], "nays": s["nays"],
                            "motion": s["motion"], "yes_pct": pct}
        bills.append({
            **row,
            "sponsors": parse_sponsors(b["sponsors_raw"]),
            "sponsors_raw": b["sponsors_raw"],
            "act_no": b["act_no"],
            "ratification_no": b.get("ratification_no"),
            "disposition": disposition,
            "stage": stage,
            "roll_call_count": len(rcs),
            "passage_votes": snaps,
            "best_passage_vote": best,
        })

    policy = [b for b in bills if b["relevance"] in ("core", "adjacent")]

    def succeeded(b):
        return b["disposition"] in ("Enacted", "Adopted")

    inventory = {
        "pass1_total": curation["counts"]["total_pass1"],
        "curated_total": len(bills),
        "by_relevance": curation["counts"]["by_relevance"],
        "policy_set": len(policy),
        "core_set": curation["counts"]["by_relevance"]["core"],
        "dispositions_core": {},
        "dispositions_policy": {},
        "first_committee_deaths_policy": 0,
        "chokepoint_committees": {},
        "note": ("Keyword-discovered, hand-curated set. Headline numbers use the policy set "
                 "(core + adjacent); context bills are audit-only."),
    }
    for b in bills:
        d = ("Enacted" if b["disposition"] == "Enacted"
             else "Adopted" if b["disposition"] == "Adopted" else "Did not pass")
        if b["relevance"] == "core":
            inventory["dispositions_core"][d] = inventory["dispositions_core"].get(d, 0) + 1
        if b["relevance"] in ("core", "adjacent"):
            inventory["dispositions_policy"][d] = inventory["dispositions_policy"].get(d, 0) + 1
            m = re.match(r"Died in its first committee \((.+)\)", b["stage"])
            if m:
                inventory["first_committee_deaths_policy"] += 1
                c = m.group(1)
                inventory["chokepoint_committees"][c] = inventory["chokepoint_committees"].get(c, 0) + 1

    sessions = []
    for sess in (123, 124, 125, 126):
        rows = [b for b in policy if b["session"] == sess]
        sessions.append({
            "session": sess, "label": SESSION_LABEL[sess],
            "bills_in_policy_set": len(rows),
            "enacted_or_adopted": sum(1 for b in rows if succeeded(b)),
            "core": sum(1 for b in rows if b["relevance"] == "core"),
            "core_enacted_or_adopted": sum(1 for b in rows if b["relevance"] == "core" and succeeded(b)),
        })

    lead_counts = {}
    for b in policy:
        if b["sponsors"]:
            lead = b["sponsors"][0]
            lead_counts.setdefault(lead, []).append(b["bill_key"])
    frequent = sorted(((n, len(ks), ks) for n, ks in lead_counts.items()),
                      key=lambda t: -t[1])
    people = {
        "note": ("Sponsors parsed from the official sponsor line; the first-listed member is "
                 "treated as lead. Party labels intentionally absent (no roster join fetched)."),
        "frequent_lead_sponsors": [
            {"name": n, "bills_led": c, "bill_keys": ks}
            for n, c, ks in frequent if c >= 3
        ],
    }

    high_support = []
    for b in bills:
        if not succeeded(b) and b["best_passage_vote"]:
            v = b["best_passage_vote"]
            if v["yes_pct"] and v["yes_pct"] > 0.5:
                high_support.append({
                    "bill_key": b["bill_key"], "title": b["title"],
                    "plain_topic": b["plain_topic"], "stage": b["stage"],
                    "chamber": v["chamber"], "yeas": v["yeas"], "nays": v["nays"],
                    "motion": v["motion"], "relevance": b["relevance"],
                })
    high_support.sort(key=lambda r: -(r["yeas"] / (r["yeas"] + r["nays"])))

    themes = []
    for t in curation["themes"]:
        rows = [b for b in bills if b["theme"] == t]
        if not rows:
            continue
        themes.append({
            "theme": t,
            "bills": len(rows),
            "enacted_or_adopted": sum(1 for b in rows if succeeded(b)),
            "bill_keys": [b["bill_key"] for b in rows],
        })

    xwalk = []
    for p in PROPOSALS:
        d = dict(CROSSWALK[p["id"]])
        d["proposal_id"] = p["id"]
        d["proposal_title"] = p["title"]
        xwalk.append(d)

    proviso = json.load(open(os.path.join(HERE, "proviso-curated.json")))

    pack = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "issue": "south-carolina-01-growth-infrastructure-roads",
        "sessions": sessions,
        "inventory": inventory,
        "themes": themes,
        "high_support_non_enactments": high_support,
        "people_signals": people,
        "proposal_crosswalk": xwalk,
        "proviso_crosswalk": {
            "note": proviso["note"],
            "cycles": [{"fiscal_year": c["fiscal_year"], "bill_no": c["bill_no"],
                        "enacted": c["enacted"],
                        "picked": [pv["caption"] for pv in c["provisos"]],
                        **({"gap_note": c["note"]} if not c["enacted"] else {})}
                       for c in proviso["cycles"]],
        },
        "data_limits": DATA_LIMITS,
        "bills": bills,
    }
    json.dump(pack, open(os.path.join(HERE, "evidence-pack.json"), "w"), indent=1)

    lines = ["# Evidence pack — Growth, Infrastructure, and Roads in South Carolina", ""]
    lines.append("Curated %d bills (of %d Pass 1 hits + 9 universe adds): %d core / %d adjacent / %d context."
                 % (len(bills), inventory["pass1_total"],
                    inventory["by_relevance"]["core"], inventory["by_relevance"]["adjacent"],
                    inventory["by_relevance"]["context"]))
    lines.append("")
    lines.append("## Sessions (policy set = core + adjacent)")
    for s in sessions:
        lines.append("- %s: %d bills, %d enacted (core: %d bills, %d enacted)"
                     % (s["label"], s["bills_in_policy_set"], s["enacted_or_adopted"],
                        s["core"], s["core_enacted_or_adopted"]))
    lines.append("")
    lines.append("## Themes")
    for t in themes:
        lines.append("- **%s** — %d bills, %d enacted" % (t["theme"], t["bills"], t["enacted_or_adopted"]))
    lines.append("")
    lines.append("## Chokepoint committees (first-committee deaths, policy set)")
    for c, n in sorted(inventory["chokepoint_committees"].items(), key=lambda kv: -kv[1]):
        lines.append("- %s: %d" % (c, n))
    lines.append("")
    lines.append("## High-support non-enactments (passage/reading votes >50%)")
    for r in high_support:
        lines.append("- %s %s — %s %d-%d (%s) — %s"
                     % (r["bill_key"], r["title"], r["chamber"], r["yeas"], r["nays"],
                        r["motion"], r["stage"]))
    lines.append("")
    lines.append("## Proposal crosswalk")
    for d in xwalk:
        lines.append("- **%s** (%s): coverage=%s; matched=%d; %s"
                     % (d["proposal_title"], d["proposal_id"], d["coverage"],
                        len(d["matched_bills"]), d["note"]))
    lines.append("")
    lines.append("## Frequent lead sponsors (3+ policy bills led)")
    for r in people["frequent_lead_sponsors"]:
        lines.append("- %s — %d bills (%s)" % (r["name"], r["bills_led"], ", ".join(r["bill_keys"])))
    lines.append("")
    lines.append("## Data limits")
    for d in DATA_LIMITS:
        lines.append("- " + d)
    lines.append("")
    lines.append("## Bills (curated)")
    lines.append("")
    lines.append("| Key | Title | Theme | Tier | Disposition | Stage | Best passage vote |")
    lines.append("|---|---|---|---|---|---|---|")
    for b in bills:
        bv = b["best_passage_vote"]
        bvs = "%s %d-%d" % (bv["chamber"], bv["yeas"], bv["nays"]) if bv else "—"
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (b["bill_key"], b["title"], b["theme"], b["relevance"],
                        b["disposition"], b["stage"], bvs))
    open(os.path.join(HERE, "evidence-pack.md"), "w").write("\n".join(lines) + "\n")
    print("evidence pack:", len(bills), "bills;", len(high_support), "high-support non-enactments")
    for s in sessions:
        print(" ", s["label"], "policy=%d enacted=%d" % (s["bills_in_policy_set"], s["enacted_or_adopted"]))
    print(" dispositions core:", inventory["dispositions_core"])
    print(" dispositions policy:", inventory["dispositions_policy"])
    print(" first-committee deaths (policy):", inventory["first_committee_deaths_policy"])
    print(" chokepoints:", dict(sorted(inventory["chokepoint_committees"].items(), key=lambda kv: -kv[1])[:6]))


if __name__ == "__main__":
    main()
