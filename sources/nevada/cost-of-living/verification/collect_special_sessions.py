#!/usr/bin/env python3
"""Manual check of the six 2020-2025 special sessions for healthcare-cost
relevant bills (RUNBOOK step 2 note), for issue nevada-02-cost-of-living.

Full bill lists for each special session were reviewed by title and digest
(see `sessions_checked` / `reviewed_not_relevant` in the output). The bills
in TARGETS are the healthcare-relevant items; this script documents each
with official title, digest, sponsors, full history, and floor votes from
NELIS, in the same shape as the housing issue's verification file.

  python3 sources/nevada/cost-of-living/verification/collect_special_sessions.py
"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "collectors"))
import pass2_nelis  # noqa: E402

OUT = Path(__file__).resolve().parent / "special-sessions.json"

SESSIONS_CHECKED = [
    "31st2020Special",
    "32nd2020Special",
    "33rd2021Special",
    "34th2023Special",
    "35th2023Special",
    "36th2025Special",
]

# (session_path, identifier, nelis bill key, short note)
TARGETS = [
    (
        "31st2020Special",
        "AB3",
        "7127",
        "Pandemic budget bill: reduced FY2020-2021 appropriations, including "
        "Department of Health and Human Services budgets; authorized DHHS "
        "budget transfers and acceptance of additional federal Medicaid money.",
    ),
    (
        "36th2025Special",
        "SB5",
        "12996",
        "Created the Statewide Health Care Access and Recruitment Grant "
        "Program and Account under the Nevada Health Authority to address "
        "critical shortages of providers of health care.",
    ),
]

REVIEWED_NOT_RELEVANT = [
    {
        "session_path": "32nd2020Special",
        "identifier": "SB4",
        "note": (
            "Public-health emergency powers, COVID-19 safety standards for "
            "public accommodations, and related liability limits; reviewed - "
            "not a healthcare cost/access/provider-supply bill."
        ),
    },
    {
        "session_path": "32nd2020Special",
        "identifier": "SCR1",
        "note": (
            "Resolution urging actions on the public health crisis caused by "
            "systemic racism magnified by COVID-19; reviewed - resolution, "
            "not healthcare cost/access legislation."
        ),
    },
    {
        "session_path": "36th2025Special",
        "identifier": "SB3",
        "note": (
            "Silver State General Assistance Program (temporary financial or "
            "in-kind assistance during benefit disruptions); reviewed - "
            "public assistance, not healthcare cost/access."
        ),
    },
    {
        "session_path": "36th2025Special",
        "identifier": "SB7",
        "note": (
            "Occupational-disease (lung disease) presumptions for police and "
            "firefighters; reviewed - workers' compensation, not healthcare "
            "cost/access."
        ),
    },
]


def main() -> None:
    client = pass2_nelis.NelisClient()
    bills = []
    for session_path, identifier, bill_key, short_note in TARGETS:
        print(f"Collecting {session_path} {identifier} (key {bill_key})")
        client.warmup(session_path, bill_key)
        overview_html = client.fill_tab(session_path, bill_key, "Overview")
        overview = pass2_nelis.parse_overview(overview_html, session_path)

        # Vote requirement printed on the bill face (e.g. two-thirds), if any.
        soup = BeautifulSoup(overview_html, "lxml")
        face = soup.get_text(" ", strip=True)
        req = ""
        m = re.search(r"REQUIRES\s+TWO-?THIRDS\s+MAJORITY\s+VOTE[^.<]*", face, re.I)
        if m:
            req = re.sub(r"\s+", " ", m.group(0)).strip()

        votes = []
        votes_shell = client.fill_tab(session_path, bill_key, "Votes")
        for vote_type_id, vote_type_label in pass2_nelis.parse_votes_shell(votes_shell):
            votes_html = client.get_bill_votes(session_path, bill_key, vote_type_id)
            for block in pass2_nelis.parse_chamber_vote_blocks(votes_html, vote_type_label):
                votes.append(
                    {
                        "vote_type": block["vote_type"],
                        "chamber": block["chamber_label"],
                        "counts": block["counts"],
                    }
                )
            time.sleep(0.4)

        bills.append(
            {
                "session_path": session_path,
                "identifier": identifier,
                "nelis_bill_key": bill_key,
                "short_note": short_note,
                "official_title": overview["official_title"],
                "digest_first_1200": overview["digest"][:1200],
                "most_recent_history_action": overview["most_recent_history_action"],
                "vote_requirement": req,
                "sponsors": [
                    {"name": s.get("name"), "classification": s.get("classification")}
                    for s in overview["sponsors"]
                ],
                "history": overview["history"],
                "votes": votes,
            }
        )
        time.sleep(0.75)

    payload = {
        "note": (
            "Manual check of the six 2020-2025 special sessions (31st2020, "
            "32nd2020, 33rd2021, 34th2023, 35th2023, 36th2025) for bills "
            "relevant to healthcare cost/access/provider supply, per RUNBOOK "
            "step 2. Full bill lists were reviewed by title (and digest where "
            "the title was ambiguous); the bills below are the "
            "healthcare-relevant items. The regular pipeline covers only the "
            "four regular sessions (80-83)."
        ),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "sessions_checked": SESSIONS_CHECKED,
        "reviewed_not_relevant": REVIEWED_NOT_RELEVANT,
        "bills": bills,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(bills)} bills)")


if __name__ == "__main__":
    main()
