#!/usr/bin/env python3
"""Diagnose OpenStates API connectivity for Nevada water-scarcity collection.

Run:
    export OPENSTATES_API_KEY=your-key-here
    python collectors/diagnose_openstates.py
"""

from __future__ import annotations

import json
import os
import sys

import requests

BASE = "https://v3.openstates.org"
SESSIONS = ["80", "81", "82", "83"]
JURISDICTIONS = [
    "Nevada",
    "nevada",
    "nv",
    "ocd-jurisdiction/country:us/state:nv",
]
KNOWN_BILL = ("82", "AB19")  # water bill from 2023 session (exists on NELIS)


def get_api_key() -> str:
    key = os.environ.get("OPENSTATES_API_KEY", "").strip()
    if not key:
        print("ERROR: Set OPENSTATES_API_KEY before running.", file=sys.stderr)
        sys.exit(1)
    return key


def call(api_key: str, path: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    params["apikey"] = api_key
    headers = {"X-API-KEY": api_key}
    response = requests.get(f"{BASE}{path}", params=params, headers=headers, timeout=120)
    return {
        "status": response.status_code,
        "url": response.url.split("apikey=")[0].rstrip("?&"),
        "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200],
    }


def count_results(body: object) -> int | str:
    if isinstance(body, dict):
        if "results" in body:
            return len(body["results"])
        if "pagination" in body:
            return body["pagination"].get("total_items", "?")
    return "n/a"


def main() -> None:
    api_key = get_api_key()
    print("OpenStates Nevada diagnostic\n" + "=" * 40)

    print("\n1. Jurisdiction metadata (sessions list)")
    meta = call(
        api_key,
        "/jurisdictions/ocd-jurisdiction/country:us/state:nv",
        {"include": "legislative_sessions"},
    )
    print(f"   HTTP {meta['status']}")
    if meta["status"] == 200 and isinstance(meta["body"], dict):
        sessions = meta["body"].get("legislative_sessions") or []
        ids = [s.get("identifier") for s in sessions if s.get("identifier")]
        print(f"   Sessions in metadata: {', '.join(ids[-8:])}")
    else:
        print(f"   Response: {json.dumps(meta['body'])[:300]}")

    session, bill_id = KNOWN_BILL
    print(f"\n2. Direct bill lookup: Nevada / {session} / {bill_id}")
    for juris in ["Nevada", "nv"]:
        result = call(api_key, f"/bills/{juris}/{session}/{bill_id}")
        title = ""
        if result["status"] == 200 and isinstance(result["body"], dict):
            title = (result["body"].get("title") or "")[:80]
        print(f"   jurisdiction={juris!r} -> HTTP {result['status']}  title={title!r}")

    print("\n3. Fetch all bills in session 82 (no text search)")
    for juris in JURISDICTIONS:
        result = call(
            api_key,
            "/bills",
            {"jurisdiction": juris, "session": "82", "per_page": 1, "page": 1},
        )
        total = count_results(result["body"])
        print(f"   jurisdiction={juris!r} -> HTTP {result['status']}  total={total}")

    print("\n4. Full-text search q=water in session 82")
    for juris in ["Nevada", "ocd-jurisdiction/country:us/state:nv"]:
        result = call(
            api_key,
            "/bills",
            {"jurisdiction": juris, "session": "82", "q": "water", "per_page": 5, "page": 1},
        )
        total = count_results(result["body"])
        print(f"   jurisdiction={juris!r} -> HTTP {result['status']}  results={total}")

    print("\n5. Summary interpretation")
    print("   - If step 2 returns HTTP 200: OpenStates has Nevada bill records.")
    print("   - If step 3 total > 0: use fetch-all + local filter (current collector).")
    print("   - If step 3 total = 0 but step 2 works: session/jurisdiction mismatch.")
    print("   - If step 4 = 0 but step 3 > 0: full-text search index is the problem.")
    print("   - If all steps fail with 401/403: check or rotate your API key.")


if __name__ == "__main__":
    main()
