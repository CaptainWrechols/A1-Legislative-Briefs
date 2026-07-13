#!/usr/bin/env python3
"""Collect Nevada legislative bills from OpenStates API for a configured issue."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

CONFIG_PATH = Path("config/issues/nevada-water-scarcity.yaml")
OUTPUT_DIR = Path("sources/nevada/water-scarcity/processed")
RAW_DIR = Path("sources/nevada/water-scarcity/raw")
MANIFEST_PATH = Path("sources/nevada/water-scarcity/manifest.json")
OPENSTATES_BASE_URL = "https://v3.openstates.org/bills"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_api_key() -> str:
    api_key = os.environ.get("OPENSTATES_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENSTATES_API_KEY environment variable. "
            "Register at https://openstates.org/accounts/register/"
        )
    return api_key


def sanitize_error_message(message: str, api_key: str) -> str:
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"apikey=[^&\\s]+", "apikey=[REDACTED]", message)
    return message


def normalize_sessions(config: dict) -> list[dict]:
    sessions = config.get("sessions", [])
    normalized = []
    for entry in sessions:
        if isinstance(entry, dict):
            normalized.append(entry)
        else:
            normalized.append(
                {
                    "label": str(entry),
                    "openstates_identifier": str(entry),
                    "name": str(entry),
                }
            )
    return normalized


def fetch_session_bills(
    api_key: str,
    jurisdiction: str,
    session_identifier: str,
    max_retries: int = 3,
) -> list[dict]:
    """Fetch all bills for a jurisdiction and session (no full-text query)."""
    headers = {"X-API-KEY": api_key}
    page = 1
    per_page = 20
    all_results: list[dict] = []

    while True:
        params = {
            "jurisdiction": jurisdiction,
            "session": session_identifier,
            "per_page": per_page,
            "page": page,
            "apikey": api_key,
        }
        last_error: requests.RequestException | None = None
        data: dict | None = None

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    OPENSTATES_BASE_URL,
                    params=params,
                    headers=headers,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                break
            except requests.RequestException as exc:
                last_error = exc
                wait = 2 ** attempt
                print(f"  page {page} attempt {attempt + 1} failed ({exc}); retry in {wait}s")
                time.sleep(wait)

        if data is None:
            raise last_error or RuntimeError(f"Failed to fetch page {page}")

        results = data.get("results", [])
        all_results.extend(results)
        print(f"  page {page}: {len(results)} bills (running total {len(all_results)})")

        pagination = data.get("pagination") or {}
        max_page = pagination.get("max_page", page)
        if page >= max_page or not results:
            break
        page += 1
        time.sleep(0.5)

    return all_results


def bill_text_blob(bill: dict) -> str:
    parts = [
        bill.get("identifier") or "",
        bill.get("title") or "",
    ]
    for abstract in bill.get("abstracts") or []:
        parts.append(abstract.get("abstract") or "")
    for subject in bill.get("subject") or []:
        parts.append(str(subject))
    return " ".join(parts).lower()


def bill_matches_terms(bill: dict, search_terms: list[str]) -> bool:
    blob = bill_text_blob(bill)
    return any(term.lower() in blob for term in search_terms)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_url(url: str, dest: Path) -> dict:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    return {
        "http_status": response.status_code,
        "sha256": sha256_bytes(response.content),
        "local_path": str(dest),
    }


def flatten_actions(bills: list[dict]) -> list[dict]:
    rows = []
    for bill in bills:
        identifier = bill.get("identifier", "")
        session = bill.get("session", "")
        for action in bill.get("actions") or []:
            rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "date": action.get("date"),
                    "organization": action.get("organization"),
                    "description": action.get("description"),
                    "classification": action.get("classification"),
                }
            )
    return rows


def flatten_votes(bills: list[dict]) -> list[dict]:
    rows = []
    for bill in bills:
        identifier = bill.get("identifier", "")
        session = bill.get("session", "")
        for vote in bill.get("votes") or []:
            rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "date": vote.get("start_date"),
                    "motion_text": vote.get("motion_text"),
                    "result": vote.get("result"),
                    "counts": vote.get("counts"),
                }
            )
    return rows


def main() -> None:
    config = load_config()
    api_key = get_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    jurisdiction = config.get("openstates_jurisdiction") or "Nevada"
    search_terms = config["search_terms"]
    sessions = normalize_sessions(config)
    all_bills: dict[str, dict] = {}
    manifest_items: list[dict] = []
    source_counter = 1

    for session_entry in sessions:
        session_id = session_entry["openstates_identifier"]
        session_label = session_entry.get("label", session_id)
        session_name = session_entry.get("name", session_label)
        print(
            f"Fetching all bills for {jurisdiction} session {session_label} "
            f"(OpenStates id={session_id}, {session_name})"
        )
        try:
            session_bills = fetch_session_bills(api_key, jurisdiction, session_id)
            matched = [b for b in session_bills if bill_matches_terms(b, search_terms)]
            print(
                f"  -> {len(session_bills)} total bills in session; "
                f"{len(matched)} match water-related search terms"
            )
            manifest_items.append(
                {
                    "source_key": f"S-{source_counter:03d}",
                    "type": "session_bill_fetch",
                    "url": OPENSTATES_BASE_URL,
                    "session_label": session_label,
                    "openstates_session_identifier": session_id,
                    "session_name": session_name,
                    "total_bills_in_session": len(session_bills),
                    "matched_bill_count": len(matched),
                    "search_terms": search_terms,
                    "http_status": 200,
                    "notes": "",
                }
            )
            source_counter += 1
            for bill in matched:
                bill_id = bill.get("id") or bill.get("identifier")
                all_bills[str(bill_id)] = bill
        except requests.RequestException as exc:
            manifest_items.append(
                {
                    "source_key": f"S-{source_counter:03d}",
                    "type": "session_bill_fetch",
                    "url": OPENSTATES_BASE_URL,
                    "session_label": session_label,
                    "openstates_session_identifier": session_id,
                    "session_name": session_name,
                    "total_bills_in_session": 0,
                    "matched_bill_count": 0,
                    "search_terms": search_terms,
                    "http_status": getattr(exc.response, "status_code", None),
                    "notes": sanitize_error_message(str(exc), api_key),
                }
            )
            source_counter += 1
        time.sleep(1)

    bills_list = list(all_bills.values())
    bills_path = OUTPUT_DIR / "bills-combined.json"
    bills_path.write_text(json.dumps(bills_list, indent=2), encoding="utf-8")

    actions_path = OUTPUT_DIR / "bill-actions.json"
    actions_path.write_text(json.dumps(flatten_actions(bills_list), indent=2), encoding="utf-8")

    votes_path = OUTPUT_DIR / "bill-votes.json"
    votes_path.write_text(json.dumps(flatten_votes(bills_list), indent=2), encoding="utf-8")

    statute_links = []
    for entry in config.get("statute_urls", []):
        statute_links.append(
            {
                "chapter": entry["chapter"],
                "url": entry["url"],
                "source_key": entry.get("source_key"),
            }
        )
    statutes_path = OUTPUT_DIR / "statute-links.json"
    statutes_path.write_text(json.dumps(statute_links, indent=2), encoding="utf-8")

    agency_docs = []
    for entry in config.get("agency_document_urls", []):
        url = entry["url"]
        filename = url.rstrip("/").split("/")[-1] or "document"
        if not filename.endswith((".pdf", ".html", ".htm")):
            filename = f"{entry.get('source_key', 'doc')}.pdf"
        dest = RAW_DIR / filename
        try:
            meta = download_url(url, dest)
            agency_docs.append(
                {
                    "title": entry["title"],
                    "url": url,
                    "source_key": entry.get("source_key"),
                    **meta,
                }
            )
            manifest_items.append(
                {
                    "source_key": entry.get("source_key", f"S-{source_counter:03d}"),
                    "type": "agency_document",
                    "url": url,
                    "local_path": str(dest),
                    "http_status": meta["http_status"],
                    "sha256": meta["sha256"],
                    "notes": "",
                }
            )
            source_counter += 1
        except requests.RequestException as exc:
            agency_docs.append(
                {
                    "title": entry["title"],
                    "url": url,
                    "source_key": entry.get("source_key"),
                    "error": sanitize_error_message(str(exc), api_key),
                }
            )
        time.sleep(1)

    agency_path = OUTPUT_DIR / "agency-documents.json"
    agency_path.write_text(json.dumps(agency_docs, indent=2), encoding="utf-8")

    manifest = {
        "issue_id": config["issue_id"],
        "state": config["state"],
        "openstates_jurisdiction": jurisdiction,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collector": "openstates_bills.py",
        "items": manifest_items,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Done. Saved {len(bills_list)} bills to {bills_path}")


if __name__ == "__main__":
    main()
