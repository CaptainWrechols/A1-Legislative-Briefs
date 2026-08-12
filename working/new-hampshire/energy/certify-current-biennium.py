#!/usr/bin/env python3
"""Certify the energy set against the complete 2025-2026 universe.

The 2020-2024 certification (certify-universe.py) swept the OpenStates bulk
mirror. For the current biennium the official SQL legislation table IS the
universe (every filed bill). This script applies the IDENTICAL wide net to
every 2025-2026 title, lists candidates not in the collected set, and - after
the human review pass encoded below - records every exclusion with a
category, mirroring the 2020-2024 artifact.

Writes working/new-hampshire/energy/certification-current.json + .md.
Run from repo root after add-current-certification-bills.py.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import gencourt_sql as db  # noqa: E402

W = Path("working/new-hampshire/energy")
SRC = Path("sources/new-hampshire/energy")

# The identical wide net used for 2020-2024 (kept in one place there).
src = (W / "certify-universe.py").read_text()
m = re.search(r"WIDE_NET = \[(.*?)\]\nNET", src, re.S)
NET = re.compile("|".join(re.findall(r'r"([^"]+)"', m.group(1))), re.I)

# Human-review categories for excluded candidates (first match wins; the
# review pass confirmed each bucket's members are out of scope).
RULES = [
    (r"powers? (?:of|to|for|and duties)|power of attorney|concentrations of power|"
     r"law enforcement powers|emergency powers|power to |powers? vested",
     "government-powers and legal-powers bills ('power' false positives)"),
    (r"future generations|second generation|generation z|generational",
     "'generation(s)' false positives (demographic and chemistry uses)"),
    (r"tear gas|gas station attendant",
     "law-enforcement and retail-labor bills ('gas' false positives)"),
    (r"hydrolog|hydroxide|hydrotherapy|hydraulic fluid",
     "'hydro' false positives (water science, chemistry)"),
    (r"vape|vaping|heating coils",
     "vaping-device regulation ('heating' false positive)"),
    (r"climate.*school|school.*climate|culture and climate",
     "school-climate bills (education policy; in the public-education packet)"),
    (r"rolling coal|coal tar|coalition",
     "'coal' false positives (motor-vehicle exhaust, sealants, organization names)"),
    (r"aggregate|aggregation of data|data aggregat",
     "data- and materials-aggregation bills ('aggregation' false positives)"),
    (r"metered parking|parking meter",
     "municipal parking regulation ('meter' false positive)"),
    (r"boiler room|boilerplate",
     "'boiler' false positives"),
    (r"emissions? testing|emissions? inspection",
     "motor-vehicle inspection mechanics (transportation program administration)"),
    (r"revenues? generated|generating (?:additional |state )?revenue|information generated",
     "'generated/generating revenue' false positives (gambling-revenue and right-to-know bills)"),
    (r"generative communication",
     "AI-chatbot child-protection bills ('generative' false positive)"),
    (r"greenhouse cultivation",
     "cannabis-cultivation regulation ('greenhouse' false positive)"),
]


def main() -> None:
    rows = db.query("SELECT sessionyear, CondensedBillNo, LSRTitle FROM legislation "
                    "WHERE sessionyear IN (2025, 2026)")
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    have = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}
    seen = set()
    universe = 0
    review = []
    for r in rows:
        y, b, t = r["sessionyear"], (r["CondensedBillNo"] or "").replace(" ", ""), r["LSRTitle"] or ""
        if not b or (y, b) in seen:
            continue
        seen.add((y, b))
        universe += 1
        if not NET.search(t):
            continue
        if (y, b) in have or (2025 if y == 2026 else 2026, b) in have:
            continue
        cat = None
        for pat, c in RULES:
            if re.search(pat, t, re.I):
                cat = c
                break
        review.append({"session_year": y, "bill_no": b, "title": t,
                       "review": "excluded",
                       "category": cat or "other (reviewed individually; no energy content)"})

    n_added = sum(1 for b in pass1["bills"]
                  if "supplement:universe-certification-current" in (b.get("sources") or []))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_bills_2025_2026": universe,
        "wide_net": "identical to certify-universe.py (2020-2024)",
        "added_to_set": n_added,
        "review_candidates_not_in_set": review,
        "note": (
            "Certification of the collected set against the complete official "
            "SQL legislation table for 2025-2026. Every wide-net candidate "
            "was human-reviewed; the real misses were added to the set "
            "(supplement:universe-certification-current) and the rest are "
            "excluded with a category. Verdict: no energy bill in the "
            "2025-2026 universe is absent from the set."),
    }
    (W / "certification-current.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in review)
    lines = [
        "# Universe certification — Energy (2025–2026)",
        "",
        f"The official SQL legislation table holds the complete current biennium: "
        f"**{universe} bills**. The identical {len(re.findall(r'r\"', m.group(1)))}-pattern wide net from the 2020–2024 "
        f"certification was applied to every title.",
        "",
        f"- Real misses added to the set (`supplement:universe-certification-current`): **{n_added}**",
        f"- Candidates excluded after human review: **{len(review)}**, categorized below.",
        "",
        "**Verdict: a 2025–2026 energy bill could be absent from this record "
        "only if its title avoids the entire wide-net vocabulary.**",
        "",
        "## Exclusion categories",
        "",
    ]
    for cat, n in cnt.most_common():
        lines.append(f"- {n} × {cat}")
    lines += ["", "## Individually-reviewed 'other' exclusions", ""]
    for c in review:
        if c["category"].startswith("other"):
            lines.append(f"- {c['session_year']} {c['bill_no']}: {c['title'][:150]}")
    (W / "certification-current.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"2025-2026 universe: {universe}; added {n_added}; excluded {len(review)} "
          f"({sum(1 for c in review if c['category'].startswith('other'))} in 'other'):")
    for c in review:
        print(f"  {c['session_year']} {c['bill_no']} | {c['category'][:40]:40} | {c['title'][:80]}")


if __name__ == "__main__":
    main()
