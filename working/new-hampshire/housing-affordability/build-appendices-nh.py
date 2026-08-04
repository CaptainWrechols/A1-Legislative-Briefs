#!/usr/bin/env python3
"""Build appendices A-F and H for the NH housing citizen brief.

NH data shapes differ from Nevada's (no NELIS milestones), so this issue uses
its own assembler; the formatting rules follow agents/appendix-builder/AGENT.md
(one H1 per file, short intro, navy-header-friendly tables, page-break markers,
`2024 HB1291`-style ids). Appendix I (sources & review notes) is hand-written.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/build-appendices-nh.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")
SRC = Path("sources/new-hampshire/housing-affordability")
OUT = Path("briefs/new-hampshire/housing-affordability/citizen-v1/appendices")

pack = json.loads((W / "evidence-pack.json").read_text())
rm = json.loads((W / "reality-map.json").read_text())
hb2 = json.loads((W / "hb2-sections.json").read_text())
dockets = {(b["session_year"], b["bill_no"]): b
           for b in json.loads((SRC / "processed" / "bill-actions.json").read_text())["bills"]}

DISP_LABEL = {
    "enacted": "Became law",
    "content_enacted_via_hb2": "Enacted via HB2",
    "vetoed": "Vetoed",
    "killed": "Did not pass",
    "interim_study": "Interim study",
    "passed": "Adopted (resolution)",
    "carryover_duplicate": "See 2026 record",
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
     "One row per bill found by the housing search, 2020–2026. 'Tier' marks how "
     "central the bill is: core (housing policy), adjacent (touches housing), or "
     "context (found by the keywords but not a housing bill; kept for audit and "
     "excluded from headline counts). Results come from official dockets and "
     "chaptered texts; Appendix E has each bill's path.", "",
     "| Year | Bill | Plain topic | Theme | Result | Tier |",
     "|---|---|---|---|---|---|"]
for b in bills:
    L.append(f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'])} "
             f"| {esc(b['theme'].replace('Context: not primarily housing', '—'))} "
             f"| {DISP_LABEL[b['disposition']]} | {b['relevance']} |")
write("A-bills-overview.md", L)

# ---------- B ----------
L = ["# Appendix B — Theme scorecards and history baskets", "",
     "Each housing theme's track record, with its history basket: what similar "
     "ideas did before. Baskets describe the record; they are not advice. "
     "Counts cover the 135-bill policy set.", ""]
for t in rm["theme_scorecards"]:
    L += [f"## {t['theme']}", "",
          f"*{t['bills']} bills · {t['enacted']} became law · basket: "
          f"**{BASKET[t['basket']]}** · certainty: {t['certainty']}*", "",
          t["note"], "",
          "Examples: " + ", ".join(k.replace(":", " ") for k in t["example_bills"]), "",
          "<!-- pdf-page-break -->" if t is not rm["theme_scorecards"][-1] and
          rm["theme_scorecards"].index(t) % 3 == 2 else "", ""]
write("B-theme-scorecards.md", [l for l in L if l != ""or True])

# ---------- C ----------
L = ["# Appendix C — Roll-call votes and support", "",
     "Every floor roll call recorded for bills in the set, from the official "
     "General Court vote database. NH decides most bills by voice vote, so a "
     "bill with no row here still had floor action. Party splits show yes–no "
     "within each party where the roster records one ('?' = party not on "
     "record). Votes on HB2 (Appendix H) are on the whole budget trailer.", "",
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
     "Sponsors are complete for 2025–2026 (official database) and 2020–2021 "
     "(official final-text pages); the collected record has no sponsor names "
     "for most 2022–2024 bills. No judgment of any legislator is implied — "
     "these are counts of who filed what.", "",
     "## Frequent primary sponsors", "",
     "| Name | Party | Bills as prime sponsor |", "|---|---|---|"]
for s in pack["people_signals"]["frequent_primary_sponsors"]:
    L.append(f"| {s['name']} | {s['party'] or '?'} | {s['bills']} |")
L += ["", f"Cross-party sponsor teams appeared on **{pack['people_signals']['cross_party_count']}** "
      "policy bills (both major parties among named sponsors).", "",
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
     "The end of each policy bill's path, from official dockets (2025–2026), "
     "gc.nh.gov final texts and archived dockets (2020–2024). Appendix F "
     "explains the older-year coverage limits.", "",
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
      "`sources/new-hampshire/housing-affordability/` and "
      "`working/new-hampshire/housing-affordability/`."]
write("F-data-limits.md", L)

# ---------- H ----------
L = ["# Appendix H — Inside the budget trailer (HB2)", "",
     "New Hampshire enacts much of its housing policy inside HB2, the omnibus "
     "policy bill that accompanies each two-year budget. Every extracted "
     "section of the last three trailers was screened against the housing "
     "terms and hand-reviewed; this appendix lists the housing sections kept. "
     "**All votes on HB2 are on the whole trailer, never on one section.**", ""]
for c in hb2["cycles"]:
    L += [f"## HB2 {c['session_year']} — {c['laws_citation']}", "",
          f"{c['total_sections_extracted']} sections; "
          f"{len(c['relevant_sections'])} housing-relevant after review. "
          "Final passage (whole bill): " + "; ".join(
              f"{v['body']} {v['yeas']}–{v['nays']} ({v['date']})"
              for v in c["whole_bill_final_votes"]) + ".", "",
          "| Section | What it does | Weight |", "|---|---|---|"]
    for s in c["relevant_sections"]:
        L.append(f"| {s['cite']} | {esc(s['plain_language'])} | {s['category']} |")
    L += ["", "<!-- pdf-page-break -->", ""]
L += ["The section-by-section review (including every candidate excluded as a "
      "false keyword match, with reasons) is in "
      "`working/new-hampshire/housing-affordability/hb2-sections.md`."]
write("H-hb2-budget-trailer.md", L)

print("done")
