#!/usr/bin/env python3
"""Refresh primary + co-sponsors from NELIS Overview for known bills.

Uses #primarySponsors and #cosponsors blocks (not the buggy label walk).

  python collectors/pass2_sponsors.py
  python collectors/pass2_sponsors.py --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
import issue_paths as ip  # noqa: E402
from pass2_party_roster import build_lookup, match_party  # noqa: E402

PASS1 = ip.PASS1
PASS2 = ip.PASS2
PROCESSED = ip.PROCESSED

BILLS = PASS1 / "bills.json"
ABSTRACT_CACHE = PASS1 / "cache_abstracts.json"
PROGRESS = PROCESSED / "bill-legislative-progress.json"
ROSTER = PASS2 / "legislator_roster.json"
SPONSOR_CACHE = PASS2 / "cache_sponsors.json"
OUT = PROCESSED / "bill-sponsors.json"

BASE = "https://www.leg.state.nv.us"
UA = {
    "User-Agent": "ForumLegislativeBrief/1.0",
    "X-Requested-With": "XMLHttpRequest",
}
REQUEST_DELAY = 0.4


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def bill_key(session: str, identifier: str) -> str:
    return f"{session}:{identifier}"


def nelis_ids(abstract_cache: dict, bill: dict) -> tuple[str, str] | None:
    key = bill_key(bill["session"], bill.get("identifier") or bill.get("bill_identifier"))
    row = abstract_cache.get(key) or {}
    if row.get("session_path") and row.get("nelis_bill_key"):
        return row["session_path"], str(row["nelis_bill_key"])
    url = bill.get("nelis_url") or ""
    match = re.search(r"/App/NELIS/REL/([^/]+)/Bill/(\d+)/", url)
    if match:
        return match.group(1), match.group(2)
    return None


def parse_sponsor_block(soup: BeautifulSoup, block_id: str, classification: str) -> list[dict]:
    block = soup.select_one(f"#{block_id}")
    if not block:
        return []
    rows = []
    for anchor in block.find_all("a", href=True):
        href = anchor["href"]
        name = clean(anchor.get_text(" ", strip=True))
        if not name:
            continue
        # Skip the expand/collapse controls
        if "view" in name.lower() and "sponsor" in name.lower():
            continue
        if "close" in name.lower() and "sponsor" in name.lower():
            continue
        entity_type = "organization" if "Committee" in name else "person"
        rows.append(
            {
                "name": name,
                "classification": classification,
                "primary": classification == "primary",
                "entity_type": entity_type,
                "source_url": urljoin(BASE, href) if href.startswith("/") else href,
            }
        )
    return rows


def sponsor_name_candidates(name: str) -> list[str]:
    """Generate roster-matching candidates, including compound surnames.

    Examples:
      'Assemblyman Howard Watts' -> Watts, Howard
      'Senator Heidi Seevers Gansert' -> Seevers Gansert, Heidi
      'Assemblymember Selena La Rue Hatch' -> La Rue Hatch, Selena
    """
    cleaned = clean(name)
    cleaned = re.sub(
        r"^(Assemblyman|Assemblywoman|Assemblymember|Senator|Sen\.|Asm\.)\s+",
        "",
        cleaned,
        flags=re.I,
    )
    parts = cleaned.split()
    candidates: list[str] = []
    if cleaned:
        candidates.append(cleaned)
    if len(parts) >= 2:
        candidates.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
    if len(parts) >= 3:
        candidates.append(f"{' '.join(parts[-2:])}, {' '.join(parts[:-2])}")
    if len(parts) >= 4:
        candidates.append(f"{' '.join(parts[-3:])}, {' '.join(parts[:-3])}")
    # Preserve order, drop dupes
    seen: set[str] = set()
    unique: list[str] = []
    for cand in candidates:
        key = cand.lower()
        if key not in seen:
            seen.add(key)
            unique.append(cand)
    return unique


def normalize_person_name(name: str) -> str:
    """Best-effort Last, First form (prefers single-token surname)."""
    cands = sponsor_name_candidates(name)
    for cand in cands:
        if "," in cand:
            return cand
    return cands[0] if cands else clean(name)


def parse_inline_primary_sponsor(soup: BeautifulSoup) -> list[dict]:
    """Committee-sponsored bills often use a single inline Primary Sponsor link."""
    label = soup.find(
        string=re.compile(r"^Primary Sponsors?$", re.I)
    )
    if not label:
        return []
    row = label.find_parent("div", class_=re.compile(r"\brow\b"))
    if not row:
        return []
    # Prefer the column next to the label
    sponsors = []
    for anchor in row.find_all("a", href=True):
        href = anchor["href"]
        name = clean(anchor.get_text(" ", strip=True))
        if not name or "view" in name.lower():
            continue
        if "Legislator" not in href and "Committee" not in href:
            continue
        sponsors.append(
            {
                "name": name,
                "classification": "primary",
                "primary": True,
                "entity_type": "organization" if "Committee" in name or "Committee" in href else "person",
                "source_url": urljoin(BASE, href) if href.startswith("/") else href,
            }
        )
    return sponsors


def fetch_sponsors(session: requests.Session, session_path: str, bill_key_id: str) -> list[dict]:
    warm = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{bill_key_id}/Overview"
    session.get(warm, timeout=60)
    time.sleep(REQUEST_DELAY)
    fill = f"{BASE}/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
    html = session.get(
        fill, params={"selectedTab": "Overview", "billKey": bill_key_id}, timeout=60
    ).text
    time.sleep(REQUEST_DELAY)
    soup = BeautifulSoup(html, "lxml")
    sponsors = []
    sponsors.extend(parse_sponsor_block(soup, "primarySponsors", "primary"))
    # Some pages use singular id
    if not any(s["classification"] == "primary" for s in sponsors):
        sponsors.extend(parse_sponsor_block(soup, "primarySponsor", "primary"))
    if not any(s["classification"] == "primary" for s in sponsors):
        sponsors.extend(parse_inline_primary_sponsor(soup))
    sponsors.extend(parse_sponsor_block(soup, "cosponsors", "cosponsor"))
    sponsors.extend(parse_sponsor_block(soup, "coSponsors", "cosponsor"))
    return sponsors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    bills_payload = load_json(BILLS, {})
    bills = bills_payload.get("bills") or []
    if not bills:
        progress = load_json(PROGRESS, [])
        bills = [
            {
                "session": p["session"],
                "identifier": p["bill_identifier"],
                "nelis_url": p.get("nelis_url"),
            }
            for p in progress
        ]
    if args.limit:
        bills = bills[: args.limit]

    abstract_cache = load_json(ABSTRACT_CACHE, {})
    sponsor_cache = {} if args.refresh else load_json(SPONSOR_CACHE, {})
    roster = load_json(ROSTER, {})
    party_lookup = build_lookup(roster.get("members") or [])

    client = requests.Session()
    client.headers.update(UA)

    all_rows: list[dict] = []
    print(f"Fetching sponsors for {len(bills)} bills")
    for index, bill in enumerate(bills, start=1):
        session = str(bill["session"])
        identifier = bill.get("identifier") or bill.get("bill_identifier")
        key = bill_key(session, identifier)
        if key in sponsor_cache and sponsor_cache[key].get("sponsors") is not None and not args.refresh:
            sponsors = sponsor_cache[key]["sponsors"]
            print(f"[{index}/{len(bills)}] {key} (cached) {len(sponsors)}")
        else:
            ids = nelis_ids(abstract_cache, bill)
            if not ids:
                print(f"[{index}/{len(bills)}] {key} SKIP — no NELIS ids")
                sponsors = []
            else:
                print(f"[{index}/{len(bills)}] {key}")
                try:
                    sponsors = fetch_sponsors(client, ids[0], ids[1])
                except Exception as exc:  # noqa: BLE001
                    print(f"  FAILED: {exc}")
                    sponsors = []
            sponsor_cache[key] = {
                "session": session,
                "identifier": identifier,
                "sponsors": sponsors,
                "collected_at": now(),
            }
            save_json(SPONSOR_CACHE, sponsor_cache)

        for sponsor in sponsors:
            party = source = matched = None
            for candidate in sponsor_name_candidates(sponsor["name"]):
                party, source, matched = match_party(candidate, party_lookup)
                if party:
                    break
            all_rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "name": sponsor["name"],
                    "classification": sponsor["classification"],
                    "primary": bool(sponsor.get("primary")),
                    "entity_type": sponsor.get("entity_type"),
                    "party": party,
                    "party_source": source,
                    "matched_roster_name": matched,
                    "source_url": sponsor.get("source_url"),
                    "source": "nelis",
                }
            )

    save_json(OUT, all_rows)
    save_json(SPONSOR_CACHE, sponsor_cache)
    primary = sum(1 for r in all_rows if r["classification"] == "primary")
    cosponsor = sum(1 for r in all_rows if r["classification"] == "cosponsor")
    print(
        f"Wrote {OUT}: rows={len(all_rows)} primary={primary} cosponsor={cosponsor} "
        f"bills={len({(r['session'], r['bill_identifier']) for r in all_rows})}"
    )


if __name__ == "__main__":
    main()
