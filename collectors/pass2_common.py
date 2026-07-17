"""Shared helpers for Pass 2 (scoped to pass1/bills.json only)."""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import requests

SESSION_PATHS = {"80": "80th2019", "81": "81st2021", "82": "82nd2023", "83": "83rd2025"}

VOTE_PANELS = ("Yea", "Nay", "Not Voting", "Absent", "Excused")

PROGRESS_FIELDS = (
    "seen_in_committee_origin",
    "passed_out_of_committee_origin",
    "floor_vote_origin_chamber",
    "passed_origin_chamber",
    "crossed_over",
    "seen_in_committee_second_chamber",
    "passed_out_of_committee_second_chamber",
    "floor_vote_second_chamber",
    "passed_second_chamber",
    "signed_into_law",
    "vetoed",
    "failed",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def origin_chamber(identifier: str) -> str:
    ident = (identifier or "").upper()
    if ident.startswith(("AB", "AJR", "ACR")):
        return "lower"
    if ident.startswith(("SB", "SJR", "SCR")):
        return "upper"
    return ""


def second_chamber(first: str) -> str:
    if first == "lower":
        return "upper"
    if first == "upper":
        return "lower"
    return ""


def chamber_label(code: str) -> str:
    return {"lower": "Assembly", "upper": "Senate"}.get(code, code or "Unknown")


def norm_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def get(
    url: str,
    *,
    params=None,
    headers=None,
    session: requests.Session | None = None,
    timeout: int = 90,
) -> requests.Response:
    client = session or requests
    last: object = None
    for attempt in range(6):
        try:
            response = client.get(url, params=params, headers=headers, timeout=timeout)
            if response.status_code in {429, 502, 503, 504}:
                wait = int(response.headers.get("Retry-After") or min(120, 15 * (2**attempt)))
                print(f"  HTTP {response.status_code}; sleep {wait}s")
                time.sleep(wait)
                last = response
                continue
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last = exc
            wait = min(120, 15 * (2**attempt))
            print(f"  failed ({exc}); sleep {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Gave up: {url} ({last})")


def empty_progress() -> dict:
    return {field: False for field in PROGRESS_FIELDS}


def derive_progress_from_nelis(
    identifier: str,
    history: list[dict],
    hearings: list[dict],
    vote_rows: list[dict],
) -> dict:
    """Infer milestone yes/no flags from NELIS history, hearings, and vote labels."""
    flags = empty_progress()
    first = origin_chamber(identifier)
    crossed = False

    for hearing in hearings:
        rec = clean_text(hearing.get("recommendation") or "").lower()
        committee = clean_text(hearing.get("committee") or "")
        if not committee:
            continue
        if not crossed:
            flags["seen_in_committee_origin"] = True
            if any(
                phrase in rec
                for phrase in (
                    "do pass",
                    "without recommendation",
                    "amend, and do pass",
                    "pass as amended",
                )
            ):
                flags["passed_out_of_committee_origin"] = True
        else:
            flags["seen_in_committee_second_chamber"] = True
            if any(
                phrase in rec
                for phrase in (
                    "do pass",
                    "without recommendation",
                    "amend, and do pass",
                    "pass as amended",
                )
            ):
                flags["passed_out_of_committee_second_chamber"] = True

    for row in history:
        desc = clean_text(row.get("description") or "")
        lower = desc.lower()

        if "referred to committee" in lower or "in committee on" in lower:
            if crossed:
                flags["seen_in_committee_second_chamber"] = True
            else:
                flags["seen_in_committee_origin"] = True

        if lower.startswith("from committee:") or "from committee, with" in lower:
            passed = any(
                phrase in lower
                for phrase in ("do pass", "without recommendation", "pass as amended")
            )
            failed = "do not pass" in lower
            if crossed:
                flags["seen_in_committee_second_chamber"] = True
                if passed:
                    flags["passed_out_of_committee_second_chamber"] = True
                if failed:
                    flags["failed"] = True
            else:
                flags["seen_in_committee_origin"] = True
                if passed:
                    flags["passed_out_of_committee_origin"] = True
                if failed:
                    flags["failed"] = True

        if "passed" in lower and (
            "second reading" in lower
            or "third reading" in lower
            or "read third time" in lower
            or "read second time" in lower
        ):
            if crossed:
                flags["floor_vote_second_chamber"] = True
                flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True

        if first == "lower" and ("to senate" in lower or "in senate" in lower):
            if flags["passed_origin_chamber"] or "passed" in lower:
                crossed = True
                flags["crossed_over"] = True
        if first == "upper" and ("to assembly" in lower or "in assembly" in lower):
            if flags["passed_origin_chamber"] or "passed" in lower:
                crossed = True
                flags["crossed_over"] = True

        if "approved by the governor" in lower or re.search(r"chapter\s+\d+", lower):
            flags["signed_into_law"] = True
        if "vetoed" in lower:
            flags["vetoed"] = True
        if "no further action" in lower:
            flags["failed"] = True

    for vote in vote_rows:
        label = clean_text(vote.get("vote_type") or "").lower()
        chamber = clean_text(vote.get("chamber_label") or "").lower()
        counts = vote.get("counts") or {}
        yea = int(counts.get("Yea") or counts.get("yea") or 0)
        nay = int(counts.get("Nay") or counts.get("nay") or 0)
        if yea + nay == 0:
            continue
        is_committee = "committee" in label or "committee" in chamber
        # Attribute floor votes by the vote's own chamber label, not by the
        # crossed flag: history is scanned before votes, so `crossed` is
        # already True for bills that crossed over even though the recorded
        # floor vote happened in the origin chamber.
        vote_chamber = ""
        if "senate" in chamber:
            vote_chamber = "upper"
        elif "assembly" in chamber:
            vote_chamber = "lower"
        in_second = vote_chamber != first if vote_chamber else crossed
        if is_committee:
            if in_second:
                flags["seen_in_committee_second_chamber"] = True
                if yea > nay:
                    flags["passed_out_of_committee_second_chamber"] = True
            else:
                flags["seen_in_committee_origin"] = True
                if yea > nay:
                    flags["passed_out_of_committee_origin"] = True
        else:
            if in_second:
                flags["floor_vote_second_chamber"] = True
                if yea >= nay:
                    flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                if yea >= nay:
                    flags["passed_origin_chamber"] = True

    return flags


def derive_progress_from_openstates(actions: list[dict], votes: list[dict]) -> dict:
    flags = empty_progress()
    first = ""
    crossed = False

    def org_class(org: object) -> str:
        if isinstance(org, dict):
            return (org.get("classification") or "").lower()
        return ""

    def org_name(org: object) -> str:
        if isinstance(org, dict):
            return (org.get("name") or "").lower()
        return ""

    for action in actions:
        classes = {str(c).lower() for c in (action.get("classification") or [])}
        desc = (action.get("description") or "").lower()
        org = org_class(action.get("organization"))
        if not first and org in {"upper", "lower"}:
            first = org

        if "referral-committee" in classes or "referred to" in desc:
            if crossed:
                flags["seen_in_committee_second_chamber"] = True
            else:
                flags["seen_in_committee_origin"] = True

        is_committee = "committee" in org or "committee" in org_name(action.get("organization"))
        if is_committee and ("do pass" in desc or "committee-passage" in classes):
            if crossed:
                flags["passed_out_of_committee_second_chamber"] = True
            else:
                flags["passed_out_of_committee_origin"] = True

        floorish = org in {"upper", "lower"} and not is_committee
        if floorish and ("passed" in desc or "passage" in classes):
            if crossed:
                flags["floor_vote_second_chamber"] = True
                flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True

        if first == "lower" and ("to senate" in desc or "in senate" in desc):
            crossed = True
            flags["crossed_over"] = True
        if first == "upper" and ("to assembly" in desc or "in assembly" in desc):
            crossed = True
            flags["crossed_over"] = True

        if "approved by the governor" in desc or "became-law" in classes:
            flags["signed_into_law"] = True
        if "veto" in classes or "vetoed" in desc:
            flags["vetoed"] = True
        if "failure" in classes or "no further action" in desc:
            flags["failed"] = True

    for vote in votes:
        org = org_class(vote.get("organization"))
        name = org_name(vote.get("organization"))
        result = (vote.get("result") or "").lower()
        passed = result in {"pass", "passed"}
        is_committee = "committee" in org or "committee" in name
        if is_committee and passed:
            if crossed or flags["crossed_over"]:
                flags["passed_out_of_committee_second_chamber"] = True
            else:
                flags["passed_out_of_committee_origin"] = True
        if not is_committee and org in {"upper", "lower"} and passed:
            if crossed or flags["crossed_over"]:
                flags["floor_vote_second_chamber"] = True
                flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True

    return flags


def merge_progress(nelis_flags: dict, openstates_flags: dict) -> dict:
    merged = empty_progress()
    for field in PROGRESS_FIELDS:
        merged[field] = bool(nelis_flags.get(field) or openstates_flags.get(field))
    return merged


def final_disposition(flags: dict) -> str:
    if flags.get("signed_into_law"):
        return "Enacted"
    if flags.get("vetoed"):
        return "Vetoed"
    if flags.get("failed"):
        return "Failed"
    if flags.get("passed_second_chamber") or flags.get("passed_origin_chamber"):
        return "In Progress"
    return "Unknown"


def attach_party_from_openstates(
    nelis_voters: list[str],
    openstates_ballots: list[dict],
) -> list[dict]:
    """Match NELIS voter names to OpenStates ballots and copy party when available."""
    by_name: dict[str, dict] = {}
    for ballot in openstates_ballots:
        name = ballot.get("voter_name") or ""
        key = norm_name(name)
        if key:
            by_name[key] = ballot

    rows = []
    for name in nelis_voters:
        ballot = by_name.get(norm_name(name))
        party = None
        party_source = None
        if ballot:
            voter = ballot.get("voter") or {}
            party = voter.get("party") if isinstance(voter, dict) else None
            if party:
                party_source = "openstates"
        rows.append(
            {
                "name": name,
                "party": party,
                "party_source": party_source,
            }
        )
    return rows
