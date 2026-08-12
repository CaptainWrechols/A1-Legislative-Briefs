#!/usr/bin/env python3
"""Add the current-biennium (2025-2026) certification catches to the set.

The 2020-2024 certification swept the complete OpenStates bulk universe; this
supplement closes the same gap for 2025-2026 by sweeping EVERY title in the
official SQL legislation table (2,234 bills) with the identical wide net
(see certify-current-biennium.py) and adding the human-reviewed real misses.
Their titles use vocabulary the seed terms missed ('adequate public
education', 'education financing', school-budget and recess phrasings, the
foundation opportunity budget, IEP-facilitation, school-materials and
vaccine-clinic bills, dual enrollment). Tagged source
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

SRC = Path("sources/new-hampshire/public-education")

ADDS = [
    # ---- 2025 ----
    # school meals / health / operations
    (2025, "SB205"), (2025, "HB361"), (2025, "HB415"), (2025, "HB677"),
    (2025, "HB763"), (2025, "HB184"), (2025, "HB650"), (2025, "HB71"),
    # funding / budgets / SWEPT overlap
    (2025, "HB502"), (2025, "HB557"), (2025, "HB407"), (2025, "HB766"),
    # curriculum, special education, choice accountability
    (2025, "HB555"), (2025, "HB532"), (2025, "HB667"), (2025, "HB324"),
    (2025, "HB116"), (2025, "HB193"), (2025, "HB178"),
    # ---- 2026 ----
    # funding and the constitutional question
    (2026, "HB734"), (2026, "HB1579"), (2026, "HR28"), (2026, "HB1815"),
    (2026, "HB491"), (2026, "HB772"), (2026, "SB659"), (2026, "HB1456"),
    (2026, "HR40"), (2026, "HB1672"), (2026, "HB1220"),
    # schools: operations, safety, health
    (2026, "HB1449"), (2026, "HB1412"), (2026, "HB1688"), (2026, "HB1635"),
    (2026, "HB1640"), (2026, "SB463"), (2026, "SB433"), (2026, "HB1507"),
    (2026, "HB1829"), (2026, "HB1604"), (2026, "SB580"), (2026, "HB1731"),
    # choice / charters / parental rights / CTE bridge
    (2026, "CACR24"), (2026, "HB129"), (2026, "HB1774"), (2026, "HB1712"),
    (2026, "HB1645"), (2026, "HB716"), (2026, "HB1202"),
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
