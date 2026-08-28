#!/usr/bin/env python3
"""Appendix Builder (data-driven parts) for south-carolina-02-responsive-elected-leaders.

Generates appendices A (bills overview), C (votes and support), D (sponsors),
and E (bill path details) from evidence-pack.json so every table is exact.
B, F, G, H, I, and README are authored by hand alongside.
"""
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
APPX = os.path.join(ROOT, "briefs/south-carolina/responsive-elected-leaders/citizen-v2/appendices")
SRC = os.path.join(ROOT, "sources/south-carolina/responsive-elected-leaders")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")

SESSION_YEARS = {123: "2019-20", 124: "2021-22", 125: "2023-24", 126: "2025-26"}

os.makedirs(APPX, exist_ok=True)
pack = json.load(open(os.path.join(HERE, "evidence-pack.json")))
core = {(b["session"], b["bill_no"]): b
        for b in json.load(open(os.path.join(SRC, "processed/bills-core.json")))["bills"]}

# universe-sourced bills (REACH Act family)
for sess, bns in {123: {"S35", "H4296"}, 124: {"S38", "H3338"}}.items():
    with gzip.open(os.path.join(UNIVERSE, str(sess), "bills.jsonl.gz"), "rt") as f:
        for line in f:
            b = json.loads(line)
            if b["bill_no"] in bns:
                b.setdefault("act_no", None)
                core[(sess, b["bill_no"])] = b

TIER_LABEL = {"core": "Core", "adjacent": "Adjacent", "context": "Context"}
RESULT = {"Enacted": "Became law", "Adopted": "Adopted (resolution)"}


def esc(s):
    return s.replace("|", "/")


def result(b):
    return RESULT.get(b["disposition"], "Did not pass")


# ---------------------------------------------------------------- Appendix A
lines = ["# Appendix A — Bills overview", ""]
lines.append("One row per bill in the curated set (189 bills, hand-reviewed from "
             "5,548 keyword hits plus four universe additions). *Tier*: Core bills are "
             "the headline set for the six citizen proposals plus the ethics/open-"
             "government accountability agenda; Adjacent bills are the same lanes but "
             "narrower, procedural, or federal-target; Context bills are kept for audit "
             "only. *Result*: what finally happened — 'Adopted (resolution)' means both "
             "chambers adopted a measure that never goes to the governor. Lead sponsor "
             "is the first member on the official sponsor line; party labels are "
             "intentionally not shown (see Appendix F).")
lines.append("")
for theme in [t["theme"] for t in pack["themes"]]:
    rows = [b for b in pack["bills"] if b["theme"] == theme]
    lines.append("## %s" % theme)
    lines.append("")
    lines.append("| Session | Bill | What it tried (plain words) | Tier | Result | Where it stopped or finished |")
    lines.append("|---|---|---|---|---|---|")
    for b in sorted(rows, key=lambda r: (r["session"], r["bill_no"])):
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            SESSION_YEARS[b["session"]], b["bill_no"], esc(b["plain_topic"]),
            TIER_LABEL[b["relevance"]], result(b), esc(b["stage"])))
    lines.append("")
    lines.append("<!-- pdf-page-break -->")
    lines.append("")
open(os.path.join(APPX, "A-bills-overview.md"), "w").write("\n".join(lines[:-2]) + "\n")

# ---------------------------------------------------------------- Appendix C
lines = ["# Appendix C — Votes and support", ""]
lines.append("Every floor passage/adoption-type roll call recorded for bills in the "
             "curated set, verbatim from the chamber vote histories. South Carolina "
             "never publishes committee vote tallies, so committee stops have no counts "
             "anywhere. Procedural motions (tabling, amendments, motions to continue) "
             "are excluded here; the full roll-call list per bill is in the source "
             "data. The failed 23–86 House vote on H3570 was a vote against concurring "
             "in Senate amendments — a version dispute, not a vote against the bill's "
             "own House version, which had passed 102–0.")
lines.append("")
lines.append("## Passage and adoption votes")
lines.append("")
lines.append("| Session | Bill | Chamber | Motion | Yes | No | Yes% | Outcome |")
lines.append("|---|---|---|---|---|---|---|---|")
for b in sorted(pack["bills"], key=lambda r: (r["session"], r["bill_no"])):
    for s in b["passage_votes"]:
        tot = s["yeas"] + s["nays"]
        pct = ("%.0f%%" % (100.0 * s["yeas"] / tot)) if tot else "—"
        motion = s["motion"]
        if ")" in motion:
            motion = motion.rsplit(")", 1)[-1].strip() or motion
        lines.append("| %s | %s | %s | %s | %d | %d | %s | %s |" % (
            SESSION_YEARS[b["session"]], b["bill_no"], s["chamber"], esc(motion),
            s["yeas"], s["nays"], pct, s["result"]))
