#!/usr/bin/env python3
"""Supplemental 2020-2024 discovery from year-end official/civic indexes.

The keyless roll-call route misses older bills that moved only by voice or
division vote. This supplement adds bills identified in authoritative
year-end sources - the NHMA Final Legislative Bulletins (2021-2024, enacted
municipal laws), the NH OPD planning-legislation summaries, NH Housing's 2024
session summary, and NH Bulletin session roundups - then pulls each bill's
official record: archived GenCourt dockets (Wayback snapshots of
openstates.org / legiscan.com) and SQL roll calls/ballots.

Appends to pass1/bills.json, processed/bills-core.json,
processed/bill-votes.json and merges docket actions into
older-bill-actions.json. Every record is tagged with its discovery source.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/supplement-older-bills.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from collectors.nh import gencourt_sql as db  # noqa: E402

osmod = __import__("wayback-openstates")
lsmod = __import__("wayback-legiscan")

W = Path("working/new-hampshire/housing-affordability")
SRC = Path("sources/new-hampshire/housing-affordability")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

# (year, bill, discovery_source)
CANDIDATES = [
    (2020, "SB721", "NHBR/Sulloway 2020 coverage: attempted repeal of the Housing Appeals Board"),
    (2020, "SB735", "NHBR/Sulloway 2020 coverage: attempted repeal of the Housing Appeals Board"),
    (2021, "SB102", "NHMA Final Bulletin 2021: Community Revitalization Tax Relief for Housing Development (Chapter 200)"),
    (2021, "HB220", "NHMA Final Bulletin 2021: eviction notice / rental assistance (Chapter 131)"),
    (2021, "HB377", "NHMA Final Bulletin 2021: recovery house fire code exemption (Chapter 26)"),
    (2021, "HB286", "NHMA Final Bulletin 2021: committee on law enforcement response to homelessness (Chapter 39)"),
    (2021, "HB284", "NHMA Final Bulletin 2021: restoration of involuntarily merged lots (Chapter 136)"),
    (2021, "HB332", "NHMA Final Bulletin 2021: planning board deadline extension (Chapter 69)"),
    (2022, "HB1661", "NHMA Final Bulletin 2022: land use statutes modified (Chapter 272)"),
    (2022, "HB1021", "NHMA Final Bulletin 2022: local regulation of religious land use restricted (Chapter 291)"),
    (2022, "SB223", "NHMA Final Bulletin 2022: minimum size of recovery houses (Chapter 88)"),
    (2022, "SB334", "NHMA Final Bulletin 2022: committee to study property blight (Chapter 167)"),
    (2023, "HB42", "NHMA Final Bulletin 2023: land use board authority over homeowners associations (Chapter 114)"),
    (2023, "HB296", "NHMA Final Bulletin 2023: residential driveway authority (Chapter 187)"),
    (2023, "HB44", "NH Bulletin 2023 coverage: statewide duplex/fourplex zoning bill"),
    (2023, "SB231", "NH OPD 2023 legislation matrix: historic housing tax credit + housing appropriations (enacted via HB2)"),
    (2024, "HB1400", "NHMA Final Bulletin 2024 / NH Bulletin: housing omnibus - office conversions, parking limits, zoning process (Chapter 370)"),
    (2024, "HB1361", "NHMA Final Bulletin 2024: manufactured home subdivision statutes rewrite (Chapter 23)"),
    (2024, "HB1065", "NHMA Final Bulletin 2024 / NH Bulletin: sprinkler exemption for 3-4 family homes (Chapter 324)"),
    (2024, "HB1202", "NHMA Final Bulletin 2024 / NH Bulletin: 60-day DOT residential driveway permits (Chapter 367)"),
    (2024, "SB406", "NHMA Final Bulletin 2024: $2.5M to raise homeless shelter program rates (Chapter 290)"),
    (2024, "HB1567", "NHMA Final Bulletin 2024: home-based childcare zoning (Chapter 271)"),
    (2024, "SB454", "NH Bulletin 2024: doubling transfer-tax revenue to the Affordable Housing Fund (failed)"),
    (2024, "HB1399", "NHBR 2024 roundup: residential-units bill referred to interim study by Senate"),
]

TS = {2020: "20210301", 2021: "20220301", 2022: "20230301",
      2023: "20240301", 2024: "20250301"}


def fetch_snapshot(year: int, bill: str) -> tuple[dict | None, str, str]:
    """Try openstates (<=2022) then legiscan snapshots; return (parsed, url, kind)."""
    tries = []
    if year <= 2022:
        tries.append(("openstates", f"https://web.archive.org/web/{TS[year]}id_/https://openstates.org/nh/bills/{year}/{bill}/"))
    tries.append(("legiscan", f"https://web.archive.org/web/{TS[year]}id_/https://legiscan.com/NH/bill/{bill}/{year}"))
    if year <= 2022:
        tries.append(("legiscan", f"https://web.archive.org/web/{int(TS[year][:4])+1}0901id_/https://legiscan.com/NH/bill/{bill}/{year}"))
    else:
        tries.append(("legiscan", f"https://web.archive.org/web/{int(TS[year][:4])+1}0901id_/https://legiscan.com/NH/bill/{bill}/{year}"))
    for kind, wb in tries:
        for attempt in range(3):
            try:
                r = requests.get(wb, timeout=90, headers=UA, allow_redirects=True)
            except requests.RequestException:
                time.sleep(8)
                continue
            if r.status_code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            if r.status_code == 200 and len(r.text) > 15000:
                mod = osmod if kind == "openstates" else lsmod
                p = mod.parse(mod.to_lines(r.text))
                if p.get("actions"):
                    cdir = SRC / "raw" / f"wayback-{kind}"
                    cdir.mkdir(parents=True, exist_ok=True)
                    (cdir / f"{year}-{bill}.html").write_text(r.text, encoding="utf-8")
                    return p, r.url, kind
            break
        time.sleep(4)
    return None, "", ""


def official_title(year: int, bill: str, page_text_kind: str) -> str:
    """Title from the cached snapshot page (<title> tag), fallback empty."""
    import re
    for kind in ("openstates", "legiscan"):
        f = SRC / "raw" / f"wayback-{kind}" / f"{year}-{bill}.html"
        if f.exists():
            t = f.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"<title>([^<]+)", t)
            if m:
                title = m.group(1)
                title = re.sub(r"\s*\|\s*(LegiScan|Open States).*", "", title).strip()
                title = re.sub(r"^NH\s+\w+\d+\s*\|\s*", "", title)
                title = re.sub(r"\s*\|\s*\d{4}.*", "", title).strip()
                if len(title) > 12:
                    return title
    return ""


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    core = json.loads((SRC / "processed" / "bills-core.json").read_text())
    votes = json.loads((SRC / "processed" / "bill-votes.json").read_text())
    actions_doc = json.loads((W / "older-bill-actions.json").read_text())
    have = {(b["session_year"], b["bill_no"]) for b in pass1["bills"]}

    added = []
    for year, bill, source_note in CANDIDATES:
        if (year, bill) in have:
            print(f"{year} {bill}: already in set")
            continue
        parsed, snap_url, kind = fetch_snapshot(year, bill)
        title = official_title(year, bill, kind)
        rec = {
            "session_year": year,
            "bill_no": bill,
            "title": title,
            "found_by_terms": [],
            "sources": [f"supplement:{kind or 'index-only'}"],
            "discovery_source": source_note,
        }
        pass1["bills"].append(rec)
        core["bills"].append(dict(rec))
        summaries = db.rollcall_summaries(bill, year)
        vrec = {"session_year": year, "bill_no": bill,
                "roll_calls": summaries, "roll_call_count": len(summaries)}
        if summaries:
            vrec["ballots"] = db.rollcall_ballots(bill, year)
        votes["bills"].append(vrec)
        arec = {"session_year": year, "bill_no": bill, "title": title,
                "source": f"{kind}_wayback" if kind else "none",
                "snapshot": snap_url,
                "status": "ok" if parsed else "no_snapshot"}
        if parsed:
            arec.update(parsed)
        actions_doc["bills"] = [x for x in actions_doc["bills"]
                                if not (x["session_year"] == year and x["bill_no"] == bill)]
        actions_doc["bills"].append(arec)
        added.append((year, bill))
        last = (parsed or {}).get("actions", [{}])[0]
        print(f"{year} {bill}: {kind or 'NO SNAPSHOT'}; rolls={len(summaries)}; "
              f"title={title[:60]!r}; latest={last.get('date','')} {last.get('description','')[:60]}")
        time.sleep(3)

    pass1["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
    core["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
    votes["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
    actions_doc["bills"].sort(key=lambda b: (b["session_year"], b["bill_no"]))
    pass1["count"] = len(pass1["bills"])
    pass1["note"] += (" Supplemented with 2020-2024 bills identified in NHMA Final "
                      "Legislative Bulletins, NH OPD legislation summaries, NH Housing's "
                      "2024 session summary, and NH Bulletin roundups (voice/division-vote "
                      "bills the roll-call route cannot see); see discovery_source per bill.")
    (SRC / "pass1" / "bills.json").write_text(json.dumps(pass1, indent=2, default=str), encoding="utf-8")
    (SRC / "processed" / "bills-core.json").write_text(json.dumps(core, indent=2, default=str), encoding="utf-8")
    (SRC / "processed" / "bill-votes.json").write_text(json.dumps(votes, indent=2, default=str), encoding="utf-8")
    (W / "older-bill-actions.json").write_text(json.dumps(actions_doc, indent=2, default=str), encoding="utf-8")
    print(f"Added {len(added)} bills: {added}")


if __name__ == "__main__":
    main()
