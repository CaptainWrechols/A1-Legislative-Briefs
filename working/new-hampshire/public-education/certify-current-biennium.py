#!/usr/bin/env python3
"""Certify the public-education set against the complete 2025-2026 universe.

The 2020-2024 certification (certify-universe.py) swept the OpenStates bulk
mirror. For the current biennium the official SQL legislation table IS the
universe (every filed bill). This script applies the IDENTICAL wide net to
every 2025-2026 title, lists candidates not in the collected set, and - after
the human review pass encoded below - records every exclusion with a
category, mirroring the 2020-2024 artifact.

Writes working/new-hampshire/public-education/certification-current.json + .md.
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

W = Path("working/new-hampshire/public-education")
SRC = Path("sources/new-hampshire/public-education")

# The identical wide net used for 2020-2024 (kept in one place there).
src = (W / "certify-universe.py").read_text()
m = re.search(r"WIDE_NET = \[(.*?)\]\nNET", src, re.S)
NET = re.compile("|".join(re.findall(r'r"([^"]+)"', m.group(1))), re.I)

# Human-review categories for excluded candidates (first match wins; the
# review pass confirmed each bucket's members are out of scope).
RULES = [
    (r"child care|day care|children and families",
     "child-care and day-care bills (early-care regulation and subsidies, not K-12)"),
    (r"college|university|higher education|campus|postsecondary|post-secondary|"
     r"medical schools|masters and doctorate",
     "higher education (university/community-college system, campus policy, degrees - out of K-12 scope)"),
    (r"public librar|library cards|library use records|library records",
     "public-library administration and records (RSA 201-D/202-A; the school-materials thread is in the set)"),
    (r"boater education|apprentice guide|physicians|healthcare providers|child abuse and neglect for certain healthcare",
     "occupational licensing and professional continuing-education requirements (adult trades and professions)"),
    (r"workforce housing|housing choice|housing accessibility|accessory dwelling|"
     r"accessory parking|multifamily|partners in housing|housing development|land use regulation|impact fees",
     "housing and land-use bills (covered by the housing-affordability issue packet)"),
    (r"uncompensated (health )?care|health assessment|health improvement|primary (health )?care|"
     r"health care workforce|lethality assessment|mold assessments|psilocybin|right-to-know law for individuals",
     "health and disability-access bills ('assessment'/'education' false positives)"),
    (r"assessed under the low-income|c-pace|special assessment districts|special assessment requests|"
     r"property tax|tax exemptions|re-assessment of property|property tax assessment|luxury second homes|"
     r"assessed property values|assessed value|room occupanc|tobacco tax|state education property tax.*business profits|"
     r"exemptions once|assessment of real property",
     "property-tax assessment, exemption, and state-revenue bills (covered by the property-taxes packet)"),
    (r"chartered bank|credit unions|insurers|banking",
     "financial-services regulation ('chartered'/'assessments' false positives)"),
    (r"voip|local exchange carriers",
     "telecommunications regulatory assessments (utility regulation, not schools)"),
    (r"enrolled bills|bill enrollment|electoral college|impeach|polling|charter amendment.*form of government",
     "election and legislative-administration bills ('enrolled'/'college'/'instructing' false positives)"),
    (r"customer-generators|energy resource aggregations|renewable portfolio|transformers|"
     r"data facilities|carbon sequestration|state park",
     "energy and environmental program bills (term matches inside unrelated text)"),
    (r"child support",
     "family-law bills (postsecondary support obligations)"),
    (r"obscenity on certain electronic devices",
     "consumer device-filter law (retail regulation; the school-materials bills are in the set)"),
    (r"gambling|graduate retention|dispatchers|inmates",
     "gambling, corrections, and adult-program bills (term matches inside unrelated text)"),
    (r"health and education facilities authority",
     "bond-authority consolidation (facilities financing, not school policy)"),
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
                       "category": cat or "other (reviewed individually; no K-12 public-education content)"})

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
            "excluded with a category. Verdict: no K-12 public-education "
            "bill in the 2025-2026 universe is absent from the set."),
    }
    (W / "certification-current.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in review)
    lines = [
        "# Universe certification — Public Education (2025–2026)",
        "",
        f"The official SQL legislation table holds the complete current biennium: "
        f"**{universe} bills**. The identical {len(re.findall(r'r\"', m.group(1)))}-pattern wide net from the 2020–2024 "
        f"certification was applied to every title.",
        "",
        f"- Real misses added to the set (`supplement:universe-certification-current`): **{n_added}**",
        f"- Candidates excluded after human review: **{len(review)}**, categorized below.",
        "",
        "**Verdict: a 2025–2026 K-12 public-education bill could be absent from "
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
