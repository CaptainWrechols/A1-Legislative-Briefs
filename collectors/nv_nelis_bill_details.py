#!/usr/bin/env python3
"""Enrich NELIS search stubs with Overview, votes, sponsors, history, and text links.

NELIS bill tabs load via AJAX. This collector uses the same endpoints the browser uses:

- FillSelectedBillTab?selectedTab=Overview|Text|Votes&billKey=...
- GetBillVotes?billKey=...&voteTypeId=...
- GetBillVoteMembers?voteKey=...&voteResultPanel=Yea|Nay|...

Committee recommendations come from Overview Past Hearings (not a separate Votes type).
Floor member names come from GetBillVoteMembers. Party is resolved from legislator pages
and cached in nelis/legislator-party-cache.json.

Env:
  NELIS_DETAIL_LIMIT=N   Process only the first N stubs (smoke tests).
  NELIS_SKIP_PARTY=1     Skip legislator party lookups.
  NELIS_DOWNLOAD_TEXT=1  Download bill PDFs into sources/.../raw/nelis-text/.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup

CONFIG_PATH = Path("config/issues/nevada-water-scarcity.yaml")
NELIS_DIR = Path("sources/nevada/water-scarcity/nelis")
RAW_DIR = Path("sources/nevada/water-scarcity/raw/nelis-text")
MANIFEST_PATH = Path("sources/nevada/water-scarcity/manifest.json")
STUBS_PATH = NELIS_DIR / "bills-search-stubs.json"
PARTY_CACHE_PATH = NELIS_DIR / "legislator-party-cache.json"
BASE = "https://www.leg.state.nv.us"
USER_AGENT = "ForumLegislativeBrief/1.0"
REQUEST_DELAY = 0.4

VOTE_PANELS = ("Yea", "Nay", "Not Voting", "Absent", "Excused")


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def bill_key_from_url(url: str) -> str | None:
    match = re.search(r"/Bill/(\d+)/", url or "")
    return match.group(1) if match else None


class NelisClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
            }
        )

    def warmup(self, session_path: str, bill_key: str) -> None:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{bill_key}/Overview"
        self.session.get(url, timeout=60)
        time.sleep(REQUEST_DELAY)

    def fill_tab(self, session_path: str, bill_key: str, selected_tab: str) -> str:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
        response = self.session.get(
            url,
            params={"selectedTab": selected_tab, "billKey": bill_key},
            timeout=60,
        )
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.text

    def get_bill_votes(self, session_path: str, bill_key: str, vote_type_id: str) -> str:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/GetBillVotes"
        response = self.session.get(
            url,
            params={"billKey": bill_key, "voteTypeId": vote_type_id},
            timeout=60,
        )
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.text

    def get_vote_members(self, session_path: str, vote_key: str, panel: str) -> list[str]:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/GetBillVoteMembers"
        response = self.session.get(
            url,
            params={"voteKey": vote_key, "voteResultPanel": panel},
            timeout=60,
        )
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        if not response.text.strip():
            return []
        soup = BeautifulSoup(response.text, "lxml")
        names = [clean_text(a.get_text(" ", strip=True)) for a in soup.find_all("a")]
        if names:
            return [n for n in names if n]
        text = clean_text(soup.get_text(" ", strip=True))
        if not text:
            return []
        # Members often appear as "Last, First Last, First ..."
        parts = re.split(r"(?<=[a-z)])\s+(?=[A-Z])", text)
        if len(parts) == 1 and "," in text:
            # Pattern: "Anderson, Natha Backus, Shea ..."
            chunks = re.findall(r"[A-Z][^,]+,\s+[A-Z][^\s]+(?:\s+[A-Z][^\s]+)?", text)
            return [clean_text(c) for c in chunks] or [text]
        return [clean_text(p) for p in parts if clean_text(p)]

    def get(self, path_or_url: str) -> requests.Response:
        url = path_or_url if path_or_url.startswith("http") else urljoin(BASE, path_or_url)
        response = self.session.get(url, timeout=60)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response


def parse_sponsors(soup: BeautifulSoup, session_path: str) -> list[dict]:
    sponsors: list[dict] = []
    seen: set[str] = set()

    def add(name: str, classification: str, href: str | None = None) -> None:
        key = f"{classification}:{name.lower()}"
        if not name or key in seen:
            return
        seen.add(key)
        sponsors.append(
            {
                "name": name,
                "classification": classification,
                "primary": classification == "primary",
                "entity_type": "organization" if "Committee" in name else "person",
                "source_url": urljoin(BASE, href) if href else None,
                "session": session_path,
            }
        )

    for label, classification in (
        ("Primary Sponsors", "primary"),
        ("Primary Sponsor", "primary"),
        ("Co-Sponsors", "cosponsor"),
        ("Cosponsors", "cosponsor"),
    ):
        node = soup.find(string=re.compile(rf"^{re.escape(label)}$", re.I))
        if not node:
            continue
        container = node.find_parent(["div", "section", "td", "li"]) or node.parent
        # Walk a modest window of following elements for person/committee links.
        for el in list(container.next_elements)[:80]:
            if getattr(el, "name", None) == "a" and el.get("href"):
                href = el["href"]
                name = clean_text(el.get_text(" ", strip=True))
                if not name:
                    continue
                if "Legislator" in href or "Committee" in href:
                    add(name, classification, href)
            if getattr(el, "name", None) in {"h2", "h3", "h4"}:
                heading = clean_text(el.get_text(" ", strip=True)).lower()
                if heading and label.lower() not in heading and "sponsor" not in heading:
                    if any(
                        stop in heading
                        for stop in ("title", "digest", "hearing", "history", "vote", "summary")
                    ):
                        break

    # Fallback: any legislator/committee links near the top summary area.
    if not sponsors:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            name = clean_text(a.get_text(" ", strip=True))
            if "Legislator" in href or ("Committee" in href and "Natural Resources" in name):
                add(name, "primary", href)

    return sponsors


def parse_history(soup: BeautifulSoup) -> list[dict]:
    rows: list[dict] = []
    for table in soup.find_all("table"):
        headers = [clean_text(th.get_text(" ", strip=True)).lower() for th in table.find_all("th")]
        if not headers:
            first = table.find("tr")
            if first:
                headers = [clean_text(c.get_text(" ", strip=True)).lower() for c in first.find_all(["th", "td"])]
        if not any("action" in h for h in headers):
            continue
        body_rows = table.find_all("tr")
        start = 1 if body_rows and body_rows[0].find("th") else 1
        for tr in body_rows[start:]:
            cells = [clean_text(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
            if len(cells) < 2:
                continue
            rows.append(
                {
                    "date": cells[0],
                    "description": cells[1],
                    "journal": cells[2] if len(cells) > 2 else "",
                }
            )
        if rows:
            break
    return rows


def parse_hearings(soup: BeautifulSoup) -> list[dict]:
    hearings: list[dict] = []
    for table in soup.find_all("table"):
        headers = [clean_text(c.get_text(" ", strip=True)).lower() for c in table.find("tr").find_all(["th", "td"])] if table.find("tr") else []
        if not any("recommendation" in h for h in headers):
            continue
        for tr in table.find_all("tr")[1:]:
            cells = [clean_text(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
            if len(cells) < 3:
                continue
            # Meeting | Video Link | Committee | Date | Time | Agenda | Minutes | Recommendation
            # Some rows collapse columns; locate by header positions when possible.
            if len(cells) >= 8:
                hearings.append(
                    {
                        "committee": cells[2],
                        "date": cells[3],
                        "time": cells[4],
                        "recommendation": cells[7],
                        "raw_cells": cells,
                    }
                )
            else:
                hearings.append(
                    {
                        "committee": cells[1] if len(cells) > 1 else "",
                        "date": cells[2] if len(cells) > 2 else "",
                        "time": cells[3] if len(cells) > 3 else "",
                        "recommendation": cells[-1],
                        "raw_cells": cells,
                    }
                )
        break
    return hearings


def parse_overview(html: str, session_path: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title_el = soup.select_one("#title")
    digest_el = soup.select_one("#digest")
    recent = ""
    heading = soup.find("h2", string=re.compile(r"Most Recent History Action", re.I))
    if heading:
        row = heading.find_parent("div", class_=re.compile(r"\brow\b"))
        blob = clean_text((row or heading.parent).get_text(" ", strip=True))
        blob = re.sub(r"^Most Recent History Actions?\s*", "", blob, flags=re.I)
        blob = re.sub(r"\s*\(See full list below\)\s*$", "", blob, flags=re.I)
        recent = blob.strip(" -|:;")

    return {
        "official_title": clean_text(title_el.get_text(" ", strip=True)) if title_el else "",
        "digest": clean_text(digest_el.get_text(" ", strip=True)) if digest_el else "",
        "most_recent_history_action": recent,
        "sponsors": parse_sponsors(soup, session_path),
        "history": parse_history(soup),
        "hearings": parse_hearings(soup),
    }


def parse_text_tab(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    docs: list[dict] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not re.search(r"\.(pdf|htm|html)(\?|$)", href, re.I):
            continue
        label = clean_text(a.get_text(" ", strip=True)) or Path(href).name
        docs.append(
            {
                "label": label,
                "url": urljoin(BASE, href) if href.startswith("/") else href,
            }
        )
    # Prefer session bill PDFs when label is empty/hash links.
    if not docs:
        for match in re.finditer(r'https://www\.leg\.state\.nv\.us/Session/[^\"\']+\.pdf', html):
            docs.append({"label": Path(match.group(0)).name, "url": match.group(0)})
    # Dedupe
    unique: dict[str, dict] = {}
    for doc in docs:
        unique[doc["url"]] = doc
    return list(unique.values())


def parse_votes_shell(html: str) -> list[tuple[str, str]]:
    """Return (vote_type_id, label) pairs from Votes tab shell."""
    pairs = re.findall(
        r"GetBillVotes\?billKey=\d+&amp;voteTypeId=(\d+)\">([^<]+)",
        html,
    )
    return [(vid, clean_text(label)) for vid, label in pairs]


def parse_chamber_vote_blocks(html: str, vote_type_label: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    blocks: list[dict] = []
    for heading in soup.find_all(["h2", "h3"]):
        chamber = clean_text(heading.get_text(" ", strip=True))
        if not chamber or chamber.lower() == "votes":
            continue
        section_html = ""
        for sib in heading.next_siblings:
            if getattr(sib, "name", None) in {"h2", "h3"}:
                break
            section_html += str(sib)
        vote_keys = re.findall(
            r"GetBillVoteMembers\?voteKey=(\d+)&amp;voteResultPanel=(Yea|Nay|Not Voting|Absent|Excused)",
            section_html,
        )
        counts: dict[str, int] = {}
        for match in re.finditer(
            r"voteResultPanel=(Yea|Nay|Not Voting|Absent|Excused)\">\s*([^:<]+):\s*(\d+)",
            section_html,
        ):
            counts[match.group(1)] = int(match.group(3))
        vote_key = vote_keys[0][0] if vote_keys else None
        blocks.append(
            {
                "vote_type": vote_type_label,
                "chamber_label": chamber,
                "vote_key": vote_key,
                "counts": counts,
            }
        )
    return blocks


def resolve_party(client: NelisClient, cache: dict[str, str], sponsor: dict) -> str | None:
    url = sponsor.get("source_url")
    if not url or "Legislator" not in url:
        return None
    if url in cache:
        return cache[url]
    try:
        html = client.get(url).text
        match = re.search(r"Party:\s*([A-Za-z]+)", html)
        party = match.group(1) if match else None
        cache[url] = party or ""
        return party
    except requests.RequestException:
        cache[url] = ""
        return None


def enrich_bill(
    client: NelisClient,
    stub: dict,
    party_cache: dict[str, str],
    skip_party: bool,
    download_text: bool,
) -> tuple[dict, list[dict], list[dict], list[dict], list[dict], list[dict]]:
    session_path = stub["session"]
    bill_key = stub.get("nelis_bill_key") or bill_key_from_url(stub.get("source_url", ""))
    if not bill_key:
        raise ValueError(f"Missing nelis_bill_key for {stub.get('identifier')}")

    client.warmup(session_path, bill_key)
    overview_html = client.fill_tab(session_path, bill_key, "Overview")
    overview = parse_overview(overview_html, session_path)

    sponsors = overview["sponsors"]
    if not skip_party:
        for sponsor in sponsors:
            party = resolve_party(client, party_cache, sponsor)
            if party:
                sponsor["party"] = party

    actions = [
        {
            "session": session_path,
            "bill_identifier": stub["identifier"],
            "date": row["date"],
            "description": row["description"],
            "journal": row.get("journal", ""),
            "source": "nelis_overview_history",
        }
        for row in overview["history"]
    ]

    hearings = [
        {
            "session": session_path,
            "bill_identifier": stub["identifier"],
            **hearing,
            "source": "nelis_overview_hearings",
        }
        for hearing in overview["hearings"]
    ]

    text_html = client.fill_tab(session_path, bill_key, "Text")
    text_docs = parse_text_tab(text_html)
    texts = []
    for doc in text_docs:
        entry = {
            "session": session_path,
            "bill_identifier": stub["identifier"],
            **doc,
        }
        if download_text and doc["url"].lower().endswith(".pdf"):
            filename = f"{session_path}_{stub['identifier']}_{Path(doc['url']).name}"
            dest = RAW_DIR / filename
            try:
                response = client.get(doc["url"])
                RAW_DIR.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(response.content)
                entry["local_path"] = str(dest)
            except requests.RequestException as exc:
                entry["download_error"] = str(exc)
        texts.append(entry)

    votes_shell = client.fill_tab(session_path, bill_key, "Votes")
    vote_rows: list[dict] = []
    for vote_type_id, vote_type_label in parse_votes_shell(votes_shell):
        votes_html = client.get_bill_votes(session_path, bill_key, vote_type_id)
        for block in parse_chamber_vote_blocks(votes_html, vote_type_label):
            members: dict[str, list[str]] = {}
            if block.get("vote_key"):
                for panel in VOTE_PANELS:
                    members[panel] = client.get_vote_members(
                        session_path, block["vote_key"], panel
                    )
            vote_rows.append(
                {
                    "session": session_path,
                    "bill_identifier": stub["identifier"],
                    "vote_type": vote_type_label,
                    "vote_type_id": vote_type_id,
                    "chamber_label": block["chamber_label"],
                    "vote_key": block.get("vote_key"),
                    "counts": block.get("counts") or {},
                    "yea_voters": members.get("Yea", []),
                    "nay_voters": members.get("Nay", []),
                    "not_voting": members.get("Not Voting", []),
                    "absent": members.get("Absent", []),
                    "excused": members.get("Excused", []),
                    "source": "nelis_get_bill_votes",
                }
            )

    bill = {
        **stub,
        "nelis_bill_key": bill_key,
        "official_title": overview["official_title"],
        "digest": overview["digest"],
        "most_recent_history_action": overview["most_recent_history_action"],
        "sponsors": sponsors,
        "history_count": len(actions),
        "hearing_count": len(hearings),
        "vote_event_count": len(vote_rows),
        "text_document_count": len(texts),
        "detail_collected_at": datetime.now(timezone.utc).isoformat(),
    }
    return bill, actions, vote_rows, sponsors_as_rows(stub, sponsors), hearings, texts


def sponsors_as_rows(stub: dict, sponsors: list[dict]) -> list[dict]:
    rows = []
    for sponsor in sponsors:
        rows.append(
            {
                "session": stub["session"],
                "bill_identifier": stub["identifier"],
                "name": sponsor.get("name"),
                "classification": sponsor.get("classification"),
                "primary": bool(sponsor.get("primary")),
                "entity_type": sponsor.get("entity_type"),
                "party": sponsor.get("party"),
                "source_url": sponsor.get("source_url"),
                "source": "nelis",
            }
        )
    return rows


def main() -> None:
    if not STUBS_PATH.exists():
        raise SystemExit(
            f"Missing {STUBS_PATH}. Run python collectors/nv_nelis_bills.py first."
        )

    stubs = json.loads(STUBS_PATH.read_text(encoding="utf-8"))
    limit = os.environ.get("NELIS_DETAIL_LIMIT")
    if limit:
        stubs = stubs[: int(limit)]
        print(f"NELIS_DETAIL_LIMIT={limit}: processing {len(stubs)} stubs")

    skip_party = os.environ.get("NELIS_SKIP_PARTY", "").lower() in {"1", "true", "yes"}
    download_text = os.environ.get("NELIS_DOWNLOAD_TEXT", "").lower() in {"1", "true", "yes"}

    party_cache: dict[str, str] = {}
    if PARTY_CACHE_PATH.exists():
        party_cache = json.loads(PARTY_CACHE_PATH.read_text(encoding="utf-8"))

    client = NelisClient()
    bills: list[dict] = []
    actions: list[dict] = []
    votes: list[dict] = []
    sponsors: list[dict] = []
    hearings: list[dict] = []
    texts: list[dict] = []
    failures: list[dict] = []

    for index, stub in enumerate(stubs, start=1):
        label = f"{stub.get('session')}:{stub.get('identifier')}"
        print(f"[{index}/{len(stubs)}] NELIS detail {label}")
        try:
            bill, bill_actions, bill_votes, bill_sponsors, bill_hearings, bill_texts = enrich_bill(
                client, stub, party_cache, skip_party, download_text
            )
            bills.append(bill)
            actions.extend(bill_actions)
            votes.extend(bill_votes)
            sponsors.extend(bill_sponsors)
            hearings.extend(bill_hearings)
            texts.extend(bill_texts)
            print(
                f"  history={len(bill_actions)} votes={len(bill_votes)} "
                f"sponsors={len(bill_sponsors)} texts={len(bill_texts)}"
            )
        except Exception as exc:  # noqa: BLE001 - collect and continue
            print(f"  FAILED: {exc}")
            failures.append({"bill": label, "error": str(exc)})
            bills.append({**stub, "detail_error": str(exc)})

    NELIS_DIR.mkdir(parents=True, exist_ok=True)
    (NELIS_DIR / "bills.json").write_text(json.dumps(bills, indent=2), encoding="utf-8")
    (NELIS_DIR / "bill-actions.json").write_text(json.dumps(actions, indent=2), encoding="utf-8")
    (NELIS_DIR / "bill-votes.json").write_text(json.dumps(votes, indent=2), encoding="utf-8")
    (NELIS_DIR / "bill-sponsors.json").write_text(json.dumps(sponsors, indent=2), encoding="utf-8")
    (NELIS_DIR / "bill-hearings.json").write_text(json.dumps(hearings, indent=2), encoding="utf-8")
    (NELIS_DIR / "bill-texts.json").write_text(json.dumps(texts, indent=2), encoding="utf-8")
    (NELIS_DIR / "detail-failures.json").write_text(json.dumps(failures, indent=2), encoding="utf-8")
    PARTY_CACHE_PATH.write_text(json.dumps(party_cache, indent=2), encoding="utf-8")

    summary = {
        "collector": "nv_nelis_bill_details.py",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "stub_count": len(stubs),
        "bill_count": len(bills),
        "action_row_count": len(actions),
        "vote_event_count": len(votes),
        "sponsor_row_count": len(sponsors),
        "hearing_row_count": len(hearings),
        "text_doc_count": len(texts),
        "failure_count": len(failures),
        "skip_party": skip_party,
        "download_text": download_text,
    }
    (NELIS_DIR / "collection-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        config = load_config()
        manifest = {"issue_id": config["issue_id"], "state": config["state"]}
    manifest["nelis_detail"] = summary
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Done. NELIS details: bills={len(bills)} actions={len(actions)} "
        f"votes={len(votes)} sponsors={len(sponsors)} failures={len(failures)}"
    )


if __name__ == "__main__":
    main()
