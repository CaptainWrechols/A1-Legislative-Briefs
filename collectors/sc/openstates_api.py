"""OpenStates v3 API fallback for South Carolina (rate-limited; needs a key).

Secondary/backfill route only — the primary discovery source is the
scstatehouse.gov full-text search, and the preferred OpenStates route is the
bulk CSVs (:mod:`collectors.sc.openstates_bulk`), which have no rate limit.

Use this module when a specific bill needs OpenStates metadata (abstracts,
classified actions, OCD ids) and the bulk files are not on disk. Free-tier
limits are harsh (~10 requests/min, 500/day), so calls are cached on disk and
throttled hard, with long backoff on 429 — the same design proven for NH.

Requires ``OPENSTATES_API_KEY`` (free, issued instantly at
https://open.pluralpolicy.com/accounts/profile/). Without a key every function
soft-fails to None and the caller must record a data gap.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

API = "https://v3.openstates.org"
JURISDICTION = "South Carolina"
CACHE = Path("sources/south-carolina/_cache/openstates-api")
MIN_INTERVAL = float(os.environ.get("OPENSTATES_MIN_INTERVAL", "7"))  # ~8/min
_last_call = 0.0


def api_key() -> str | None:
    return os.environ.get("OPENSTATES_API_KEY") or None


def _get(path: str, params: dict) -> dict | None:
    """Throttled, cached, soft-failing GET against the v3 API."""
    global _last_call
    key = api_key()
    if not key:
        print("  [soft-fail] OPENSTATES_API_KEY not set; record a data gap")
        return None
    CACHE.mkdir(parents=True, exist_ok=True)
    cache_name = json.dumps([path, sorted(params.items())], separators=(",", ":"))
    cache_file = CACHE / (str(abs(hash(cache_name))) + ".json")
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    for attempt in range(5):
        wait = _last_call + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()
        try:
            r = requests.get(f"{API}{path}", params={**params},
                             headers={"X-API-KEY": key}, timeout=45)
        except requests.RequestException as exc:
            print(f"  [soft-fail] OpenStates {path}: {exc}")
            return None
        if r.status_code == 429:
            backoff = 60 * (attempt + 1)
            print(f"  [429] OpenStates rate limit; sleeping {backoff}s")
            time.sleep(backoff)
            continue
        if r.status_code != 200:
            print(f"  [soft-fail] OpenStates {path} -> {r.status_code}")
            return None
        data = r.json()
        cache_file.write_text(json.dumps(data), encoding="utf-8")
        return data
    return None


def search_bills(term: str, session_identifier: str, *, page: int = 1) -> dict | None:
    """One page of full-text bill search for a term in one SC session."""
    return _get("/bills", {
        "jurisdiction": JURISDICTION,
        "session": session_identifier,
        "q": term,
        "sort": "updated_desc",
        "page": page,
        "per_page": 20,
        "include": ["abstracts", "sponsorships"],
    })


def bill_detail(session_identifier: str, bill_no: str) -> dict | None:
    """Detail for one known bill (Pass 2: detail on known bills only)."""
    # v3 path form: /bills/sc/{session}/{identifier with space, e.g. "H 4025"}
    ident = bill_no.upper().replace(" ", "")
    spaced = f"{ident[0]} {ident[1:]}"
    return _get(f"/bills/sc/{session_identifier}/{spaced}", {
        "include": ["abstracts", "sponsorships", "actions", "votes", "versions"],
    })


if __name__ == "__main__":
    print(f"OPENSTATES_API_KEY set: {bool(api_key())}")
    if api_key():
        res = search_bills("minimum wage", "2025-2026")
        n = (res or {}).get("pagination", {}).get("total_items")
        print(f"  'minimum wage' 2025-2026: total_items={n}")
