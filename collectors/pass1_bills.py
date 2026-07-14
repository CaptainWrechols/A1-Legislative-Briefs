#!/usr/bin/env python3
"""Pass 1: collect bill id, title, and abstract only (NELIS + OpenStates).

Simple on purpose:
- No PDF downloads
- No votes / actions / sponsors
- Disk cache so re-runs skip bills we already have
- Slow OpenStates paging to reduce 429s

Usage:
  python collectors/pass1_bills.py
  python collectors/pass1_bills.py --refresh   # ignore cache and re-collect
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

CONFIG = Path("config/issues/nevada-water-scarcity.yaml")
OUT = Path("sources/nevada/water-scarcity/pass1")
NELIS_CACHE = OUT / "cache_nelis.json"
OPENSTATES_CACHE = OUT / "cache_openstates.json"
SEARCH_CACHE = OUT / "cache_searches.json"  # which session+term queries already finished
OPENSTATES_URL = "https://v3.openstates.org/bills"

SESSION_PATHS = {
    "80": "80th2019",
    "81": "81st2021",
    "82": "82nd2023",
    "83": "83rd2025",
}

# Keep titles that are actually about water (same idea for both sources).
WATER_WORDS = (
    "water",
    "groundwater",
    "colorado river",
    "consumptive use",
    "water rights",
    "irrigation",
    "drought",
    "aquifer",
    "wastewater",
    "reclaimed water",
    "snwa",
    "water conservation",
    "data center",
    "data centers",
)

BILL_RE = re.compile(
    r'<a id="(?P<id>AB\d+|SB\d+|AJR\d+|SJR\d+|SCR\d+|ACR\d+)" '
    r'href="/App/NELIS/REL/(?P<session>[^/]+)/Bill/(?P<key>\d+)/Overview">'
    r'(?P=id)</a>\s*</div>\s*<div class="col-md-10[^"]*">\s*(?P<title>.*?)\s*</div>',
    re.DOTALL | re.IGNORECASE,
)


def load_yaml() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def load_cache(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def norm_id(identifier: str) -> str:
    return re.sub(r"\s+", "", identifier or "").upper()


def is_water(title: str, abstract: str = "") -> bool:
    blob = f"{title} {abstract}".lower()
    return any(word in blob for word in WATER_WORDS)


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(text or ""))
    return re.sub(r"\s+", " ", text).strip()


def get_with_retry(url: str, *, params=None, headers=None, tries: int = 6) -> requests.Response:
    """GET with long backoff on 429/5xx. Never spin-loops."""
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=90)
            if r.status_code in {429, 502, 503, 504}:
                wait = int(r.headers.get("Retry-After") or min(120, 15 * (2**i)))
                print(f"  HTTP {r.status_code}; sleeping {wait}s")
                time.sleep(wait)
                last = r
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            last = exc
            wait = min(120, 15 * (2**i))
            print(f"  request failed ({exc}); sleeping {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gave up on {url}: {last}")


def collect_nelis(cfg: dict, cache: dict, searches: dict, refresh: bool) -> tuple[dict, dict]:
    """Search NELIS list pages only. Title field is the search-result summary."""
    ua = {"User-Agent": "ForumLegislativeBrief/1.0"}
    for session in cfg["sessions"]:
        sid = session["openstates_identifier"]
        path = SESSION_PATHS[sid]
        for term in cfg["search_terms"]:
            search_key = f"nelis:{sid}:{term}"
            if search_key in searches and not refresh:
                print(f"NELIS {path} / {term!r} (cached search, skip)")
                continue
            print(f"NELIS {path} / {term!r}")
            page = 1
            while True:
                url = (
                    f"https://www.leg.state.nv.us/App/NELIS/REL/{path}/HomeBill/BillsTab"
                    f"?Filters.SearchText={quote(term)}&Filters.PageSize=100&Page={page}"
                )
                html = get_with_retry(url, headers=ua).text
                matches = list(BILL_RE.finditer(html))
                if not matches:
                    break
                for m in matches:
                    key = f"{sid}:{norm_id(m.group('id'))}"
                    if key in cache and not refresh:
                        continue
                    title = clean_html(m.group("title"))
                    cache[key] = {
                        "source": "nelis",
                        "session": sid,
                        "session_path": path,
                        "identifier": norm_id(m.group("id")),
                        "title": title,
                        "abstract": title,  # NELIS list shows summary as the title block
                        "nelis_bill_key": m.group("key"),
                        "source_url": (
                            f"https://www.leg.state.nv.us/App/NELIS/REL/{path}"
                            f"/Bill/{m.group('key')}/Overview"
                        ),
                        "search_term": term,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    }
                if f"Page={page + 1}" not in html:
                    break
                page += 1
                time.sleep(0.75)
            searches[search_key] = datetime.now(timezone.utc).isoformat()
            time.sleep(0.75)
    return cache, searches


def collect_openstates(
    cfg: dict, cache: dict, searches: dict, refresh: bool, api_key: str
) -> tuple[dict, dict]:
    """Search OpenStates only (no per-bill detail calls)."""
    headers = {"X-API-KEY": api_key}
    for session in cfg["sessions"]:
        sid = session["openstates_identifier"]
        for term in cfg["search_terms"]:
            search_key = f"openstates:{sid}:{term}"
            if search_key in searches and not refresh:
                print(f"OpenStates session={sid} / {term!r} (cached search, skip)")
                continue
            print(f"OpenStates session={sid} / {term!r}")
            page = 1
            while True:
                query = [
                    ("jurisdiction", cfg.get("openstates_jurisdiction") or "Nevada"),
                    ("session", sid),
                    ("q", term),
                    ("per_page", 20),
                    ("page", page),
                    ("apikey", api_key),
                    ("include", "abstracts"),
                ]
                data = get_with_retry(OPENSTATES_URL, params=query, headers=headers).json()
                results = data.get("results") or []
                print(f"  page {page}: {len(results)}")
                for bill in results:
                    ident = norm_id(bill.get("identifier") or "")
                    key = f"{sid}:{ident}"
                    if key in cache and not refresh:
                        continue
                    abstracts = [
                        (a.get("abstract") or "") for a in (bill.get("abstracts") or [])
                    ]
                    abstract = " ".join(a for a in abstracts if a).strip()
                    cache[key] = {
                        "source": "openstates",
                        "session": sid,
                        "identifier": ident,
                        "title": bill.get("title") or "",
                        "abstract": abstract,
                        "openstates_id": bill.get("id"),
                        "openstates_url": bill.get("openstates_url"),
                        "search_term": term,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    }
                max_page = (data.get("pagination") or {}).get("max_page", page)
                if page >= max_page or not results:
                    break
                page += 1
                time.sleep(2.0)  # slow on purpose
            searches[search_key] = datetime.now(timezone.utc).isoformat()
            time.sleep(2.0)
    return cache, searches


def main() -> None:
    parser = argparse.ArgumentParser(description="Pass 1 bill discovery (titles + abstracts)")
    parser.add_argument("--refresh", action="store_true", help="Re-fetch even if cached")
    parser.add_argument("--skip-openstates", action="store_true")
    parser.add_argument("--skip-nelis", action="store_true")
    args = parser.parse_args()

    cfg = load_yaml()
    OUT.mkdir(parents=True, exist_ok=True)

    nelis = {} if args.refresh else load_cache(NELIS_CACHE)
    openstates = {} if args.refresh else load_cache(OPENSTATES_CACHE)
    searches = {} if args.refresh else load_cache(SEARCH_CACHE)

    if not args.skip_nelis:
        nelis, searches = collect_nelis(cfg, nelis, searches, args.refresh)
        save_json(NELIS_CACHE, nelis)
        save_json(SEARCH_CACHE, searches)
        print(f"NELIS cache: {len(nelis)} bills -> {NELIS_CACHE}")

    if not args.skip_openstates:
        api_key = os.environ.get("OPENSTATES_API_KEY")
        if not api_key:
            print("OPENSTATES_API_KEY not set; skipping OpenStates")
        else:
            openstates, searches = collect_openstates(
                cfg, openstates, searches, args.refresh, api_key
            )
            save_json(OPENSTATES_CACHE, openstates)
            save_json(SEARCH_CACHE, searches)
            print(f"OpenStates cache: {len(openstates)} bills -> {OPENSTATES_CACHE}")

    # Water filter + merge for review
    nelis_water = [b for b in nelis.values() if is_water(b.get("title", ""), b.get("abstract", ""))]
    os_water = [
        b for b in openstates.values() if is_water(b.get("title", ""), b.get("abstract", ""))
    ]

    merged: dict[str, dict] = {}
    for bill in nelis_water:
        key = f"{bill['session']}:{bill['identifier']}"
        merged[key] = {
            "session": bill["session"],
            "identifier": bill["identifier"],
            "title": bill["title"],
            "abstract": bill.get("abstract") or "",
            "in_nelis": True,
            "in_openstates": False,
            "nelis_url": bill.get("source_url"),
            "openstates_url": None,
        }
    for bill in os_water:
        key = f"{bill['session']}:{bill['identifier']}"
        if key in merged:
            merged[key]["in_openstates"] = True
            merged[key]["openstates_url"] = bill.get("openstates_url")
            if not merged[key]["abstract"] and bill.get("abstract"):
                merged[key]["abstract"] = bill["abstract"]
        else:
            merged[key] = {
                "session": bill["session"],
                "identifier": bill["identifier"],
                "title": bill["title"],
                "abstract": bill.get("abstract") or "",
                "in_nelis": False,
                "in_openstates": True,
                "nelis_url": None,
                "openstates_url": bill.get("openstates_url"),
            }

    bills = sorted(merged.values(), key=lambda b: (b["session"], b["identifier"]))
    payload = {
        "pass": 1,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "fields": ["session", "identifier", "title", "abstract"],
        "note": "Pass 1 only. Votes/actions/sponsors/PDFs are Pass 2 (later).",
        "counts": {
            "nelis_cached": len(nelis),
            "openstates_cached": len(openstates),
            "nelis_water": len(nelis_water),
            "openstates_water": len(os_water),
            "merged_water": len(bills),
            "both_sources": sum(1 for b in bills if b["in_nelis"] and b["in_openstates"]),
        },
        "bills": bills,
    }
    out_path = OUT / "bills.json"
    save_json(out_path, payload)
    print(
        f"Pass 1 done. {payload['counts']['merged_water']} water bills "
        f"({payload['counts']['both_sources']} in both) -> {out_path}"
    )


if __name__ == "__main__":
    main()
