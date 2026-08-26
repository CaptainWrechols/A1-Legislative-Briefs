#!/usr/bin/env python3
"""Appendix Builder (data-driven parts) for south-carolina-04-slow-wage-growth.

Generates appendices A (bills overview), C (votes and support), D (sponsors),
and E (bill path details) from evidence-pack.json so every table is exact.
B, F, G, H, I, and README are authored by hand alongside.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
APPX = os.path.join(ROOT, "briefs/south-carolina/slow-wage-growth/citizen-v2/appendices")
SRC = os.path.join(ROOT, "sources/south-carolina/slow-wage-growth")

SESSION_YEARS = {123: "2019-20", 124: "2021-22", 125: "2023-24", 126: "2025-26"}

pack = json.load(open(os.path.join(HERE, "evidence-pack.json")))
core = {(b["session"], b["bill_no"]): b
        for b in json.load(open(os.path.join(SRC, "processed/bills-core.json")))["bills"]}

TIER_LABEL = {"core": "Core", "adjacent": "Adjacent", "context": "Context"}


def cite(b):
    return "%s %s" % (SESSION_YEARS[b["session"]], b["bill_no"])


def esc(s):
    return s.replace("|", "/")


# ---------------------------------------------------------------- Appendix A
lines = ["# Appendix A — Bills overview", ""]
lines.append("One row per bill in the curated set (133 bills, hand-reviewed from "
             "5,744 keyword hits). *Tier*: Core bills are the headline set for the four "
             "citizen proposals; Adjacent bills are wage-related but outside them; Context "
             "bills are kept for audit only. *Result*: what finally happened. Lead sponsor "
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
            TIER_LABEL[b["relevance"]],
            "Became law" if b["disposition"] == "Enacted" else "Did not pass",
            esc(b["stage"])))
    lines.append("")
    lines.append("<!-- pdf-page-break -->")
    lines.append("")
open(os.path.join(APPX, "A-bills-overview.md"), "w").write("\n".join(lines[:-2]) + "\n")

# ---------------------------------------------------------------- Appendix C
lines = ["# Appendix C — Votes and support", ""]
lines.append("Every floor passage-type roll call recorded for bills in the curated set, "
             "verbatim from the chamber vote histories. South Carolina never publishes "
             "committee vote tallies, so committee stops have no counts anywhere. "
             "Procedural motions (tabling, amendments, cloture) are excluded here; the "
             "full roll-call list per bill is in the source data.")
lines.append("")
lines.append("## Passage votes")
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
lines.append("Bills that won a passage vote with more than 50% support and still did not "
             "become law. A late-stage death is often a timing or process story, not a "
             "recorded 'no' — except where a losing floor vote is shown.")
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
KEY_BILLS = ["123:H3576", "123:H3759", "123:S419", "124:H3144", "124:H3244", "124:H3348",
             "124:S533", "125:H3605", "125:H3726", "125:S557", "125:S859", "125:S1001",
             "126:H3368", "126:H3863", "126:H4603"]
lines = ["# Appendix E — Bill path details", ""]
lines.append("Milestone paths for the bills the front brief leans on most. Dates and "
             "actions are from the official bill histories; routine steps (sponsor "
             "additions, scrivener corrections) are omitted.")
lines.append("")
by_key = {b["bill_key"]: b for b in pack["bills"]}
import re
KEEP_RE = re.compile(r"Introduced|Referred to Committee|Committee report|Read second|"
                     r"Read third|Roll call|Ratified|Signed|Veto|conference|concurrence|"
                     r"Non-concurrence|Second Reading Failed|Special order|returned to",
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
            lines.append("| %s | %s | %s |" % (a["date"], a["body"], esc(act)))
    for g in cb.get("governor_actions", []):
        lines.append("| %s | Governor | %s |" % (g.get("date", "—"), esc(g.get("action", ""))))
    lines.append("")
open(os.path.join(APPX, "E-bill-path-details.md"), "w").write("\n".join(lines) + "\n")

print("wrote A, C, D, E")
