#!/usr/bin/env python3
"""Build the human-facing core Pass 2 dataset.

Merges:
  - Pass 1 titles + full NELIS digests (abstracts)
  - Pass 2 legislative progress milestones
  - Introduced vs enrolled text-change summaries (Governor-bound bills)

Output: sources/nevada/water-scarcity/processed/bills-core.json

  python collectors/pass2_build_core.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PASS1 = Path("sources/nevada/water-scarcity/pass1/bills.json")
PROCESSED = Path("sources/nevada/water-scarcity/processed")
PROGRESS = PROCESSED / "bill-legislative-progress.json"
TEXT_CHANGES = PROCESSED / "bill-text-changes.json"
SPONSORS = PROCESSED / "bill-sponsors.json"
OUT = PROCESSED / "bills-core.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def main() -> None:
    bills_payload = load_json(PASS1, {})
    bills = bills_payload.get("bills") or []
    progress = {
        f"{r['session']}:{r['bill_identifier']}": r
        for r in load_json(PROGRESS, [])
    }
    text_payload = load_json(TEXT_CHANGES, {})
    text_by_key = {
        f"{r['session']}:{r['bill_identifier']}": r
        for r in (text_payload.get("bills") or [])
    }
    sponsors_by_key: dict[str, list[dict]] = {}
    for row in load_json(SPONSORS, []):
        key = f"{row['session']}:{row['bill_identifier']}"
        sponsors_by_key.setdefault(key, []).append(
            {
                "name": row.get("name"),
                "classification": row.get("classification"),
                "primary": bool(row.get("primary")),
                "party": row.get("party"),
                "entity_type": row.get("entity_type"),
            }
        )

    core = []
    for bill in bills:
        key = f"{bill['session']}:{bill['identifier']}"
        prog = progress.get(key) or {}
        text = text_by_key.get(key)
        milestones = prog.get("milestones") or {}
        sponsors = sponsors_by_key.get(key) or []
        core.append(
            {
                "session": bill["session"],
                "identifier": bill["identifier"],
                "title": bill.get("title"),
                "official_title": bill.get("official_title"),
                "abstract": bill.get("abstract"),
                "abstract_source": bill.get("abstract_source"),
                "what_the_bill_does": bill.get("abstract"),
                "primary_sponsors": [
                    s for s in sponsors if s.get("classification") == "primary"
                ],
                "co_sponsors": [
                    s for s in sponsors if s.get("classification") == "cosponsor"
                ],
                "sponsors": sponsors,
                "final_disposition": prog.get("final_disposition"),
                "most_recent_action": prog.get("most_recent_action"),
                "origin_chamber_label": prog.get("origin_chamber_label"),
                "milestones": milestones,
                "governor_bound": bool(
                    milestones.get("signed_into_law")
                    or prog.get("final_disposition") == "Enacted"
                    or text is not None
                ),
                "text_changes": (
                    {
                        "status": text.get("status"),
                        "was_textually_amended": text.get("was_textually_amended"),
                        "similarity_ratio": text.get("similarity_ratio"),
                        "narrative": text.get("narrative"),
                        "amendments_listed": text.get("amendments_listed"),
                        "introduced_summary": text.get("introduced_summary"),
                        "enrolled_act_clause": text.get("enrolled_act_clause"),
                        "enrolled_legislative_counsel_digest": text.get(
                            "enrolled_legislative_counsel_digest"
                        ),
                        "notable_additions": text.get("notable_additions"),
                        "notable_removals": text.get("notable_removals"),
                        "introduced_url": (text.get("introduced") or {}).get("url"),
                        "enrolled_url": (text.get("enrolled") or {}).get("url"),
                    }
                    if text
                    else None
                ),
                "nelis_url": bill.get("nelis_url") or prog.get("nelis_url"),
                "openstates_url": bill.get("openstates_url") or prog.get("openstates_url"),
                "passes_water_title_filter": bill.get("passes_water_title_filter"),
            }
        )

    payload = {
        "pass": 2,
        "built_at": now(),
        "bill_count": len(core),
        "with_abstract": sum(1 for b in core if b.get("abstract")),
        "governor_bound_with_text_diff": sum(
            1 for b in core if b.get("text_changes") and b["text_changes"].get("status") == "ok"
        ),
        "note": (
            "Core review dataset: title + full NELIS digest (what the bill does) + "
            "legislative milestones + introduced-vs-enrolled changes for Governor-bound bills."
        ),
        "bills": core,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT}: bills={payload['bill_count']} "
        f"abstracts={payload['with_abstract']} "
        f"text_diffs={payload['governor_bound_with_text_diff']}"
    )


if __name__ == "__main__":
    main()
