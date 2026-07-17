#!/usr/bin/env python3
"""Pass 1b: authoritative discovery from the LCB Subject Index of Bills.

The Legislative Counsel Bureau publishes an official subject index per
session (Reports > Tables and Index > Subject Index). Bills are indexed by
professional staff under headings like WATER, WATER RIGHTS AND APPROPRIATION
OF PUBLIC WATERS, DATA CENTERS, DROUGHT. This catches bills that keyword
title search misses (NELIS BillsTab search only matches name/title/summary).

Merges its findings into sources/nevada/water-scarcity/pass1/bills.json,
tagging each with found_by_terms = ["subject-index: HEADING"].

  python collectors/pass1_subject_index.py
  python collectors/pass1_subject_index.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import requests

OUT = Path("sources/nevada/water-scarcity/pass1")
BILLS = OUT / "bills.json"
CACHE_DIR = OUT / "cache_subject_index"
NELIS_CACHE = OUT / "cache_nelis.json"

BASE = "https://www.leg.state.nv.us"
UA = {"User-Agent": "ForumLegislativeBrief/1.0"}

SESSIONS = {
    "80": ("80th2019", f"{BASE}/Session/80th2019/Reports/TablesAndIndex/2019_80-index.html"),
    "81": ("81st2021", f"{BASE}/Session/81st2021/Reports/TablesAndIndex/2021_81-index.html"),
    "82": ("82nd2023", f"{BASE}/Session/82nd2023/Reports/TablesAndIndex/2023_82-index.html"),
    "83": ("83rd2025", f"{BASE}/Session/83rd2025/Reports/TablesAndIndex/Index.html"),
}

# Subject headings to harvest (regex against the cleaned heading text).
HEAD_PATTERNS = (
    r"^WATER\b",
    r"^WASTEWATER",
    r"^COLORADO RIVER",
    r"^LAKE POWELL",
    r"^STATE ENGINEER",
    r"^IRRIGATION",
    r"^DROUGHT",
    r"^WELLS\b",
    r"^WELL DRILLERS",
    r"^DATA CENTERS",
    r"^SOUTHERN NEVADA WATER",
    r"^MOAPA VALLEY WATER",
    r"^VIRGIN VALLEY WATER",
    r"^CARSON WATER",
    r"^MARLETTE LAKE",
    r"INTERSTATE WATERS",
    r"^WATER BANKING",
)

# Headings that match above but are not about water policy.
HEAD_EXCLUDE = (
    r"^WELLS, CITY OF",
    r"^WATER SLIDES",
)

# Entry-level keywords harvested from ANY heading (catches e.g. the 2023
# evaporative-cooling ordinance bill filed under BUILDING CODES).
ENTRY_KEYWORDS = (
    "data center",
    "desalination",
    "evaporative cooling",
    "closed-loop",
    "cloud seeding",
    "water importation",
)

IDENT_RE = re.compile(r">\s*((?:AB|SB|AJR|SJR|ACR|SCR)\s*\d+)\s*</a>")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", unescape(text)).replace("\u2011", "-").strip()


def fetch_index(session: str, url: str, refresh: bool) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{session}.html"
    if cache_file.exists() and not refresh:
        return cache_file.read_text(encoding="windows-1252", errors="replace")
    print(f"Fetching subject index {session}: {url}")
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    cache_file.write_bytes(r.content)
    time.sleep(0.75)
    return r.content.decode("windows-1252", errors="replace")


def parse_index(html: str) -> dict[str, dict]:
    """Return identifier -> {headings: [...], entries: [...]}."""
    picked: dict[str, dict] = {}
    starts = [m.start() for m in re.finditer(r"<p class=Level0", html)] + [len(html)]
    for a, b in zip(starts, starts[1:]):
        section = html[a:b]
        heading = strip_tags(section.split("</p>")[0])
        head_match = any(re.search(p, heading, re.I) for p in HEAD_PATTERNS) and not any(
            re.search(p, heading, re.I) for p in HEAD_EXCLUDE
        )
        for m in re.finditer(r"<p class=Level[123][^>]*>(.*?)</p>", section, re.S):
            entry_html = m.group(1)
            entry_text = strip_tags(entry_html)
            keyword_match = any(k in entry_text.lower() for k in ENTRY_KEYWORDS)
            if not (head_match or keyword_match):
                continue
            for ident in IDENT_RE.findall(entry_html):
                ident = re.sub(r"\s+", "", ident).upper()
                rec = picked.setdefault(ident, {"headings": [], "entries": []})
                short_head = heading.split("(")[0].strip()
                if short_head not in rec["headings"]:
                    rec["headings"].append(short_head)
                if len(rec["entries"]) < 8 and entry_text not in rec["entries"]:
                    rec["entries"].append(entry_text[:200])
    return picked


def resolve_nelis_key(session_path: str, identifier: str) -> tuple[str, str] | None:
    """Resolve AB123 -> (numeric NELIS bill key, canonical overview URL)."""
    url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{identifier}/Overview"
    try:
        r = requests.get(url, headers=UA, timeout=60)
        r.raise_for_status()
    except requests.RequestException as exc:
        print(f"  resolve failed for {identifier}: {exc}")
        return None
    m = re.search(r'name="SelectedBillKey"[^>]*value="(\d+)"', r.text)
    if not m:
        m = re.search(r'id="billKey"[^>]*value="(\d+)"', r.text)
    if not m:
        print(f"  no SelectedBillKey on page for {identifier}")
        return None
    key = m.group(1)
    title = ""
    tm = re.search(r"<title>\s*([^<]+?)\s*</title>", r.text)
    if tm:
        title = tm.group(1)
    time.sleep(0.5)
    return key, f"{BASE}/App/NELIS/REL/{session_path}/Bill/{key}/Overview"


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = load_json(BILLS, {})
    bills = payload.get("bills") or []
    by_key = {f"{b['session']}:{b['identifier']}": b for b in bills}
    nelis_cache = load_json(NELIS_CACHE, {})

    added = 0
    tagged = 0
    report = []
    for session, (session_path, url) in SESSIONS.items():
        html = fetch_index(session, url, args.refresh)
        found = parse_index(html)
        print(f"Session {session}: {len(found)} bills under selected headings/keywords")
        for ident, meta in sorted(found.items()):
            key = f"{session}:{ident}"
            terms = [f"subject-index: {h}" for h in meta["headings"]]
            if key in by_key:
                existing_terms = by_key[key].setdefault("found_by_terms", [])
                for t in terms:
                    if t not in existing_terms:
                        existing_terms.append(t)
                by_key[key]["passes_water_title_filter"] = True
                tagged += 1
                continue
            report.append({"key": key, "headings": meta["headings"], "entries": meta["entries"]})
            if args.dry_run:
                added += 1
                continue
            resolved = resolve_nelis_key(session_path, ident)
            if not resolved:
                continue
            nelis_key, nelis_url = resolved
            print(f"  + {key} ({', '.join(meta['headings'][:3])})")
            new_bill = {
                "session": session,
                "identifier": ident,
                "title": "",  # filled by enrich_abstracts from the Overview digest
                "abstract": "",
                "in_nelis": True,
                "in_openstates": False,
                "nelis_url": nelis_url,
                "openstates_url": None,
                "found_by_terms": terms,
                "passes_water_title_filter": True,
                "discovered_via": "lcb_subject_index",
            }
            bills.append(new_bill)
            by_key[key] = new_bill
            nelis_cache[key] = {
                "source": "nelis",
                "session": session,
                "session_path": session_path,
                "identifier": ident,
                "title": "",
                "abstract": "",
                "nelis_bill_key": nelis_key,
                "source_url": nelis_url,
                "found_by_terms": terms,
                "collected_at": now(),
            }
            added += 1

    if args.dry_run:
        print(json.dumps(report, indent=2))
        print(f"DRY RUN: would add {added} bills")
        return

    bills.sort(key=lambda b: (b["session"], b["identifier"]))
    payload["bills"] = bills
    counts = payload.setdefault("counts", {})
    counts["merged_bills"] = len(bills)
    counts["subject_index_added"] = counts.get("subject_index_added", 0) + added
    counts["passes_water_title_filter"] = sum(
        1 for b in bills if b.get("passes_water_title_filter")
    )
    payload["subject_index"] = {
        "updated_at": now(),
        "note": (
            "LCB Subject Index of Bills harvested per session; headings matched: "
            "water/wastewater/Colorado River/State Engineer/irrigation/drought/wells/"
            "data centers + entry keywords (data center, desalination, evaporative "
            "cooling, closed-loop, cloud seeding)."
        ),
        "added_bills": [r["key"] for r in report],
        "details": report,
    }
    save_json(BILLS, payload)
    save_json(NELIS_CACHE, nelis_cache)
    print(f"Done: +{added} new bills, {tagged} existing bills re-tagged -> {BILLS}")


if __name__ == "__main__":
    main()
