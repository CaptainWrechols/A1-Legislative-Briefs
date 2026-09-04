#!/usr/bin/env python3
"""Evidence Curator build for south-carolina-02-responsive-elected-leaders.

Combines curation-map.json (hand-reviewed set) with the prebuilt processed
artifacts (bills-core, bill-votes) into the evidence pack the Reality Mapper
and writers consume. Universe-sourced bills (the REACH Act civics family)
take their records and roll calls from sources/south-carolina/_universe/.
No scraping; local files only.

Outputs:
  working/south-carolina/responsive-elected-leaders/evidence-pack.json
  working/south-carolina/responsive-elected-leaders/evidence-pack.md
"""
import datetime
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "sources/south-carolina/responsive-elected-leaders")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")

SESSION_LABEL = {123: "123rd (2019-2020)", 124: "124th (2021-2022)",
                 125: "125th (2023-2024)", 126: "126th (2025-2026)"}

PROPOSALS = [
    {"id": "term-limits",
     "title": "Term limits / rotation rules for elected officials"},
    {"id": "campaign-finance-reform",
     "title": "Limits on money in politics / campaign finance reform"},
    {"id": "ranked-choice-voting",
     "title": "Ranked choice voting"},
    {"id": "independent-redistricting",
     "title": "Independent/nonpartisan redistricting commission"},
    {"id": "financial-disclosure",
     "title": "Better financial-disclosure and conflict-of-interest tracking (incl. PACs)"},
    {"id": "voter-civics-education",
     "title": "Better voter education / civics and neutral civic information tools"},
]

