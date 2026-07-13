#!/usr/bin/env python3
"""Collect Nevada legislative bills from OpenStates API for a configured issue."""

from __future__ import annotations

import hashlib
import json
import os
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


def search_bills(api_key: str, jurisdiction: str, session: str, search_term: str) -> dict:
    params = {
        "jurisdiction": jurisdiction,
        "session": session,
        "q": search_term,
        "per_page": 20,
        "apikey": api_key,
    }
    response = requests.get(OPENSTATES_BASE_URL, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


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

    jurisdiction = config["state"]
    all_bills: dict[str, dict] = {}
    manifest_items: list[dict] = []
    source_counter = 1

    for session in config["sessions"]:
        for term in config["search_terms"]:
            print(f"Searching {jurisdiction} session {session} for: {term}")
            try:
                data = search_bills(api_key, jurisdiction, session, term)
                results = data.get("results", [])
                manifest_items.append(
                    {
                        "source_key": f"S-{source_counter:03d}",
                        "type": "bill_search",
                        "url": OPENSTATES_BASE_URL,
                        "search_term": term,
                        "session": session,
                        "bill_count": len(results),
                        "http_status": 200,
                        "notes": "",
                    }
                )
                source_counter += 1
                for bill in results:
                    bill_id = bill.get("id") or bill.get("identifier")
                    all_bills[str(bill_id)] = bill
            except requests.RequestException as exc:
                manifest_items.append(
                    {
                        "source_key": f"S-{source_counter:03d}",
                        "type": "bill_search",
                        "url": OPENSTATES_BASE_URL,
                        "search_term": term,
                        "session": session,
                        "bill_count": 0,
                        "http_status": None,
                        "notes": str(exc),
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
                    "error": str(exc),
                }
            )
        time.sleep(1)

    agency_path = OUTPUT_DIR / "agency-documents.json"
    agency_path.write_text(json.dumps(agency_docs, indent=2), encoding="utf-8")

    manifest = {
        "issue_id": config["issue_id"],
        "state": config["state"],
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collector": "openstates_bills.py",
        "items": manifest_items,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Done. Saved {len(bills_list)} bills to {bills_path}")


if __name__ == "__main__":
    main()
