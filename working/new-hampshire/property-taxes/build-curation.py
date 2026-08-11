#!/usr/bin/env python3
"""Assemble curation-map.json for the NH property-taxes set (the judgment step).

Each entry: plain_topic (one plain sentence), theme (one of THEMES), and
relevance tier (core / adjacent / context). Context bills stay in the set for
audit but are excluded from headline numbers. Dispositions/stages are merged
in from dispositions.json (evidence-backed; nothing invented here).

The per-bill judgments live in curation-entries.json (same directory), keyed
"YEAR:BILL" -> [plain_topic, theme_key, relevance]; this script validates the
set is fully covered and merges dispositions in.

Run from repo root:
  python3 working/new-hampshire/property-taxes/build-curation.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")

THEMES = {
    "T1": "Property tax relief: exemptions, credits, and deferrals",
    "T2": "Assessment, abatement, and property tax administration",
    "T3": "The statewide education property tax and school funding",
    "T4": "State business taxes: BPT and BET",
    "T5": "The interest and dividends tax",
    "T6": "Meals and rooms, gaming, and other existing revenue streams",
    "T7": "New or broad-based taxes and constitutional tax limits",
    "T8": "Municipal revenue, state aid, and cost shifting",
    "T9": "Current use, timber, utility, and other property-tax bases",
    "T10": "School district and municipal consolidation or cooperation",
    "T11": "Tax caps and local budget limits",
    "CTX": "Context: not primarily a property-tax or revenue bill",
}


def main() -> None:
    disp = {f"{b['session_year']}:{b['bill_no']}": b
            for b in json.loads((W / "dispositions.json").read_text())["bills"]}
    E = json.loads((W / "curation-entries.json").read_text())
    missing = [k for k in disp if k not in E]
    extra = [k for k in E if k not in disp]
    assert not missing, f"bills without curation ({len(missing)}): {missing[:20]}"
    assert not extra, f"curation for unknown bills: {extra[:20]}"

    bills = []
    for key, (topic, tkey, rel) in sorted(E.items()):
        d = disp[key]
        bills.append({
            "bill_key": key,
            "session_year": d["session_year"],
            "bill_no": d["bill_no"],
            "title": d["title"],
            "plain_topic": topic,
            "theme": THEMES[tkey],
            "relevance": rel,
            "disposition": d["disposition"],
            "stage": d["stage"],
            "roll_call_count": d["roll_call_count"],
        })
    from collections import Counter
    out = {
        "issue": "new-hampshire-02-property-taxes",
        "note": ("Curation of the keyword-discovered set: one plain sentence, one "
                 "theme, and a relevance tier per bill. 'context' bills are kept "
                 "for audit but excluded from headline numbers; first-year records "
                 "of biennium carryover bills are counted once, in their decision "
                 "year."),
        "themes": list(THEMES.values()),
        "counts": {
            "total": len(bills),
            "by_relevance": dict(Counter(b["relevance"] for b in bills)),
            "policy_set": sum(1 for b in bills if b["relevance"] != "context"
                              and b["disposition"] != "carryover_duplicate"),
        },
        "bills": bills,
    }
    (W / "curation-map.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["counts"], indent=1))
    print(dict(Counter(b["theme"] for b in bills)))


if __name__ == "__main__":
    main()