lines.append("")
lines.append("<!-- pdf-page-break -->")
lines.append("")
lines.append("## High support, not enacted")
lines.append("")
lines.append("Measures that won a passage or adoption vote with more than 50% support "
             "and still did not finish. A late-stage death is often a timing or process "
             "story, not a recorded 'no' — though the Senate's 26–18 motion to continue "
             "H5683 and the House's 23–86 non-concurrence on H3570 are recorded "
             "resistance to a specific version.")
lines.append("")
lines.append("| Session | Bill | What it tried | Best vote | Where it ended |")
lines.append("|---|---|---|---|---|")
for r in pack["high_support_non_enactments"]:
    sess = int(r["bill_key"].split(":")[0])
    lines.append("| %s | %s | %s | %s %d–%d | %s |" % (
        SESSION_YEARS[sess], r["bill_key"].split(":")[1], esc(r["plain_topic"]),
        r["chamber"], r["yeas"], r["nays"], esc(r["stage"])))
lines.append("")
open(os.path.join(APPX, "C-votes-and-support.md"), "w").write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- Appendix D
lines = ["# Appendix D — Sponsors and people", ""]
lines.append("Sponsors come verbatim from each bill's official sponsor line; the first "
             "member listed is treated as the lead. Party labels are intentionally not "
             "shown: this dataset does not include a roster join, and the product rules "
             "bar party claims without one (see Appendix F).")
lines.append("")
lines.append("## Frequent lead sponsors (3+ bills in the policy set)")
lines.append("")
lines.append("| Lead sponsor | Bills led | Which bills |")
lines.append("|---|---|---|")
for r in pack["people_signals"]["frequent_lead_sponsors"]:
    keys = ", ".join("%s %s" % (SESSION_YEARS[int(k.split(":")[0])], k.split(":")[1])
                     for k in r["bill_keys"])
    lines.append("| %s | %d | %s |" % (r["name"], r["bills_led"], keys))
lines.append("")
lines.append("<!-- pdf-page-break -->")
lines.append("")
lines.append("## Sponsor line per bill (policy set)")
lines.append("")
lines.append("| Session | Bill | Sponsor line (verbatim) |")
lines.append("|---|---|---|")
for b in sorted(pack["bills"], key=lambda r: (r["session"], r["bill_no"])):
    if b["relevance"] == "context":
        continue
    raw = b["sponsors_raw"] or "—"
    if len(raw) > 220:
        raw = raw[:217] + "..."
    lines.append("| %s | %s | %s |" % (SESSION_YEARS[b["session"]], b["bill_no"], esc(raw)))
lines.append("")
open(os.path.join(APPX, "D-sponsors-and-people.md"), "w").write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- Appendix E
KEY_BILLS = ["126:H3570", "126:S70", "126:H3008", "124:S38", "123:S35", "125:H4561",
             "124:S133", "125:H3676", "126:H5683", "124:H4493", "124:S865",
             "124:S499", "126:H3547", "123:H3125", "126:S813"]
lines = ["# Appendix E — Bill path details", ""]
lines.append("Milestone paths for the measures the front brief leans on most. Dates and "
             "actions are from the official bill histories; routine steps (sponsor "
             "additions, scrivener corrections) are omitted.")
lines.append("")
by_key = {b["bill_key"]: b for b in pack["bills"]}
KEEP_RE = re.compile(r"Introduced|Referred to Committee|Committee report|Read second|"
                     r"Read third|Roll call|Ratified|Signed|Veto|conference|concurrence|"
                     r"Non-concurrence|Second Reading Failed|Special order|returned to|"
                     r"Adopted|Recalled from|Recommitted|Continued|Polled out|Debate adjourned until Wed., 5-13-20",
                     re.IGNORECASE)
for key in KEY_BILLS:
    b = by_key[key]
    cb = core[(b["session"], b["bill_no"])]
    lines.append("## %s %s — %s" % (SESSION_YEARS[b["session"]], b["bill_no"], esc(b["title"])))
    lines.append("")
    lines.append("*%s* — %s" % (esc(b["plain_topic"]),
                                "Became law (Act %s)" % b["act_no"].lstrip("A") if b["act_no"] else esc(b["stage"])))
    lines.append("")
    lines.append("| Date | Chamber | Action |")
    lines.append("|---|---|---|")
    for a in cb["actions"]:
        if KEEP_RE.search(a["action"]):
            act = a["action"].split("(")[0].strip()
            lines.append("| %s | %s | %s |" % (a["date"], a["body"] or "—", esc(act)))
    for g in cb.get("governor_actions", []):
        lines.append("| %s | Governor | %s |" % (g.get("date", "—"), esc(g.get("action", ""))))
    lines.append("")
open(os.path.join(APPX, "E-bill-path-details.md"), "w").write("\n".join(lines) + "\n")

print("wrote A, C, D, E")
