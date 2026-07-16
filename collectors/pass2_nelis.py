"""NELIS Pass 2 enrichment for bills already in pass1/bills.json."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pass2_common import (  # noqa: E402
    VOTE_PANELS,
    clean_text,
    get,
    now,
)

BASE = "https://www.leg.state.nv.us"
UA = {
    "User-Agent": "ForumLegislativeBrief/1.0",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "*/*",
}
REQUEST_DELAY = 0.4


class NelisClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(UA)

    def _pause(self) -> None:
        import time

        time.sleep(REQUEST_DELAY)

    def warmup(self, session_path: str, bill_key: str) -> None:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{bill_key}/Overview"
        get(url, session=self.session)
        self._pause()

    def fill_tab(self, session_path: str, bill_key: str, selected_tab: str) -> str:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
        response = get(
            url,
            params={"selectedTab": selected_tab, "billKey": bill_key},
            session=self.session,
        )
        self._pause()
        return response.text

    def get_bill_votes(self, session_path: str, bill_key: str, vote_type_id: str) -> str:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/GetBillVotes"
        response = get(
            url,
            params={"billKey": bill_key, "voteTypeId": vote_type_id},
            session=self.session,
        )
        self._pause()
        return response.text

    def get_vote_members(self, session_path: str, vote_key: str, panel: str) -> list[str]:
        url = f"{BASE}/App/NELIS/REL/{session_path}/Bill/GetBillVoteMembers"
        response = get(
            url,
            params={"voteKey": vote_key, "voteResultPanel": panel},
            session=self.session,
        )
        self._pause()
        return parse_vote_member_names(response.text)

    def fetch_legislator_party(self, url: str, party_cache: dict[str, str]) -> str | None:
        if not url or "Legislator" not in url:
            return None
        if url in party_cache:
            return party_cache[url] or None
        try:
            response = get(url if url.startswith("http") else urljoin(BASE, url), session=self.session)
            match = re.search(r"Party:\s*([A-Za-z]+)", response.text)
            party = match.group(1) if match else ""
            party_cache[url] = party
            return party or None
        except RuntimeError:
            party_cache[url] = ""
            return None


def parse_vote_member_names(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    names: list[str] = []
    for div in soup.find_all("div", class_=re.compile(r"\bvote\b")):
        text = clean_text(div.get_text(" ", strip=True))
        if text:
            names.append(text)
    if names:
        return names
    for anchor in soup.find_all("a"):
        text = clean_text(anchor.get_text(" ", strip=True))
        if text:
            names.append(text)
    return names


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
                "session_path": session_path,
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
        for element in list(container.next_elements)[:80]:
            if getattr(element, "name", None) == "a" and element.get("href"):
                href = element["href"]
                name = clean_text(element.get_text(" ", strip=True))
                if name and ("Legislator" in href or "Committee" in href):
                    add(name, classification, href)
            if getattr(element, "name", None) in {"h2", "h3", "h4"}:
                heading = clean_text(element.get_text(" ", strip=True)).lower()
                if heading and "sponsor" not in heading and any(
                    stop in heading
                    for stop in ("title", "digest", "hearing", "history", "vote", "summary")
                ):
                    break
    return sponsors


def parse_history(soup: BeautifulSoup) -> list[dict]:
    rows: list[dict] = []
    for table in soup.find_all("table"):
        headers = [clean_text(th.get_text(" ", strip=True)).lower() for th in table.find_all("th")]
        if not headers:
            first = table.find("tr")
            if first:
                headers = [
                    clean_text(cell.get_text(" ", strip=True)).lower()
                    for cell in first.find_all(["th", "td"])
                ]
        if not any("action" in header for header in headers):
            continue
        body_rows = table.find_all("tr")
        start = 1 if body_rows and body_rows[0].find("th") else 1
        for row in body_rows[start:]:
            cells = [clean_text(cell.get_text(" ", strip=True)) for cell in row.find_all("td")]
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
        first = table.find("tr")
        headers = (
            [clean_text(cell.get_text(" ", strip=True)).lower() for cell in first.find_all(["th", "td"])]
            if first
            else []
        )
        if not any("recommendation" in header for header in headers):
            continue
        for row in table.find_all("tr")[1:]:
            cells = [clean_text(cell.get_text(" ", strip=True)) for cell in row.find_all("td")]
            if len(cells) < 3:
                continue
            if len(cells) >= 8:
                hearings.append(
                    {
                        "committee": cells[2],
                        "date": cells[3],
                        "time": cells[4],
                        "recommendation": cells[7],
                    }
                )
            else:
                hearings.append(
                    {
                        "committee": cells[1] if len(cells) > 1 else "",
                        "date": cells[2] if len(cells) > 2 else "",
                        "time": cells[3] if len(cells) > 3 else "",
                        "recommendation": cells[-1],
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


def parse_votes_shell(html: str) -> list[tuple[str, str]]:
    pairs = re.findall(
        r"GetBillVotes\?billKey=\d+&amp;voteTypeId=(\d+)\">([^<]+)",
        html,
    )
    return [(vote_id, clean_text(label)) for vote_id, label in pairs]


def parse_chamber_vote_blocks(html: str, vote_type_label: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    blocks: list[dict] = []
    for heading in soup.find_all(["h2", "h3"]):
        chamber = clean_text(heading.get_text(" ", strip=True))
        if not chamber or chamber.lower() == "votes":
            continue
        section_html = ""
        for sibling in heading.next_siblings:
            if getattr(sibling, "name", None) in {"h2", "h3"}:
                break
            section_html += str(sibling)
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


def enrich_bill(
    client: NelisClient,
    *,
    session: str,
    identifier: str,
    session_path: str,
    bill_key: str,
    party_cache: dict[str, str],
    skip_party: bool,
    skip_votes: bool,
) -> dict:
    client.warmup(session_path, bill_key)
    overview_html = client.fill_tab(session_path, bill_key, "Overview")
    overview = parse_overview(overview_html, session_path)

    sponsors = overview["sponsors"]
    if not skip_party:
        for sponsor in sponsors:
            party = client.fetch_legislator_party(sponsor.get("source_url") or "", party_cache)
            if party:
                sponsor["party"] = party

    actions = [
        {
            "session": session,
            "bill_identifier": identifier,
            "date": row["date"],
            "description": row["description"],
            "journal": row.get("journal", ""),
            "source": "nelis",
        }
        for row in overview["history"]
    ]

    hearings = [
        {
            "session": session,
            "bill_identifier": identifier,
            **hearing,
            "source": "nelis",
        }
        for hearing in overview["hearings"]
    ]

    vote_rows: list[dict] = []
    if not skip_votes:
        votes_shell = client.fill_tab(session_path, bill_key, "Votes")
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
                        "session": session,
                        "bill_identifier": identifier,
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
                        "source": "nelis",
                    }
                )

    return {
        "session": session,
        "identifier": identifier,
        "nelis_bill_key": bill_key,
        "session_path": session_path,
        "official_title": overview["official_title"],
        "most_recent_history_action": overview["most_recent_history_action"],
        "sponsors": sponsors,
        "actions": actions,
        "hearings": hearings,
        "votes": vote_rows,
        "collected_at": now(),
    }
