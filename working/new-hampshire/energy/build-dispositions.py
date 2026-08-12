#!/usr/bin/env python3
"""Derive per-bill dispositions from official records (no invention).

Merges, per (session_year, bill_no):
  * current biennium: SQL docket actions (processed/bill-actions.json)
  * 2020-2024: complete official dockets mirrored in the OpenStates bulk CSVs
    (bulk-dockets.json)
  * roll calls everywhere (processed/bill-votes.json)
  * optional hand-researched resolutions (manual-resolutions.json), each with
    citations, for the rare bill the dockets cannot stage

Writes working/new-hampshire/energy/dispositions.json.
Every record carries the evidence string it was derived from.

Adapted for the energy issue from the housing pipeline script; the
2020-2021 Wayback fallback layers were dropped because the bulk dockets stage
every older bill in this set.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/energy")
SRC = Path("sources/new-hampshire/energy")

CH = {"H": "House", "S": "Senate"}


def classify_current(actions: list[dict]) -> tuple[str, str, str]:
    """(disposition, stage, evidence) from the full docket, latest-first scan."""
    joined = " || ".join(a["description"] for a in actions)
    m = re.search(r"Signed by (?:the )?Governor[^|]*?Chapter 0*(\d+)", joined)
    if m:
        return ("enacted", f"became law (Chapter {m.group(1)})", m.group(0)[:120])
    m = re.search(r"Law Without Signature[^|]*?Chapter 0*(\d+)", joined)
    if m:
        return ("enacted", f"became law without the Governor's signature (Chapter {m.group(1)})",
                m.group(0)[:120])
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
        if re.search(r"Conference Committee Report.*(Failed|: MF)", d, re.I):
            return ("died_between_chambers", f"conference report rejected by the {body}", d[:140])
        if re.search(r"Conference Committee Report[:;] Not (Filed|Signed Off)", d, re.I):
            return ("died_between_chambers", "died in a committee of conference (no agreed report)", d[:140])
        if re.search(r"Pending Motion Committee of Conference", d, re.I):
            return ("died_between_chambers", "died with the conference report pending at adjournment", d[:140])
        if re.search(r"Nonconcur.*(MA|Adopted)", d, re.I) and "Request" not in d:
            return ("died_between_chambers", f"{body} refused to accept the other chamber's changes; no conference", d[:140])
        if re.search(r"Refuses to Accede.*(MA|Adopted)", d, re.I):
            return ("died_between_chambers", f"{body} refused the other chamber's request for a conference committee", d[:140])
        if re.search(r"Lacking Necessary Three-Fifths Vote", d, re.I):
            return ("killed_floor", f"failed to reach the three-fifths vote a constitutional amendment needs in the {body}", d[:140])
        if re.search(r"Died,?\s*Session ended", d, re.I):
            return ("died_other", f"died in the {body} when the session ended", d[:140])
        if re.search(r"Reconsider.*ITL.*MF", d, re.I):
            return ("killed_floor", f"killed on the {body} floor (Inexpedient to Legislate; reconsideration failed)", d[:140])
        if re.search(r"Ought to Pass.*(MA|Adopted)", d, re.I) and actions[-1] is a:
            return ("passed", f"adopted/passed by the {body} (last recorded action)", d[:140])
        if re.search(r"Death of all un-acted", d, re.I):
            return ("died_other", f"died un-acted upon in the {body}", d[:140])
        if (re.search(r"Committee Report: Ought to Pass", d, re.I)
                and "Minority" not in d and d is actions[-1]["description"]):
            return ("died_other", f"committee recommended Ought to Pass but the "
                    f"{body} never took a floor vote before the session ended", d[:140])
    last = actions[-1]["description"] if actions else ""
    if any(re.search(r"Committee Report: Inexpedient to Legislate", a["description"], re.I)
           for a in actions):
        body = CH.get(actions[-1]["body"], actions[-1]["body"])
        return ("killed_committee",
                f"{body} committee recommended Inexpedient to Legislate; no final floor "
                "action recorded in the docket",
                next(a["description"] for a in actions
                     if "Committee Report: Inexpedient" in a["description"])[:140])
    return ("unresolved", f"last docket action: {last[:120]}", last[:140])


def _load_optional(path: Path) -> dict:
    if not path.exists():
        return {}
    doc = json.loads(path.read_text())
    return {(b["session_year"], b["bill_no"]): b for b in doc["bills"]}


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    dockets = {(b["session_year"], b["bill_no"]): b
               for b in json.loads((SRC / "processed" / "bill-actions.json").read_text())["bills"]}
    votes = {(b["session_year"], b["bill_no"]): b
             for b in json.loads((SRC / "processed" / "bill-votes.json").read_text())["bills"]}
    manual = _load_optional(W / "manual-resolutions.json")
    bulk_dockets = {}
    for key, acts in json.loads((W / "bulk-dockets.json").read_text())["bills"].items():
        y, b = key.split(":", 1)
        bulk_dockets[(int(y), b)] = [
            {"body": {"House": "H", "Senate": "S"}.get(
                (a.get("organization") or "").replace("New Hampshire ", ""),
                a.get("organization", "")),
             "date": a["date"], "description": a["description"]}
            for a in acts]

    all_keys = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}
    out = []
    for b in pass1["bills"]:
        key = (b["session_year"], b["bill_no"])
        rec = {"session_year": key[0], "bill_no": key[1], "title": b["title"]}
        rolls = votes.get(key, {}).get("roll_calls", [])
        if key[0] in (2021, 2023, 2025) and (key[0] + 1, key[1]) in all_keys:
            # First-year record of a biennium bill that continued into the
            # second year under the same number; count it once (next year) —
            # unless the first-year docket already reached a terminal action.
            k2 = (bulk_dockets.get(key) or
                  [{"description": a["description"]} for a in
                   (dockets.get(key) or {}).get("actions", [])])
            terminal = any(re.search(
                r"Inexpedient to Legislate.*(MA|Adopted)|Indefinitely Postpone.*(MA|Adopted)|"
                r"=== BILL KILLED ===|Signed by", a["description"], re.I) for a in k2)
            if not terminal:
                rec.update({"disposition": "carryover_duplicate",
                            "stage": f"same bill as {key[0]+1} {key[1]} (carried across "
                                     f"the biennium); see the {key[0]+1} record",
                            "evidence_source": "biennium carryover"})
                rec["roll_call_count"] = len(rolls)
                out.append(rec)
                continue
        if key in manual and manual[key].get("resolution"):
            m = manual[key]
            rec.update({"disposition": m.get("disposition", "resolved_manually"),
                        "stage": m["resolution"],
                        "evidence_source": m.get("resolution_source", "manual research"),
                        "citations": m.get("citations")})
        elif key in dockets and dockets[key]["actions"]:
            disp, stage, ev = classify_current(dockets[key]["actions"])
            rec.update({"disposition": disp, "stage": stage,
                        "evidence": ev, "evidence_source": "sql_docket"})
            if b.get("chapter_no"):
                rec["chapter"] = b["chapter_no"]
        elif key in bulk_dockets:
            disp, stage, ev = classify_current(bulk_dockets[key])
            rec.update({"disposition": disp, "stage": stage, "evidence": ev,
                        "evidence_source": "bulk_docket"})
        else:
            rec.update({"disposition": "unresolved", "stage": "no records",
                        "evidence_source": "none"})
        rec["roll_call_count"] = len(rolls)
        out.append(rec)

    (W / "dispositions.json").write_text(json.dumps({
        "note": ("Per-bill dispositions derived from official dockets (SQL for "
                 "2025-2026; the OpenStates bulk mirror of the GenCourt docket "
                 "for 2020-2024) and roll calls. Nothing invented; every record "
                 "names its evidence."),
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
