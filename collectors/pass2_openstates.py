"""OpenStates Pass 2 detail fetch (no search) for bills in pass1/bills.json."""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pass2_common import get, now  # noqa: E402

OPENSTATES_BASE_URL = "https://v3.openstates.org/bills"
DETAIL_INCLUDES = ["actions", "votes", "sponsorships", "abstracts"]
DETAIL_DELAY_SECONDS = 2.5


def sanitize_error_message(message: str, api_key: str) -> str:
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    return re.sub(r"apikey=[^&\s]+", "apikey=[REDACTED]", message)


def org_name(org: object) -> str:
    if isinstance(org, dict):
        return org.get("name") or org.get("classification") or ""
    return str(org or "")


def org_classification(org: object) -> str:
    if isinstance(org, dict):
        return (org.get("classification") or "").lower()
    return ""


def fetch_bill_detail(api_key: str, session: str, identifier: str) -> dict | None:
    headers = {"X-API-KEY": api_key}
    url = f"{OPENSTATES_BASE_URL}/Nevada/{session}/{identifier}"
    query = [("apikey", api_key)] + [("include", item) for item in DETAIL_INCLUDES]
    try:
        response = requests.get(url, params=query, headers=headers, timeout=120)
        if response.status_code == 404:
            print(f"  OpenStates: {session}:{identifier} not found (404)")
            return None
        if response.status_code == 429:
            response = get(url, params=query, headers=headers, timeout=120)
            return response.json()
        response.raise_for_status()
        return response.json()
    except (RuntimeError, requests.RequestException) as exc:
        print(f"  OpenStates detail failed for {session}:{identifier} ({exc})")
        return None


def flatten_actions(bill: dict) -> list[dict]:
    rows = []
    session = bill.get("session", "")
    identifier = bill.get("identifier", "")
    for action in bill.get("actions") or []:
        rows.append(
            {
                "session": session,
                "bill_identifier": identifier,
                "date": action.get("date"),
                "organization": org_name(action.get("organization")),
                "organization_classification": org_classification(action.get("organization")),
                "description": action.get("description"),
                "classification": action.get("classification"),
                "source": "openstates",
            }
        )
    return rows


def flatten_votes(bill: dict) -> list[dict]:
    rows = []
    session = bill.get("session", "")
    identifier = bill.get("identifier", "")
    for vote in bill.get("votes") or []:
        ballots = []
        for ballot in vote.get("votes") or []:
            voter = ballot.get("voter") or {}
            option = (ballot.get("option") or "").lower()
            ballots.append(
                {
                    "name": ballot.get("voter_name") or "",
                    "vote": option,
                    "party": voter.get("party") if isinstance(voter, dict) else None,
                    "party_source": "openstates" if isinstance(voter, dict) and voter.get("party") else None,
                }
            )
        rows.append(
            {
                "session": session,
                "bill_identifier": identifier,
                "vote_id": vote.get("id"),
                "date": vote.get("start_date"),
                "motion_text": vote.get("motion_text"),
                "result": vote.get("result"),
                "organization": org_name(vote.get("organization")),
                "organization_classification": org_classification(vote.get("organization")),
                "counts": vote.get("counts"),
                "ballots": ballots,
                "source": "openstates",
            }
        )
    return rows


def flatten_sponsors(bill: dict) -> list[dict]:
    rows = []
    session = bill.get("session", "")
    identifier = bill.get("identifier", "")
    for sponsor in bill.get("sponsorships") or []:
        person = sponsor.get("person") or {}
        entity = sponsor.get("entity") or {}
        rows.append(
            {
                "session": session,
                "bill_identifier": identifier,
                "name": sponsor.get("name") or person.get("name") or entity.get("name"),
                "classification": sponsor.get("classification"),
                "primary": bool(sponsor.get("primary")),
                "entity_type": sponsor.get("entity_type"),
                "party": person.get("party") if isinstance(person, dict) else None,
                "source": "openstates",
            }
        )
    return rows


def collect_openstates_details(
    bills: list[dict],
    *,
    api_key: str,
    cache: dict,
    refresh: bool,
) -> tuple[list[dict], list[dict]]:
    """Return (detail_records, failures)."""
    details: list[dict] = []
    failures: list[dict] = []
    for index, bill in enumerate(bills, start=1):
        key = f"{bill['session']}:{bill['identifier']}"
        if key in cache and cache[key].get("detail") and not refresh:
            print(f"[{index}/{len(bills)}] OpenStates {key} (cached)")
            details.append(cache[key])
            continue
        print(f"[{index}/{len(bills)}] OpenStates {key}")
        detail = fetch_bill_detail(api_key, bill["session"], bill["identifier"])
        if detail:
            record = {
                "session": bill["session"],
                "identifier": bill["identifier"],
                "openstates_url": detail.get("openstates_url") or bill.get("openstates_url"),
                "detail": detail,
                "collected_at": now(),
                "found": True,
            }
            cache[key] = record
            details.append(record)
        else:
            record = {
                "session": bill["session"],
                "identifier": bill["identifier"],
                "openstates_url": bill.get("openstates_url"),
                "detail": None,
                "collected_at": now(),
                "found": False,
            }
            cache[key] = record
            details.append(record)
            failures.append({"bill": key, "error": "not_found_or_rate_limited"})
        time.sleep(DETAIL_DELAY_SECONDS)
    return details, failures


def get_api_key() -> str | None:
    return os.environ.get("OPENSTATES_API_KEY") or None
