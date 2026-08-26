#!/usr/bin/env python3
"""Evidence Curator build for south-carolina-04-slow-wage-growth.

Combines curation-map.json (hand-reviewed set) with the prebuilt processed
artifacts (bills-core, bill-votes) into the evidence pack the Reality Mapper
and writers consume. No scraping; local files only.

Outputs:
  working/south-carolina/slow-wage-growth/evidence-pack.json
  working/south-carolina/slow-wage-growth/evidence-pack.md
"""
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "sources/south-carolina/slow-wage-growth")

SESSION_LABEL = {123: "123rd (2019-2020)", 124: "124th (2021-2022)",
                 125: "125th (2023-2024)", 126: "126th (2025-2026)"}

PROPOSALS = [
    {"id": "age-bracketed-minimum-wage",
     "title": "Age-bracketed minimum wage with a separate youth wage"},
    {"id": "workforce-development",
     "title": "Apprenticeships, career pathways, and technical training"},
    {"id": "raise-minimum-wage",
     "title": "Raise the minimum wage / livable wage"},
    {"id": "employer-living-wage-incentives",
     "title": "Government incentives/bonuses for employers paying a living wage"},
]

# Hand-reviewed crosswalk (bill keys verified in the curation map).
CROSSWALK = {
    "age-bracketed-minimum-wage": {
        "matched_bills": [],
        "near_miss_bills": ["124:S533"],
        "coverage": "none",
        "note": ("No bill in the 2019-2026 record proposes a youth wage, training wage, or any "
                 "age-bracketed minimum wage; the search terms 'youth wage' and 'training wage' "
                 "return zero hits in all bill text. The nearest action runs the other way: "
                 "S533 (2022) banned subminimum wages for workers with disabilities."),
    },
    "workforce-development": {
        "matched_bills": ["123:H3576", "124:H3144", "123:H3759", "123:S419", "125:H3726",
                          "125:H3605", "125:S557", "124:H4766", "123:H4022", "123:S650",
                          "123:H3757", "124:H3611", "125:H4060", "125:S461", "126:H3197",
                          "126:H3863", "126:H4984", "126:H3225", "125:S859", "126:H3479",
                          "126:S272", "124:H3348", "125:H4600"],
        "near_miss_bills": ["123:H4414", "124:H3470", "125:H3326"],
        "coverage": "substantial",
        "note": ("The most active and most successful lane in this record: SC WINS scholarships, "
                 "the Earn and Learn Act, a bigger apprenticeship tax credit, and the Statewide "
                 "Education and Workforce Development Act all became law between 2021 and 2025."),
    },
    "raise-minimum-wage": {
        "matched_bills": ["123:H3114", "123:H3217", "123:H3395", "123:H3467", "123:H4154",
                          "123:S147", "123:S149", "124:H3018", "124:H3184", "124:H3341",
                          "124:H3480", "124:H3675", "124:S159", "124:S343", "124:S633",
                          "124:S634", "125:H3805", "125:H5187", "125:S216", "125:S28",
                          "125:S291", "126:H3226", "126:H3735", "126:H3809"],
        "near_miss_bills": ["124:S533", "125:S1001"],
        "coverage": "substantial_attempts_zero_movement",
        "note": ("Filed every session (24 bills, $10-$17 an hour, plus two advisory-referendum "
                 "resolutions and a constitutional amendment) and never received a recorded vote "
                 "at any stage; every one died in its first committee. The only wage floors that "
                 "became law were for specific groups (disability subminimum ban 2022; inmate "
                 "private-industry floor 2024)."),
    },
    "employer-living-wage-incentives": {
        "matched_bills": ["126:H4603", "124:S398", "126:H4245"],
        "near_miss_bills": ["125:S557", "125:H4087", "124:S901", "126:H4174",
                            "126:H5471", "126:S1118", "124:H4252"],
        "coverage": "thin",
        "note": ("A direct precedent exists: H4603 (2026), the Small Business Livable Wage Tax "
                 "Credit Act, sits in House Ways and Means without a vote. The adjacent machinery "
                 "is well established: the state already runs wage-linked employer incentives "
                 "(job development credits, apprenticeship credit), and those pass routinely "
                 "inside larger tax bills."),
    },
}

DATA_LIMITS = [
    "The set is keyword-discovered from official full-text search plus a title/summary scan of the certified universe; it is a curated selection, not a proven-complete universe of wage-related bills.",
    "South Carolina publishes committee outcomes in bill histories but never committee vote tallies; no committee vote counts exist anywhere in this record and none may be implied.",
    "Party labels are not attached to sponsors or floor votes in this pack: the roster/ballot join was not fetched for this brief, so the brief makes no party claims.",
    "Floor roll-call counts are verbatim from the chamber vote-history tables; motions labeled 'to lay on the table' or 'to adopt amendment' are procedural, and only passage/reading votes are used as support signals.",
    "For non-enacted 126th-session (2025-2026) bills, disposition is 'did not pass' as of the collection date (2026-08-26), after the regular session's final regular calendar.",
    "FY 2020-21 has no enacted Part IB proviso set (COVID continuing resolution), so budget-proviso coverage runs FY 2021-22 through FY 2026-27.",
    "The four Phase 2 constituent proposals are Forum process input from Community Conversations (labels [P-...]), not verified facts.",
]


