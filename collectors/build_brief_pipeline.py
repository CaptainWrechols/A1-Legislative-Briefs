#!/usr/bin/env python3
"""Build synthesis, analysis, and appendix scaffolding from collected bill data."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BILLS_PATH = Path("sources/nevada/water-scarcity/processed/bills-combined.json")
WORKING = Path("working/nevada/water-scarcity")
BRIEF = Path("briefs/nevada/water-scarcity/version-0")
ISSUE_ID = "nevada-04-water-scarcity"


def load_bills() -> list[dict]:
    return json.loads(BILLS_PATH.read_text(encoding="utf-8"))


def session_label(session_path: str) -> str:
    mapping = {
        "80th2019": "2019",
        "81st2021": "2021",
        "82nd2023": "2023",
        "83rd2025": "2025",
    }
    return mapping.get(session_path, session_path)


def build_synthesis(bills: list[dict]) -> dict:
    facts = []
    fid = 1
    by_session: dict[str, list[dict]] = defaultdict(list)
    for bill in bills:
        by_session[bill["session"]].append(bill)

    for session_path, session_bills in sorted(by_session.items()):
        for bill in session_bills:
            facts.append(
                {
                    "fact_id": f"F-{fid:03d}",
                    "theme": "legislative_history_by_session",
                    "session": session_label(session_path),
                    "fact_type": "bill_identified",
                    "statement": f"{bill['identifier']} in {session_path}: {bill['title']}",
                    "source_keys": ["S-NELIS"],
                    "source_urls": [bill.get("source_url", "")],
                    "bill_identifier": bill["identifier"],
                    "confidence": "verified",
                    "is_forum_process_input": False,
                }
            )
            fid += 1

    return {
        "issue_id": ISSUE_ID,
        "synthesized_at": datetime.now(timezone.utc).isoformat(),
        "themes": {
            "legislative_history_by_session": facts,
            "data_gaps": [
                {
                    "fact_id": "F-GAP-001",
                    "statement": "Bill action timelines and vote records require additional NELIS detail scraping.",
                    "confidence": "verified",
                },
                {
                    "fact_id": "F-GAP-002",
                    "statement": "20-year enacted policy impact requires crosswalk to Bills that Became Law reports.",
                    "confidence": "verified",
                },
            ],
        },
        "bill_count": len(bills),
    }


def build_analysis(bills: list[dict]) -> tuple[dict, str]:
    by_session = Counter(session_label(b["session"]) for b in bills)
    title_keywords = Counter()
    for bill in bills:
        title = bill.get("title", "").lower()
        for kw in ["water", "groundwater", "conservation", "colorado", "rights"]:
            if kw in title:
                title_keywords[kw] += 1

    analysis = {
        "issue_id": ISSUE_ID,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "bills_per_session": dict(by_session),
        "title_keyword_hits": dict(title_keywords),
        "total_bills": len(bills),
    }

    memo_lines = [
        "# Analysis Memo — Nevada Water Scarcity",
        "",
        "## Scope and limitations",
        f"- {len(bills)} water-related bills identified via Nevada NELIS text search across four sessions.",
        "- Action dates, vote counts, and final disposition are not yet populated (INSUFFICIENT DATA at bill-action level).",
        "- Enacted-law impact over 20 years requires follow-up collection from NELIS 'Bills that Became Law' reports.",
        "",
        "## Session-by-session summary",
    ]
    for year in ["2019", "2021", "2023", "2025"]:
        count = by_session.get(year, 0)
        memo_lines.append(f"- **{year} session:** {count} water-related bills identified in NELIS search results [S-NELIS].")

    memo_lines += [
        "",
        "## Recurring policy approaches",
        f"- Titles frequently reference water, conservation, groundwater, and water rights (keyword hits: {dict(title_keywords)}) [S-NELIS].",
        "- Pattern certainty: **medium** (based on bill title text only).",
        "",
        "## Viability indicators (Version 0)",
        "- Water-related legislation appears regularly in each of the last four Nevada sessions.",
        "- Data gaps prevent assessment of enactment rates and bipartisan sponsorship until action/vote data is collected.",
        "",
    ]
    return analysis, "\n".join(memo_lines) + "\n"


def write_appendices(bills: list[dict]) -> None:
    BRIEF.mkdir(parents=True, exist_ok=True)
    gaps = [
        "# Appendix F: Data Gaps",
        "**Issue:** Growth, Water Scarcity, and Long-Term Supply in Nevada",
        "",
        "| Search Term or Topic | Session | Result | Notes |",
        "|---|---|---|---|",
        "| Bill actions and votes | All | Not yet collected | Requires NELIS bill detail scrape |",
        "| Enacted law impact (20 years) | All | Not yet collected | Requires Bills that Became Law crosswalk |",
        "| OpenStates full-text search | All | 0 results | Used NELIS fallback successfully |",
        "",
    ]
    (BRIEF / "appendix-f-data-gaps.md").write_text("\n".join(gaps), encoding="utf-8")

    for name, content in [
        ("appendix-b-bill-actions.md", "# Appendix B: Bill Actions\n\nNo action timelines collected yet.\n"),
        ("appendix-c-votes.md", "# Appendix C: Votes\n\nNo vote records were collected for this issue.\n"),
        (
            "appendix-d-statutes.md",
            "# Appendix D: Statutes\n\nSee sources/nevada/water-scarcity/processed/statute-links.json\n",
        ),
        (
            "appendix-e-agency-documents.md",
            "# Appendix E: Agency Documents\n\nSee sources/nevada/water-scarcity/processed/agency-documents.json\n",
        ),
    ]:
        (BRIEF / name).write_text(content, encoding="utf-8")

    registry = {
        "issue_id": ISSUE_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": [
            {
                "key": "S-NELIS",
                "title": "Nevada Legislature NELIS bill search",
                "url": "https://www.leg.state.nv.us/App/NELIS/",
                "type": "bill_record",
                "used_in_appendices": ["appendix-a-bills.md"],
            },
            {
                "key": "S25",
                "title": "LCB Data Centers Background Information",
                "url": "https://www.leg.state.nv.us/App/InterimCommittee/REL/Document/32531",
                "type": "agency_document",
            },
            {
                "key": "S13",
                "title": "Nevada Division of Water Resources - Water Planning",
                "url": "https://water.nv.gov/programs/water-planning",
                "type": "agency_document",
            },
            {
                "key": "S2",
                "title": "SNWA Where Your Water Comes From",
                "url": "https://www.snwa.com/water-resources/where-water-comes-from/",
                "type": "agency_document",
            },
        ],
    }
    (BRIEF / "sources-registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")


def write_executive_summary(bills: list[dict], analysis: dict) -> None:
    by_session = analysis["bills_per_session"]
    text = f"""# Legislative Brief Version 0 — Executive Summary