# Hand-reviewed crosswalk (bill keys verified in the curation map).
CROSSWALK = {
    "term-limits": {
        "matched_bills": ["123:H3023", "123:H3024", "123:H3166", "123:S268", "123:S269",
                          "123:S663", "123:S944", "123:S945", "124:H3257", "124:H3259",
                          "124:H3260", "124:H3663", "124:H3746", "124:S302", "124:S338",
                          "124:S339", "124:S384", "125:H3249", "125:H3250", "125:H3444",
                          "125:H3574", "125:S172", "125:S213", "125:S214", "126:H3744",
                          "126:H3745", "126:H4462", "126:H5360", "126:S590", "126:H3008"],
        "near_miss_bills": ["125:H4692", "126:H3102", "123:H3125", "123:S112",
                            "124:S133", "124:S141", "125:H3676"],
        "coverage": "substantial_attempts_zero_state_movement",
        "note": ("Thirty bills and resolutions in four sessions. Every state-level design - "
                 "constitutional amendments (direct caps of 2-6 terms, or authorizing the "
                 "General Assembly to set limits by law) and straight statutes - died in its "
                 "first Judiciary committee with no recorded vote. The only term-limits measure "
                 "that passed anything targets Congress, not the State House: H3008, the "
                 "Article V application for a congressional term limits convention, adopted by "
                 "the House in March 2025 and the Senate in May 2025 (29-14). The broader Convention of the "
                 "States application (which includes federal term limits) failed at the last "
                 "step twice (S133 in 2022, H3676 in 2024) before splitting into single-subject "
                 "applications that passed in 2025-26."),
    },
    "campaign-finance-reform": {
        "matched_bills": ["124:H4877", "126:S813", "123:S3", "124:S174", "126:S960",
                          "123:H4192", "123:H3097", "123:S231", "124:S306", "125:S199",
                          "123:S184", "123:S986", "124:S187", "124:S214", "125:S137",
                          "126:S84", "123:S210", "124:S189", "124:S250", "125:S159",
                          "126:S91", "124:H3522", "125:H4561", "125:H3242"],
        "near_miss_bills": ["123:H4333", "123:S800", "124:H3197", "125:H3474", "126:H3554",
                            "123:S537", "123:S192", "125:H4660", "126:H3517"],
        "coverage": "substantial_attempts_one_house_passage",
        "note": ("The lane citizens asked about - limiting money - exists mostly as disclosure "
                 "bills: dark-money ad disclosure (filed by Senate leadership three times), "
                 "contributor employer disclosure, bank-statement filing, and a corporate-"
                 "contribution ban. One bill in eight years got a floor vote: H4561 (campaign "
                 "funds for dependent care) passed the House 53-45 in 2024 and died in Senate "
                 "Judiciary. Note the direction of the contribution-limit bills actually filed: "
                 "all five would raise South Carolina's limits, not lower them. No bill "
                 "proposes lowering a limit; one (H3522) proposed public financing, for "
                 "Attorney General races only."),
    },
    "ranked-choice-voting": {
        "matched_bills": ["124:H5135", "125:H4022", "126:H3589", "125:H4591", "126:H3386"],
        "near_miss_bills": ["125:H3606", "126:H3552", "125:H4592", "126:H3318"],
        "coverage": "attempts_both_directions_zero_movement",
        "note": ("Both directions have been filed and neither has ever had a hearing: three "
                 "bills to allow ranked choice (instant runoff) voting in municipal/local "
                 "elections (2022, 2023, 2025) and two bills to ban ranked choice voting "
                 "statewide (2024, 2025). All five died in House Judiciary without a vote. "
                 "The adjacent runoff-abolition bills (plurality primaries) also never moved."),
    },
    "independent-redistricting": {
        "matched_bills": ["123:H3044", "123:S6", "123:S135", "124:H3279", "124:S561",
                          "125:H3173", "123:H3167", "123:H3390", "123:S249", "124:H4201",
                          "125:H3243", "123:H3432", "123:S254", "124:H4202", "125:H3245",
                          "123:H3054", "123:S230", "124:H4229", "124:S750", "125:H3069",
                          "125:H4222"],
        "near_miss_bills": ["124:H4493", "124:S865", "124:H4492", "126:H4717", "126:H5683"],
        "coverage": "substantial_attempts_zero_movement",
        "note": ("Twenty-one commission or criteria bills across the 123rd-125th sessions - "
                 "independent commissions by constitutional amendment, citizens commissions by "
                 "statute, and binding-criteria acts - and none ever received a hearing or "
                 "vote; all died in Judiciary committees. The legislature drew the actual maps "
                 "(Act 117 and Act 118 of 2021-22) on party-line-shaped votes. In May 2026 a "
                 "mid-decade congressional redraw (H5683) passed the House 74-37 and was "
                 "shelved on the Senate floor by a 26-18 vote to continue the bill. No "
                 "commission bill was filed in the 126th session - the first session without "
                 "one in this record."),
    },
    "financial-disclosure": {
        "matched_bills": ["126:H3570", "123:H4191", "123:S111", "123:S339", "124:S299",
                          "125:S169", "123:H3435", "123:S253", "124:S309", "125:S195",
                          "124:S548", "125:S395", "123:H3321", "124:S188", "125:S986",
                          "126:S75", "126:S70", "126:S1130", "123:S284", "124:S375",
                          "123:H4193", "125:H5181", "123:H3387", "123:H3579", "123:H4756"],
        "near_miss_bills": ["123:S932", "126:H3321", "124:H4876", "126:S632"],
        "coverage": "one_enactment_one_conference_death",
        "note": ("The most movement of any proposal. Enacted: S70, the School Board Ethics Act "
                 "(Act 191 of 2026, 39-2 and 109-4), after two earlier versions died. Nearly "
                 "enacted: H3570, the economic-interests disclosure rewrite, passed the House "
                 "102-0 and the Senate 40-0 in different versions and died in conference in "
                 "May 2026 - and a piece of it (naming the government body behind budget-paid "
                 "income) reappeared as FY 2026-27 budget proviso 117.219. Everything else - "
                 "tax-return disclosure, e-filing audits, special-purpose-district coverage, "
                 "ethics-fine ballot bars - died in Senate or House Judiciary without votes."),
    },
    "voter-civics-education": {
        "matched_bills": ["126:H3547", "124:S38", "123:S35", "123:H4296", "124:H3338"],
        "near_miss_bills": ["124:H4392"],
        "coverage": "thin_with_one_enactment",
        "note": ("A small but real lane with one law: the REACH Act (S38, Act 26 of 2021) "
                 "requires every public college student to study the founding documents; it "
                 "passed 45-0 and 91-12 on its second try after the 2019 version passed the "
                 "Senate and died in a House committee. The K-12 design citizens described - "
                 "a required middle-school civics unit with hands-on projects (H3547, 2025) - "
                 "sits in House Education without a vote. Civic-education money has moved "
                 "through the budget instead: a Clemson civic-engagement center study "
                 "(FY 2024-25 proviso 45.11) and $2.5 million for a USC civic leadership "
                 "center (FY 2026-27, in proviso 118.21). No bill proposes a neutral voter-"
                 "information tool."),
    },
}

DATA_LIMITS = [
    "The set is keyword-discovered from official full-text search plus a title/summary scan of the certified universe; it is a curated selection, not a proven-complete universe of accountability bills. Four REACH Act civics bills were hand-added from the certified universe because their text contains none of the issue's search terms.",
    "South Carolina publishes committee outcomes in bill histories but never committee vote tallies; no committee vote counts exist anywhere in this record and none may be implied.",
    "Party labels are not attached to sponsors or floor votes in this pack: the roster/ballot join was not fetched for this brief, so the brief makes no party claims.",
    "Floor roll-call counts are verbatim from the chamber vote-history tables; motions to table, to adopt amendments, or to continue are procedural, and only passage/reading/adoption votes are used as support signals. The Senate's 26-18 vote on H5683 was a motion to continue (shelve) the bill, not a vote on passage.",
    "Article V applications and internal rule changes travel as resolutions: concurrent resolutions (H3008, H3007) take effect when both chambers adopt them and never go to the governor; House resolutions (H4692) bind only the House.",
    "For non-enacted 126th-session (2025-2026) bills, disposition is 'did not pass' as of the collection date (2026-08-26), after the regular session's final regular calendar.",
    "FY 2020-21 has no enacted Part IB proviso set (COVID continuing resolution), so budget-proviso coverage runs FY 2021-22 through FY 2026-27.",
    "The six Phase 2 constituent proposals are Forum process input from Community Conversations (labels [P-...]), not verified facts.",
]