def parse_sponsors(raw):
    if not raw:
        return []
    s = raw.replace("Reps.", "").replace("Rep.", "").replace("Senators", "").replace("Senator", "")
    parts = [p.strip() for p in re.split(r",| and ", s) if p.strip()]
    return parts


def _committee(actions):
    for a in actions:
        m = re.match(r"Referred to Committee on (.+?)(?:\s*\(|$)", a["action"])
        if m:
            return m.group(1).strip()
    return None


def classify(b, roll_calls):
    """Return (disposition, stage_plain)."""
    acts = [a["action"] for a in b["actions"]]
    joined = " || ".join(acts)
    if b["act_no"]:
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
    crossed = any(re.search(r"Introduced and read first time|Referred to Committee",
                            a["action"]) for a in second_acts)
    if crossed:
        if any("Second Reading Failed" in a["action"] for a in second_acts):
            return (died, "Passed the %s; failed on the %s floor" % (origin, second))
        committee = _committee(second_acts)
        if committee:
            return (died, "Passed the %s; died in %s %s Committee" %
                    (origin, second, committee))
        return (died, "Passed the %s; died in the %s" % (origin, second))
    # never left origin chamber
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
    """Best passage-type floor votes per chamber (verbatim counts)."""
    keep = []
    for rc in roll_calls:
        motion = rc["motion"].lower()
        if re.search(r"passage of bill|3rd reading|third reading|2nd reading|second reading|ratif", motion):
            keep.append({
                "chamber": rc["chamber"], "motion": rc["motion"],
                "yeas": rc["yeas"], "nays": rc["nays"], "result": rc["result"],
                "datetime": rc["datetime"], "ballot_pdf_key": rc["ballot_pdf_key"],
            })
    return keep


def main():
    curation = json.load(open(os.path.join(HERE, "curation-map.json")))
    core = {(b["session"], b["bill_no"]): b
            for b in json.load(open(os.path.join(SRC, "processed/bills-core.json")))["bills"]}
    votes = {(v["session"], v["bill_no"]): v
             for v in json.load(open(os.path.join(SRC, "processed/bill-votes.json")))["bills"]}

    bills = []
    for row in curation["bills"]:
        key = (row["session"], row["bill_no"])
        b = core[key]
        rcs = votes.get(key, {}).get("roll_calls", [])
        disposition, stage = classify(b, rcs)
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
    inventory = {
        "pass1_total": curation["counts"]["total_pass1"],
        "curated_total": len(bills),
        "by_relevance": curation["counts"]["by_relevance"],
        "policy_set": len(policy),
        "core_set": curation["counts"]["by_relevance"]["core"],
        "dispositions_core": {},
        "dispositions_policy": {},
        "note": ("Keyword-discovered, hand-curated set. Headline numbers use the core set; "
                 "adjacent bills appear in appendices; context bills are audit-only."),
    }
    for b in bills:
        if b["relevance"] == "core":
            d = "Enacted" if b["disposition"] == "Enacted" else "Did not pass"
            inventory["dispositions_core"][d] = inventory["dispositions_core"].get(d, 0) + 1
        if b["relevance"] in ("core", "adjacent"):
            d = "Enacted" if b["disposition"] == "Enacted" else "Did not pass"
            inventory["dispositions_policy"][d] = inventory["dispositions_policy"].get(d, 0) + 1

    sessions = []
    for sess in (123, 124, 125, 126):
        rows = [b for b in policy if b["session"] == sess]
        sessions.append({
            "session": sess, "label": SESSION_LABEL[sess],
            "bills_in_policy_set": len(rows),
            "enacted": sum(1 for b in rows if b["disposition"] == "Enacted"),
            "core": sum(1 for b in rows if b["relevance"] == "core"),
            "core_enacted": sum(1 for b in rows if b["relevance"] == "core" and b["disposition"] == "Enacted"),
        })

    # people signals: frequent first-named (lead) sponsors in policy set
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
        if b["disposition"] != "Enacted" and b["best_passage_vote"]:
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
            "enacted": sum(1 for b in rows if b["disposition"] == "Enacted"),
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
        "issue": "south-carolina-04-slow-wage-growth",
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

    # human skim
    lines = ["# Evidence pack — Slow Wage Growth in South Carolina", ""]
    lines.append("Curated %d bills (of %d Pass 1 hits): %d core / %d adjacent / %d context."
                 % (len(bills), inventory["pass1_total"],
                    inventory["by_relevance"]["core"], inventory["by_relevance"]["adjacent"],
                    inventory["by_relevance"]["context"]))
    lines.append("")
    lines.append("## Sessions (policy set = core + adjacent)")
    for s in sessions:
        lines.append("- %s: %d bills, %d enacted (core: %d bills, %d enacted)"
                     % (s["label"], s["bills_in_policy_set"], s["enacted"], s["core"], s["core_enacted"]))
    lines.append("")
    lines.append("## Themes")
    for t in themes:
        lines.append("- **%s** — %d bills, %d enacted" % (t["theme"], t["bills"], t["enacted"]))
    lines.append("")
    lines.append("## High-support non-enactments (passage votes >50%)")
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


if __name__ == "__main__":
    main()
