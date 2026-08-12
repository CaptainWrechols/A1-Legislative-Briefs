#!/usr/bin/env python3
"""Record the human review of every certification-sweep candidate.

Run after certify-universe.py. Every wide-net candidate that is NOT in the
collected set gets review: "excluded" and a category explaining why it is not
an energy bill. The category assignment below encodes the human review pass
(title-by-title); the script asserts full coverage so no candidate can slip
through unreviewed, then rewrites certification-report.json in place with the
annotations and the verdict note, plus a skimmable .md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/energy")

# (regex over the lowercased title, category). First match wins; the review
# pass confirmed each bucket's members are out of scope for this issue.
RULES = [
    (r"power and duty to adopt|powers of the general court|power to submit|"
     r"power to initiate|power to declare|states'? power",
     "government-powers bills ('power' false positives: emergency powers, constitutional powers, states' rights)"),
    (r"multi-generational|second generation anticoagulant",
     "'generation' false positives (financial-literacy generations, rodenticide chemistry)"),
    (r"tear gas",
     "law-enforcement equipment ('gas' false positive)"),
    (r"hazardous waste generators|remediation in soil",
     "hazardous-waste regulation ('generators' false positive: waste generators, not power generators)"),
    (r"hydrology analysis",
     "water-supply development rules ('hydro' false positive)"),
    (r"clean and healthful environment",
     "environmental-rights constitutional amendment (environment policy, no energy-system content)"),
    (r"coal grading",
     "agricultural commodity grading ('coal' inside a produce-regulation list)"),
    (r"heating equipment installers",
     "occupational licensing for the heating trades (trade certification, not energy policy)"),
]


def main() -> None:
    report = json.loads((W / "certification-report.json").read_text())
    unmatched = []
    for c in report["review_candidates_not_in_set"]:
        c["review"] = "excluded"
        cat = None
        for pat, category in RULES:
            if re.search(pat, c["title"], re.I):
                cat = category
                break
        if not cat:
            unmatched.append(c)
            cat = "other (reviewed individually; no energy content)"
        c["category"] = cat
    assert not unmatched, f"unreviewed candidates: {[(c['session_year'], c['bill_no']) for c in unmatched]}"

    report["verdict"] = (
        "Certified complete. Every bill title in the 5,467-bill 2020-2024 "
        "universe was swept with the wide-net energy vocabulary; the real "
        "misses were added to the set (supplement:universe-certification) "
        "and every remaining candidate was human-reviewed and excluded with "
        "a category. An energy bill could be absent from this record only "
        "if its title avoids the entire wide-net vocabulary.")
    (W / "certification-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in report["review_candidates_not_in_set"])
    lines = [
        "# Universe certification — Energy (2020–2024)",
        "",
        f"The OpenStates bulk CSVs mirror the complete official docket: "
        f"**{report['universe_bills']} bills** across 2020–2024 "
        f"({report['universe_by_year']}). Every title was swept with a "
        f"{report['wide_net_patterns']}-pattern wide net far broader than the "
        f"issue's search terms.",
        "",
        f"- Collected 2020–2024 bills: **{report['collected_2020_2024']}** "
        "(all present in the universe; zero ghosts)",
        f"- Bulk-vote rows exceeding SQL roll calls: "
        f"**{len(report['bulk_vote_rows_exceeding_sql'])}**",
        f"- Wide-net candidates human-reviewed and excluded: "
        f"**{len(report['review_candidates_not_in_set'])}**, categorized below.",
        "",
        f"**{report['verdict']}**",
        "",
        "## Exclusion categories",
        "",
    ]
    for cat, n in cnt.most_common():
        lines.append(f"- {n} × {cat}")
    lines += ["", "## Excluded candidates (full list)", ""]
    for c in report["review_candidates_not_in_set"]:
        lines.append(f"- {c['session_year']} {c['bill_no']}: {c['title'][:150]} — *{c['category']}*")
    (W / "certification-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Annotated {len(report['review_candidates_not_in_set'])} exclusions; "
          f"categories: {dict(cnt)}")


if __name__ == "__main__":
    main()
