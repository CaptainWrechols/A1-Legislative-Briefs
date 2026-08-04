#!/usr/bin/env python3
"""Programmatic fact-check of reality-map.json against evidence-pack.json.

Verifies, before any brief writing:
  * every cited bill_key exists in the pack
  * every claimed disposition matches the pack
  * every claimed vote (body, motion substring, yeas-nays) matches a real roll call
  * theme scorecard bill/enacted counts match the pack
  * session snapshot counts match the pack
  * watchlist laws are actually enacted
  * sponsor counts match people_signals

Exit 1 on any failure. Run from repo root.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")
pack = json.loads((W / "evidence-pack.json").read_text())
rm = json.loads((W / "reality-map.json").read_text())

bills = {b["bill_key"]: b for b in pack["bills"]}
policy = [b for b in pack["bills"] if b["relevance"] != "context"
          and b["disposition"] != "carryover_duplicate"]
errors: list[str] = []


def check_claim(where, c):
    b = bills.get(c["bill_key"])
    if not b:
        errors.append(f"{where}: unknown bill {c['bill_key']}")
        return
    if c.get("disposition") and b["disposition"] != c["disposition"]:
        errors.append(f"{where}: {c['bill_key']} disposition pack={b['disposition']} claim={c['disposition']}")
    v = c.get("vote")
    if v:
        ok = any(
            r["body"] == v["body"]
            and v["motion_contains"].lower() in (r["motion"] or "").lower()
            and r["yeas"] == v["yeas"] and r["nays"] == v["nays"]
            for r in b["roll_calls"])
        if not ok:
            errors.append(f"{where}: {c['bill_key']} no roll call matching {v}; "
                          f"have {[(r['body'], r['motion'], r['yeas'], r['nays']) for r in b['roll_calls']]}")


for card in rm["topic_reality_cards"]:
    for c in card["claims"]:
        check_claim(f"card:{card['id']}", c)

# theme scorecards vs pack
pack_themes = {t["theme"]: t for t in pack["themes"]}
for sc in rm["theme_scorecards"]:
    pt = pack_themes.get(sc["theme"])
    if not pt:
        errors.append(f"scorecard theme not in pack: {sc['theme']}")
        continue
    if sc["bills"] != pt["bills"]:
        errors.append(f"scorecard {sc['theme']}: bills {sc['bills']} != pack {pt['bills']}")
    if sc["enacted"] != pt["enacted"]:
        errors.append(f"scorecard {sc['theme']}: enacted {sc['enacted']} != pack {pt['enacted']}")
    for k in sc["example_bills"]:
        if k not in bills:
            errors.append(f"scorecard {sc['theme']}: unknown example {k}")

# session snapshot vs pack
snap = defaultdict(Counter)
for b in policy:
    snap[str(b["session_year"])]["in_set"] += 1
    snap[str(b["session_year"])][b["disposition"]] += 1
for y, claimed in rm["session_snapshot"].items():
    for k, v in claimed.items():
        have = snap[y].get(k, 0)
        if v != have:
            errors.append(f"snapshot {y}.{k}: claim {v} != pack {have}")

# watchlist enacted
for law in rm["recent_enactments_watchlist"]["laws"]:
    b = bills.get(law["bill_key"])
    if not b or b["disposition"] != "enacted":
        errors.append(f"watchlist {law['bill_key']}: not enacted in pack "
                      f"({(b or {}).get('disposition')})")

# high-support list keys exist
for h in rm["high_support_non_enactments"]:
    if h["bill_key"] not in bills:
        errors.append(f"high-support unknown bill {h['bill_key']}")

# sponsors
pack_sp = {s["name"]: s for s in pack["people_signals"]["frequent_primary_sponsors"]}
for s in rm["people_and_process"]["frequent_primary_sponsors"]:
    ps = pack_sp.get(s["name"])
    if not ps:
        errors.append(f"sponsor {s['name']} not in pack top list")
    elif ps["bills"] != s["bills"] or (ps.get("party") or None) != s["party"]:
        errors.append(f"sponsor {s['name']}: claim {s['bills']}/{s['party']} != pack {ps['bills']}/{ps.get('party')}")

xp = rm["people_and_process"]["cross_party_sponsorship"]["count"]
if xp != pack["people_signals"]["cross_party_count"]:
    errors.append(f"cross-party count {xp} != pack {pack['people_signals']['cross_party_count']}")

if errors:
    print(f"FACT-CHECK FAILED ({len(errors)} problems):")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("FACT-CHECK PASSED: all reality-map claims verified against the evidence pack.")
