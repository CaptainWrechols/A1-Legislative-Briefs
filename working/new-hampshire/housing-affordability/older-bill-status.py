#!/usr/bin/env python3
"""Determine dispositions for 2020-2024 bills in the housing set.

GenCourt's SQL keeps only current-biennium bill status, but every chaptered
law is published as static HTML at gc.nh.gov/legislation/{year}/{BILL}.html
(the same government route hb2_fetch uses for HB2 2021). This script:

  1. probes that page for each pass1 bill with session_year <= 2024
     (present => became law; the page carries the chapter number);
  2. summarizes the bill's roll-call motions (Ought to Pass, Inexpedient to
     Legislate, Veto Override ...) so deaths can be staged without invention.

Output: working/new-hampshire/housing-affordability/older-bill-status.json
Run from repo root:
  python3 working/new-hampshire/housing-affordability/older-bill-status.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from collectors.nh import fortiweb  # noqa: E402

SRC = Path("sources/new-hampshire/housing-affordability")
OUT = Path("working/new-hampshire/housing-affordability/older-bill-status.json")
CACHE = SRC / "raw" / "chaptered"


def bill_file(bill_no: str) -> str:
    m = re.match(r"([A-Z]+)(\d+)", bill_no)
    prefix, num = m.group(1), m.group(2)
    return f"{prefix}{int(num):04d}"


def is_404(text: str) -> bool:
    title = re.search(r"<title>([^<]+)", text, re.I)
    return bool(title and "404" in title.group(1))


def find_chapter(text: str) -> str | None:
    m = re.search(r"CHAPTER\s+(\d+)", text)
    return m.group(1) if m else None


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    votes = json.loads((SRC / "processed" / "bill-votes.json").read_text())
    vidx = {(v["session_year"], v["bill_no"]): v for v in votes["bills"]}

    CACHE.mkdir(parents=True, exist_ok=True)
    session = fortiweb.new_session()
    results = []
    for b in pass1["bills"]:
        year, bill_no = b["session_year"], b["bill_no"]
        if year > 2024:
            continue
        url = f"https://gc.nh.gov/legislation/{year}/{bill_file(bill_no)}.html"
        cache = CACHE / f"{year}-{bill_file(bill_no)}.html"
        if cache.exists():
            text = cache.read_text(encoding="utf-8", errors="replace")
        else:
            try:
                r = fortiweb.get(session, url)
                text = r.text
            except Exception as exc:  # WAF hiccup: record and continue
                results.append({"session_year": year, "bill_no": bill_no,
                                "chaptered_page": "fetch_error", "url": url,
                                "error": str(exc)})
                continue
            cache.write_text(text, encoding="utf-8")
            time.sleep(1.0)
        chaptered = (not is_404(text)) and len(text) > 3000
        rec = {
            "session_year": year,
            "bill_no": bill_no,
            "title": b.get("title"),
            "url": url,
            "chaptered_page": bool(chaptered),
            "chapter": find_chapter(text) if chaptered else None,
        }
        rc = vidx.get((year, bill_no), {})
        rec["roll_call_motions"] = [
            {"body": r["legislativeBody"], "date": str(r["voteDate"])[:10],
             "motion": r["question_Motion"], "yeas": r["yeas"], "nays": r["nays"]}
            for r in rc.get("roll_calls", [])
        ]
        results.append(rec)
        print(f"{year} {bill_no}: chaptered={rec['chaptered_page']} "
              f"chapter={rec['chapter']} rolls={len(rec['roll_call_motions'])}")

    OUT.write_text(json.dumps({
        "note": ("Disposition evidence for 2020-2024 bills. chaptered_page=True "
                 "means gc.nh.gov publishes a chaptered final law for the bill "
                 "(became law). Deaths are staged from roll-call motions only; "
                 "nothing is invented. Bills without a chaptered page and "
                 "without a killing roll call have an unresolved final status."),
        "bills": results,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(results)} bills)")


if __name__ == "__main__":
    main()
