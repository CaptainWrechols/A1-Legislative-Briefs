#!/usr/bin/env python3
"""Derive per-bill dispositions from official records (no invention).

Merges, per (session_year, bill_no):
  * current biennium: SQL docket actions (processed/bill-actions.json)
  * 2020-2021: gc.nh.gov latest-version headers + archived dockets
    (older-bill-status.json)
  * 2022-2024: archived docket actions + cited research (older-bill-actions.json)
  * roll calls everywhere (processed/bill-votes.json)

Writes working/new-hampshire/housing-affordability/dispositions.json.
Every record carries the evidence string it was derived from.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")
SRC = Path("sources/new-hampshire/housing-affordability")

CH = {"H": "House", "S": "Senate"}


def classify_current(actions: list[dict]) -> tuple[str, str, str]:
    """(disposition, stage, evidence) from the full docket, latest-first scan."""
    joined = " || ".join(a["description"] for a in actions)
    m = re.search(r"Signed by (?:the )?Governor[^|]*?Chapter (\d+)", joined)
    if m:
        return ("enacted", f"became law (Chapter {m.group(1)})", m.group(0)[:120])
    if re.search(r"Vetoed by Governor", joined, re.I):
        if re.search(r"Veto Override", joined, re.I):
            return ("vetoed", "vetoed; override attempted (see roll calls)", "veto + override rows")
        return ("vetoed", "vetoed (no override action recorded as of collection)",
                next(a["description"] for a in actions if "Vetoed" in a["description"])[:120])
    for a in reversed(actions):
        d, body = a["description"], CH.get(a["body"], a["body"])
        if re.search(r"Inexpedient to Legislate.*Senate Rule 3-23", d, re.I):
            return ("killed_deadline", "killed at the Senate's end-of-year deadline (Senate Rule 3-23)", d[:140])
        if re.search(r"Inexpedient to Legislate.*(MA|Adopted)|=== BILL KILLED ===", d, re.I):
            return ("killed_floor", f"killed on the {body} floor (Inexpedient to Legislate)", d[:140])
        if re.search(r"Indefinitely Postpone.*(MA|Adopted)", d, re.I):
            return ("killed_floor", f"indefinitely postponed by the {body}", d[:140])
        if re.search(r"(Lay|Laid).*on Table.*(MA\b|Adopted)", d, re.I):
            return ("died_on_table", f"laid on the table in the {body}; never taken back up", d[:140])
        if re.search(r"Remove from Table.*MF", d, re.I):
            return ("died_on_table", f"stayed on the {body} table (motion to remove failed)", d[:140])
        if re.search(r"(Refer|Referred|Rereferred).*Interim Study.*(MA|MF)?|Refer for Interim Study", d, re.I):
            return ("interim_study", f"sent to interim study by the {body}", d[:140])
        if re.search(r"Conference Committee Report[:;] Not (Filed|Signed Off)", d, re.I):
            return ("died_between_chambers", "died in a committee of conference (no agreed report)", d[:140])
        if re.search(r"Pending Motion Committee of Conference", d, re.I):
            return ("died_between_chambers", "died with the conference report pending at adjournment", d[:140])
        if re.search(r"Nonconcur.*(MA|Adopted)", d, re.I) and "Request" not in d:
            return ("died_between_chambers", f"{body} refused to accept the other chamber's changes; no conference", d[:140])
        if re.search(r"Reconsider.*ITL.*MF", d, re.I):
            return ("killed_floor", f"killed on the {body} floor (Inexpedient to Legislate; reconsideration failed)", d[:140])
        if re.search(r"Ought to Pass.*(MA|Adopted)", d, re.I) and actions[-1] is a:
            return ("passed", f"adopted/passed by the {body} (last recorded action)", d[:140])
        if re.search(r"Death of all un-acted", d, re.I):
            return ("died_other", f"died un-acted upon in the {body}", d[:140])
    last = actions[-1]["description"] if actions else ""
    if any(re.search(r"Committee Report: Inexpedient to Legislate", a["description"], re.I)
           for a in actions[-3:]):
        body = CH.get(actions[-1]["body"], actions[-1]["body"])
        return ("killed_committee",
                f"{body} committee recommended Inexpedient to Legislate; no floor "
                "action recorded in the docket",
                next(a["description"] for a in actions
                     if "Committee Report: Inexpedient" in a["description"])[:140])
    return ("unresolved", f"last docket action: {last[:120]}", last[:140])


def classify_older(os_: dict, rolls: list[dict]) -> tuple[str, str, str] | None:
    """2020-2021 fallback: version header + archived docket + roll motions."""
    header = os_.get("version_header", "")
    docket = os_.get("docket_actions") or []
    if docket:
        d0 = docket[0]["description"]
        if re.search(r"Died on Table", d0, re.I):
            return ("died_on_table", "died on the table", d0[:140])
        if re.search(r"Laid on Table", d0, re.I):
            body = "Senate" if " SJ" in d0 else "House"
            return ("died_on_table", f"laid on the table in the {body} at the pandemic-shortened "
                    "session's end; never taken back up", d0[:140])
    for r in reversed(rolls):
        m = r.get("question_Motion") or ""
        yeas, nays = r.get("yeas") or 0, r.get("nays") or 0
        if "Veto Override" in m:
            if yeas < 2 * nays:  # needs two-thirds
                return ("vetoed", f"vetoed; House override failed {yeas}-{nays} (short of two-thirds)",
                        f"roll call: Veto Override {yeas}-{nays}")
            return ("vetoed", f"veto override roll call {yeas}-{nays}", "roll call")
        if m.strip() == "Table" and yeas > nays:
            return ("died_on_table", "laid on the table; never taken back up", f"roll call: Table {yeas}-{nays}")
        if "Remove from Table" in m and yeas < nays:
            return ("died_on_table", "stayed on the table (motion to remove failed)",
                    f"roll call: Remove from Table {yeas}-{nays}")
        if re.search(r"Inexpedient", m) and yeas > nays:
            return ("killed_floor", "killed on the floor (Inexpedient to Legislate)",
                    f"roll call: ITL {yeas}-{nays}")
        if re.search(r"OTP|Ought to Pass", m) and yeas < nays:
            return ("killed_floor", f"Ought to Pass failed on the floor {yeas}-{nays}",
                    f"roll call: {m} {yeas}-{nays}")
    if "AS INTRODUCED" in header or "AS AMENDED" in header:
        return ("died_other", f"died mid-process (latest official text: {header.title()})",
                f"gc.nh.gov version header: {header}")
    return None


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    dockets = {(b["session_year"], b["bill_no"]): b
               for b in json.loads((SRC / "processed" / "bill-actions.json").read_text())["bills"]}
    votes = {(b["session_year"], b["bill_no"]): b
             for b in json.loads((SRC / "processed" / "bill-votes.json").read_text())["bills"]}
    older_status = {(b["session_year"], b["bill_no"]): b
                    for b in json.loads((W / "older-bill-status.json").read_text())["bills"]}
    older_actions = {(b["session_year"], b["bill_no"]): b
                     for b in json.loads((W / "older-bill-actions.json").read_text())["bills"]}

    out = []
    for b in pass1["bills"]:
        key = (b["session_year"], b["bill_no"])
        rec = {"session_year": key[0], "bill_no": key[1], "title": b["title"]}
        rolls = votes.get(key, {}).get("roll_calls", [])
        if key == (2025, "SB84"):
            rec.update({"disposition": "carryover_duplicate",
                        "stage": "same bill as 2026 SB84 (introduced 2025, carried over); "
                                 "see the 2026 record",
                        "evidence_source": "biennium carryover"})
        elif key in dockets and dockets[key]["actions"]:
            disp, stage, ev = classify_current(dockets[key]["actions"])
            rec.update({"disposition": disp, "stage": stage,
                        "evidence": ev, "evidence_source": "sql_docket"})
            if b.get("chapter_no"):
                rec["chapter"] = b["chapter_no"]
        elif key in older_status:
            os_ = older_status[key]
            oa = older_actions.get(key, {})
            manual = os_.get("resolution") or oa.get("resolution")
            if os_.get("chapter"):
                rec.update({"disposition": "enacted",
                            "stage": f"became law (Laws of {key[0]}, Chapter {os_['chapter']})",
                            "evidence": f"gc.nh.gov chaptered final text (CHAPTER {os_['chapter']})",
                            "evidence_source": "gencourt_final_text"})
            elif manual:
                rec.update({"disposition": "resolved_manually", "stage": manual,
                            "evidence_source": os_.get("resolution_source") or oa.get("resolution_source") or oa.get("source"),
                            "citations": os_.get("citations") or oa.get("citations")})
            else:
                r = classify_older(os_, rolls)
                if r:
                    rec.update({"disposition": r[0], "stage": r[1], "evidence": r[2],
                                "evidence_source": "gencourt_version_header+rollcalls+archived_docket"})
                elif oa.get("actions"):
                    # Archived actions are newest-first; reverse into docket
                    # order and reuse the docket classifier (same phrasing).
                    acts = [{"body": {"House": "H", "Senate": "S"}.get(a.get("actor", ""), a.get("actor", "")),
                             "description": a["description"]}
                            for a in reversed(oa["actions"])]
                    disp, stage, ev = classify_current(acts)
                    if disp == "unresolved":
                        last = oa["actions"][0]
                        rec.update({"disposition": "see_actions",
                                    "stage": f"latest archived docket action: {last['date']} {last['description'][:110]}",
                                    "evidence_source": oa.get("source", "wayback")})
                    else:
                        rec.update({"disposition": disp, "stage": stage, "evidence": ev,
                                    "evidence_source": f"archived_docket:{oa.get('source', 'wayback')}"})
                else:
                    rec.update({"disposition": "unresolved", "stage": "no terminal evidence",
                                "evidence_source": "none"})
            if os_.get("version_header"):
                rec["gencourt_version_header"] = os_["version_header"]
            if os_.get("sponsors_line"):
                rec["sponsors_line"] = os_["sponsors_line"]
        else:
            rec.update({"disposition": "unresolved", "stage": "no records", "evidence_source": "none"})
        rec["roll_call_count"] = len(rolls)
        out.append(rec)

    (W / "dispositions.json").write_text(json.dumps({
        "note": ("Per-bill dispositions derived from official dockets, chaptered "
                 "texts, archived dockets, and cited research. Nothing invented; "
                 "every record names its evidence."),
        "bills": out,
    }, indent=2), encoding="utf-8")

    from collections import Counter
    c = Counter(r["disposition"] for r in out)
    print(dict(c))
    for r in out:
        if r["disposition"] in ("unresolved", "see_actions", "passed"):
            print(f"{r['disposition'].upper()}: {r['session_year']} {r['bill_no']} | {r['stage'][:110]}")


if __name__ == "__main__":
    main()