# Stage overrides for bills whose histories the generic classifier cannot
# describe accurately (verified against full action lists).
STAGE_OVERRIDES = {
    (126, "H3570"): ("Did not pass (session ended)",
                     "Passed the House 102-0 and the Senate 40-0 in different versions; died in conference"),
    (126, "H5683"): ("Did not pass (session ended)",
                     "Passed the House 74-37; shelved on the Senate floor by a 26-18 vote to continue"),
    (124, "S133"):  ("Did not pass",
                     "Passed both chambers in different forms; died when the House never took up the conference report"),
    (125, "H3676"): ("Did not pass",
                     "Passed the House 68-30; died on the Senate calendar after a favorable committee report"),
    (123, "H3125"): ("Did not pass",
                     "Reported favorably; died on the House calendar when COVID ended the session"),
    (124, "H4492"): ("Did not pass",
                     "Reported out of House Judiciary, then recommitted (the congressional maps moved through S865 instead)"),
    (126, "H3007"): ("Adopted", "Adopted (House March 2025; Senate January 2026); resolutions never go to the governor"),
    (126, "H3008"): ("Adopted", "Adopted (House March 2025; Senate May 2025, 29-14); resolutions never go to the governor"),
    (123, "S35"):   ("Did not pass",
                     "Passed the Senate; died in House Education and Public Works Committee"),
}

PASSAGE_RE = re.compile(
    r"passage of bill|3rd reading|third reading|2nd reading|second reading|ratif"
    r"|adopt concurrent resolution|adopt the resolution|conference report"
    r"|concur in senate amendments", re.I)
PROCEDURAL_RE = re.compile(r"\btable\b|amendment number|adopt amendment|to continue|rule \d|adjourn|special order|reconsider|recall|order of the day|waive|suspend", re.I)


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
    crossed = any(re.search(r"Introduced and read first time|Introduced \(|Referred to Committee",
                            a["action"]) for a in second_acts)
    if crossed:
        if any("Second Reading Failed" in a["action"] for a in second_acts):
            return (died, "Passed the %s; failed on the %s floor" % (origin, second))
        committee = _committee(second_acts)
        if committee:
            return (died, "Passed the %s; died in %s %s Committee" %
                    (origin, second, committee))
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
            "ratification_no": b["ratification_no"],
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
        "note": ("Keyword-discovered, hand-curated set. Headline numbers use the core set; "
                 "adjacent bills appear in appendices; context bills are audit-only. "
                 "'Adopted' = resolution adopted by both chambers (no governor step)."),
    }
    for b in bills:
        d = ("Enacted" if b["disposition"] == "Enacted"
             else "Adopted" if b["disposition"] == "Adopted" else "Did not pass")
        if b["relevance"] == "core":
            inventory["dispositions_core"][d] = inventory["dispositions_core"].get(d, 0) + 1
        if b["relevance"] in ("core", "adjacent"):
            inventory["dispositions_policy"][d] = inventory["dispositions_policy"].get(d, 0) + 1

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
        "issue": "south-carolina-02-responsive-elected-leaders",
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
                        "picked": [pv["display_caption"] for pv in c["provisos"]],
                        **({"gap_note": c["note"]} if not c["enacted"] else {})}
                       for c in proviso["cycles"]],
        },
        "data_limits": DATA_LIMITS,
        "bills": bills,
    }
    json.dump(pack, open(os.path.join(HERE, "evidence-pack.json"), "w"), indent=1)

    lines = ["# Evidence pack — Responsive Elected Leaders in South Carolina", ""]
    lines.append("Curated %d bills (of %d Pass 1 hits + 4 universe adds): %d core / %d adjacent / %d context."
                 % (len(bills), inventory["pass1_total"],
                    inventory["by_relevance"]["core"], inventory["by_relevance"]["adjacent"],
                    inventory["by_relevance"]["context"]))
    lines.append("")
    lines.append("## Sessions (policy set = core + adjacent)")
    for s in sessions:
        lines.append("- %s: %d bills, %d enacted/adopted (core: %d bills, %d enacted/adopted)"
                     % (s["label"], s["bills_in_policy_set"], s["enacted_or_adopted"],
                        s["core"], s["core_enacted_or_adopted"]))
    lines.append("")
    lines.append("## Themes")
    for t in themes:
        lines.append("- **%s** — %d bills, %d enacted/adopted" % (t["theme"], t["bills"], t["enacted_or_adopted"]))
    lines.append("")
    lines.append("## High-support non-enactments (passage/adoption votes >50%)")
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
        print(" ", s["label"], s)
    print(" dispositions core:", inventory["dispositions_core"])
    print(" dispositions policy:", inventory["dispositions_policy"])


if __name__ == "__main__":
    main()
