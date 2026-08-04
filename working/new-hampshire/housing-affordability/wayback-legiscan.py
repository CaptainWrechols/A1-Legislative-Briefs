#!/usr/bin/env python3
"""Resolve final actions for remaining 2022-2024 bills via archived LegiScan pages.

Companion to wayback-openstates.py: openstates.org stopped being archived
after its 2023 move to pluralpolicy.com, so bills the OpenStates snapshots
could not resolve are looked up in Internet Archive snapshots of LegiScan
bill pages instead (LegiScan mirrors the official GenCourt docket verbatim,
including journal citations). Results are merged into
older-bill-actions.json with per-record provenance.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/wayback-legiscan.py
"""

from __future__ import annotations

import html as htmllib
import json
import re
import time
from pathlib import Path

import requests

SRC = Path("sources/new-hampshire/housing-affordability")
ACTIONS = Path("working/new-hampshire/housing-affordability/older-bill-actions.json")
CACHE = SRC / "raw" / "wayback-legiscan"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
TS = {2022: "20230301", 2023: "20240301", 2024: "20250301"}


def to_lines(page: str) -> list[str]:
    t = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = htmllib.unescape(t)
    return [l.strip() for l in t.split("\n") if l.strip()]


def parse(lines: list[str]) -> dict:
    out: dict = {"actions": [], "sponsors": []}
    for l in lines:
        if l.startswith("Status:") and "status_line" not in out:
            out["status_line"] = l
        if l.startswith("Spectrum:") and "sponsor_spectrum" not in out:
            out["sponsor_spectrum"] = l.replace("Spectrum:", "").strip()
    try:
        i = lines.index("History")
    except ValueError:
        return out
    j = i + 1
    # skip the Date/Chamber/Action header row
    while j < len(lines) and lines[j] in ("Date", "Chamber", "Action"):
        j += 1
    while j + 2 < len(lines) and re.match(r"^\d{4}-\d{2}-\d{2}$", lines[j]):
        out["actions"].append({
            "date": lines[j], "actor": lines[j + 1], "description": lines[j + 2],
        })
        j += 3
    return out


def fetch(session: requests.Session, year: int, bill_no: str) -> tuple[str, str]:
    target = f"https://legiscan.com/NH/bill/{bill_no}/{year}"
    for ts in (TS[year], "20250601", "20240601", "20230601"):
        wb = f"https://web.archive.org/web/{ts}id_/{target}"
        for attempt in range(3):
            try:
                r = session.get(wb, timeout=90, headers={"User-Agent": UA},
                                allow_redirects=True)
            except requests.RequestException:
                time.sleep(10)
                continue
            if r.status_code == 200 and "History" in r.text:
                return r.text, r.url
            if r.status_code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            break
        time.sleep(3)
    return "", target


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    doc = json.loads(ACTIONS.read_text())
    have = {(b["session_year"], b["bill_no"]) for b in doc["bills"]
            if b.get("status") == "ok"}
    CACHE.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    added = 0
    for b in pass1["bills"]:
        year, bill_no = b["session_year"], b["bill_no"]
        if year not in TS or (year, bill_no) in have:
            continue
        cache = CACHE / f"{year}-{bill_no}.html"
        if cache.exists():
            text = cache.read_text(encoding="utf-8", errors="replace")
            url = f"(cached) legiscan {year} {bill_no}"
        else:
            text, url = fetch(session, year, bill_no)
            if text:
                cache.write_text(text, encoding="utf-8")
            time.sleep(5)
        rec = {"session_year": year, "bill_no": bill_no, "title": b.get("title"),
               "source": "legiscan_wayback", "snapshot": url}
        if not text:
            rec["status"] = "no_snapshot"
        else:
            rec.update(parse(to_lines(text)))
            rec["status"] = "ok" if rec.get("actions") else "parsed_empty"
        # replace any earlier unresolved record for this bill
        doc["bills"] = [x for x in doc["bills"]
                        if not (x["session_year"] == year and x["bill_no"] == bill_no)]
        doc["bills"].append(rec)
        added += 1
        last = (rec.get("actions") or [{}])[0]
        print(f"{year} {bill_no}: {rec['status']}; latest: {last.get('date','')} "
              f"{last.get('description','')[:70]}")

    doc["bills"].sort(key=lambda x: (x["session_year"], x["bill_no"]))
    doc["note"] += (" 2023-2024 bills (and 2022 leftovers) come from archived "
                    "LegiScan bill pages (source=legiscan_wayback), which "
                    "mirror the GenCourt docket with journal citations.")
    ACTIONS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Updated {ACTIONS} (+{added} records)")


if __name__ == "__main__":
    main()
