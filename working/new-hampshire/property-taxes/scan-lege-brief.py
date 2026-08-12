#!/usr/bin/env python3
"""Automated reviewer scans for the property-taxes lege brief.

1. Advice-language scan: no should/must/ought to/recommend/urge/need to used
   as advocacy in the citizen-facing text (quoted descriptive uses whitelisted).
2. Bill-existence scan: every bill cited in the brief exists in the evidence
   pack (or is HB2/HB1, handled by the trailer analysis).
3. Vote-pair scan: every N-M tally in the brief matches an official roll call
   for a bill cited nearby, an HB2 whole-trailer vote, or a documented
   division-vote tally from the official docket (whitelisted explicitly).

Exit 1 on any failure. Run from repo root.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BRIEF = Path("briefs/new-hampshire/property-taxes/citizen-v2/lege-brief.md")
W = Path("working/new-hampshire/property-taxes")

text = BRIEF.read_text(encoding="utf-8")
body = text.split("---", 2)[2]
pack = json.loads((W / "evidence-pack.json").read_text())
hb2 = json.loads((W / "hb2-sections.json").read_text())
bills = {b["bill_key"]: b for b in pack["bills"]}
errors = []

# ---- 1. advice language ----
ADVICE = re.compile(r"\b(should|must|ought to|recommend(?:s|ed)?|urge[sd]?|need to)\b", re.I)
ALLOWED_ADVICE = [
    # descriptive uses: quoting bill/motion content or legal requirements
    "urged Congress to fund IDEA",
    "urged Congress",
    # process-glossary descriptions of legal requirements (identical wording
    # to the housing lege brief's shared glossary)
    "A bill must pass both to reach the Governor",
    "Ought to Pass",
    "the first chamber must accept (concur in)",
]
for m in ADVICE.finditer(body):
    ctx = body[max(0, m.start() - 80):m.end() + 80].replace("\n", " ")
    if any(a.lower() in ctx.lower() for a in ALLOWED_ADVICE):
        continue
    errors.append(f"advice language: ...{ctx}...")

# ---- 2. cited bills exist ----
cited = set()
for m in re.finditer(r"\b(HB|SB|CACR|HCR|HR|SR)\s?(\d+)\s?\((\d{4})(?:[–-]\d{2,4})?\)", body):
    cited.add((int(m.group(3)), f"{m.group(1)}{m.group(2)}"))
for m in re.finditer(r"\b(HB|SB|CACR|HCR|HR|SR)(\d+),?\s(\d{4})\b", body):
    cited.add((int(m.group(3)), f"{m.group(1)}{m.group(2)}"))
for m in re.finditer(r"(\d{4})'s\s(HB|SB|CACR|HCR|HR|SR)(\d+)", body):
    cited.add((int(m.group(1)), f"{m.group(2)}{m.group(3)}"))
missing = []
for (y, b) in sorted(cited):
    if b in ("HB1", "HB2"):
        continue
    key = f"{y}:{b}"
    key2 = f"{y - 1}:{b}"  # biennium first-year record (e.g. HB10 2021-22)
    if key not in bills and key2 not in bills:
        missing.append(key)
if missing:
    errors.append(f"cited bills not in pack: {missing}")

# ---- 3. vote pairs ----
# Division-vote or docket-only tallies verified by hand against the official
# docket (never invented; each carries its docket citation here).
DIVISION_WHITELIST = {
    (170, 185): "2025 HB675 reconsideration: 'Reconsider ITL (Rep. Weber): MF DV 170-185 01/08/2026 HJ 2' (division vote in the official docket)",
    (18, 0): "2025 HB765 committee report: 'Committee Report: Inexpedient to Legislate 03/17/2025 (Vote 18-0; CC) HC 17' (recorded committee vote in the official docket, labeled as such in the brief)",
}
hb2_votes = set()
for cyc in hb2["cycles"]:
    for v in cyc["whole_bill_final_votes"]:
        hb2_votes.add((v["yeas"], v["nays"]))
hb2_votes.add((198, 181))  # HB2 2021 House CCR (also in WHOLE_BILL_VOTES)

all_rc = set()
for b in pack["bills"]:
    for r in b["roll_calls"]:
        all_rc.add((r["yeas"], r["nays"]))

for m in re.finditer(r"\b(\d{1,3})[–-](\d{1,3})\b", body):
    prefix = body[max(0, m.start() - 6):m.start()]
    if prefix.endswith(":") or prefix.endswith("Rule "):
        continue  # chapter-section ranges (91:109–110) and Senate Rule 3-23
    pair = (int(m.group(1)), int(m.group(2)))
    if pair in all_rc or pair in hb2_votes or pair in DIVISION_WHITELIST:
        continue
    # date ranges like 2021-22 are excluded by the 1-3 digit bound; year
    # spans like 2020-2026 don't match either
    ctx = body[max(0, m.start() - 60):m.end() + 40].replace("\n", " ")
    errors.append(f"vote pair {pair} not in official record: ...{ctx}...")

if errors:
    print(f"LEGE-BRIEF SCAN FAILED ({len(errors)} problems):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"LEGE-BRIEF SCAN PASSED: no advice language; all {len(cited)} cited "
      "bills exist in the pack; every vote pair matches the official record "
      f"({len(DIVISION_WHITELIST)} documented division-vote exception).")
