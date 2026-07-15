#!/usr/bin/env python3
"""Fill full NELIS digests into Pass 1 abstracts (only for known bills).

Reads sources/nevada/water-scarcity/pass1/bills.json and, for each bill with a
NELIS URL, loads the Overview tab digest (not the short search-list title).

  python collectors/enrich_abstracts.py
  python collectors/enrich_abstracts.py --refresh
  python collectors/enrich_abstracts.py --limit 5
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

PASS1 = Path("sources/nevada/water-scarcity/pass1")
BILLS = PASS1 / "bills.json"
CACHE = PASS1 / "cache_abstracts.json"
UA = {"User-Agent": "ForumLegislativeBrief/1.0", "X-Requested-With": "XMLHttpRequest"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def bill_key(bill: dict) -> str:
    return f"{bill.get('session')}:{bill.get('identifier')}"


def parse_overview_url(url: str) -> tuple[str, str] | None:
    # .../App/NELIS/REL/{session_path}/Bill/{key}/Overview
    m = re.search(r"/App/NELIS/REL/([^/]+)/Bill/(\d+)/", url or "")
    if not m:
        return None
    return m.group(1), m.group(2)


def fetch_digest(session: requests.Session, session_path: str, bill_key_id: str) -> dict:
    warm = f"https://www.leg.state.nv.us/App/NELIS/REL/{session_path}/Bill/{bill_key_id}/Overview"
    session.get(warm, timeout=60)
    time.sleep(0.4)
    fill = (
        f"https://www.leg.state.nv.us/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
    )
    html = session.get(
        fill, params={"selectedTab": "Overview", "billKey": bill_key_id}, timeout=60
    ).text
    time.sleep(0.4)
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.select_one("#title")
    digest_el = soup.select_one("#digest")
    official = title_el.get_text(" ", strip=True) if title_el else ""
    digest = digest_el.get_text(" ", strip=True) if digest_el else ""
    digest = re.sub(r"\s+", " ", digest).strip()
    official = re.sub(r"\s+", " ", official).strip()
    if digest.lower() in {"", "this bill does not have a digest."}:
        digest = ""
    return {
        "official_title": official,
        "digest": digest,
        "fetched_at": now(),
        "session_path": session_path,
        "nelis_bill_key": bill_key_id,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Only first N bills (smoke test)")
    args = parser.parse_args()

    if not BILLS.exists():
        raise SystemExit(f"Missing {BILLS}. Run pass1_bills.py first.")

    payload = load_json(BILLS, {})
    bills = payload.get("bills") or []
    cache = {} if args.refresh else load_json(CACHE, {})
    session = requests.Session()
    session.headers.update(UA)

    targets = [b for b in bills if b.get("nelis_url")]
    if args.limit:
        targets = targets[: args.limit]

    print(f"Enriching abstracts for {len(targets)} bills (cache={len(cache)})")
    filled = 0
    failed = 0
    for i, bill in enumerate(targets, start=1):
        key = bill_key(bill)
        if key in cache and (cache[key].get("digest") or cache[key].get("official_title")) and not args.refresh:
            row = cache[key]
            body = row.get("digest") or row.get("official_title") or ""
            bill["abstract"] = body
            bill["official_title"] = row.get("official_title") or bill.get("official_title")
            bill["abstract_source"] = (
                "nelis_overview_digest" if row.get("digest") else "nelis_overview_title"
            )
            filled += 1
            print(f"[{i}/{len(targets)}] {key} (cached)")
            continue

        parsed = parse_overview_url(bill.get("nelis_url") or "")
        if not parsed:
            print(f"[{i}/{len(targets)}] {key} SKIP — bad NELIS URL")
            failed += 1
            continue
        session_path, nelis_id = parsed
        print(f"[{i}/{len(targets)}] {key} fetching Overview digest…")
        try:
            row = fetch_digest(session, session_path, nelis_id)
            # Prefer full digest; fall back to official title when NELIS has no digest.
            body = row.get("digest") or row.get("official_title") or ""
            if not body:
                raise RuntimeError("empty digest and official title")
            cache[key] = row
            bill["abstract"] = body
            bill["official_title"] = row.get("official_title") or ""
            bill["abstract_source"] = (
                "nelis_overview_digest" if row.get("digest") else "nelis_overview_title"
            )
            bill["abstract_fetched_at"] = row["fetched_at"]
            filled += 1
            save_json(CACHE, cache)  # checkpoint after each success
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {exc}")
            failed += 1

    payload["bills"] = bills
    payload["abstract_enrichment"] = {
        "filled": filled,
        "failed": failed,
        "updated_at": now(),
        "note": "abstract = NELIS Overview digest (#digest), not search-list title",
    }
    save_json(BILLS, payload)
    save_json(CACHE, cache)
    print(f"Done. filled={filled} failed={failed} -> {BILLS}")


if __name__ == "__main__":
    main()
