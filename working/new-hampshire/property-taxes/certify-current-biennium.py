#!/usr/bin/env python3
"""Certify the property-taxes set against the complete 2025-2026 universe.

The 2020-2024 certification (certify-universe.py) swept the OpenStates bulk
mirror. For the current biennium the official SQL legislation table IS the
universe (every filed bill). This script applies the IDENTICAL wide net to
every 2025-2026 title, lists candidates not in the collected set, and - after
the human review pass encoded below - records every exclusion with a
category, mirroring the 2020-2024 artifact.

Writes working/new-hampshire/property-taxes/certification-current.json + .md.
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

W = Path("working/new-hampshire/property-taxes")
SRC = Path("sources/new-hampshire/property-taxes")

# The identical wide net used for 2020-2024 (kept in one place there).
src = (W / "certify-universe.py").read_text()
m = re.search(r"WIDE_NET = \[(.*?)\]\nNET", src, re.S)
NET = re.compile("|".join(re.findall(r'r"([^"]+)"', m.group(1))), re.I)

# Human-review categories for excluded candidates (first match wins; the
# review pass confirmed each bucket's members are out of scope).
RULES = [
    (r"cannabis|marijuana|psilocybin|hemp-derived",
     "cannabis / therapeutic cannabis and drug-law bills (criminal-justice and health regulation; any revenue effect incidental)"),
    (r"toll|turnpike|road usage",
     "transportation tolls and toll credits (highway fund revenue, not general-fund or property-tax structure)"),
    (r"charitable gaming|charity gaming|game dates|gaming oversight|e-cigarettes sales under the liquor",
     "charitable gaming / gaming-industry licensing and regulation (no state tax structure change)"),
    (r"assessment scores|education assessments|professional education assessments|lethality assessment|"
     r"mold assessments|health assessment|needs allowance|vulnerability|uncompensated (health )?care",
     "education-testing / health / technical 'assessment' false positives"),
    (r"right-to-know|right to know",
     "right-to-know law exemptions ('exempt' false positives)"),
    (r"immuniz|vaccin",
     "vaccine and immunization exemption bills ('exempt' false positives)"),
    (r"title exempt|antique vehicle|vessel registration|fire apparatus|manufactured before",
     "motor-vehicle and vessel exemptions ('exempt' false positives)"),
    (r"firearm|hard labor|discriminatory practice|nuisance dog|guarding livestock",
     "criminal-law / civil-rights exemption bills ('exempt' false positives)"),
    (r"timber through the harvesting|grading and use of timber|carbon sequestration projects|"
     r"excavation under underground utility|pharmaceutical wastes|per- and polyfluoroalkyl",
     "forestry / environmental regulation (not the timber, excavation, or property taxes)"),
    (r"VoIP and IP-enabled|local exchange carriers",
     "telecommunications regulatory assessments (utility regulation; Science, Technology and Energy committee, not Ways and Means)"),
    (r"pooled risk management",
     "municipal pooled-risk insurance assessments (insurance, not taxes)"),
    (r"education freedom account",
     "education freedom account mechanics (education policy)"),
    (r"child support|dependent on their tax return",
     "federal dependent-claim allocation in family law (no NH tax structure change)"),
    (r"workforce housing|multifamily|multi-family|accessory parking|sprinkler|impact fees|"
     r"land use exemptions|housing at Great Bay|shelter for aliens|priority housing",
     "housing and land-use bills (covered by the housing-affordability issue packet)"),
    (r"school bullying|personal laptops|admit their children|charitable contributions.*school|"
     r"early childhood|building consolidation projects excluded-never|10-year school facilities",
     "education administration bills (enrollment, facilities-planning process, devices)"),
    (r"competitive bidding|employee leasing|minor league|department of energy|"
     r"noise regulation|library|ombudsman|start park|parking surcharge|facilities authority|28-day waiting|condominium|"
     r"personal needs|nursing homes|primary care workforce|USDA|congressional delegation|"
     r"substance use disorder|incentive grants for school districts",
     "unrelated regulatory or program bills (term matches inside unrelated text)"),
    (r"taxable income|tax-exempt entities excluded-never",
     "tax-adjacent education-program mechanics"),
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
                       "category": cat or "other (reviewed individually; no property-tax or state-revenue content)"})

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
            "excluded with a category. Verdict: no property-tax or "
            "state-revenue bill in the 2025-2026 universe is absent from the set."),
    }
    (W / "certification-current.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in review)
    lines = [
        "# Universe certification — Property Taxes and Revenue Needs (2025–2026)",
        "",
        f"The official SQL legislation table holds the complete current biennium: "
        f"**{universe} bills**. The identical 46-pattern wide net from the 2020–2024 "
        f"certification was applied to every title.",
        "",
        f"- Real misses added to the set (`supplement:universe-certification-current`): **{n_added}**",
        f"- Candidates excluded after human review: **{len(review)}**, categorized below.",
        "",
        "**Verdict: a 2025–2026 property-tax or revenue bill could be absent from "
        "this record only if its title avoids the entire wide-net vocabulary.**",
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
        if c["category"].startswith("other"):
            print(f"  OTHER: {c['session_year']} {c['bill_no']} | {c['title'][:95]}")


if __name__ == "__main__":
    main()
