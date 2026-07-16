#!/usr/bin/env python3
"""Extract committee work-session votes from NELIS Meetings + minutes PDFs.

NELIS Votes tab only exposes floor Final Passage roll calls. Committee outcomes
and (when recorded) who voted no / was absent live in committee minutes PDFs.

  python collectors/pass2_committee_votes.py
  python collectors/pass2_committee_votes.py --limit 5
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pass2_party_roster import build_lookup, match_party  # noqa: E402

PASS1 = Path("sources/nevada/water-scarcity/pass1")
PASS2 = Path("sources/nevada/water-scarcity/pass2")
PROCESSED = Path("sources/nevada/water-scarcity/processed")
RAW = Path("sources/nevada/water-scarcity/raw/committee-minutes")

ABSTRACT_CACHE = PASS1 / "cache_abstracts.json"
PROGRESS = PROCESSED / "bill-legislative-progress.json"
NELIS_CACHE = PASS2 / "cache_nelis_pass2.json"
ROSTER = PASS2 / "legislator_roster.json"
MEETINGS_CACHE = PASS2 / "cache_committee_meetings.json"
OUT = PROCESSED / "bill-committee-votes.json"
VOTES = PROCESSED / "bill-votes.json"

BASE = "https://www.leg.state.nv.us"
UA = {
    "User-Agent": "ForumLegislativeBrief/1.0",
    "X-Requested-With": "XMLHttpRequest",
}
REQUEST_DELAY = 0.4

ACTION_RECS = re.compile(
    r"(do pass|do not pass|without recommendation|amend,\s*and do pass|indefinitely postpone)",
    re.I,
)


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


def nelis_ids(abstract_cache: dict, progress_row: dict, nelis_cache: dict) -> tuple[str, str] | None:
    key = bill_key(progress_row["session"], progress_row["bill_identifier"])
    for store in (abstract_cache, nelis_cache):
        row = store.get(key) or {}
        if row.get("session_path") and row.get("nelis_bill_key"):
            return row["session_path"], str(row["nelis_bill_key"])
    url = progress_row.get("nelis_url") or ""
    match = re.search(r"/App/NELIS/REL/([^/]+)/Bill/(\d+)/", url)
    if match:
        return match.group(1), match.group(2)
    return None


def fetch_meetings(
    session: requests.Session, session_path: str, bill_key_id: str
) -> list[dict]:
    warm = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{bill_key_id}/Overview"
    session.get(warm, timeout=60)
    time.sleep(REQUEST_DELAY)
    fill = f"{BASE}/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
    html = session.get(
        fill, params={"selectedTab": "Meetings", "billKey": bill_key_id}, timeout=60
    ).text
    time.sleep(REQUEST_DELAY)
    soup = BeautifulSoup(html, "lxml")
    meetings: list[dict] = []

    # Each meeting starts with an h2 (committee + date). Content lives in following
    # sibling rows of the heading's parent .row, so walk from that row downward.
    headings = soup.find_all("h2")
    for index, heading in enumerate(headings):
        committee = ""
        date = ""
        for anchor in heading.find_all("a", href=True):
            href = anchor.get("href") or ""
            name = clean(anchor.get_text(" ", strip=True))
            if "/Committee/" in href:
                committee = name
            elif "/Meeting/" in href:
                date = name
        if not committee and not date:
            continue

        start_row = heading.find_parent("div", class_=re.compile(r"\brow\b"))
        if start_row is None:
            start_row = heading.parent
        end_row = None
        if index + 1 < len(headings):
            end_row = headings[index + 1].find_parent("div", class_=re.compile(r"\brow\b"))

        block_bits = [str(start_row)]
        for sibling in start_row.next_siblings:
            if end_row is not None and sibling == end_row:
                break
            if getattr(sibling, "name", None) is not None:
                # Stop if we hit another meeting heading row.
                if sibling.find("h2"):
                    break
                block_bits.append(str(sibling))
        block = BeautifulSoup("".join(block_bits), "lxml")

        minutes_url = None
        agenda_url = None
        for anchor in block.find_all("a", href=True):
            label = clean(anchor.get_text(" ", strip=True)).lower()
            href = anchor["href"]
            url = href if href.startswith("http") else f"{BASE}{href}"
            if label == "minutes" or "/Minutes/" in href:
                minutes_url = url
            elif label == "agenda" or "/Agendas/" in href:
                agenda_url = url

        recommendation = ""
        actions_h = block.find(["h3", "h4"], string=re.compile(r"^\s*Actions\s*$", re.I))
        if actions_h:
            para = actions_h.find_next("p")
            if para:
                recommendation = clean(para.get_text(" ", strip=True))
        if not recommendation:
            blob = clean(block.get_text(" ", strip=True))
            full = re.search(
                r"(Heard(?:,\s*No Action)?|Amend,\s*and do pass as amended|Do pass(?: as amended)?|"
                r"Do not pass|Without recommendation|Indefinitely postpone)",
                blob,
                flags=re.I,
            )
            if full:
                recommendation = clean(full.group(1))

        meetings.append(
            {
                "committee": committee,
                "date": date,
                "recommendation": recommendation,
                "minutes_url": minutes_url,
                "agenda_url": agenda_url,
                "is_work_session": "work session" in clean(heading.get_text(" ", strip=True)).lower(),
            }
        )

    # Dedupe by minutes URL + recommendation
    unique: dict[str, dict] = {}
    for meeting in meetings:
        key = f"{meeting.get('minutes_url')}|{meeting.get('recommendation')}|{meeting.get('date')}"
        unique[key] = meeting
    return list(unique.values())


def download_pdf(session: requests.Session, url: str, dest: Path) -> bytes:
    if dest.exists() and dest.stat().st_size > 0:
        return dest.read_bytes()
    response = session.get(url, timeout=120)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    time.sleep(REQUEST_DELAY)
    return response.content


def pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def bill_patterns(identifier: str) -> list[re.Pattern]:
    m = re.match(r"([A-Z]+)(\d+)", identifier or "")
    if not m:
        return []
    prefix, num = m.group(1), m.group(2)
    # Assembly Bill 163 / A.B. 163 / AB 163 / AB163
    variants = [
        rf"\b{prefix}\s*{num}\b",
        rf"\b{prefix[0]}\.?B\.?\s*{num}\b" if prefix.endswith("B") else rf"\b{prefix}\s*{num}\b",
        rf"Assembly Bill\s*{num}" if prefix.startswith("A") else rf"Senate Bill\s*{num}",
        rf"A\.B\.\s*{num}" if prefix.startswith("A") else rf"S\.B\.\s*{num}",
    ]
    return [re.compile(p, re.I) for p in variants]


def extract_names_list(blob: str) -> list[str]:
    """Parse 'ASSEMBLYMEN ELLISON, HANSEN, TITUS, AND WHEELER' style lists."""
    blob = clean(blob)
    blob = re.sub(
        r"^(ASSEMBLYMEN|ASSEMBLYWOM[AE]N|ASSEMBLYMEMBERS|SENATORS|SENATOR)\s+",
        "",
        blob,
        flags=re.I,
    )
    blob = re.sub(r"\s+AND\s+", ", ", blob, flags=re.I)
    parts = [clean(p) for p in blob.split(",") if clean(p)]
    names = []
    for part in parts:
        part = re.sub(r"\b(WAS|WERE|VOTED|ABSENT|FOR THE VOTE)\b.*$", "", part, flags=re.I)
        part = clean(part)
        if not part or len(part) < 2:
            continue
        # Minutes usually use LAST only or FIRST LAST; convert "ELLISON" stays,
        # "STEVE YEAGER" -> "Yeager, Steve" if two tokens.
        tokens = part.title().split()
        if len(tokens) == 1:
            names.append(tokens[0])
        else:
            names.append(f"{tokens[-1]}, {' '.join(tokens[:-1])}")
    return names


def parse_committee_vote_from_minutes(text: str, identifier: str) -> dict | None:
    patterns = bill_patterns(identifier)
    if not patterns:
        return None

    # Normalize whitespace for regex windows
    flat = re.sub(r"[ \t]+", " ", text)
    # Find windows that mention the bill and a motion result nearby
    hits = []
    for pat in patterns:
        for match in pat.finditer(flat):
            start = max(0, match.start() - 400)
            end = min(len(flat), match.end() + 1200)
            hits.append(flat[start:end])
    if not hits:
        return None

    # Prefer a window containing MOTION PASSED/FAILED near the bill
    window = None
    for hit in hits:
        if re.search(r"THE MOTION (PASSED|FAILED|WAS)", hit, re.I):
            window = hit
            break
    if not window:
        window = hits[0]

    result = None
    if re.search(r"MOTION PASSED UNANIMOUSLY", window, re.I):
        result = "pass_unanimous"
    elif re.search(r"THE MOTION PASSED", window, re.I):
        result = "pass"
    elif re.search(r"THE MOTION FAILED", window, re.I):
        result = "fail"
    elif re.search(r"do pass", window, re.I):
        result = "pass_inferred"
    else:
        result = "unknown"

    nay: list[str] = []
    absent: list[str] = []
    nay_match = re.search(
        r"\(([^)]*?)\s+VOTED NO\.?\s*([^)]*)\)",
        window,
        flags=re.I | re.S,
    )
    if nay_match:
        nay = extract_names_list(nay_match.group(1))
        absent_part = nay_match.group(2) or ""
        abs_match = re.search(
            r"((?:ASSEMBLYMEN|ASSEMBLYWOM[AE]N|ASSEMBLYMEMBERS|SENATORS).+?)\s+(?:WAS|WERE)\s+ABSENT",
            absent_part,
            flags=re.I,
        )
        if abs_match:
            absent = extract_names_list(abs_match.group(1))
    else:
        abs_only = re.search(
            r"\(((?:ASSEMBLYMEN|ASSEMBLYWOM[AE]N|ASSEMBLYMEMBERS|SENATORS).+?)\s+(?:WAS|WERE)\s+ABSENT[^)]*\)",
            window,
            flags=re.I | re.S,
        )
        if abs_only:
            absent = extract_names_list(abs_only.group(1))

    motion = None
    motion_match = re.search(
        r"(MOVED TO|MOTION TO|MADE A MOTION TO)\s+([^\n\.]{5,80})",
        window,
        flags=re.I,
    )
    if motion_match:
        motion = clean(motion_match.group(2))

    return {
        "result": result,
        "motion": motion,
        "nay_voters": nay,
        "absent": absent,
        "excerpt": clean(window)[:900],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    progress = load_json(PROGRESS, [])
    abstract_cache = load_json(ABSTRACT_CACHE, {})
    nelis_cache = load_json(NELIS_CACHE, {})
    meetings_cache = {} if args.refresh else load_json(MEETINGS_CACHE, {})
    roster = load_json(ROSTER, {})
    lookup = build_lookup(roster.get("members") or [])

    if args.limit:
        progress = progress[: args.limit]

    client = requests.Session()
    client.headers.update(UA)

    committee_votes: list[dict] = []
    print(f"Collecting committee meetings/votes for {len(progress)} bills")

    for index, row in enumerate(progress, start=1):
        key = bill_key(row["session"], row["bill_identifier"])
        print(f"[{index}/{len(progress)}] {key}")
        if key in meetings_cache and not args.refresh:
            meetings = meetings_cache[key].get("meetings") or []
        else:
            ids = nelis_ids(abstract_cache, row, nelis_cache)
            if not ids:
                print("  skip — no NELIS ids")
                continue
            try:
                meetings = fetch_meetings(client, ids[0], ids[1])
                meetings_cache[key] = {
                    "session": row["session"],
                    "bill_identifier": row["bill_identifier"],
                    "meetings": meetings,
                    "collected_at": now(),
                }
                save_json(MEETINGS_CACHE, meetings_cache)
            except Exception as exc:  # noqa: BLE001
                print(f"  meetings FAILED: {exc}")
                continue

        # Keep all meetings as hearing rows; parse minutes only for action recommendations.
        for meeting in meetings:
            rec = meeting.get("recommendation") or ""
            if not ACTION_RECS.search(rec):
                committee_votes.append(
                    {
                        "session": row["session"],
                        "bill_identifier": row["bill_identifier"],
                        "vote_kind": "committee_hearing",
                        "committee": meeting.get("committee"),
                        "date": meeting.get("date"),
                        "chamber": meeting.get("committee"),
                        "motion": rec or "Heard",
                        "result": rec or "Heard",
                        "recommendation": rec,
                        "counts": {},
                        "ballots": [],
                        "minutes_url": meeting.get("minutes_url"),
                        "source": "nelis_meetings",
                        "roll_call_available": False,
                    }
                )

        actionable = [
            m
            for m in meetings
            if m.get("recommendation")
            and ACTION_RECS.search(m.get("recommendation") or "")
            and m.get("minutes_url")
        ]
        seen_minutes: set[str] = set()
        for meeting in actionable:
            minutes_url = meeting.get("minutes_url") or ""
            dedupe_key = f"{minutes_url}|{meeting.get('recommendation')}"
            if dedupe_key in seen_minutes:
                continue
            seen_minutes.add(dedupe_key)
            dest = (
                RAW
                / row["session"]
                / row["bill_identifier"]
                / re.sub(r"[^A-Za-z0-9._-]+", "_", Path(meeting["minutes_url"]).name)
            )
            try:
                data = download_pdf(client, meeting["minutes_url"], dest)
                text = pdf_text(data)
                parsed = parse_committee_vote_from_minutes(text, row["bill_identifier"])
            except Exception as exc:  # noqa: BLE001
                print(f"  minutes FAILED ({meeting.get('date')}): {exc}")
                parsed = None

            ballots = []
            if parsed:
                for name in parsed.get("nay_voters") or []:
                    party, source, matched = match_party(name, lookup)
                    if not party:
                        # last-name only fallback
                        cands = [
                            m
                            for m in {id(v): v for v in lookup.values()}.values()
                            if (m.get("name") or "").split(",")[0].lower() == name.lower()
                            or (m.get("name") or "").lower().startswith(name.lower() + ",")
                        ]
                        if len(cands) == 1:
                            party, source, matched = (
                                cands[0].get("party"),
                                cands[0].get("source"),
                                cands[0].get("name"),
                            )
                    ballots.append(
                        {
                            "name": matched or name,
                            "vote": "nay",
                            "party": party,
                            "party_source": source,
                            "raw_name": name,
                        }
                    )
                for name in parsed.get("absent") or []:
                    party, source, matched = match_party(name, lookup)
                    ballots.append(
                        {
                            "name": matched or name,
                            "vote": "absent",
                            "party": party,
                            "party_source": source,
                            "raw_name": name,
                        }
                    )

            committee_votes.append(
                {
                    "session": row["session"],
                    "bill_identifier": row["bill_identifier"],
                    "vote_kind": "committee_work_session",
                    "committee": meeting.get("committee"),
                    "date": meeting.get("date"),
                    "chamber": meeting.get("committee"),
                    "motion": (parsed or {}).get("motion") or meeting.get("recommendation"),
                    "result": (parsed or {}).get("result") or meeting.get("recommendation"),
                    "recommendation": meeting.get("recommendation"),
                    "counts": {
                        "no": len((parsed or {}).get("nay_voters") or []),
                        "absent": len((parsed or {}).get("absent") or []),
                    },
                    "ballots": ballots,
                    "nay_voters": (parsed or {}).get("nay_voters") or [],
                    "absent": (parsed or {}).get("absent") or [],
                    "minutes_url": meeting.get("minutes_url"),
                    "excerpt": (parsed or {}).get("excerpt"),
                    "source": "nelis_committee_minutes",
                    "roll_call_available": bool(parsed and parsed.get("result") not in {None, "unknown"}),
                    "note": (
                        "Nevada committee minutes usually list only NO and ABSENT by name; "
                        "YEAs are not individually itemized unless the motion was not unanimous."
                    ),
                }
            )
            print(
                f"  committee vote: {meeting.get('committee')} / {meeting.get('recommendation')} "
                f"parsed={bool(parsed)}"
            )

    save_json(OUT, committee_votes)

    # Merge into bill-votes.json: keep floor votes, append committee votes
    floor_votes = load_json(VOTES, [])
    floor_only = [
        v
        for v in floor_votes
        if v.get("vote_kind") not in {"committee_work_session", "committee_hearing"}
        and v.get("source") != "nelis_committee_minutes"
    ]
    # mark floor votes
    for vote in floor_only:
        vote.setdefault("vote_kind", "floor_final_passage")
    merged = floor_only + committee_votes
    save_json(VOTES, merged)

    print(
        f"Wrote {OUT}: {len(committee_votes)} committee rows; "
        f"merged votes file now {len(merged)} events"
    )


if __name__ == "__main__":
    main()
