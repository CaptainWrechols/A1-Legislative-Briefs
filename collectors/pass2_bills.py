#!/usr/bin/env python3
"""Pass 2: votes, actions, sponsors, and legislative progress for known bills only.

Reads sources/nevada/water-scarcity/pass1/bills.json (88 bills). Does not discover
new bills. NELIS is authoritative for Nevada history and roll-call names; OpenStates
adds structured actions/votes and voter party when the bill exists there.

  python collectors/pass2_bills.py
  python collectors/pass2_bills.py --limit 3
  python collectors/pass2_bills.py --skip-openstates
  python collectors/pass2_bills.py --skip-votes   # faster: history + progress only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pass2_common import (  # noqa: E402
    attach_party_from_openstates,
    chamber_label,
    derive_progress_from_nelis,
    derive_progress_from_openstates,
    final_disposition,
    merge_progress,
    now,
    origin_chamber,
    second_chamber,
)
from pass2_nelis import NelisClient, enrich_bill  # noqa: E402
from pass2_openstates import (  # noqa: E402
    collect_openstates_details,
    flatten_actions,
    flatten_sponsors,
    flatten_votes,
    get_api_key,
)

PASS1 = Path("sources/nevada/water-scarcity/pass1")
PASS2 = Path("sources/nevada/water-scarcity/pass2")
PROCESSED = Path("sources/nevada/water-scarcity/processed")

BILLS_JSON = PASS1 / "bills.json"
ABSTRACT_CACHE = PASS1 / "cache_abstracts.json"
NELIS_CACHE = PASS2 / "cache_nelis_pass2.json"
OPENSTATES_CACHE = PASS2 / "cache_openstates_pass2.json"
PARTY_CACHE = PASS2 / "legislator_party_cache.json"


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def bill_key(bill: dict) -> str:
    return f"{bill['session']}:{bill['identifier']}"


def nelis_lookup(abstract_cache: dict, bill: dict) -> tuple[str, str] | None:
    key = bill_key(bill)
    row = abstract_cache.get(key) or {}
    session_path = row.get("session_path")
    nelis_bill_key = row.get("nelis_bill_key")
    if session_path and nelis_bill_key:
        return session_path, str(nelis_bill_key)
    url = bill.get("nelis_url") or ""
    import re

    match = re.search(r"/App/NELIS/REL/([^/]+)/Bill/(\d+)/", url)
    if match:
        return match.group(1), match.group(2)
    return None


def merge_vote_events(nelis_votes: list[dict], openstates_votes: list[dict]) -> list[dict]:
    """Prefer NELIS roll calls; attach OpenStates party to matching ballots when possible."""
    merged: list[dict] = []
    os_by_motion: dict[str, list[dict]] = {}
    for vote in openstates_votes:
        motion = (vote.get("motion_text") or "").lower()
        os_by_motion.setdefault(motion, []).append(vote)

    for vote in nelis_votes:
        motion_key = (vote.get("vote_type") or "").lower()
        os_match = None
        for candidate in os_by_motion.get(motion_key, []):
            os_match = candidate
            break
        if not os_match:
            for candidates in os_by_motion.values():
                for candidate in candidates:
                    if (candidate.get("organization") or "").lower() in (
                        vote.get("chamber_label") or ""
                    ).lower():
                        os_match = candidate
                        break
                if os_match:
                    break

        ballots = []
        for name in vote.get("yea_voters") or []:
            ballots.append({"name": name, "vote": "yea"})
        for name in vote.get("nay_voters") or []:
            ballots.append({"name": name, "vote": "nay"})
        for name in vote.get("not_voting") or []:
            ballots.append({"name": name, "vote": "not voting"})
        for name in vote.get("absent") or []:
            ballots.append({"name": name, "vote": "absent"})
        for name in vote.get("excused") or []:
            ballots.append({"name": name, "vote": "excused"})

        if os_match:
            os_ballots = os_match.get("ballots") or []
            yea_names = attach_party_from_openstates(vote.get("yea_voters") or [], os_ballots)
            nay_names = attach_party_from_openstates(vote.get("nay_voters") or [], os_ballots)
            party_by_name = {row["name"]: row for row in yea_names + nay_names}
            for ballot in ballots:
                enriched = party_by_name.get(ballot["name"])
                if enriched and enriched.get("party"):
                    ballot["party"] = enriched["party"]
                    ballot["party_source"] = enriched.get("party_source")

        counts = vote.get("counts") or {}
        merged.append(
            {
                "session": vote.get("session"),
                "bill_identifier": vote.get("bill_identifier"),
                "date": os_match.get("date") if os_match else None,
                "chamber": vote.get("chamber_label"),
                "motion": vote.get("vote_type"),
                "result": os_match.get("result") if os_match else None,
                "counts": {
                    "yes": counts.get("Yea"),
                    "no": counts.get("Nay"),
                    "not_voting": counts.get("Not Voting"),
                    "absent": counts.get("Absent"),
                    "excused": counts.get("Excused"),
                },
                "ballots": ballots,
                "sources": ["nelis"] + (["openstates"] if os_match else []),
            }
        )

    nelis_keys = {
        (
            (vote.get("motion") or "").lower(),
            (vote.get("chamber") or "").lower(),
        )
        for vote in merged
    }
    for vote in openstates_votes:
        key = (
            (vote.get("motion_text") or "").lower(),
            (vote.get("organization") or "").lower(),
        )
        if key in nelis_keys:
            continue
        merged.append(
            {
                "session": vote.get("session"),
                "bill_identifier": vote.get("bill_identifier"),
                "date": vote.get("date"),
                "chamber": vote.get("organization"),
                "motion": vote.get("motion_text"),
                "result": vote.get("result"),
                "counts": vote.get("counts"),
                "ballots": vote.get("ballots") or [],
                "sources": ["openstates"],
            }
        )
    return merged


def build_progress_row(
    bill: dict,
    nelis: dict | None,
    openstates_detail: dict | None,
) -> dict:
    identifier = bill["identifier"]
    first = origin_chamber(identifier)
    nelis_flags = derive_progress_from_nelis(
        identifier,
        (nelis or {}).get("actions") or [],
        (nelis or {}).get("hearings") or [],
        (nelis or {}).get("votes") or [],
    )
    os_flags = derive_progress_from_openstates(
        (openstates_detail or {}).get("actions") or [],
        (openstates_detail or {}).get("votes") or [],
    )
    flags = merge_progress(nelis_flags, os_flags)
    return {
        "session": bill["session"],
        "bill_identifier": identifier,
        "title": bill.get("title"),
        "origin_chamber": first,
        "origin_chamber_label": chamber_label(first),
        "second_chamber": second_chamber(first),
        "second_chamber_label": chamber_label(second_chamber(first)),
        "milestones": {
            "seen_in_committee_origin": flags["seen_in_committee_origin"],
            "passed_out_of_committee_origin": flags["passed_out_of_committee_origin"],
            "floor_vote_origin_chamber": flags["floor_vote_origin_chamber"],
            "passed_origin_chamber": flags["passed_origin_chamber"],
            "crossed_over": flags["crossed_over"],
            "seen_in_committee_second_chamber": flags["seen_in_committee_second_chamber"],
            "passed_out_of_committee_second_chamber": flags["passed_out_of_committee_second_chamber"],
            "floor_vote_second_chamber": flags["floor_vote_second_chamber"],
            "passed_second_chamber": flags["passed_second_chamber"],
            "signed_into_law": flags["signed_into_law"],
            "vetoed": flags["vetoed"],
            "failed": flags["failed"],
        },
        "final_disposition": final_disposition(flags),
        "most_recent_action": (nelis or {}).get("most_recent_history_action")
        or (openstates_detail or {}).get("latest_action_description"),
        "nelis_url": bill.get("nelis_url"),
        "openstates_url": (openstates_detail or {}).get("openstates_url") or bill.get("openstates_url"),
        "sources": {
            "nelis": bool(nelis),
            "openstates": bool(openstates_detail),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-openstates", action="store_true")
    parser.add_argument("--skip-votes", action="store_true", help="Skip NELIS roll-call member fetches")
    parser.add_argument("--skip-party", action="store_true", help="Skip NELIS legislator party lookups")
    args = parser.parse_args()

    if not BILLS_JSON.exists():
        raise SystemExit(f"Missing {BILLS_JSON}. Run pass1_bills.py first.")

    payload = load_json(BILLS_JSON, {})
    bills = payload.get("bills") or []
    if args.limit:
        bills = bills[: args.limit]

    abstract_cache = load_json(ABSTRACT_CACHE, {})
    nelis_cache = {} if args.refresh else load_json(NELIS_CACHE, {})
    openstates_cache = {} if args.refresh else load_json(OPENSTATES_CACHE, {})
    party_cache = load_json(PARTY_CACHE, {})

    PASS2.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    client = NelisClient()
    nelis_failures: list[dict] = []
    all_actions: list[dict] = []
    all_sponsors: list[dict] = []
    all_vote_events: list[dict] = []
    progress_rows: list[dict] = []
    data_gaps: list[dict] = []

    print(f"Pass 2 NELIS enrichment for {len(bills)} known bills")
    for index, bill in enumerate(bills, start=1):
        key = bill_key(bill)
        if key in nelis_cache and nelis_cache[key].get("actions") is not None and not args.refresh:
            print(f"[{index}/{len(bills)}] NELIS {key} (cached)")
            nelis_row = nelis_cache[key]
        else:
            lookup = nelis_lookup(abstract_cache, bill)
            if not lookup:
                print(f"[{index}/{len(bills)}] NELIS {key} SKIP — no NELIS URL/key")
                nelis_failures.append({"bill": key, "error": "missing_nelis_key"})
                nelis_row = None
            else:
                session_path, nelis_bill_key = lookup
                print(f"[{index}/{len(bills)}] NELIS {key} fetching…")
                try:
                    nelis_row = enrich_bill(
                        client,
                        session=bill["session"],
                        identifier=bill["identifier"],
                        session_path=session_path,
                        bill_key=nelis_bill_key,
                        party_cache=party_cache,
                        skip_party=args.skip_party,
                        skip_votes=args.skip_votes,
                    )
                    nelis_cache[key] = nelis_row
                    save_json(NELIS_CACHE, nelis_cache)
                except Exception as exc:  # noqa: BLE001
                    print(f"  FAILED: {exc}")
                    nelis_failures.append({"bill": key, "error": str(exc)})
                    nelis_row = None

        if nelis_row:
            all_actions.extend(nelis_row.get("actions") or [])
            for sponsor in nelis_row.get("sponsors") or []:
                all_sponsors.append(
                    {
                        "session": bill["session"],
                        "bill_identifier": bill["identifier"],
                        "name": sponsor.get("name"),
                        "classification": sponsor.get("classification"),
                        "primary": sponsor.get("primary"),
                        "entity_type": sponsor.get("entity_type"),
                        "party": sponsor.get("party"),
                        "source": "nelis",
                    }
                )

    openstates_details: list[dict] = []
    openstates_failures: list[dict] = []
    api_key = get_api_key()
    if args.skip_openstates:
        print("Skipping OpenStates (--skip-openstates)")
    elif not api_key:
        print("No OPENSTATES_API_KEY — skipping OpenStates detail fetch")
        data_gaps.append(
            {
                "topic": "openstates_detail",
                "session": "all",
                "result": "skipped",
                "notes": "OPENSTATES_API_KEY not set; voter party may be missing on NELIS-only roll calls",
            }
        )
    else:
        openstates_details, openstates_failures = collect_openstates_details(
            bills, api_key=api_key, cache=openstates_cache, refresh=args.refresh
        )
        save_json(OPENSTATES_CACHE, openstates_cache)

    os_by_key = {
        f"{row['session']}:{row['identifier']}": row.get("detail")
        for row in openstates_details
        if row.get("detail")
    }

    for bill in bills:
        key = bill_key(bill)
        nelis_row = nelis_cache.get(key)
        os_detail = os_by_key.get(key)
        if os_detail:
            all_actions.extend(flatten_actions(os_detail))
            all_sponsors.extend(flatten_sponsors(os_detail))
        os_votes = flatten_votes(os_detail) if os_detail else []
        nelis_votes = (nelis_row or {}).get("votes") or []
        merged_votes = merge_vote_events(nelis_votes, os_votes)
        all_vote_events.extend(merged_votes)
        progress_rows.append(build_progress_row(bill, nelis_row, os_detail))

        missing_party = 0
        total_ballots = 0
        for vote in merged_votes:
            for ballot in vote.get("ballots") or []:
                total_ballots += 1
                if not ballot.get("party"):
                    missing_party += 1
        if total_ballots and missing_party:
            data_gaps.append(
                {
                    "topic": "voter_party",
                    "session": bill["session"],
                    "bill_identifier": bill["identifier"],
                    "result": "partial",
                    "notes": (
                        f"{missing_party}/{total_ballots} roll-call rows lack party "
                        f"(OpenStates missing or name mismatch)"
                    ),
                }
            )
        if not os_detail:
            data_gaps.append(
                {
                    "topic": "openstates_detail",
                    "session": bill["session"],
                    "bill_identifier": bill["identifier"],
                    "result": "missing",
                    "notes": "Bill not returned from OpenStates detail lookup",
                }
            )

    save_json(PARTY_CACHE, party_cache)
    save_json(PROCESSED / "bill-actions.json", all_actions)
    save_json(PROCESSED / "bill-sponsors.json", all_sponsors)
    save_json(PROCESSED / "bill-votes.json", all_vote_events)
    save_json(PROCESSED / "bill-legislative-progress.json", progress_rows)
    save_json(
        PROCESSED / "pass2-summary.json",
        {
            "pass": 2,
            "collected_at": now(),
            "bill_count": len(bills),
            "action_rows": len(all_actions),
            "sponsor_rows": len(all_sponsors),
            "vote_events": len(all_vote_events),
            "openstates_found": len(os_by_key),
            "nelis_failures": nelis_failures,
            "openstates_failures": openstates_failures,
            "skip_votes": args.skip_votes,
            "note": (
                "Scoped to pass1/bills.json only. NELIS provides roll-call names; "
                "OpenStates provides voter party when the bill exists and names match."
            ),
        },
    )
    save_json(PROCESSED / "data-gaps.json", data_gaps)

    print(
        f"Done. actions={len(all_actions)} votes={len(all_vote_events)} "
        f"progress={len(progress_rows)} openstates_found={len(os_by_key)} "
        f"-> {PROCESSED}"
    )


if __name__ == "__main__":
    main()
