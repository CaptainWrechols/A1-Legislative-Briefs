#!/usr/bin/env python3
"""Add the current-biennium (2025-2026) certification catches to the set.

The 2020-2024 certification swept the complete OpenStates bulk universe; this
supplement closes the same gap for 2025-2026 by sweeping EVERY title in the
official SQL legislation table (2,234 bills) with the identical wide net
(see certify-current-biennium.py) and adding the human-reviewed real misses.
Their titles use vocabulary the seed terms missed ('tax impact statements',
'budget caps' without 'tax', 'land value tax', 'levy payments', 'enterprise
value', C-PACER, SAU consolidation). Tagged source
'supplement:universe-certification-current' so re-collections preserve them.
Enrichment matches collect.py's SQL path: legislation record (with the
cross-biennium-year fallback), sponsors, roll calls, ballots.

Run from repo root.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import gencourt_sql as db  # noqa: E402

SRC = Path("sources/new-hampshire/property-taxes")

ADDS = [
    # tax transparency / communication thread
    (2025, "HB284"), (2025, "HB138"), (2025, "HB495"), (2025, "SB225"),
    (2026, "HB1581"),
    # tax caps / budget limits
    (2025, "SB105"), (2026, "HB1288"),
    # constitutional tax-law amendments (three-fifths failures)
    (2026, "CACR10"), (2026, "CACR12"),
    # exemptions, non-profits, and the property-tax base
    (2025, "HB625"), (2025, "HB421"), (2025, "HB425"), (2026, "HB1293"),
    (2026, "HB635"), (2026, "HB1380"), (2026, "HB1417"), (2026, "HB1654"),
    # local-option revenue
    (2025, "HB688"), (2025, "HB544"), (2026, "SB634"), (2026, "HB1583"),
    (2026, "HB1649"),
    # assessment / appeals administration
    (2025, "HB268"), (2026, "SB489"), (2025, "SB4"), (2025, "HB450"),
    # state revenue streams
    (2025, "HB290"), (2026, "HB1596"),
    # consolidation
    (2025, "HB765"), (2026, "HB1804"), (2026, "HB1818"),
]


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    core = json.loads((SRC / "processed" / "bills-core.json").read_text())
    votes = json.loads((SRC / "processed" / "bill-votes.json").read_text())
    actions = json.loads((SRC / "processed" / "bill-actions.json").read_text())
    have = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}
    sql_years = sorted(db.legislation_years())

    added = 0
    for year, bill in ADDS:
        if (year, bill) in have:
            print(f"{year} {bill}: already in set")
            continue
        lr = db.legislation_record(bill, year)
        rec_year_note = None
        if lr is None:
            for other in sql_years:
                if other == year:
                    continue
                lr = db.legislation_record(bill, other)
                if lr:
                    rec_year_note = other
                    break
        assert lr, f"{year} {bill}: no legislation record!"
        rec = {"session_year": year, "bill_no": bill,
               "title": lr.get("LSRTitle") or "",
               "found_by_terms": [],
               "sources": ["supplement:universe-certification-current"],
               "discovery_source": ("current-biennium certification sweep over the "
                                    "complete SQL legislation table (wide-net title "
                                    "match, human-reviewed)"),
               "expanded_bill_no": lr.get("ExpandedBillNo"),
               "general_status": lr.get("general_status"),
               "chapter_no": lr.get("ChapterNo"),
               "bill_type": lr.get("BillType"),
               "legislationID": lr.get("legislationID"),
               "effective_date": lr.get("EffectiveDate"),
               "text_available_in_sql": True}
        if rec_year_note:
            rec["biennium_record_year"] = rec_year_note
        sp = db.sponsors_by_legislation_id(lr["legislationID"])
        rec["sponsors"] = [
            {"name": f"{s['FirstName']} {s['LastName']}".strip(),
             "party": s.get("Party"), "body": s.get("LegislativeBody"),
             "prime": bool(s.get("primeSponsor"))}
            for s in sp]
        pass1["bills"].append(rec)
        core["bills"].append(dict(rec))
        summaries = db.rollcall_summaries(bill, year)
        vrec = {"session_year": year, "bill_no": bill,
                "roll_calls": summaries, "roll_call_count": len(summaries)}
        if summaries:
            vrec["ballots"] = db.rollcall_ballots(bill, year)
        votes["bills"].append(vrec)
        rows = db.docket_actions(bill, year)
        if not rows:
            for other in sql_years:
                if other != year:
                    rows = db.docket_actions(bill, other)
                    if rows:
                        break
        actions["bills"].append({
            "session_year": year, "bill_no": bill, "action_count": len(rows),
            "actions": [{"body": r["LegislativeBody"],
                         "date": str(r["StatusDate"])[:10],
                         "description": r["Description"]} for r in rows]})
        added += 1
        print(f"{year} {bill}: added; rolls={len(summaries)}; docket={len(rows)}; "
              f"{rec['title'][:65]}")
        time.sleep(0.3)

    for doc, name in ((pass1, "pass1/bills.json"), (core, "processed/bills-core.json"),
                      (votes, "processed/bill-votes.json"),
                      (actions, "processed/bill-actions.json")):
        doc["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
        if "count" in doc:
            doc["count"] = len(doc["bills"])
        (SRC / name).write_text(json.dumps(doc, indent=2, default=str), encoding="utf-8")
    print(f"Added {added} current-biennium certification bills; set now {len(pass1['bills'])}.")


if __name__ == "__main__":
    main()
