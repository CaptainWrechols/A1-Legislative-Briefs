#!/usr/bin/env python3
"""Evidence Curator build for south-carolina-03-rising-cost-of-living.

Combines curation-map.json (hand-reviewed set) with the prebuilt processed
artifacts (bills-core, bill-votes) into the evidence pack the Reality Mapper
and writers consume. The two universe-added financial-education bills (which
matched no Pass 1 term) are loaded from _universe with their (zero) roll
calls joined from the universe roll-call tables. No scraping; local files
only.

Outputs:
  working/south-carolina/rising-cost-of-living/evidence-pack.json
  working/south-carolina/rising-cost-of-living/evidence-pack.md
"""
import datetime
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(ROOT, "sources/south-carolina/rising-cost-of-living")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")

SESSION_LABEL = {123: "123rd (2019-2020)", 124: "124th (2021-2022)",
                 125: "125th (2023-2024)", 126: "126th (2025-2026)"}

PROPOSALS = [
    {"id": "utility-transparency",
     "title": "Greater transparency into utility rates and legislator/utility financial ties"},
    {"id": "utility-competition",
     "title": "Open the utility market / end monopoly / lower competition barriers"},
    {"id": "financial-education",
     "title": "Personal budgeting and financial education"},
    {"id": "reduce-property-vehicle-taxes",
     "title": "Reduce or eliminate property and vehicle taxes"},
]

# Hand-reviewed crosswalk (bill keys verified in the curation map).
CROSSWALK = {
    "utility-transparency": {
        "matched_bills": ["123:H4260", "124:H3683", "124:H4149", "125:H3614",
                          "124:S344", "125:S218", "123:H3642", "123:H3641",
                          "123:H4531", "123:H4194", "123:H4776", "123:H4809",
                          "123:S947", "123:S996", "125:S749", "126:S271",
                          "126:H4402", "125:S779", "125:S909", "126:H5283",
                          "126:H5282", "124:H3194", "123:H4287", "126:S51"],
        "near_miss_bills": ["126:H3309", "123:S1129", "126:H3928", "126:S446",
                            "123:S334", "124:S301", "123:H5232"],
        "coverage": "substantial_attempts_partial_enactment",
        "note": ("A rich, live lane. The exact citizen concern — financial ties between "
                 "legislators and utilities — was in the 2019 Ratepayer Protection Act (H4260), "
                 "which banned utilities from giving campaign contributions or anything of value "
                 "to the legislators' panel that screens utility regulators; it passed the House "
                 "105-1 and died in Senate Judiciary, as did the narrower 2023 whistleblower "
                 "version (114-0). What did become law: Santee Cooper oversight (Act 90 of 2021), "
                 "restarted PSC elections (Acts 74/75 of 2025), and public-witness rights at the "
                 "PSC inside the 2025 Energy Security Act."),
    },
    "utility-competition": {
        "matched_bills": ["123:H4940", "123:S998", "126:H5439", "126:H5440",
                          "126:S878", "126:H5525"],
        "near_miss_bills": ["123:H3344", "124:S439", "124:S751", "126:S12"],
        "coverage": "study_enacted_bills_never_moved",
        "note": ("The state officially studied this: the Electricity Market Reform Measures "
                 "Study Committee (Act 187 of 2020) was created by law, with an independent "
                 "expert consultant, after the House passed it 81-31. Every bill that would "
                 "actually open the retail market — H5439, H5440, S878, H5525 — was filed in "
                 "2026 and died in its first committee without a vote."),
    },
    "financial-education": {
        "matched_bills": ["123:S15", "123:H4149", "123:H3199", "124:S16",
                          "124:S405", "124:H3116", "124:H3022", "124:H4582",
                          "125:S732"],
        "near_miss_bills": [],
        "coverage": "enacted_via_budget_proviso_and_regulation",
        "note": ("The one proposal that is already policy — just not through a bill. The "
                 "graduation-requirement bills (S15, H4149, H3199, S16, S405, H3116) never "
                 "finished: S16 passed both chambers in differing versions and died in "
                 "conference in 2022. That same year, FY 2022-23 budget proviso 1.101 ordered "
                 "the State Board of Education to write the half-credit personal finance "
                 "requirement into regulation; Regulation Document 5130 (amending R.43-234) "
                 "took effect May 26, 2023 and applies beginning with the 2023-24 freshman "
                 "class (Class of 2027). South Carolina has also had a financial-literacy "
                 "instruction statute since 2005 (Section 59-29-410)."),
    },
    "reduce-property-vehicle-taxes": {
        "matched_bills": ["126:H3378", "126:H3424", "125:H3127", "126:S768",
                          "123:H3122", "123:H3207", "123:H3736", "123:H4818",
                          "123:S565", "124:S12", "125:S12", "124:H3386",
                          "125:H3086", "125:H3778", "123:H3332", "123:H3687",
                          "123:H4994", "123:S910", "124:H3108", "124:H3452",
                          "124:H4197", "124:H4222", "125:H3423", "125:H3927",
                          "125:H5264", "126:H3380", "126:H3419", "126:H3427",
                          "126:H3511", "126:H3742", "126:H4599", "126:H4690",
                          "126:S223", "126:H5014", "123:H4564", "124:H4511",
                          "126:H3410", "125:S943", "126:H4138", "123:H5111",
                          "125:S38", "126:S866", "123:S171", "124:S233",
                          "125:H3116", "126:H3841", "123:H3630", "124:H3482"],
        "near_miss_bills": ["124:S1087", "126:H4216", "125:H3809", "125:H4910",
                            "124:H3674", "126:S439"],
        "coverage": "many_attempts_narrow_enactments_plus_budget_relief",
        "note": ("The most-filed lane in this record, with the narrowest wins. Full "
                 "elimination was proposed once (H3378, 2025: every property tax, with state "
                 "reimbursement) and died in its first committee. More than twenty bills to "
                 "raise the $50,000 senior/disabled homestead exemption died the same way. "
                 "What passed instead: targeted fixes (disabled veterans, surviving spouses, "
                 "estates), a municipal sales-tax-for-property-relief option (S866, Act 228 of "
                 "2026), and one-year relief inside the budget — an extra $25,000 homestead "
                 "exemption (FY 2026-27 proviso 117.220) and the accelerated income tax cut "
                 "(proviso 117.208 / 117.191). On vehicle taxes, no bill proposes statewide "
                 "elimination; the broadest attempt (H5014, 2026: exempt one car for seniors) "
                 "died in House Ways and Means."),
    },
}

