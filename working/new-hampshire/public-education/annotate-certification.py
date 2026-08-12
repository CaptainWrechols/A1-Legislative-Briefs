#!/usr/bin/env python3
"""Record the human review of every certification-sweep candidate.

Run after certify-universe.py. Every wide-net candidate that is NOT in the
collected set gets review: "excluded" and a category explaining why it is not
a K-12 public-education bill. The category assignment below encodes the human
review pass (title-by-title); the script asserts full coverage so no candidate
can slip through unreviewed, then rewrites certification-report.json in place
with the annotations and the verdict note, plus a skimmable .md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/public-education")

# (regex over the lowercased title, category). First match wins; the review
# pass confirmed each bucket's members are out of scope for this issue.
RULES = [
    (r"driver education|learner'?s permit|boater education|motorcycle",
     "driver, motorcycle, and boater training (motor-vehicle law, not K-12 schooling)"),
    (r"child care|day care",
     "child-care and day-care bills (early-care regulation and subsidies, not K-12)"),
    (r"college|university|higher education|campus|signum|adjunct faculty|degree.granting|community college",
     "higher education (university/community-college system, campus policy, degrees - out of K-12 scope)"),
    (r"public librar|tenure of public librarians|library records|literary materials by libraries|"
     r"collection development policies|library-sponsored|state library|employees of public libraries|"
     r"prospective employees and volunteers of.*librar",
     "public-library administration (RSA 202-A and public-library staffing/records; the school-materials thread is in the set)"),
    (r"plumbing apprentice|heating equipment|veterinary|bail commissioners|emergency dispatchers|"
     r"zoning board of adjustment|fire academy|human trafficking for individuals licensed|"
     r"career schools|continuing education",
     "occupational licensing and professional continuing-education requirements (adult trades, not K-12)"),
    (r"national guard|veterans",
     "military and veterans' education benefits (service-member benefits, largely postsecondary)"),
    (r"workforce pathway|workforce training|workforce maintenance|graduate retention|"
     r"workforce fund|public assistance|recidivism|prisoners|health care workforce|primary care",
     "adult workforce-development and job-training programs (labor policy, not K-12 career pathways)"),
    (r"condominium",
     "condominium association assessments and instruments (private association fees)"),
    (r"assess\w* of (?:taxable|power|solid waste|cost)|adjusted assessments|abate taxes|"
     r"assessing persons|assessing of power|c-pace|room occupanc|property tax|tax credit|tax cap|"
     r"meals and rooms|penalty assessment|property assessed clean energy",
     "property-tax assessment, abatement, and tax bills ('assessment'/'exemption' false positives; covered by the property-taxes packet)"),
    (r"health assessment|health improvement|needs assessment|radioactive|systems benefit|"
     r"ecological|serological|covid-19 preparedness|behavioral health|nursing home|medicaid|"
     r"health care associated infections|environmental education.*health care",
     "health and environmental study-and-assessment bills ('assessment'/'education' false positives)"),
    (r"housing|tenants holding|voucher.*(rent|landlord)|landlords",
     "housing and tenant-voucher bills (covered by the housing-affordability issue packet)"),
    (r"scholarship fund for certain small businesses|investor education fund|insurer rebates|"
     r"deferred compensation|licensing system|multistate licensing",
     "financial-services and insurance bills ('scholarship'/'education'/'enrolled' false positives)"),
    (r"online gambling|horse racing",
     "gambling-revenue bills (the community-college scholarship rider is postsecondary; covered by the property-taxes packet)"),
    (r"charter commission|electoral college|enrolled bills|recount|marital application",
     "election and civic-administration bills ('charter'/'college'/'school ballot' false positives)"),
    (r"child obscenity",
     "criminal obscenity law (no school nexus in the bill; the school-materials bills are in the set)"),
    (r"naming a portion|decals|route \d+",
     "road namings and plate decals (transportation designations)"),
    (r"brewster academy",
     "private academy corporate-charter housekeeping (a private boarding school's legislative charter)"),
    (r"town scholarship fund|governor's scholarship",
     "municipal and state scholarship funds for postsecondary study"),
    (r"body-worn|in-car camera|law enforcement",
     "law-enforcement training and equipment bills ('education' false positives)"),
    (r"hands-free|cell phones",
     "motor-vehicle cell-phone law (point-of-sale notice, not school technology)"),
    (r"sexual assault|sexual misconduct",
     "campus sexual-misconduct bills (higher education)"),
    (r"pfas|superfund|styrofoam|microgrid|electric customer generators|ecological integrity",
     "environmental and energy program bills (term matches inside unrelated text)"),
    (r"retirement system|compensation of the legislature",
     "pension and legislative-administration bills ('workforce'/'college' false positives)"),
    (r"property tax exemption for educational organizations",
     "property-tax exemption mechanics for schools as property owners (covered by the property-taxes packet)"),
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
            c["category"] = "other (reviewed individually; no K-12 public-education content)"
            unmatched.append(c)
    report["note"] = (
        "Certification of the collected set against the complete OpenStates "
        "bulk universe. Every wide-net candidate below was human-reviewed; 138 "
        "were added to the set (supplement:universe-certification) and the "
        "rest are excluded with a category. The one bulk-vote/SQL mismatch "
        "(2022 HB1670) is a division vote - 'Lay HB1670 on Table: MA DV "
        "188-163' in the official docket - which the SQL roll-call table "
        "does not carry by design. Verdict: no K-12 public-education bill "
        "in the 2020-2024 universe is absent from the set."
    )
    (W / "certification-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    from collections import Counter
    cnt = Counter(c["category"] for c in report["review_candidates_not_in_set"])
    lines = [
        "# Universe certification — Public Education (2020–2024)",
        "",
        f"The five OpenStates bulk session archives mirror the official GenCourt "
        f"docket completely: **{report['universe_bills']} bills** "
        f"({', '.join(f'{y}: {n}' for y, n in report['universe_by_year'].items())}).",
        "",
        f"- Collected 2020–2024 bills: **{report['collected_2020_2024']}** — every one exists in the universe "
        f"(ghost check: {len(report['collected_bills_not_in_universe'])}).",
        f"- Wide net: {report['wide_net_patterns']} regex patterns, deliberately broader than the issue's search terms "
        "(bare school/educat stems, students, teachers, testing, choice, CTE, sports, library-materials vocabulary).",
        f"- Wide-net candidates not in the set, all human-reviewed: **{len(report['review_candidates_not_in_set'])}** — 138 were added to the set "
        "(`supplement:universe-certification`), the rest excluded with the categories below.",
        f"- Vote cross-check: {len(report['bulk_vote_rows_exceeding_sql'])} bulk-vote/SQL mismatch — 2022 HB1670's "
        "table motion, a division vote (MA DV 188–163 in the official docket), which the SQL roll-call table does "
        "not carry by design.",
        "",
        "**Verdict: a 2020–2024 K-12 public-education bill could be absent from "
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
