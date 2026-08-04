"""OpenStates backfill for New Hampshire sessions GenCourt no longer serves.

Why this exists: the live NH General Court site and its public SQL database
only hold the **current biennium** for bill identity/title/status/text (only
roll-call votes go back to 1999). So for older sessions (2020-2024) we need
OpenStates for the bill *list* and *metadata/text*; the **votes still come from
the SQL database** (``gencourt_sql``), which is the whole point -- votes are the
heaviest per-bill OpenStates calls, and offloading them to SQL is what keeps us
under OpenStates' rate limits.

This module therefore uses OpenStates *only* for discovery + light metadata:
one cached ``/bills?q=<term>`` search per (term, session). Everything is cached
to disk and resumable, so a rate-limit pause never loses progress.

Requires ``OPENSTATES_API_KEY``. If it is not set, callers should skip the
older sessions (the collector records a data gap rather than failing).
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import requests

OPENSTATES_URL = "https://v3.openstates.org/bills"
JURISDICTION = "New Hampshire"


class NoApiKey(RuntimeError):
    pass


class RateLimitExhausted(RuntimeError):
    """The free-tier daily/throughput cap is spent; stop calling OpenStates."""


# Budgets so a throttled free-tier key can never hang the job for hours.
MAX_REQUESTS = int(os.environ.get("OPENSTATES_MAX_REQUESTS", "450"))  # stay < 500/day
MAX_RETRY_WAIT = int(os.environ.get("OPENSTATES_MAX_RETRY_WAIT", "20"))
PAGE_SLEEP = float(os.environ.get("OPENSTATES_PAGE_SLEEP", "2"))
_requests_made = 0


def _key() -> str:
    key = os.environ.get("OPENSTATES_API_KEY")
    if not key:
        raise NoApiKey(
            "OPENSTATES_API_KEY is not set; cannot backfill older NH sessions. "
            "Add it as a Cloud Agent / GitHub Actions secret."
        )
    return key


def _get(url: str, params: list, headers: dict, *, max_tries: int = 4) -> dict:
    """GET with bounded backoff. Bails with RateLimitExhausted instead of looping."""
    global _requests_made
    if _requests_made >= MAX_REQUESTS:
        raise RateLimitExhausted(
            f"hit local request budget ({MAX_REQUESTS}); stopping OpenStates."
        )
    last = None
    for i in range(max_tries):
        _requests_made += 1
        r = requests.get(url, params=params, headers=headers, timeout=60)
        if r.status_code == 429:
            wait = min(MAX_RETRY_WAIT, int(r.headers.get("Retry-After") or 10 * (2 ** i)))
            print(f"  OpenStates 429 (try {i + 1}/{max_tries}); sleeping {wait}s")
            time.sleep(wait)
            last = r
            continue
        if r.status_code in {500, 502, 503, 504}:
            time.sleep(min(MAX_RETRY_WAIT, 5 * (2 ** i)))
            last = r
            continue
        r.raise_for_status()
        return r.json()
    if last is not None and getattr(last, "status_code", None) == 429:
        raise RateLimitExhausted(
            "OpenStates kept returning 429 -- the free-tier daily cap looks "
            "spent. Use the bulk-CSV route, or a higher tier / different day."
        )
    raise RuntimeError(f"OpenStates gave up after {max_tries} tries ({last})")


def search_session(term: str, session_identifier: str) -> list[dict]:
    """All bills matching ``term`` in one NH session (paginated, with abstracts,
    sponsors, sources). Returns lightweight bill dicts.
    """
    headers = {"X-API-KEY": _key()}
    out: list[dict] = []
    page = 1
    while True:
        params = [
            ("jurisdiction", JURISDICTION),
            ("session", session_identifier),
            ("q", term),
            ("per_page", 20),
            ("page", page),
            ("include", "abstracts"),
            ("include", "sponsorships"),
            ("include", "sources"),
            ("include", "versions"),
        ]
        data = _get(OPENSTATES_URL, params, headers)
        for b in data.get("results", []):
            out.append(
                {
                    "identifier": (b.get("identifier") or "").replace(" ", ""),
                    "session": session_identifier,
                    "title": b.get("title") or "",
                    "abstract": " ".join(
                        a.get("abstract", "") for a in (b.get("abstracts") or [])
                    ).strip(),
                    "sponsors": [
                        {"name": s.get("name"), "primary": s.get("primary")}
                        for s in (b.get("sponsorships") or [])
                    ],
                    "sources": [s.get("url") for s in (b.get("sources") or [])],
                    "versions": [
                        {"note": v.get("note"),
                         "links": [ln.get("url") for ln in (v.get("links") or [])]}
                        for v in (b.get("versions") or [])
                    ],
                    "openstates_url": b.get("openstates_url"),
                    "found_by_terms": [term],
                }
            )
        pagination = data.get("pagination") or {}
        if page >= pagination.get("max_page", page) or not data.get("results"):
            break
        page += 1
        time.sleep(PAGE_SLEEP)
    time.sleep(PAGE_SLEEP)
    return out


def discover(terms: list[str], session_identifier: str) -> list[dict]:
    """Merge per-term searches for one session, deduped by bill identifier."""
    merged: dict[str, dict] = {}
    for term in terms:
        for bill in search_session(term, session_identifier):
            rec = merged.setdefault(bill["identifier"], bill)
            for t in bill["found_by_terms"]:
                if t not in rec["found_by_terms"]:
                    rec["found_by_terms"].append(t)
    return sorted(merged.values(), key=lambda b: b["identifier"])


def available() -> bool:
    return bool(os.environ.get("OPENSTATES_API_KEY"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