DATA_LIMITS = [
    "The set is keyword-discovered from official full-text search plus a title/summary scan of the certified universe; it is a curated selection, not a proven-complete universe of cost-of-living bills. Two financial-education bills that matched no search term were added from a hand full-text scan of the universe and are marked in the curation map.",
    "This is the broadest of the four SC issues (housing, utilities, taxes, insurance). The curation kept 256 bills of 6,814 Pass 1 hits; the exclusion rules in the curation map say what was pruned (health-insurance mandates, 'parental' false hits on 'rent', utility-terrain vehicles, industry tax bills, and similar).",
    "South Carolina publishes committee outcomes in bill histories but never committee vote tallies; no committee vote counts exist anywhere in this record and none may be implied.",
    "Party labels are not attached to sponsors or floor votes in this pack: the roster/ballot join was not fetched for this brief, so the brief makes no party claims.",
    "Floor roll-call counts are verbatim from the chamber vote-history tables; only passage/reading votes are used as support signals.",
    "For non-enacted 126th-session (2025-2026) bills, disposition is 'did not pass' as of the collection date (2026-08-27), after the regular session's final regular calendar.",
    "FY 2020-21 has no enacted Part IB proviso set (COVID continuing resolution), so budget-proviso coverage runs FY 2021-22 through FY 2026-27.",
    "The financial-literacy graduation requirement's current status (Regulation 43-234 as amended by Document 5130, effective May 26, 2023) was verified against the State Register and the State Board of Education's published regulation, since regulation approval joint resolutions can stall while the regulation still takes effect under the APA's review clock.",
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
    crossed = any(re.search(r"Introduced.{0,15}read first time|Referred to Committee",
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
    if re.search(r"Recommitted to Committee", joined) and re.search(r"Read second time", joined):
        where = ("%s %s Committee" % (origin, committee)) if committee else "committee"
        return (died, "Advanced in its own chamber; recommitted to %s" % where)
    if re.search(r"Read second time", joined):
        return (died, "Advanced in its own chamber; never finished passage there")
    m = re.search(r"Recommitted to Committee on ([^(]+?)\s*\(", joined)
    if m:
        return (died, "Placed on the %s calendar; recommitted to %s %s Committee" %
                (origin, origin, m.group(1).strip()))
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


def load_universe_bill(session, bill_no):
    path = os.path.join(UNIVERSE, str(session), "bills.jsonl.gz")
    with gzip.open(path) as f:
        for line in f:
            b = json.loads(line)
            if b["bill_no"] == bill_no:
                b["chamber"] = "H" if bill_no.startswith("H") else "S"
                b.setdefault("act_no", None)
                b.setdefault("ratification_no", None)
                return b
    raise SystemExit("universe bill not found: %s:%s" % (session, bill_no))


def load_universe_rollcalls(session, bill_no):
    path = os.path.join(UNIVERSE, str(session), "rollcalls.json")
    d = json.load(open(path))
    return [r for r in d["roll_calls"] if r.get("bill_no") == bill_no]


def main():
    curation = json.load(open(os.path.join(HERE, "curation-map.json")))
    core = {(b["session"], b["bill_no"]): b
            for b in json.load(open(os.path.join(SRC, "processed/bills-core.json")))["bills"]}
    votes = {(v["session"], v["bill_no"]): v
             for v in json.load(open(os.path.join(SRC, "processed/bill-votes.json")))["bills"]}

    bills = []
    for row in curation["bills"]:
        key = (row["session"], row["bill_no"])
        if key in core:
            b = core[key]
            rcs = votes.get(key, {}).get("roll_calls", [])
        else:
            b = load_universe_bill(*key)
            rcs = load_universe_rollcalls(*key)
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
        "note": ("Keyword-discovered, hand-curated set. Headline numbers use the core set "
                 "(the four constituent proposals' lanes); adjacent bills appear in "
                 "appendices; context bills are audit-only."),
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
        "issue": "south-carolina-03-rising-cost-of-living",
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

    lines = ["# Evidence pack — Rising Cost of Living in South Carolina", ""]
    lines.append("Curated %d bills (of %d Pass 1 hits, plus 2 universe adds): %d core / %d adjacent / %d context."
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
