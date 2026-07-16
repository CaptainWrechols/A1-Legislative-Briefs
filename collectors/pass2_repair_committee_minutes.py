#!/usr/bin/env python3
"""Re-parse committee work-session minutes URLs already stored on vote rows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pass2_committee_votes import (  # noqa: E402
    download_pdf,
    parse_committee_vote_from_minutes,
    pdf_text,
)
from pass2_party_roster import build_lookup, match_party  # noqa: E402

PASS2 = Path("sources/nevada/water-scarcity/pass2")
PROCESSED = Path("sources/nevada/water-scarcity/processed")
COMMITTEE_VOTES = PROCESSED / "bill-committee-votes.json"
RAW = Path("sources/nevada/water-scarcity/raw/committee-minutes")
ROSTER = PASS2 / "legislator_roster.json"


def main() -> None:
    votes = json.loads(COMMITTEE_VOTES.read_text(encoding="utf-8"))
    roster = json.loads(ROSTER.read_text(encoding="utf-8")) if ROSTER.exists() else {}
    lookup = build_lookup(roster.get("members") or [])
    client = requests.Session()
    client.headers.update({"User-Agent": "ForumLegislativeBrief/1.0"})

    updated = 0
    for vote in votes:
        if vote.get("vote_kind") != "committee_work_session":
            continue
        url = vote.get("minutes_url")
        if not url:
            continue
        dest = (
            RAW
            / str(vote.get("session"))
            / str(vote.get("bill_identifier"))
            / Path(url).name
        )
        try:
            data = download_pdf(client, url, dest)
            text = pdf_text(data)
            parsed = parse_committee_vote_from_minutes(text, vote["bill_identifier"])
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED {vote.get('session')}:{vote.get('bill_identifier')} {exc}")
            continue
        if not parsed:
            continue
        ballots = []
        for name in parsed.get("nay_voters") or []:
            party, source, matched = match_party(name, lookup)
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
        vote["result"] = parsed.get("result") or vote.get("result")
        vote["motion"] = parsed.get("motion") or vote.get("motion")
        vote["nay_voters"] = parsed.get("nay_voters") or []
        vote["absent"] = parsed.get("absent") or []
        vote["excerpt"] = parsed.get("excerpt")
        vote["ballots"] = ballots
        vote["counts"] = {
            "no": len(vote["nay_voters"]),
            "absent": len(vote["absent"]),
        }
        vote["roll_call_available"] = bool(
            parsed.get("result") not in {None, "unknown"}
        )
        # Clear prior inferred yeas; pass2_committee_yeas will rebuild them.
        vote.pop("yea_voters", None)
        vote.pop("yea_inference", None)
        vote.pop("yea_inference_note", None)
        updated += 1
        print(
            f"{vote['session']}:{vote['bill_identifier']} {vote.get('committee')} "
            f"nays={vote['nay_voters']} absent={vote['absent']} result={vote.get('result')}"
        )

    COMMITTEE_VOTES.write_text(json.dumps(votes, indent=2), encoding="utf-8")
    print(f"Repaired {updated} work-session rows -> {COMMITTEE_VOTES}")


if __name__ == "__main__":
    main()
