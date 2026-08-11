#!/usr/bin/env python3
"""Build appendices A-H for the NH property-taxes lege brief.

NH data shapes differ from Nevada's (no NELIS milestones), so this issue uses
its own assembler; the formatting rules follow agents/appendix-builder/AGENT.md
(one H1 per file, short intro, navy-header-friendly tables, page-break markers,
`2024 HB1034`-style ids). Appendix I (sources & review notes) is hand-written.

Run from repo root:
  python3 working/new-hampshire/property-taxes/build-appendices-nh.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")
SRC = Path("sources/new-hampshire/property-taxes")
OUT = Path("briefs/new-hampshire/property-taxes/citizen-v2/appendices")

pack = json.loads((W / "evidence-pack.json").read_text())
rm = json.loads((W / "reality-map.json").read_text())
hb2 = json.loads((W / "hb2-sections.json").read_text())

DISP_LABEL = {
    "enacted": "Became law",
    "vetoed": "Vetoed",
    "killed": "Did not pass",
    "interim_study": "Interim study",
    "passed": "Adopted (resolution)",
    "carryover_duplicate": "See next-year record",
}
BASKET = {"often_moved": "Often moved before", "unfinished": "Got support but didn't finish",
          "rarely_moved": "Rarely moved before", "mixed": "Mixed"}


def bid(b):
    return f"{b['session_year']} {b['identifier']}"


def esc(s):
    return (s or "").replace("|", "/")


def primes(b):
    return ", ".join(s["name"] for s in (b.get("sponsors") or []) if s.get("prime")) or "—"


def party_str(split):
    if not split:
        return "—"
    parts = []
    for p in ("R", "D", "I"):
        v = split.get(p)
        if v:
            parts.append(f"{p} {v.get('yea', 0)}–{v.get('nay', 0)}")
    return ", ".join(parts) or "—"


def write(name, lines):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", name)


bills = sorted(pack["bills"], key=lambda b: (b["session_year"], b["identifier"]))
policy = [b for b in bills if b["relevance"] != "context" and b["disposition"] != "carryover_duplicate"]

# ---------- A ----------
L = ["# Appendix A — Every bill in the set", "",
     "One row per bill found by the property-tax and revenue search, 2020–2026. "
     "'Tier' marks how central the bill is: core (tax or revenue policy), "
     "adjacent (touches the issue), or context (found by the keywords but not "
     "a tax bill; kept for audit and excluded from headline counts). Results "
     "come from official dockets and chaptered texts; Appendix E has each "
     "bill's path.", "",
     "| Year | Bill | Plain topic | Theme | Result | Tier |",
     "|---|---|---|---|---|---|"]
for b in bills:
    L.append(f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'])} "
             f"| {esc(b['theme'].replace('Context: not primarily a property-tax or revenue bill', '—'))} "
             f"| {DISP_LABEL[b['disposition']]} | {b['relevance']} |")
write("A-bills-overview.md", L)

# ---------- B ----------
L = ["# Appendix B — Theme scorecards and history baskets", "",
     "Each theme's track record, with its history basket: what similar ideas "
     "did before. Baskets describe the record; they are not advice. Counts "
     f"cover the {pack['inventory']['policy_set']}-bill policy set.", ""]
for t in rm["theme_scorecards"]:
    L += [f"## {t['theme']}", "",
          f"*{t['bills']} bills · {t['enacted']} became law · basket: "
          f"**{BASKET[t['basket']]}** · certainty: {t['certainty']}*", "",
          t["note"], "",
          "Examples: " + ", ".join(k.replace(":", " ") for k in t["example_bills"]), "",
          "<!-- pdf-page-break -->" if t is not rm["theme_scorecards"][-1] and
          rm["theme_scorecards"].index(t) % 3 == 2 else "", ""]
write("B-theme-scorecards.md", [l for l in L if l != "" or True])

# ---------- C ----------
L = ["# Appendix C — Roll-call votes and support", "",
     "Every floor roll call recorded for policy bills in the set, from the "
     "official General Court vote database. NH decides most bills by voice "
     "vote, so a bill with no row here still had floor action. Party splits "
     "show yes–no within each party where the roster records one ('?' = party "
     "not on record). Votes on HB2 (Appendix H) are on the whole budget "
     "trailer.", "",
     "| Year | Bill | Chamber | Date | Motion | Yes | No | Yes% | By party |",
     "|---|---|---|---|---|---|---|---|---|"]
for b in policy:
    for r in b["roll_calls"]:
        L.append(f"| {b['session_year']} | {b['identifier']} | {r['body']} | {r['date']} "
                 f"| {esc(r['motion'])} | {r['yeas']} | {r['nays']} "
                 f"| {r['yes_pct'] if r['yes_pct'] is not None else '—'} "
                 f"| {party_str(r.get('party_split'))} |")
L += ["", "<!-- pdf-page-break -->", "", "## High support, not enacted", "",
      "Bills that won a floor majority somewhere and still did not become law.", "",
      "| Bill | What it tried | Winning vote | What happened |", "|---|---|---|---|"]
for h in pack["high_support_non_enactments"]:
    bb = next(x for x in policy if x["bill_key"] == h["bill_key"])
    L.append(f"| {bid(bb)} | {esc(h['plain_topic'])} | {esc(h['vote'])} | {esc(h['outcome'][:160])} |")
write("C-votes-and-support.md", L)

# ---------- D ----------
L = ["# Appendix D — Sponsors and people", "",
     "Sponsors come from the official database (2025–2026, with party labels) "
     "and the OpenStates bulk sponsorship files (2020–2024); where the bulk "
     "files carry no prime flag, the first-listed sponsor is treated as prime "
     "(New Hampshire lists the prime sponsor first). Party labels exist only "
     "on the 2025–2026 layer. No judgment of any legislator is implied — "
     "these are counts of who filed what.", "",
     "## Frequent primary sponsors", "",
     "| Name | Party | Bills as prime sponsor |", "|---|---|---|"]
for s in pack["people_signals"]["frequent_primary_sponsors"]:
    L.append(f"| {s['name']} | {s['party'] or '?'} | {s['bills']} |")
L += ["", f"Cross-party sponsor teams appeared on **{pack['people_signals']['cross_party_count']}** "
      "policy bills (both major parties among named sponsors; party labels "
      "exist only for 2025–2026, so this understates).", "",
      "<!-- pdf-page-break -->", "", "## Primary sponsors by bill", "",
      "| Year | Bill | Primary sponsor(s) | All sponsors |", "|---|---|---|---|"]
for b in policy:
    sp = b.get("sponsors") or []
    if not sp:
        continue
    all_names = ", ".join(f"{s['name']} ({s.get('party') or '?'})" for s in sp[:8])
    if len(sp) > 8:
        all_names += f", +{len(sp)-8} more"
    L.append(f"| {b['session_year']} | {b['identifier']} | {esc(primes(b))} | {esc(all_names)} |")
write("D-sponsors-and-people.md", L)

# ---------- E ----------
L = ["# Appendix E — Where each bill ended", "",
     "The end of each policy bill's path, from official dockets (the state "
     "database for 2025–2026; the OpenStates mirror of the GenCourt docket "
     "for 2020–2024). Appendix F explains the coverage limits.", "",
     "| Year | Bill | Where it ended |", "|---|---|---|"]
for b in policy:
    L.append(f"| {b['session_year']} | {b['identifier']} | {esc(b['stage'][:220])} |")
write("E-bill-path-details.md", L)

# ---------- F ----------
L = ["# Appendix F — What this data can and cannot say", "",
     "Plain-language limits of the collected record. Anyone quoting the brief "
     "should know these.", ""]
for d in pack["data_limits"]:
    L.append(f"- {d}")
L += ["", "The full machine-readable record — bills, votes, ballots, dockets, HB2 "
      "sections, and per-claim evidence — lives in the repository under "
      "`sources/new-hampshire/property-taxes/` and "
      "`working/new-hampshire/property-taxes/`."]
write("F-data-limits.md", L)


# ---------- G ----------
def origin_chamber(bill_no):
    return "House" if bill_no.startswith(("HB", "HR", "CACR", "HCR")) else "Senate"


def motion_rank(motion, yeas, nays):
    m = (motion or "").lower()
    carried = (yeas or 0) > (nays or 0)
    if "veto override" in m:
        return 6
    if any(k in m for k in ("concur", "cofc", "conference")):
        return 5 if carried else 4
    if any(k in m for k in ("inexpedient", "itl", "indefinitely", "postpone")) or m.strip() == "table" or "laid on table" in m:
        # a kill motion that carried is the decision; one that failed is a survival
        return 5 if carried else 2
    if "ought to pass" in m or m.startswith("otp"):
        return 3  # decisive either way (passage or defeat)
    if "remove from table" in m:
        return 2
    return 1  # amendments, divides, procedural


def decisive_roll(b, chamber):
    rcs = [r for r in b["roll_calls"] if r["body"] == chamber]
    if not rcs:
        return None
    # The chamber's outcome is its LAST decisive action (rank >= 3): a kill
    # that was later reconsidered and reversed is not the outcome (2022
    # HB1417's House ITL 173-172 was undone; the final OTP 186-159 is).
    decisive = [(i, r) for i, r in enumerate(rcs)
                if motion_rank(r["motion"], r["yeas"], r["nays"]) >= 3]
    if decisive:
        r = decisive[-1][1]
    else:
        r = max(enumerate(rcs), key=lambda ir: (motion_rank(ir[1]["motion"], ir[1]["yeas"], ir[1]["nays"]), ir[0]))[1]
    return r, f"{r['motion']} {r['yeas']}\u2013{r['nays']}"


BILL_INDEX = {(b["session_year"], b["identifier"]): b for b in bills}


def death_suffix(stage):
    if "interim study" in stage:
        return "sent to interim study (voice)"
    if "table" in stage:
        return "tabled (voice/division)"
    if "indefinitely postponed" in stage:
        return "indefinitely postponed (voice)"
    if "deadline" in stage:
        return "died at the Senate deadline"
    if "committee recommended" in stage:
        return "died in committee"
    if "session ended" in stage:
        return "died at session's end"
    return "killed (voice/division)"


def chamber_votes(b):
    disp, stage = b["disposition"], b["stage"]
    origin = origin_chamber(b["identifier"])
    single_chamber = b["identifier"].startswith(("HR", "SR"))
    dm = re.search(r"(?:killed on the|died in the|died on the|tabled in the|laid on the table in the|"
                   r"indefinitely postponed by the|sent to interim study by the|stayed on the|"
                   r"recommended by the)\s+(House|Senate)", stage)
    if not dm:
        dm = re.search(r"(House|Senate)(?:'s)? (?:floor|table|committee recommended|deadline)", stage)
    named = dm.group(1) if dm else ("House" if "House" in stage else ("Senate" if "Senate" in stage else None))

    def fill(ch):
        other = "Senate" if ch == "House" else "House"
        got = decisive_roll(b, ch)
        if got:
            r, txt = got
            rank = motion_rank(r["motion"], r["yeas"], r["nays"])
            # a non-decisive roll in the chamber that killed the bill gets an
            # honest suffix so an amendment tally is not mistaken for the death
            if named == ch and disp == "killed":
                if rank < 3 or ("deadline" in stage and "override" not in (r["motion"] or "").lower()):
                    return f"{txt}; {death_suffix(stage)}"
            # an enacted/passed bill whose only recorded rolls are amendments
            # or failed motions actually passed by voice - say so
            if disp in ("enacted", "passed", "vetoed") and rank < 3:
                return f"{txt}; passed (voice/consent)"
            return txt
        if single_chamber and ch != origin:
            return "n/a"
        if disp == "carryover_duplicate":
            return "see later-year row"
        # carryover continuation: origin-chamber vote may sit on the prior-year row
        prev = BILL_INDEX.get((b["session_year"] - 1, b["identifier"]))
        if prev and ch == origin:
            got_prev = decisive_roll(prev, ch)
            if got_prev:
                return f"{got_prev[1]} ({b['session_year'] - 1})"
        if disp in ("enacted", "passed", "vetoed"):
            return "passed (voice/consent)"
        if named == ch:
            return death_suffix(stage)
        if named == other and ch == origin:
            # died in the second chamber, so the origin chamber had passed it
            return "passed (voice/consent)"
        if "conference" in stage or "between" in disp:
            return "passed (voice/consent)"
        if ch == origin:
            return "no floor roll call"
        return "\u2014"

    return fill("House"), fill("Senate")


def governor_cell(b):
    disp, stage = b["disposition"], b["stage"]
    if disp == "enacted":
        m = re.search(r"Chapter (\d+)", stage)
        suffix = " (no signature)" if "without" in stage else ""
        return (f"Signed \u2014 Ch. {m.group(1)}" if m else "Signed") + suffix
    if disp == "vetoed":
        if "override failed" in stage:
            return "VETOED \u2014 override failed"
        for r in b["roll_calls"]:
            if "Veto Override" in (r["motion"] or ""):
                total = r["yeas"] + r["nays"]
                if total and r["yeas"] < 2 * total / 3:
                    return "VETOED \u2014 override failed"
                return f"VETOED \u2014 override {r['yeas']}\u2013{r['nays']}"
        return "VETOED \u2014 no override recorded (as of Aug 2026)"
    if disp == "passed":
        return "n/a (resolution)"
    return "\u2014"


L = ["# Appendix G \u2014 Bill-by-bill grid: sponsors, chamber votes, governor", "",
     "One row per bill: year, number, subject, prime sponsor, each chamber's "
     "decisive floor vote, and the Governor's action. New Hampshire decides "
     "most bills by voice or division vote, which record no tallies \u2014 those "
     "cells say so rather than invent numbers ('\u2014' means the bill never "
     "reached that chamber). Every recorded roll call, with party splits, is "
     "in Appendix C; where each bill ended is in Appendix E. Prime sponsors "
     "for 2020\u20132024 come from the OpenStates sponsor files; where those files "
     "carry no prime flag, the first-listed sponsor is shown (New Hampshire "
     "lists the prime sponsor first).", "",
     "| Year | Bill | Title/subject | Prime sponsor | House vote | Senate vote | Governor |",
     "|---|---|---|---|---|---|---|"]
for b in bills:
    primes_list = [s["name"] for s in (b.get("sponsors") or []) if s.get("prime")]
    prime = primes_list[0] + (" et al." if len(primes_list) > 1 else "") if primes_list else "\u2014"
    hv, sv = chamber_votes(b)
    L.append(f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'][:110])} "
             f"| {esc(prime)} | {esc(hv)} | {esc(sv)} | {esc(governor_cell(b))} |")
write("G-bill-grid.md", L)

# ---------- H ----------
L = ["# Appendix H — Inside the budget trailer (HB2)", "",
     "New Hampshire makes much of its tax law inside HB2, the omnibus policy "
     "bill that accompanies each two-year budget. Every extracted section of "
     "the last three trailers was screened against the tax and revenue terms "
     "and hand-reviewed; this appendix lists the sections kept (three rate "
     "sections the term matcher missed were added by hand and flagged in the "
     "working files). **All votes on HB2 are on the whole trailer, never on "
     "one section.**", ""]
for c in hb2["cycles"]:
    L += [f"## HB2 {c['session_year']} — {c['laws_citation']}", "",
          f"{c['total_sections_extracted']} sections; "
          f"{len(c['relevant_sections'])} tax/revenue-relevant after review. "
          "Final passage (whole bill): " + "; ".join(
              f"{v['body']} {v['yeas']}–{v['nays']} ({v['date']})"
              for v in c["whole_bill_final_votes"]) + ".", "",
          "| Section | What it does | Weight |", "|---|---|---|"]
    for s in c["relevant_sections"]:
        L.append(f"| {s['cite']} | {esc(s['plain_language'])} | {s['category']} |")
    L += ["", "<!-- pdf-page-break -->", ""]
L += ["The section-by-section review (including every candidate excluded as a "
      "false keyword match, with reasons) is in "
      "`working/new-hampshire/property-taxes/hb2-sections.md`."]
write("H-hb2-budget-trailer.md", L)

print("done")
