#!/usr/bin/env python3
"""Resolve final actions + sponsors for 2022-2024 bills via archived OpenStates pages.

GenCourt keeps no bill status for past biennia and its static /legislation/
archive stops after 2021, so for 2022-2024 the only reachable mirror of the
official docket (without an API key) is the Internet Archive's snapshots of
openstates.org bill pages, which render the complete action history and
sponsor list. This fetches one snapshot per bill (taken after the session
ended), extracts the action list and sponsors, and writes
older-bill-actions.json for curation. Nothing is invented; every record
carries the snapshot URL it came from.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/wayback-openstates.py
"""

from __future__ import annotations

import html as htmllib
import json
import re
import time
from pathlib import Path

import requests

SRC = Path("sources/new-hampshire/housing-affordability")
OUT = Path("working/new-hampshire/housing-affordability/older-bill-actions.json")
CACHE = SRC / "raw" / "wayback-openstates"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"

# Snapshot target: shortly after each session's end-of-year, so the action
# history is complete.
TS = {2022: "20230301", 2023: "20240301", 2024: "20250301"}

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|"
          "Oct|Nov|Dec")
DATE_RE = re.compile(rf"^({MONTHS}) \d{{1,2}}, \d{{4}}$")


def to_lines(page: str) -> list[str]:
    t = re.sub(r"<script.*?</script>", "", page, flags=re.S)
    t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = htmllib.unescape(t)
    return [l.strip() for l in t.split("\n") if l.strip()]


def parse(lines: list[str]) -> dict:
    out: dict = {"actions": [], "sponsors": []}
    # Actions: after the "Actions" header, repeating [date, actor, description].
    try:
        i = len(lines) - 1 - lines[::-1].index("Actions")
    except ValueError:
        i = -1
    if i >= 0:
        j = i + 1
        cur_date = None
        # Rows render as [date, actor, description]; when several actions share
        # a date, the date is not repeated ([actor, description] only).
        while j + 1 < len(lines):
            if DATE_RE.match(lines[j]):
                cur_date = lines[j]
                j += 1
                continue
            if cur_date and lines[j] in ("House", "Senate", "Governor"):
                out["actions"].append({
                    "date": cur_date, "actor": lines[j],
                    "description": lines[j + 1],
                })
                j += 2
                continue
            break
    # Sponsors: between "Sponsors" and "Votes"/"Actions" — lines look like
    # [Name, Party, Senator|Representative, District, ..., Cosponsor|Primary...]
    try:
        s = lines.index("Sponsors")
    except ValueError:
        s = -1
    if s >= 0:
        end = len(lines)
        for stop in ("Votes", "Actions"):
            if stop in lines[s + 1:]:
                end = min(end, s + 1 + lines[s + 1:].index(stop))
        seg = lines[s + 1:end]
        role = "Primary sponsor"
        cur_name = None
        for k, l in enumerate(seg):
            if l in ("Democratic", "Republican", "Independent") and k > 0:
                cur_name = seg[k - 1]
                out["sponsors"].append({"name": cur_name, "party": l, "role": role})
            if l.lower().startswith("cosponsor"):
                role = "Cosponsor"
                # the marker precedes the *next* sponsor entries
    return out


def main() -> None:
    pass1 = json.loads((SRC / "pass1" / "bills.json").read_text())
    CACHE.mkdir(parents=True, exist_ok=True)
    results = []
    for b in pass1["bills"]:
        year, bill_no = b["session_year"], b["bill_no"]
        if year not in TS:
            continue
        target = f"https://openstates.org/nh/bills/{year}/{bill_no}/"
        wb = f"https://web.archive.org/web/{TS[year]}id_/{target}"
        cache = CACHE / f"{year}-{bill_no}.html"
        if cache.exists():
            text = cache.read_text(encoding="utf-8", errors="replace")
            final_url = f"(cached) {wb}"
        else:
            text, final_url = "", wb
            for attempt in range(4):
                try:
                    r = requests.get(wb, timeout=90, headers={"User-Agent": UA},
                                     allow_redirects=True)
                    if r.status_code == 200 and len(r.text) > 20000:
                        text, final_url = r.text, r.url
                        break
                    if r.status_code == 429:
                        time.sleep(20 * (attempt + 1))
                        continue
                    if r.status_code == 404:
                        break
                except requests.RequestException:
                    time.sleep(10)
            if text:
                cache.write_text(text, encoding="utf-8")
            time.sleep(6)
        rec = {"session_year": year, "bill_no": bill_no, "title": b.get("title"),
               "snapshot": final_url}
        if not text:
            rec["status"] = "no_snapshot"
            results.append(rec)
            print(f"{year} {bill_no}: NO SNAPSHOT")
            continue
        parsed = parse(to_lines(text))
        rec.update(parsed)
        rec["status"] = "ok" if parsed["actions"] else "parsed_empty"
        results.append(rec)
        last = parsed["actions"][0] if parsed["actions"] else None
        print(f"{year} {bill_no}: {len(parsed['actions'])} actions, "
              f"{len(parsed['sponsors'])} sponsors; latest: "
              f"{(last or {}).get('date')} {(last or {}).get('description','')[:60]}")

    OUT.write_text(json.dumps({
        "note": ("Action histories + sponsors for 2022-2024 bills, from Internet "
                 "Archive snapshots of openstates.org bill pages (OpenStates "
                 "mirrors the official GenCourt docket). Actions are listed "
                 "newest first, as rendered. Each record carries its snapshot "
                 "URL. Used to stage deaths that roll calls alone cannot "
                 "resolve; vote counts still come only from GenCourt SQL."),
        "bills": results,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(results)} bills)")


if __name__ == "__main__":
    main()
