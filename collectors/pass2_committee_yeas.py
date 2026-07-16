#!/usr/bin/env python3
"""Infer committee Yea votes from session membership minus Nay/Absent.

Nevada committee minutes usually list only NO and ABSENT by name. This script:
1. Loads each committee's membership for the session from NELIS Overview
2. For each work-session vote, marks remaining members (not Nay/Absent) as Yea
3. Updates bill-committee-votes.json and bill-votes.json

  python collectors/pass2_committee_yeas.py
  python collectors/pass2_committee_yeas.py --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pass2_party_roster import build_lookup, match_party, name_keys  # noqa: E402

PASS2 = Path("sources/nevada/water-scarcity/pass2")
PROCESSED = Path("sources/nevada/water-scarcity/processed")

COMMITTEE_VOTES = PROCESSED / "bill-committee-votes.json"
ALL_VOTES = PROCESSED / "bill-votes.json"
ROSTER = PASS2 / "legislator_roster.json"
MEMBERSHIP_CACHE = PASS2 / "cache_committee_membership.json"

SESSION_PATHS = {
    "80": "80th2019",
    "81": "81st2021",
    "82": "82nd2023",
    "83": "83rd2025",
}
BASE = "https://www.leg.state.nv.us"
UA = {
    "User-Agent": "ForumLegislativeBrief/1.0",
    "X-Requested-With": "XMLHttpRequest",
}
REQUEST_DELAY = 0.35

# Common OCR/transcription variants in minutes last names.
LAST_NAME_ALIASES = {
    "goiceochea": "goicoechea",
    "goicoecha": "goicoechea",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def last_name(name: str) -> str:
    name = clean(name)
    if "," in name:
        last = name.split(",", 1)[0]
    else:
        parts = name.split()
        last = parts[-1] if parts else name
    last = re.sub(r"[^A-Za-z\-']+", "", last).lower()
    return LAST_NAME_ALIASES.get(last, last)


def normalize_committee_label(label: str) -> str:
    text = clean(label)
    text = re.sub(r"^(Senate|Assembly)\s+", "", text, flags=re.I)
    text = re.sub(r"\s*\(.*?\)\s*", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def chamber_of_committee(label: str) -> str:
    low = (label or "").lower()
    if low.startswith("senate"):
        return "Senate"
    if low.startswith("assembly"):
        return "Assembly"
    return ""


class NelisCommittees:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(UA)
        self.directory: dict[str, list[dict]] = {}

    def load_directory(self, session_id: str) -> list[dict]:
        if session_id in self.directory:
            return self.directory[session_id]
        session_path = SESSION_PATHS[session_id]
        url = f"{BASE}/App/NELIS/REL/{session_path}/NavTree/GetCommitteeHierarchy"
        rows: list[dict] = []
        for parent_id, chamber in ((1000, "Assembly"), (2000, "Senate")):
            data = self.session.get(url, params={"id": parent_id}, timeout=60).json()
            time.sleep(REQUEST_DELAY)
            for item in data:
                rows.append(
                    {
                        "session": session_id,
                        "session_path": session_path,
                        "chamber": chamber,
                        "committee_key": str(item["Id"]),
                        "name": item.get("text") or "",
                        "label": f"{chamber} {item.get('text') or ''}".strip(),
                    }
                )
        self.directory[session_id] = rows
        return rows

    def resolve_committee(self, session_id: str, committee_label: str) -> dict | None:
        rows = self.load_directory(session_id)
        target = normalize_committee_label(committee_label)
        chamber = chamber_of_committee(committee_label)
        candidates = [r for r in rows if not chamber or r["chamber"] == chamber]
        # Exact short-name match
        for row in candidates:
            if normalize_committee_label(row["name"]) == target:
                return row
            if normalize_committee_label(row["label"]) == normalize_committee_label(
                committee_label
            ):
                return row
        # Prefix / containment (Natural Resources vs Natural Resources, Agriculture...)
        scored = []
        for row in candidates:
            short = normalize_committee_label(row["name"])
            if not short:
                continue
            if target.startswith(short) or short.startswith(target) or short in target or target in short:
                scored.append((abs(len(short) - len(target)), row))
        if scored:
            scored.sort(key=lambda x: x[0])
            return scored[0][1]
        return None

    def fetch_members(self, session_path: str, committee_key: str) -> list[dict]:
        warm = f"{BASE}/App/NELIS/REL/{session_path}/Committee/{committee_key}/Overview"
        self.session.get(warm, timeout=60)
        time.sleep(REQUEST_DELAY)
        fill = f"{BASE}/App/NELIS/REL/{session_path}/Committee/FillSelectedCommitteeTab"
        html = self.session.get(
            fill,
            params={
                "selectedTab": "Overview",
                "committeeOrSubCommitteeKey": committee_key,
            },
            timeout=60,
        ).text
        time.sleep(REQUEST_DELAY)
        soup = BeautifulSoup(html, "lxml")
        members: list[dict] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if "Legislator" not in href:
                continue
            raw = clean(anchor.get_text(" ", strip=True))
            # "Melanie Scheible - Chair"
            role = None
            name = raw
            if " - " in raw:
                name, role = [clean(p) for p in raw.split(" - ", 1)]
            # Convert "First Last" -> "Last, First" for roster matching
            parts = name.split()
            if len(parts) >= 2:
                roster_name = f"{parts[-1]}, {' '.join(parts[:-1])}"
            else:
                roster_name = name
            members.append(
                {
                    "name": roster_name,
                    "display_name": name,
                    "role": role,
                    "source_url": href if href.startswith("http") else f"{BASE}{href}",
                }
            )
        # Dedupe by last+first
        unique: dict[str, dict] = {}
        for member in members:
            unique[last_name(member["name"]) + "|" + member["name"].lower()] = member
        return list(unique.values())


def match_member(raw_name: str, members: list[dict]) -> dict | None:
    raw_last = last_name(raw_name)
    hits = [m for m in members if last_name(m["name"]) == raw_last or last_name(m["display_name"]) == raw_last]
    if len(hits) == 1:
        return hits[0]
    # Try fuller match via name_keys
    for member in members:
        if set(name_keys(raw_name)) & set(name_keys(member["name"])):
            return member
    return hits[0] if hits else None


def infer_yeas_for_vote(
    vote: dict,
    members: list[dict],
    party_lookup: dict,
) -> dict:
    excluded_lasts: set[str] = set()
    kept_ballots = []
    for ballot in vote.get("ballots") or []:
        option = (ballot.get("vote") or "").lower()
        if option not in {"nay", "absent", "excused", "not voting"}:
            # drop prior inferred yeas so re-runs are clean
            continue
        member = match_member(ballot.get("raw_name") or ballot.get("name") or "", members)
        if member:
            excluded_lasts.add(last_name(member["name"]))
            party, source, matched = match_party(member["name"], party_lookup)
            kept_ballots.append(
                {
                    "name": matched or member["name"],
                    "vote": option,
                    "party": party or ballot.get("party"),
                    "party_source": source or ballot.get("party_source"),
                    "raw_name": ballot.get("raw_name") or ballot.get("name"),
                    "inferred": False,
                }
            )
        else:
            excluded_lasts.add(last_name(ballot.get("raw_name") or ballot.get("name") or ""))
            kept_ballots.append({**ballot, "inferred": False})

    yea_ballots = []
    for member in members:
        if last_name(member["name"]) in excluded_lasts:
            continue
        party, source, matched = match_party(member["name"], party_lookup)
        yea_ballots.append(
            {
                "name": matched or member["name"],
                "vote": "yea",
                "party": party,
                "party_source": source,
                "raw_name": member["display_name"],
                "inferred": True,
                "inference": "committee_membership_minus_nay_absent",
            }
        )

    ballots = yea_ballots + kept_ballots
    vote = {
        **vote,
        "ballots": ballots,
        "yea_voters": [b["name"] for b in yea_ballots],
        "counts": {
            **(vote.get("counts") or {}),
            "yes": len(yea_ballots),
            "no": sum(1 for b in kept_ballots if b.get("vote") == "nay"),
            "absent": sum(1 for b in kept_ballots if b.get("vote") == "absent"),
            "excused": sum(1 for b in kept_ballots if b.get("vote") == "excused"),
            "not_voting": sum(1 for b in kept_ballots if b.get("vote") == "not voting"),
        },
        "committee_membership_count": len(members),
        "yea_inference": "membership_minus_nay_absent",
        "yea_inference_note": (
            "Yeas inferred as committee members for this session who were not listed "
            "as Nay/Absent/Excused in the minutes vote record."
        ),
    }
    return vote


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    committee_votes = load_json(COMMITTEE_VOTES, [])
    all_votes = load_json(ALL_VOTES, [])
    roster = load_json(ROSTER, {})
    party_lookup = build_lookup(roster.get("members") or [])
    membership_cache = {} if args.refresh else load_json(MEMBERSHIP_CACHE, {})

    client = NelisCommittees()
    needed = {
        (str(v.get("session")), v.get("committee") or "")
        for v in committee_votes
        if v.get("vote_kind") == "committee_work_session" and v.get("committee")
    }

    print(f"Resolving membership for {len(needed)} session/committee pairs")
    membership_by_pair: dict[tuple[str, str], list[dict]] = {}
    unresolved = []
    for session_id, committee_label in sorted(needed):
        cache_key = f"{session_id}|{committee_label}"
        if cache_key in membership_cache and membership_cache[cache_key].get("members") and not args.refresh:
            membership_by_pair[(session_id, committee_label)] = membership_cache[cache_key]["members"]
            print(f"  {cache_key} (cached) -> {len(membership_cache[cache_key]['members'])} members")
            continue
        resolved = client.resolve_committee(session_id, committee_label)
        if not resolved:
            print(f"  UNRESOLVED {cache_key}")
            unresolved.append(cache_key)
            membership_cache[cache_key] = {
                "session": session_id,
                "committee_label": committee_label,
                "members": [],
                "error": "committee_not_found",
                "collected_at": now(),
            }
            continue
        members = client.fetch_members(resolved["session_path"], resolved["committee_key"])
        # Attach party
        for member in members:
            party, source, matched = match_party(member["name"], party_lookup)
            if party:
                member["party"] = party
                member["party_source"] = source
                if matched:
                    member["name"] = matched
        membership_by_pair[(session_id, committee_label)] = members
        membership_cache[cache_key] = {
            "session": session_id,
            "committee_label": committee_label,
            "committee_key": resolved["committee_key"],
            "resolved_name": resolved["label"],
            "members": members,
            "collected_at": now(),
        }
        save_json(MEMBERSHIP_CACHE, membership_cache)
        print(f"  {cache_key} -> {resolved['label']} ({len(members)} members)")

    save_json(MEMBERSHIP_CACHE, membership_cache)

    updated_committee = []
    inferred_events = 0
    inferred_yeas = 0
    for vote in committee_votes:
        if vote.get("vote_kind") != "committee_work_session":
            updated_committee.append(vote)
            continue
        key = (str(vote.get("session")), vote.get("committee") or "")
        members = membership_by_pair.get(key) or membership_cache.get(
            f"{key[0]}|{key[1]}", {}
        ).get("members")
        if not members:
            updated_committee.append(vote)
            continue
        new_vote = infer_yeas_for_vote(vote, members, party_lookup)
        inferred_events += 1
        inferred_yeas += len(new_vote.get("yea_voters") or [])
        updated_committee.append(new_vote)

    save_json(COMMITTEE_VOTES, updated_committee)

    # Replace committee rows in bill-votes.json
    floor_and_other = [
        v
        for v in all_votes
        if v.get("vote_kind") not in {"committee_work_session", "committee_hearing"}
        and v.get("source") not in {"nelis_committee_minutes", "nelis_meetings"}
    ]
    merged = floor_and_other + updated_committee
    save_json(ALL_VOTES, merged)

    print(
        f"Done. work_sessions_updated={inferred_events} "
        f"inferred_yea_ballots={inferred_yeas} unresolved={len(unresolved)}"
    )
    if unresolved:
        for item in unresolved:
            print(f"  unresolved: {item}")


if __name__ == "__main__":
    main()
