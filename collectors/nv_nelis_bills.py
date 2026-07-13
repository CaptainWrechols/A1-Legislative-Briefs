#!/usr/bin/env python3
"""Fetch Nevada water-related bills from the state NELIS website."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

CONFIG_PATH = Path("config/issues/nevada-water-scarcity.yaml")
OUTPUT_DIR = Path("sources/nevada/water-scarcity/processed")
MANIFEST_PATH = Path("sources/nevada/water-scarcity/manifest.json")

SESSION_PATHS = {
    "80": "80th2019",
    "81": "81st2021",
    "82": "82nd2023",
    "83": "83rd2025",
}

BILL_BLOCK_RE = re.compile(
    r'<a id="(?P<identifier>AB\d+|SB\d+|AJR\d+|SJR\d+|SCR\d+|ACR\d+)" '
    r'href="/App/NELIS/REL/(?P<session_path>[^/]+)/Bill/(?P<bill_id>\d+)/Overview">'
    r'(?P=identifier)</a>\s*</div>\s*<div class="col-md-10[^"]*">\s*(?P<summary>.*?)\s*</div>',
    re.DOTALL | re.IGNORECASE,
)


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def normalize_sessions(config: dict) -> list[dict]:
    sessions = []
    for entry in config.get("sessions", []):
        if isinstance(entry, dict):
            sessions.append(entry)
    return sessions


def fetch_session_bills(session_path: str, search_term: str) -> list[dict]:
    bills: dict[str, dict] = {}
    page = 1
    while True:
        url = (
            f"https://www.leg.state.nv.us/App/NELIS/REL/{session_path}/HomeBill/BillsTab"
            f"?Filters.SearchText={quote(search_term)}&Filters.PageSize=100&Page={page}"
        )
        response = requests.get(url, timeout=60, headers={"User-Agent": "ForumLegislativeBrief/1.0"})
        response.raise_for_status()
        html = response.text
        matches = list(BILL_BLOCK_RE.finditer(html))
        if not matches:
            break
        for match in matches:
            identifier = match.group("identifier").upper()
            summary = re.sub(r"<[^>]+>", " ", unescape(match.group("summary")))
            summary = re.sub(r"\s+", " ", summary).strip()
            bills[identifier] = {
                "identifier": identifier,
                "title": summary,
                "session": session_path,
                "source": "nevada_nelis",
                "source_url": (
                    f"https://www.leg.state.nv.us/App/NELIS/REL/{session_path}"
                    f"/Bill/{match.group('bill_id')}/Overview"
                ),
                "search_term": search_term,
            }
        if "Page=" + str(page + 1) not in html:
            break
        page += 1
        time.sleep(0.5)
    return list(bills.values())


def main() -> None:
    config = load_config()
    sessions = normalize_sessions(config)
    search_terms = config["search_terms"]
    all_bills: dict[str, dict] = {}
    manifest_items: list[dict] = []

    for session_entry in sessions:
        session_id = session_entry["openstates_identifier"]
        session_path = SESSION_PATHS.get(session_id)
        if not session_path:
            print(f"Skipping unknown session id {session_id}")
            continue
        session_label = session_entry.get("label", session_id)
        session_matches: dict[str, dict] = {}
        for term in search_terms:
            print(f"NELIS {session_path} search: {term}")
            try:
                results = fetch_session_bills(session_path, term)
                print(f"  -> {len(results)} bills")
                for bill in results:
                    key = f"{session_path}:{bill['identifier']}"
                    session_matches[key] = bill
            except requests.RequestException as exc:
                print(f"  -> error: {exc}")
            time.sleep(0.5)
        for bill in session_matches.values():
            all_bills[f"{bill['session']}:{bill['identifier']}"] = bill
        manifest_items.append(
            {
                "source_key": f"NELIS-{session_id}",
                "type": "nelis_session_search",
                "session_label": session_label,
                "session_path": session_path,
                "matched_bill_count": len(session_matches),
                "search_terms": search_terms,
                "source": "https://www.leg.state.nv.us/App/NELIS/",
            }
        )

    bills_list = list(all_bills.values())
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "bills-combined.json"
    output_path.write_text(json.dumps(bills_list, indent=2), encoding="utf-8")

  # merge into manifest
    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.update(
        {
            "issue_id": config["issue_id"],
            "state": config["state"],
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "collector": "nv_nelis_bills.py",
            "nelis_items": manifest_items,
            "nelis_bill_count": len(bills_list),
        }
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Done. Saved {len(bills_list)} NELIS bills to {output_path}")


if __name__ == "__main__":
    main()
