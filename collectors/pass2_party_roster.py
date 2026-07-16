#!/usr/bin/env python3
"""Build a Nevada legislator party roster by session (no OpenStates).

Primary source: official NELIS legislator directory pages, which list each
member with party in the same "Last, First" format used on NELIS vote rolls.

Fallback: Ballotpedia chamber pages for any remaining unmatched names.

  python collectors/pass2_party_roster.py
  python collectors/pass2_party_roster.py --refresh
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

PASS2 = Path("sources/nevada/water-scarcity/pass2")
ROSTER_PATH = PASS2 / "legislator_roster.json"
PROCESSED_VOTES = Path("sources/nevada/water-scarcity/processed/bill-votes.json")

SESSION_PATHS = {
    "80": "80th2019",
    "81": "81st2021",
    "82": "82nd2023",
    "83": "83rd2025",
}

CHAMBERS = ("Assembly", "Senate")

BALLOTPEDIA_URLS = {
    ("80", "Assembly"): "https://ballotpedia.org/Nevada_State_Assembly_elections,_2018",
    ("80", "Senate"): "https://ballotpedia.org/Nevada_State_Senate_elections,_2018",
    ("81", "Assembly"): "https://ballotpedia.org/Nevada_State_Assembly_elections,_2020",
    ("81", "Senate"): "https://ballotpedia.org/Nevada_State_Senate_elections,_2020",
    ("82", "Assembly"): "https://ballotpedia.org/Nevada_State_Assembly_elections,_2022",
    ("82", "Senate"): "https://ballotpedia.org/Nevada_State_Senate_elections,_2022",
    ("83", "Assembly"): "https://ballotpedia.org/Nevada_State_Assembly_elections,_2024",
    ("83", "Senate"): "https://ballotpedia.org/Nevada_State_Senate_elections,_2024",
}

LEADERSHIP_SUFFIX = re.compile(
    r"\b("
    r"Speaker(?:\s+pro\s+Tempore)?|"
    r"(?:Co-)?(?:Majority|Minority)\s+(?:Floor\s+)?(?:Leader|Whip)|"
    r"Assistant\s+(?:Majority|Minority)\s+(?:Floor\s+)?(?:Leader|Whip)|"
    r"Legislative\s+Executive\s+Committee\s+Chair|"
    r"President\s+pro\s+Tempore"
    r")\b.*$",
    re.I,
)

# Generational / title suffixes that break Last, First matching.
NAME_SUFFIX = re.compile(r",?\s*\b(II|III|IV|Jr\.?|Sr\.?)\s*$", re.I)

# Known NELIS vote-roll aliases → roster directory names (same person).
NAME_ALIASES = {
    "seevers o'gara, heidi": "Seevers Gansert, Heidi",
    "seevers ogara, heidi": "Seevers Gansert, Heidi",
}

UA = {"User-Agent": "ForumLegislativeBrief/1.0 (research; contact via GitHub)"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strip_leadership(name: str) -> str:
    name = clean_text(name)
    name = LEADERSHIP_SUFFIX.sub("", name).strip(" ,;-")
    return clean_text(name)


def normalize_party(party: str) -> str | None:
    text = clean_text(party).lower()
    if not text:
        return None
    if text.startswith("dem") or text == "d":
        return "Democratic"
    if text.startswith("rep") or text == "r":
        return "Republican"
    if "independent" in text or text == "i":
        return "Independent"
    if "libertarian" in text:
        return "Libertarian"
    # Keep other labels as title-case if they look like a party.
    if text in {"nonpartisan", "other"}:
        return text.title()
    return clean_text(party).title()


def name_keys(name: str) -> list[str]:
    """Generate match keys for Last, First [Middle] style names."""
    cleaned = strip_leadership(name)
    cleaned = NAME_SUFFIX.sub("", cleaned).strip(" ,")
    alias = NAME_ALIASES.get(cleaned.lower())
    if alias:
        cleaned = alias
    if not cleaned:
        return []
    keys = {cleaned.lower()}
    if "," in cleaned:
        # Handle "McCurdy, William, II" after suffix strip → "McCurdy, William"
        parts = [part.strip() for part in cleaned.split(",") if part.strip()]
        last = parts[0]
        first = parts[1] if len(parts) > 1 else ""
    else:
        tokens = cleaned.split()
        if len(tokens) < 2:
            return [cleaned.lower()]
        last, first = tokens[-1], " ".join(tokens[:-1])
    last = last.lower()
    first_tokens = [t for t in re.split(r"[\s.]+", first.lower()) if t]
    if not first_tokens:
        return list(keys)
    keys.add(f"{last}|{first_tokens[0]}")
    if len(first_tokens) > 1:
        keys.add(f"{last}|{first_tokens[0]}|{first_tokens[1][0]}")
        keys.add(f"{last}|{' '.join(first_tokens)}")
    # Compound last names: "Seevers Gansert" / "Seevers O'Gara" → also key first surname token
    last_tokens = [t for t in re.split(r"[\s]+", last) if t]
    if len(last_tokens) > 1:
        keys.add(f"{last_tokens[0]}|{first_tokens[0]}")
    return list(keys)


def get(url: str) -> str:
    last = None
    for attempt in range(5):
        try:
            response = requests.get(url, headers=UA, timeout=90)
            if response.status_code in {429, 502, 503, 504}:
                wait = int(response.headers.get("Retry-After") or min(60, 10 * (2**attempt)))
                print(f"  HTTP {response.status_code}; sleep {wait}s")
                time.sleep(wait)
                last = response
                continue
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last = exc
            wait = min(60, 10 * (2**attempt))
            print(f"  failed ({exc}); sleep {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gave up: {url} ({last})")


def scrape_nelis_roster(session: str, session_path: str, chamber: str) -> list[dict]:
    url = f"https://www.leg.state.nv.us/App/Legislator/A/{chamber}/{session_path}"
    print(f"NELIS roster {session}:{chamber} -> {url}")
    html = get(url)
    time.sleep(0.4)
    soup = BeautifulSoup(html, "lxml")
    members: list[dict] = []
    for tr in soup.find_all("tr"):
        cells = [clean_text(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
        if len(cells) < 3:
            continue
        # Typical: ['', 'Assefa, Alexander', 'Democratic', 'No. 42', 'Clark (Part)']
        name_cell = cells[1] if cells[0] == "" and len(cells) >= 3 else cells[0]
        party_cell = cells[2] if cells[0] == "" and len(cells) >= 3 else cells[1]
        if "," not in name_cell:
            continue
        party = normalize_party(party_cell)
        if not party:
            continue
        name = strip_leadership(name_cell)
        members.append(
            {
                "name": name,
                "raw_name": name_cell,
                "party": party,
                "chamber": chamber,
                "session": session,
                "session_path": session_path,
                "source": "nelis_legislator_directory",
                "source_url": url,
            }
        )
    print(f"  {len(members)} members")
    return members


def scrape_ballotpedia_fallback(session: str, chamber: str) -> list[dict]:
    """Light Ballotpedia scrape for leftover names (winner/incumbent party tables)."""
    url = BALLOTPEDIA_URLS.get((session, chamber))
    if not url:
        return []
    print(f"Ballotpedia fallback {session}:{chamber} -> {url}")
    try:
        html = get(url)
    except RuntimeError as exc:
        print(f"  skipped ({exc})")
        return []
    time.sleep(0.75)
    soup = BeautifulSoup(html, "lxml")
    members: list[dict] = []
    # Look for links like "John Doe (D)" or table cells with (D)/(R)
    text_blobs = [clean_text(a.get_text(" ", strip=True)) for a in soup.find_all("a")]
    text_blobs += [clean_text(td.get_text(" ", strip=True)) for td in soup.find_all("td")]
    for blob in text_blobs:
        match = re.match(r"^([A-Z][A-Za-z.'\-]+(?:\s+[A-Z][A-Za-z.'\-]+)+)\s*\(([DR])\)\s*$", blob)
        if not match:
            continue
        full = match.group(1)
        party = "Democratic" if match.group(2) == "D" else "Republican"
        parts = full.split()
        if len(parts) < 2:
            continue
        name = f"{parts[-1]}, {' '.join(parts[:-1])}"
        members.append(
            {
                "name": name,
                "raw_name": blob,
                "party": party,
                "chamber": chamber,
                "session": session,
                "source": "ballotpedia",
                "source_url": url,
            }
        )
    # Dedupe by name
    unique: dict[str, dict] = {}
    for member in members:
        unique[member["name"].lower()] = member
    print(f"  {len(unique)} candidate names")
    return list(unique.values())


def build_lookup(members: list[dict]) -> dict[str, dict]:
    """Map normalized keys -> member record (prefer NELIS over Ballotpedia)."""
    lookup: dict[str, dict] = {}
    priority = {"nelis_legislator_directory": 2, "ballotpedia": 1}

    def score(member: dict) -> int:
        return priority.get(member.get("source") or "", 0)

    for member in members:
        for key in name_keys(member["name"]) + name_keys(member.get("raw_name") or ""):
            existing = lookup.get(key)
            if not existing or score(member) > score(existing):
                lookup[key] = member
    return lookup


def match_party(name: str, lookup: dict[str, dict]) -> tuple[str | None, str | None, str | None]:
    for key in name_keys(name):
        member = lookup.get(key)
        if member:
            return member.get("party"), member.get("source"), member.get("name")
    return None, None, None


def collect_voter_names_from_votes() -> dict[str, set[str]]:
    """session -> set of voter names appearing on roll calls."""
    if not PROCESSED_VOTES.exists():
        return {}
    votes = json.loads(PROCESSED_VOTES.read_text(encoding="utf-8"))
    by_session: dict[str, set[str]] = {}
    for vote in votes:
        session = str(vote.get("session") or "")
        for ballot in vote.get("ballots") or []:
            name = ballot.get("name") or ""
            if name:
                by_session.setdefault(session, set()).add(name)
    return by_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--skip-ballotpedia", action="store_true")
    args = parser.parse_args()

    if ROSTER_PATH.exists() and not args.refresh:
        print(f"Roster already exists at {ROSTER_PATH} (use --refresh to rebuild)")
        return

    members: list[dict] = []
    for session, session_path in SESSION_PATHS.items():
        for chamber in CHAMBERS:
            members.extend(scrape_nelis_roster(session, session_path, chamber))

    if not args.skip_ballotpedia:
        for session in SESSION_PATHS:
            for chamber in CHAMBERS:
                members.extend(scrape_ballotpedia_fallback(session, chamber))

    lookup = build_lookup(members)
    voter_names = collect_voter_names_from_votes()

    match_report = []
    unmatched = []
    for session, names in sorted(voter_names.items()):
        session_members = [m for m in members if m.get("session") == session]
        session_lookup = build_lookup(session_members) if session_members else lookup
        for name in sorted(names):
            party, source, matched_as = match_party(name, session_lookup)
            if not party:
                party, source, matched_as = match_party(name, lookup)
            row = {
                "session": session,
                "voter_name": name,
                "party": party,
                "matched_roster_name": matched_as,
                "source": source,
            }
            match_report.append(row)
            if not party:
                unmatched.append(row)

    payload = {
        "collected_at": now(),
        "source_note": (
            "Primary: NELIS legislator directory (Assembly/Senate per session). "
            "Fallback: Ballotpedia election pages for leftover names."
        ),
        "member_count": len(members),
        "lookup_key_count": len(lookup),
        "vote_names_seen": sum(len(v) for v in voter_names.values()),
        "vote_names_matched": sum(1 for r in match_report if r.get("party")),
        "vote_names_unmatched": len(unmatched),
        "members": members,
        "match_report": match_report,
        "unmatched": unmatched,
    }
    PASS2.mkdir(parents=True, exist_ok=True)
    ROSTER_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f"Wrote {ROSTER_PATH}: members={len(members)} "
        f"vote_names_matched={payload['vote_names_matched']}/"
        f"{payload['vote_names_seen']} unmatched={len(unmatched)}"
    )
    if unmatched:
        print("Unmatched examples:")
        for row in unmatched[:15]:
            print(f"  {row['session']}:{row['voter_name']}")


if __name__ == "__main__":
    main()
