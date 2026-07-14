#!/usr/bin/env python3
"""Collect Nevada legislative bills from OpenStates API for a configured issue.

Strategy:
1. Per-term full-text search (q=) with partial pagination on timeouts
2. Local title/abstract relevance filter (OpenStates full-text is broader than NELIS)
3. Per-bill detail fetch with actions, votes, and sponsorships
4. Derive legislative-progress milestones used by briefing agents
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

CONFIG_PATH = Path("config/issues/nevada-water-scarcity.yaml")
OUTPUT_DIR = Path("sources/nevada/water-scarcity/openstates")
LEGACY_PROCESSED_DIR = Path("sources/nevada/water-scarcity/processed")
RAW_DIR = Path("sources/nevada/water-scarcity/raw")
MANIFEST_PATH = Path("sources/nevada/water-scarcity/manifest.json")
OPENSTATES_BASE_URL = "https://v3.openstates.org/bills"
PER_PAGE = 20
PAGE_DELAY_SECONDS = 1.0
SEARCH_DELAY_SECONDS = 1.5
DETAIL_DELAY_SECONDS = float(os.environ.get("OPENSTATES_DETAIL_DELAY", "2.0"))
DETAIL_INCLUDES = ["actions", "votes", "sponsorships", "abstracts"]

# Narrow terms → bill is relevant if any appear in title/abstract.
CORE_TITLE_TERMS = [
    "water",
    "groundwater",
    "colorado river",
    "consumptive use",
    "water rights",
    "snwa",
    "aquifer",
    "irrigation",
    "drought",
    "wastewater",
    "reclaimed water",
]


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_api_key() -> str:
    api_key = os.environ.get("OPENSTATES_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing OPENSTATES_API_KEY environment variable. "
            "Register at https://openstates.org/accounts/register/"
        )
    return api_key


def sanitize_error_message(message: str, api_key: str) -> str:
    if api_key:
        message = message.replace(api_key, "[REDACTED]")
    message = re.sub(r"apikey=[^&\\s]+", "apikey=[REDACTED]", message)
    return message


def normalize_sessions(config: dict) -> list[dict]:
    sessions = config.get("sessions", [])
    normalized = []
    for entry in sessions:
        if isinstance(entry, dict):
            normalized.append(entry)
        else:
            normalized.append(
                {
                    "label": str(entry),
                    "openstates_identifier": str(entry),
                    "name": str(entry),
                }
            )
    return normalized


def bill_key(bill: dict) -> str:
    return str(bill.get("id") or f"{bill.get('session')}:{bill.get('identifier')}")


def bill_title_abstract_blob(bill: dict) -> str:
    parts = [bill.get("title") or ""]
    for abstract in bill.get("abstracts") or []:
        parts.append(abstract.get("abstract") or "")
    return " ".join(parts).lower()


def is_water_relevant(bill: dict) -> bool:
    """Local filter so OpenStates full-text hits approximate NELIS title/summary focus."""
    blob = bill_title_abstract_blob(bill)
    title = (bill.get("title") or "").lower()
    has_core = any(term in blob for term in CORE_TITLE_TERMS)
    if has_core:
        return True
    # Keep explicit data-center search matches even without "water" in title.
    if "data center" in title or "data centers" in title:
        return True
    return False


def paginate_bills(
    api_key: str,
    params: dict,
    label: str,
    max_retries: int = 3,
) -> tuple[list[dict], dict]:
    """Paginate /bills with retries; keep partial results if a page fails."""
    headers = {"X-API-KEY": api_key}
    page = 1
    all_results: list[dict] = []
    meta = {
        "http_status": 200,
        "pages_fetched": 0,
        "incomplete": False,
        "notes": "",
    }

    while True:
        page_params = {
            **params,
            "per_page": PER_PAGE,
            "page": page,
            "apikey": api_key,
        }
        data: dict | None = None
        last_error: requests.RequestException | None = None

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    OPENSTATES_BASE_URL,
                    params=page_params,
                    headers=headers,
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
                meta["http_status"] = response.status_code
                break
            except requests.RequestException as exc:
                last_error = exc
                wait = 2**attempt
                print(f"  {label} page {page} attempt {attempt + 1} failed ({exc}); retry in {wait}s")
                time.sleep(wait)

        if data is None:
            meta["incomplete"] = True
            response = getattr(last_error, "response", None)
            meta["http_status"] = getattr(response, "status_code", None) or 0
            meta["notes"] = sanitize_error_message(str(last_error), api_key) if last_error else ""
            if all_results:
                print(f"  {label}: keeping {len(all_results)} partial results after page {page} failure")
            break

        results = data.get("results", [])
        all_results.extend(results)
        meta["pages_fetched"] = page
        print(f"  {label} page {page}: {len(results)} bills (running total {len(all_results)})")

        pagination = data.get("pagination") or {}
        max_page = pagination.get("max_page", page)
        if page >= max_page or not results:
            break
        page += 1
        time.sleep(PAGE_DELAY_SECONDS)

    return all_results, meta


def search_bills_by_term(
    api_key: str,
    jurisdiction: str,
    session_identifier: str,
    search_term: str,
) -> tuple[list[dict], dict]:
    label = f"q={search_term!r} session={session_identifier}"
    return paginate_bills(
        api_key,
        {
            "jurisdiction": jurisdiction,
            "session": session_identifier,
            "q": search_term,
        },
        label=label,
    )


def fetch_bill_detail(api_key: str, bill: dict, max_retries: int = 6) -> dict | None:
    """Load actions, votes, and sponsorships for one bill.

    Retries with backoff on timeouts and 429/5xx. Honors Retry-After when present.
    """
    headers = {"X-API-KEY": api_key}
    bill_id = bill.get("id")
    if bill_id and str(bill_id).startswith("ocd-bill/"):
        url = f"{OPENSTATES_BASE_URL}/{bill_id}"
    else:
        jurisdiction = "Nevada"
        juris = bill.get("jurisdiction") or {}
        if isinstance(juris, dict) and juris.get("name"):
            jurisdiction = juris["name"]
        session = bill.get("session")
        identifier = bill.get("identifier")
        if not session or not identifier:
            return None
        url = f"{OPENSTATES_BASE_URL}/{jurisdiction}/{session}/{identifier}"

    # requests encodes repeated include keys correctly when passed as a list of tuples
    query = [("apikey", api_key)] + [("include", item) for item in DETAIL_INCLUDES]

    last_error: requests.RequestException | None = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=query, headers=headers, timeout=120)
            if response.status_code in {429, 502, 503, 504}:
                retry_after = response.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else min(60, 3 * (2**attempt))
                print(
                    f"  detail {bill.get('identifier')} HTTP {response.status_code}; "
                    f"backoff {wait}s (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            last_error = exc
            wait = min(60, 3 * (2**attempt))
            print(
                f"  detail {bill.get('identifier')} attempt {attempt + 1} failed ({exc}); "
                f"retry in {wait}s"
            )
            time.sleep(wait)
    print(f"  detail {bill.get('identifier')}: failed ({last_error})")
    return None


def org_name(org: object) -> str:
    if isinstance(org, dict):
        return org.get("name") or org.get("classification") or ""
    return str(org or "")


def org_classification(org: object) -> str:
    if isinstance(org, dict):
        return (org.get("classification") or "").lower()
    return ""


def action_flags(actions: list[dict]) -> dict:
    """Derive chamber/committee progression milestones from OpenStates actions."""
    flags = {
        "introduced": False,
        "referred_to_committee": False,
        "committee_vote_origin_chamber": False,
        "floor_vote_origin_chamber": False,
        "passed_origin_chamber": False,
        "crossed_over": False,
        "committee_vote_second_chamber": False,
        "floor_vote_second_chamber": False,
        "passed_second_chamber": False,
        "enrolled": False,
        "sent_to_governor": False,
        "signed_into_law": False,
        "vetoed": False,
        "failed": False,
    }
    first_chamber = ""
    for action in actions:
        classes = {str(c).lower() for c in (action.get("classification") or [])}
        desc = (action.get("description") or "").lower()
        org_class = org_classification(action.get("organization"))
        if not first_chamber and org_class in {"upper", "lower"}:
            first_chamber = org_class

        if "introduction" in classes or "filing" in classes:
            flags["introduced"] = True
        if "referral-committee" in classes or "referred to" in desc:
            flags["referred_to_committee"] = True

        is_committee_org = "committee" in org_class or "committee" in org_name(action.get("organization")).lower()
        is_passage = "passage" in classes or "committee-passage" in classes
        is_failure = "failure" in classes or "committee-failure" in classes

        if is_committee_org and (is_passage or "do pass" in desc or "without recommendation" in desc):
            if not flags["passed_origin_chamber"] and not flags["crossed_over"]:
                flags["committee_vote_origin_chamber"] = True
            else:
                flags["committee_vote_second_chamber"] = True

        floorish = org_class in {"upper", "lower"} and not is_committee_org
        if floorish and (is_passage or "passed" in desc):
            if first_chamber and org_class == first_chamber and not flags["crossed_over"]:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True
            elif flags["crossed_over"] or (first_chamber and org_class != first_chamber):
                flags["floor_vote_second_chamber"] = True
                flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True

        if "became-law" in classes or "executive-signature" in classes or "approved by the governor" in desc:
            flags["signed_into_law"] = True
        if "executive-receipt" in classes or "delivered to governor" in desc or "enrolled and delivered" in desc:
            flags["sent_to_governor"] = True
        if "enrolled" in desc:
            flags["enrolled"] = True
        if "veto" in classes or "vetoed" in desc:
            flags["vetoed"] = True
        if is_failure or "no further action" in desc:
            flags["failed"] = True
        if flags["passed_origin_chamber"] and (
            "in senate" in desc
            or "in assembly" in desc
            or "to senate" in desc
            or "to assembly" in desc
        ):
            flags["crossed_over"] = True

    return flags


def summarize_progress(bill: dict) -> dict:
    actions = bill.get("actions") or []
    votes = bill.get("votes") or []
    flags = action_flags(actions)

    # Vote-event based refinement (committee vs chamber body).
    for vote in votes:
        org_class = org_classification(vote.get("organization"))
        org = org_name(vote.get("organization")).lower()
        result = (vote.get("result") or "").lower()
        passed = result in {"pass", "passed"}
        is_committee = "committee" in org_class or "committee" in org
        if is_committee and passed:
            if flags["crossed_over"] or flags["passed_origin_chamber"]:
                flags["committee_vote_second_chamber"] = True
            else:
                flags["committee_vote_origin_chamber"] = True
        if not is_committee and org_class in {"upper", "lower"} and passed:
            if flags["crossed_over"] or flags["passed_origin_chamber"]:
                flags["floor_vote_second_chamber"] = True
                flags["passed_second_chamber"] = True
            else:
                flags["floor_vote_origin_chamber"] = True
                flags["passed_origin_chamber"] = True

    latest = (bill.get("latest_action_description") or "").lower()
    if "approved by the governor" in latest or "chapter" in latest:
        flags["signed_into_law"] = True

    return {
        "session": bill.get("session"),
        "bill_identifier": bill.get("identifier"),
        "title": bill.get("title"),
        "openstates_url": bill.get("openstates_url"),
        "latest_action_date": bill.get("latest_action_date"),
        "latest_action_description": bill.get("latest_action_description"),
        "latest_passage_date": bill.get("latest_passage_date"),
        "action_count": len(actions),
        "vote_event_count": len(votes),
        "sponsor_count": len(bill.get("sponsorships") or []),
        **flags,
    }


def flatten_actions(bills: list[dict]) -> list[dict]:
    rows = []
    for bill in bills:
        identifier = bill.get("identifier", "")
        session = bill.get("session", "")
        for action in bill.get("actions") or []:
            rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "date": action.get("date"),
                    "organization": org_name(action.get("organization")),
                    "organization_classification": org_classification(action.get("organization")),
                    "description": action.get("description"),
                    "classification": action.get("classification"),
                }
            )
    return rows


def flatten_votes(bills: list[dict]) -> list[dict]:
    """One row per vote event, with yes/no/other voter name lists when available."""
    rows = []
    for bill in bills:
        identifier = bill.get("identifier", "")
        session = bill.get("session", "")
        for vote in bill.get("votes") or []:
            yes_voters: list[str] = []
            no_voters: list[str] = []
            other_voters: list[str] = []
            for ballot in vote.get("votes") or []:
                name = ballot.get("voter_name") or ""
                option = (ballot.get("option") or "").lower()
                if option in {"yes", "aye"}:
                    yes_voters.append(name)
                elif option in {"no", "nay"}:
                    no_voters.append(name)
                else:
                    other_voters.append(f"{name}:{option}" if name else option)

            rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "vote_id": vote.get("id"),
                    "date": vote.get("start_date"),
                    "motion_text": vote.get("motion_text"),
                    "result": vote.get("result"),
                    "organization": org_name(vote.get("organization")),
                    "organization_classification": org_classification(vote.get("organization")),
                    "counts": vote.get("counts"),
                    "yes_voters": yes_voters,
                    "no_voters": no_voters,
                    "other_voters": other_voters,
                    "yes_count": len(yes_voters),
                    "no_count": len(no_voters),
                }
            )
    return rows


def flatten_sponsors(bills: list[dict]) -> list[dict]:
    rows = []
    for bill in bills:
        identifier = bill.get("identifier", "")
        session = bill.get("session", "")
        for sponsor in bill.get("sponsorships") or []:
            entity = sponsor.get("entity") or {}
            person = sponsor.get("person") or {}
            rows.append(
                {
                    "session": session,
                    "bill_identifier": identifier,
                    "name": sponsor.get("name") or person.get("name") or entity.get("name"),
                    "classification": sponsor.get("classification"),  # primary / cosponsor
                    "primary": bool(sponsor.get("primary")),
                    "entity_type": sponsor.get("entity_type"),
                    "party": (person.get("party") if isinstance(person, dict) else None)
                    or (entity.get("party") if isinstance(entity, dict) else None),
                    "person_id": person.get("id") if isinstance(person, dict) else None,
                }
            )
    return rows


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_url(url: str, dest: Path) -> dict:
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(response.content)
    return {
        "http_status": response.status_code,
        "sha256": sha256_bytes(response.content),
        "local_path": str(dest),
    }


def write_outputs(
    enriched: list[dict],
    candidates_list: list[dict],
    relevant: list[dict],
    enrich_failures: int,
    manifest_items: list[dict],
    source_counter: int,
    api_key: str,
    config: dict,
    jurisdiction: str,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LEGACY_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    candidates_path = OUTPUT_DIR / "bills-search-candidates.json"
    candidates_path.write_text(json.dumps(candidates_list, indent=2), encoding="utf-8")

    actions = flatten_actions(enriched)
    votes = flatten_votes(enriched)
    sponsors = flatten_sponsors(enriched)
    progress = [summarize_progress(b) for b in enriched]

    bills_path = OUTPUT_DIR / "bills.json"
    bills_path.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    # Compatibility alias for older tools/docs
    (OUTPUT_DIR / "bills-combined.json").write_text(
        json.dumps(enriched, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "bill-actions.json").write_text(json.dumps(actions, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "bill-votes.json").write_text(json.dumps(votes, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "bill-sponsors.json").write_text(json.dumps(sponsors, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "bill-legislative-progress.json").write_text(
        json.dumps(progress, indent=2), encoding="utf-8"
    )

    statute_links = []
    for entry in config.get("statute_urls", []):
        statute_links.append(
            {
                "chapter": entry["chapter"],
                "url": entry["url"],
                "source_key": entry.get("source_key"),
            }
        )
    (OUTPUT_DIR / "statute-links.json").write_text(
        json.dumps(statute_links, indent=2), encoding="utf-8"
    )

    agency_docs = []
    for entry in config.get("agency_document_urls", []):
        url = entry["url"]
        filename = url.rstrip("/").split("/")[-1] or "document"
        if not filename.endswith((".pdf", ".html", ".htm")):
            filename = f"{entry.get('source_key', 'doc')}.pdf"
        dest = RAW_DIR / filename
        try:
            meta = download_url(url, dest)
            agency_docs.append(
                {
                    "title": entry["title"],
                    "url": url,
                    "source_key": entry.get("source_key"),
                    **meta,
                }
            )
            manifest_items.append(
                {
                    "source_key": entry.get("source_key", f"S-{source_counter:03d}"),
                    "type": "agency_document",
                    "url": url,
                    "local_path": str(dest),
                    "http_status": meta["http_status"],
                    "sha256": meta["sha256"],
                    "notes": "",
                }
            )
            source_counter += 1
        except requests.RequestException as exc:
            agency_docs.append(
                {
                    "title": entry["title"],
                    "url": url,
                    "source_key": entry.get("source_key"),
                    "error": sanitize_error_message(str(exc), api_key),
                }
            )
        time.sleep(1)

    (OUTPUT_DIR / "agency-documents.json").write_text(
        json.dumps(agency_docs, indent=2), encoding="utf-8"
    )

    signed = sum(1 for row in progress if row.get("signed_into_law"))
    with_votes = sum(1 for row in progress if row.get("vote_event_count", 0) > 0)
    with_sponsors = sum(1 for row in progress if row.get("sponsor_count", 0) > 0)

    openstates_summary = {
        "collector": "openstates_bills.py",
        "collection_strategy": "per_term_q_search_plus_detail_enrichment",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "openstates_candidate_count": len(candidates_list),
        "openstates_relevant_count": len(relevant),
        "openstates_bill_count": len(enriched),
        "enrich_failures": enrich_failures,
        "action_row_count": len(actions),
        "vote_event_count": len(votes),
        "sponsor_row_count": len(sponsors),
        "bills_with_vote_events": with_votes,
        "bills_with_sponsors": with_sponsors,
        "bills_signed_into_law": signed,
        "relevance_note": (
            "OpenStates q= searches full bill text (broader than NELIS title/summary search). "
            "bills.json is locally filtered to water-relevant titles/abstracts; "
            "bills-search-candidates.json retains the full OpenStates hit list."
        ),
        "output_dir": str(OUTPUT_DIR),
    }
    (OUTPUT_DIR / "collection-summary.json").write_text(
        json.dumps(openstates_summary, indent=2), encoding="utf-8"
    )

    manifest: dict = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest.update(
        {
            "issue_id": config["issue_id"],
            "state": config["state"],
            "openstates_jurisdiction": jurisdiction,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "openstates": openstates_summary,
            "items": manifest_items,
        }
    )
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Done. Saved {len(enriched)} relevant enriched bills "
        f"({len(candidates_list)} full-text candidates) to {bills_path}"
    )
    print(
        f"  actions={len(actions)} vote_events={len(votes)} sponsors={len(sponsors)} "
        f"signed_into_law={signed} enrich_failures={enrich_failures}"
    )


def main() -> None:
    config = load_config()
    api_key = get_api_key()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    jurisdiction = config.get("openstates_jurisdiction") or "Nevada"
    search_terms = config["search_terms"]
    sessions = normalize_sessions(config)
    candidate_bills: dict[str, dict] = {}
    manifest_items: list[dict] = []
    source_counter = 1

    for session_entry in sessions:
        session_id = session_entry["openstates_identifier"]
        session_label = session_entry.get("label", session_id)
        session_name = session_entry.get("name", session_label)
        session_unique: dict[str, dict] = {}

        print(
            f"Searching {jurisdiction} session {session_label} "
            f"(OpenStates id={session_id}, {session_name})"
        )

        for search_term in search_terms:
            print(f"  search term: {search_term}")
            try:
                results, meta = search_bills_by_term(
                    api_key, jurisdiction, session_id, search_term
                )
                for bill in results:
                    session_unique[bill_key(bill)] = bill
                manifest_items.append(
                    {
                        "source_key": f"S-{source_counter:03d}",
                        "type": "bill_search",
                        "url": OPENSTATES_BASE_URL,
                        "search_term": search_term,
                        "session_label": session_label,
                        "openstates_session_identifier": session_id,
                        "session_name": session_name,
                        "bill_count": len(results),
                        "session_unique_so_far": len(session_unique),
                        "http_status": meta["http_status"],
                        "incomplete": meta["incomplete"],
                        "notes": meta["notes"],
                    }
                )
                source_counter += 1
                print(f"  -> {len(results)} bills for {search_term!r}")
            except requests.RequestException as exc:
                manifest_items.append(
                    {
                        "source_key": f"S-{source_counter:03d}",
                        "type": "bill_search",
                        "url": OPENSTATES_BASE_URL,
                        "search_term": search_term,
                        "session_label": session_label,
                        "openstates_session_identifier": session_id,
                        "session_name": session_name,
                        "bill_count": 0,
                        "session_unique_so_far": len(session_unique),
                        "http_status": getattr(exc.response, "status_code", None),
                        "incomplete": True,
                        "notes": sanitize_error_message(str(exc), api_key),
                    }
                )
                source_counter += 1
            time.sleep(SEARCH_DELAY_SECONDS)

        for key, bill in session_unique.items():
            candidate_bills[key] = bill
        print(f"  session total unique bills: {len(session_unique)}")
        time.sleep(1)

    candidates_list = list(candidate_bills.values())
    relevant = [b for b in candidates_list if is_water_relevant(b)]
    print(
        f"Candidates from OpenStates full-text: {len(candidates_list)}; "
        f"after local water-relevance filter: {len(relevant)}"
    )

    detail_limit = os.environ.get("OPENSTATES_DETAIL_LIMIT")
    if detail_limit:
        relevant = relevant[: int(detail_limit)]
        print(f"OPENSTATES_DETAIL_LIMIT={detail_limit}: enriching {len(relevant)} bills")

    # Resume: keep already-enriched details when id matches.
    prior_by_id: dict[str, dict] = {}
    prior_path = OUTPUT_DIR / "bills.json"
    if os.environ.get("OPENSTATES_RESUME", "").lower() in {"1", "true", "yes"} and prior_path.exists():
        for prior in json.loads(prior_path.read_text(encoding="utf-8")):
            pid = prior.get("id")
            if pid and (prior.get("actions") or prior.get("votes") or prior.get("sponsorships")):
                prior_by_id[str(pid)] = prior
        print(f"OPENSTATES_RESUME: loaded {len(prior_by_id)} previously enriched bills")

    enriched: list[dict] = []
    enrich_failures = 0
    for index, bill in enumerate(relevant, start=1):
        print(f"Enriching {index}/{len(relevant)}: {bill.get('identifier')} ({bill.get('session')})")
        existing = prior_by_id.get(str(bill.get("id")))
        if existing:
            enriched.append(existing)
            print("  reused cached detail")
            continue
        detail = fetch_bill_detail(api_key, bill)
        if detail:
            enriched.append(detail)
        else:
            enrich_failures += 1
            enriched.append(bill)
        time.sleep(DETAIL_DELAY_SECONDS)

    write_outputs(
        enriched=enriched,
        candidates_list=candidates_list,
        relevant=relevant,
        enrich_failures=enrich_failures,
        manifest_items=manifest_items,
        source_counter=source_counter,
        api_key=api_key,
        config=config,
        jurisdiction=jurisdiction,
    )


if __name__ == "__main__":
    main()
