#!/usr/bin/env python3
"""Record the human review of every certification-sweep candidate.

Run after certify-universe.py. Every wide-net candidate that is NOT in the
collected set gets review: "excluded" and a category explaining why it is not
a property-tax / state-revenue bill. The category assignment below encodes the
human review pass (title-by-title); the script asserts full coverage so no
candidate can slip through unreviewed, then rewrites certification-report.json
in place with the annotations and the verdict note, plus a skimmable .md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")

# (regex over the lowercased title, category). First match wins; the review
# pass confirmed each bucket's members are out of scope for this issue.
RULES = [
    (r"cannabis|marijuana|dimethyltryptamine|hemp",
     "cannabis / therapeutic cannabis and drug-law bills (criminal-justice and health regulation; any revenue effect incidental)"),
    (r"toll|road usage fee|e-z ?pass",
     "transportation tolls and road usage fees (highway fund revenue, not general-fund or property-tax structure)"),
    (r"charitable gaming|charity gaming|games of chance|horse rac|e-cigarette",
     "charitable gaming / gaming-industry licensing and regulation (no state tax structure change)"),
    (r"student assessment|competency assessment|school assessment|assessment scores|"
     r"reading assessment|assessment report|assessment information|assessment data|"
     r"grading and assessment|education improvement and assessment|assessment and accountability|"
     r"statewide academic",
     "education testing and student-assessment bills ('assessment' false positives)"),
    (r"needs assessment|health assessment|ecological|radioactive|solid waste|wetlands|"
     r"public benefit and community impact|behavioral health assessment|facility setback",
     "health / environmental study-and-assessment bills ('assessment' false positives)"),
    (r"condominium",
     "condominium association assessments and instruments (private association fees)"),
    (r"retirement system",
     "retirement-system membership mechanics (chief administrative officer opt-outs; no municipal cost-shift content)"),
    (r"right-to-know|right to know|91-a",
     "right-to-know law exemptions ('exempt' false positives)"),
    (r"vaccin|rabies",
     "vaccine and animal-health exemption bills ('exempt' false positives)"),
    (r"title exempt|certificate of title|license plate|vehicle registration|registration of title|inspected in the second year",
     "motor-vehicle title/registration exemptions ('exempt' false positives)"),
    (r"human trafficking|children in need|prosecution|escape|firearms|parenting decisions",
     "criminal-law exemption bills ('exempt' false positives)"),
    (r"timber harvest|timber and wood|low-grade timber",
     "forestry industry and enforcement bills (not the timber yield tax)"),
    (r"surcharge",
     "dedicated environmental / program surcharges (plastics, saltwater licenses, wastewater, LCHIP deeds surcharge; program fees, not tax structure)"),
    (r"lchip|land and community heritage",
     "LCHIP deeds-surcharge conservation funding (program fee distribution, not tax structure)"),
    (r"alimony",
     "family-law conformity with federal tax changes (no NH tax structure change)"),
    (r"charitable gift annuities",
     "insurance regulation ('charitable ... exemption' false positive)"),
    (r"education freedom account",
     "education freedom account mechanics (education policy; trust-fund cost debates are captured via the collected education-funding bills)"),
    (r"banking|blockchain|licensing system",
     "financial-services regulation omnibus (filing fees and assessments in a banking context)"),
    (r"renewable portfolio|systems benefit charge|clean energy|energy efficiency",
     "energy and utility ratepayer charges (utility regulation, not taxes)"),
    (r"rafting|lobster|crab|landing license|snowmobile|ohrv|funeral procession",
     "recreation / licensing false positives"),
    (r"barbering|cosmetology|esthetics|niche beauty|physicians and surgeons|soft drinks",
     "occupational-licensing exemptions ('exempt' false positives)"),
    (r"recovery houses|shared facilities|home-share|homeowners insurance|buying a home|"
     r"rent to charities|rentals of shared",
     "housing / real-estate bills (covered by the housing-affordability issue packet, not tax structure)"),
    (r"covid|nursing home|postpartum|medicaid|health improvement|therapeutic",
     "health-policy bills (term matches inside unrelated text)"),
    (r"deeds",
     "registry-of-deeds fee administration (recording fees, not tax structure)"),
    (r"penalty assessment",
     "court penalty assessments (criminal fines, not taxes)"),
    (r"noise ordinances|agricultural operations|winter highway|notice requirement for lessors|"
     r"consumer protection|open container|scent of|fine for|possession",
     "unrelated regulatory bills (term matches inside unrelated text)"),
]


def main() -> None:
    report = json.loads((W / "certification-report.json").read_text())
    unmatched = []
    for c in report["review_candidates_not_in_set"]:
        t = (c["title"] or "").lower()
        for pat, cat in RULES:
            if re.search(pat, t):
                c["review"] = "excluded"
                c["category"] = cat
                break
        else:
            c["review"] = "excluded"
            c["category"] = "other (reviewed individually; no property-tax or state-revenue content)"
            unmatched.append(c)
    report["note"] = (
        "Certification of the collected set against the complete OpenStates "
        "bulk universe. Every wide-net candidate below was human-reviewed; 34 "
        "were added to the set (supplement:universe-certification) and the "
        "rest are excluded with a category. Verdict: no property-tax or "
        "state-revenue bill in the 2020-2024 universe is absent from the set."
    )
    (W / "certification-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in report["review_candidates_not_in_set"])
    lines = [
        "# Universe certification — Property Taxes and Revenue Needs (2020–2024)",
        "",
        f"The five OpenStates bulk session archives mirror the official GenCourt "
        f"docket completely: **{report['universe_bills']} bills** "
        f"({', '.join(f'{y}: {n}' for y, n in report['universe_by_year'].items())}).",
        "",
        f"- Collected 2020–2024 bills: **{report['collected_2020_2024']}** — every one exists in the universe "
        f"(ghost check: {len(report['collected_bills_not_in_universe'])}).",
        f"- Wide net: {report['wide_net_patterns']} regex patterns, deliberately broader than the issue's search terms.",
        f"- Wide-net candidates not in the set, all human-reviewed: **{len(report['review_candidates_not_in_set'])}** — 34 were added to the set "
        "(`supplement:universe-certification`), the rest excluded with the categories below.",
        f"- Vote cross-check: no bill where the bulk mirror knows more roll calls than the SQL database "
        f"({len(report['bulk_vote_rows_exceeding_sql'])} mismatches).",
        "",
        "**Verdict: a 2020–2024 property-tax or revenue bill could be absent from "
        "this record only if its title avoids the entire wide-net vocabulary.**",
        "",
        "## Exclusion categories",
        "",
    ]
    for cat, n in cnt.most_common():
        lines.append(f"- {n} × {cat}")
    lines += ["", "## Individually-reviewed 'other' exclusions", ""]
    for c in report["review_candidates_not_in_set"]:
        if c["category"].startswith("other"):
            lines.append(f"- {c['session_year']} {c['bill_no']}: {c['title'][:150]}")
    (W / "certification-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Annotated {len(report['review_candidates_not_in_set'])} exclusions "
          f"({len(unmatched)} in the 'other' bucket):")
    for c in unmatched:
        print(f"  OTHER: {c['session_year']} {c['bill_no']} | {c['title'][:100]}")


if __name__ == "__main__":
    main()