## Growth, Water Scarcity, and Long-Term Supply in Nevada
**State:** nevada
**Issue ID:** nevada-04-water-scarcity
**Brief version:** version-0
**Audience:** Internal Forum team (assembly viability assessment)
**Generated:** {datetime.now(timezone.utc).date().isoformat()}
**Status:** DRAFT — requires human review

---

### 1. Issue framing
Nevada faces persistent water scarcity pressures tied to Colorado River reliability, groundwater management, conservation, and growth-related demand [S-NELIS][S2]. Legislative activity in the last four sessions shows water remains an active policy area in Carson City [S-NELIS].

### 2. Legislative history (last 4 sessions)
NELIS text search identified {len(bills)} water-related bills across the 2019, 2021, 2023, and 2025 sessions: {by_session.get('2019', 0)} (2019), {by_session.get('2021', 0)} (2021), {by_session.get('2023', 0)} (2023), and {by_session.get('2025', 0)} (2025) [S-NELIS]. Examples include AB19 and AB20 (2023), which revise provisions relating to water [S-NELIS]. Bill action progression (committee, floor, enacted) is INSUFFICIENT DATA pending detailed NELIS bill history collection.

### 3. Enacted policy and 20-year impact
INSUFFICIENT DATA — this Version 0 brief identifies introduced and referenced measures but does not yet crosswalk to NELIS "Bills that Became Law" reports for enactment and impact analysis [S-NELIS].

### 4. Patterns and stall points
Water, conservation, groundwater, and water-rights language appears repeatedly in bill titles across all four sessions [S-NELIS]. This is an inference from title text, not from final disposition data. Stall points cannot be assessed until committee and floor actions are collected.

### 5. Bipartisan signals
INSUFFICIENT DATA — sponsor party data is not yet in the collected bill records.

### 6. Assembly viability indicators (Version 0)
Evidence suggests water remains a recurring legislative topic in Nevada with dozens of related measures per session in recent years [S-NELIS]. That pattern may indicate the issue is legislatively tractable for deliberation, but enactment feasibility cannot be assessed without action and vote data.

### 7. Key data gaps
- Bill action timelines and final disposition per bill
- Vote records and bipartisan sponsorship
- Enacted-law impact over 20 years
- OpenStates Application Programming Interface full-text search returned zero Nevada results; NELIS used as primary source

---
## Source notes
[S-NELIS] Nevada Legislature NELIS bill search — see appendix-a-bills.md
[S2] Southern Nevada Water Authority water supply overview
"""
    (BRIEF / "executive-summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    bills = load_bills()
    WORKING.mkdir(parents=True, exist_ok=True)
    synthesis = build_synthesis(bills)
    (WORKING / "synthesis.json").write_text(json.dumps(synthesis, indent=2), encoding="utf-8")
    analysis, memo = build_analysis(bills)
    (WORKING / "analysis.json").write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    (WORKING / "analysis-memo.md").write_text(memo, encoding="utf-8")
    write_appendices(bills)
    write_executive_summary(bills, analysis)
    print(f"Pipeline scaffolding written for {len(bills)} bills")


if __name__ == "__main__":
    main()
