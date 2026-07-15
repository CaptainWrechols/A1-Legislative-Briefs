#!/usr/bin/env python3
"""Pass 1: bill id, title, abstract from NELIS + OpenStates (cached).

  python collectors/pass1_bills.py
  python collectors/pass1_bills.py --refresh
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
SEARCH_CACHE = OUT / "cache_searches.json"
OPENSTATES_URL = "https://v3.openstates.org/bills"

SESSION_PATHS = {"80": "80th2019", "81": "81st2021", "82": "82nd2023", "83": "83rd2025"}

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


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def norm_id(identifier: str) -> str:
    return re.sub(r"\s+", "", identifier or "").upper()


def is_water(title: str, abstract: str = "") -> bool:
    blob = f"{title} {abstract}".lower()
    return any(w in blob for w in WATER_WORDS)


def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(text or ""))
    return re.sub(r"\s+", " ", text).strip()


def get(url: str, *, params=None, headers=None) -> requests.Response:
    last = None
    for i in range(6):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=90)
            if r.status_code in {429, 502, 503, 504}:
                wait = int(r.headers.get("Retry-After") or min(120, 15 * (2**i)))
                print(f"  HTTP {r.status_code}; sleep {wait}s")
                time.sleep(wait)
                last = r
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            last = exc
            wait = min(120, 15 * (2**i))
            print(f"  failed ({exc}); sleep {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gave up: {url} ({last})")


def collect_nelis(cfg: dict, cache: dict, searches: dict, refresh: bool) -> None:
    ua = {"User-Agent": "ForumLegislativeBrief/1.0"}
    for session in cfg["sessions"]:
        sid = session["openstates_identifier"]
        path = SESSION_PATHS[sid]
        for term in cfg["search_terms"]:
            sk = f"nelis:{sid}:{term}"
            if sk in searches and not refresh:
                print(f"NELIS {path} / {term!r} (cached)")
                continue
            print(f"NELIS {path} / {term!r}")
            page = 1
            while True:
                url = (
                    f"https://www.leg.state.nv.us/App/NELIS/REL/{path}/HomeBill/BillsTab"
                    f"?Filters.SearchText={quote(term)}&Filters.PageSize=100&Page={page}"
                )
                html = get(url, headers=ua).text
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
                        "identifier": norm_id(m.group("id")),
                        "title": title,
                        "abstract": title,
                        "source_url": (
                            f"https://www.leg.state.nv.us/App/NELIS/REL/{path}"
                            f"/Bill/{m.group('key')}/Overview"
                        ),
                        "search_term": term,
                        "collected_at": now(),
                    }
                if f"Page={page + 1}" not in html:
                    break
                page += 1
                time.sleep(0.75)
            searches[sk] = now()
            time.sleep(0.75)


def collect_openstates(cfg: dict, cache: dict, searches: dict, refresh: bool, api_key: str) -> None:
    headers = {"X-API-KEY": api_key}
    for session in cfg["sessions"]:
        sid = session["openstates_identifier"]
        for term in cfg["search_terms"]:
            sk = f"openstates:{sid}:{term}"
            if sk in searches and not refresh:
                print(f"OpenStates {sid} / {term!r} (cached)")
                continue
            print(f"OpenStates {sid} / {term!r}")
            try:
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
                    data = get(OPENSTATES_URL, params=query, headers=headers).json()
                    results = data.get("results") or []
                    print(f"  page {page}: {len(results)}")
                    for bill in results:
                        ident = norm_id(bill.get("identifier") or "")
                        key = f"{sid}:{ident}"
                        if key in cache and not refresh:
                            continue
                        abstract = " ".join(
                            (a.get("abstract") or "") for a in (bill.get("abstracts") or [])
                        ).strip()
                        cache[key] = {
                            "source": "openstates",
                            "session": sid,
                            "identifier": ident,
                            "title": bill.get("title") or "",
                            "abstract": abstract,
                            "openstates_url": bill.get("openstates_url"),
                            "search_term": term,
                            "collected_at": now(),
                        }
                    max_page = (data.get("pagination") or {}).get("max_page", page)
                    if page >= max_page or not results:
                        break
                    page += 1
                    time.sleep(3.0)
                searches[sk] = now()
                time.sleep(3.0)
            except RuntimeError as exc:
                # Rate limits are common; keep NELIS results and retry this term next run.
                print(f"  OpenStates skipped ({exc})")
                time.sleep(5.0)
                continue


def merge(nelis: dict, openstates: dict) -> list[dict]:
    """Prefer recall: keep every NELIS search hit for human review.

    OpenStates-only additions still use the water-title helper (OpenStates
    full-text search is noisier). Each bill is tagged with
    passes_water_title_filter so reviewers can sort later.
    """
    merged: dict[str, dict] = {}
    for bill in nelis.values():
        key = f"{bill['session']}:{bill['identifier']}"
        title = bill.get("title") or ""
        abstract = bill.get("abstract") or ""
        merged[key] = {
            "session": bill["session"],
            "identifier": bill["identifier"],
            "title": title,
            "abstract": abstract,
            "in_nelis": True,
            "in_openstates": False,
            "nelis_url": bill.get("source_url"),
            "openstates_url": None,
            "passes_water_title_filter": is_water(title, abstract),
        }
    for bill in openstates.values():
        key = f"{bill['session']}:{bill['identifier']}"
        title = bill.get("title") or ""
        abstract = bill.get("abstract") or ""
        waterish = is_water(title, abstract)
        if key in merged:
            merged[key]["in_openstates"] = True
            merged[key]["openstates_url"] = bill.get("openstates_url")
            if not merged[key]["abstract"] and abstract:
                merged[key]["abstract"] = abstract
            merged[key]["passes_water_title_filter"] = (
                merged[key]["passes_water_title_filter"] or waterish
            )
        elif waterish:
            merged[key] = {
                "session": bill["session"],
                "identifier": bill["identifier"],
                "title": title,
                "abstract": abstract,
                "in_nelis": False,
                "in_openstates": True,
                "nelis_url": None,
                "openstates_url": bill.get("openstates_url"),
                "passes_water_title_filter": True,
            }
    return sorted(merged.values(), key=lambda b: (b["session"], b["identifier"]))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--skip-openstates", action="store_true")
    p.add_argument("--skip-nelis", action="store_true")
    args = p.parse_args()

    cfg = load_yaml()
    OUT.mkdir(parents=True, exist_ok=True)
    nelis = {} if args.refresh else load_json(NELIS_CACHE)
    openstates = {} if args.refresh else load_json(OPENSTATES_CACHE)
    searches = {} if args.refresh else load_json(SEARCH_CACHE)

    if not args.skip_nelis:
        collect_nelis(cfg, nelis, searches, args.refresh)
        save_json(NELIS_CACHE, nelis)
        save_json(SEARCH_CACHE, searches)
        print(f"NELIS: {len(nelis)} cached")

    if not args.skip_openstates:
        key = os.environ.get("OPENSTATES_API_KEY")
        if not key:
            print("No OPENSTATES_API_KEY — skipping OpenStates")
        else:
            collect_openstates(cfg, openstates, searches, args.refresh, key)
            save_json(OPENSTATES_CACHE, openstates)
            save_json(SEARCH_CACHE, searches)
            print(f"OpenStates: {len(openstates)} cached")

    bills = merge(nelis, openstates)
    payload = {
        "pass": 1,
        "collected_at": now(),
        "note": (
            "All NELIS search hits are kept for human review. "
            "passes_water_title_filter marks stricter title matches."
        ),
        "counts": {
            "nelis_cached": len(nelis),
            "openstates_cached": len(openstates),
            "merged_bills": len(bills),
            "passes_water_title_filter": sum(
                1 for b in bills if b.get("passes_water_title_filter")
            ),
            "both_sources": sum(1 for b in bills if b["in_nelis"] and b["in_openstates"]),
        },
        "bills": bills,
    }
    save_json(OUT / "bills.json", payload)
    print(
        f"Done: {payload['counts']['merged_bills']} bills "
        f"({payload['counts']['passes_water_title_filter']} pass water-title filter; "
        f"{payload['counts']['both_sources']} in both) -> {OUT / 'bills.json'}"
    )


if __name__ == "__main__":
    main()
