#!/usr/bin/env python3
"""Compare As Introduced vs As Enrolled text for Governor-bound bills.

Only processes bills that were enrolled/delivered to the Governor (or signed).
Downloads NELIS PDFs, extracts text, and writes a change summary.

  python collectors/pass2_text_diff.py
  python collectors/pass2_text_diff.py --limit 3
  python collectors/pass2_text_diff.py --refresh
"""

from __future__ import annotations

import argparse
import difflib
import io
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

PASS1 = Path("sources/nevada/water-scarcity/pass1")
PASS2 = Path("sources/nevada/water-scarcity/pass2")
PROCESSED = Path("sources/nevada/water-scarcity/processed")
RAW = Path("sources/nevada/water-scarcity/raw/bill-text")

BILLS = PASS1 / "bills.json"
ABSTRACT_CACHE = PASS1 / "cache_abstracts.json"
PROGRESS = PROCESSED / "bill-legislative-progress.json"
ACTIONS = PROCESSED / "bill-actions.json"
NELIS_CACHE = PASS2 / "cache_nelis_pass2.json"
TEXT_CACHE = PASS2 / "cache_text_diff.json"
OUT = PROCESSED / "bill-text-changes.json"

BASE = "https://www.leg.state.nv.us"
UA = {
    "User-Agent": "ForumLegislativeBrief/1.0",
    "X-Requested-With": "XMLHttpRequest",
}
REQUEST_DELAY = 0.45


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


def governor_bound_keys(progress: list[dict], actions: list[dict]) -> set[str]:
    keys: set[str] = set()
    for row in progress:
        m = row.get("milestones") or {}
        if m.get("signed_into_law") or row.get("final_disposition") == "Enacted":
            keys.add(bill_key(row["session"], row["bill_identifier"]))
    for action in actions:
        if action.get("source") != "nelis":
            continue
        desc = (action.get("description") or "").lower()
        if any(
            phrase in desc
            for phrase in (
                "delivered to governor",
                "enrolled and delivered",
                "approved by the governor",
            )
        ):
            keys.add(bill_key(action["session"], action["bill_identifier"]))
    return keys


def nelis_ids(abstract_cache: dict, progress_row: dict, nelis_cache: dict) -> tuple[str, str] | None:
    key = bill_key(progress_row["session"], progress_row["bill_identifier"])
    if key in abstract_cache:
        row = abstract_cache[key]
        if row.get("session_path") and row.get("nelis_bill_key"):
            return row["session_path"], str(row["nelis_bill_key"])
    if key in nelis_cache:
        row = nelis_cache[key]
        if row.get("session_path") and row.get("nelis_bill_key"):
            return row["session_path"], str(row["nelis_bill_key"])
    url = progress_row.get("nelis_url") or ""
    match = re.search(r"/App/NELIS/REL/([^/]+)/Bill/(\d+)/", url)
    if match:
        return match.group(1), match.group(2)
    return None


def fetch_text_docs(
    session: requests.Session, session_path: str, bill_key_id: str
) -> tuple[list[dict], list[str]]:
    warm = f"{BASE}/App/NELIS/REL/{session_path}/Bill/{bill_key_id}/Overview"
    session.get(warm, timeout=60)
    time.sleep(REQUEST_DELAY)
    fill = f"{BASE}/App/NELIS/REL/{session_path}/Bill/FillSelectedBillTab"
    html = session.get(
        fill, params={"selectedTab": "Text", "billKey": bill_key_id}, timeout=60
    ).text
    time.sleep(REQUEST_DELAY)
    soup = BeautifulSoup(html, "lxml")
    docs = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if not re.search(r"\.(pdf)(\?|$)", href, re.I):
            continue
        label = clean(anchor.get_text(" ", strip=True)) or Path(href).name
        url = href if href.startswith("http") else f"{BASE}{href}"
        docs.append({"label": label, "url": url})
    # Amendments tab labels (optional metadata)
    amend_html = session.get(
        fill, params={"selectedTab": "Amendments", "billKey": bill_key_id}, timeout=60
    ).text
    time.sleep(REQUEST_DELAY)
    amendments = re.findall(r"Amendment\s+\d+", amend_html, flags=re.I)
    return docs, sorted(set(amendments), key=lambda x: int(re.search(r"\d+", x).group()))


def pick_version(docs: list[dict], *needles: str) -> dict | None:
    for needle in needles:
        for doc in docs:
            if needle.lower() in (doc.get("label") or "").lower():
                return doc
    return None


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
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages)


def normalize_for_compare(text: str) -> str:
    text = text.lower()
    text = re.sub(r"page\s+\d+\s+of\s+\d+", " ", text)
    text = re.sub(r"\*+[a-z0-9]+\*+", " ", text)
    text = re.sub(r"[^a-z0-9\s\.\,\;\:\(\)\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_summary(text: str) -> str:
    match = re.search(
        r"SUMMARY\s*[—\-]\s*(.+?)(?:FISCAL NOTE|EXPLANATION|THE PEOPLE|AN ACT)",
        text,
        flags=re.I | re.S,
    )
    if match:
        return clean(match.group(1))
    return ""


def extract_act_clause(text: str) -> str:
    match = re.search(
        r"(AN ACT relating to .+?)(?:Legislative Counsel.?s Digest|THE PEOPLE OF THE STATE)",
        text,
        flags=re.I | re.S,
    )
    if match:
        return clean(match.group(1))
    return ""


def extract_counsel_digest(text: str) -> str:
    match = re.search(
        r"Legislative Counsel.?s Digest:\s*(.+?)(?:THE PEOPLE OF THE STATE|WHEREAS)",
        text,
        flags=re.I | re.S,
    )
    if match:
        return clean(match.group(1))
    return ""


def strip_bill_boilerplate(text: str) -> str:
    """Keep substance; drop cover pages / digest wrappers that differ by format."""
    # Prefer body after "THE PEOPLE OF THE STATE OF NEVADA"
    match = re.search(
        r"THE PEOPLE OF THE STATE OF NEVADA[, ]+REPRESENTED IN SENATE AND ASSEMBLY[, ]+DO ENACT AS FOLLOWS[:.]?\s*(.*)",
        text,
        flags=re.I | re.S,
    )
    if match:
        return match.group(1)
    # Fallback: drop common front-matter markers
    text = re.sub(r"(?is)^.*?SUMMARY\s*[—\-].*?(?=Section\s+1\.|Sec\.\s*1\.|THE PEOPLE)", "", text)
    return text


def summarize_diff(
    introduced: str,
    enrolled: str,
    *,
    amendments_listed: list[str] | None = None,
    max_chunks: int = 8,
) -> dict:
    intro_body = strip_bill_boilerplate(introduced)
    enrol_body = strip_bill_boilerplate(enrolled)
    intro_n = normalize_for_compare(intro_body)
    enrol_n = normalize_for_compare(enrol_body)
    ratio = difflib.SequenceMatcher(None, intro_n, enrol_n).ratio() if intro_n and enrol_n else 0.0

    intro_lines = [ln.strip() for ln in intro_body.splitlines() if ln.strip()]
    enrol_lines = [ln.strip() for ln in enrol_body.splitlines() if ln.strip()]
    matcher = difflib.SequenceMatcher(None, intro_lines, enrol_lines)
    added: list[str] = []
    removed: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            chunk = clean(" ".join(enrol_lines[j1:j2]))
            if len(chunk) >= 80:
                added.append(chunk[:500])
        elif tag == "delete":
            chunk = clean(" ".join(intro_lines[i1:i2]))
            if len(chunk) >= 80:
                removed.append(chunk[:500])
        elif tag == "replace":
            new = clean(" ".join(enrol_lines[j1:j2]))
            old = clean(" ".join(intro_lines[i1:i2]))
            if len(new) >= 80:
                added.append(new[:500])
            if len(old) >= 80:
                removed.append(old[:500])
        if len(added) >= max_chunks and len(removed) >= max_chunks:
            break

    intro_summary = extract_summary(introduced)
    enrol_act = extract_act_clause(enrolled)
    enrol_digest = extract_counsel_digest(enrolled)
    amendments_listed = amendments_listed or []

    # Prefer official amendment list; use body similarity only as backup.
    if amendments_listed:
        was_amended = True
        amendment_note = f"NELIS lists adopted amendments: {', '.join(amendments_listed)}."
    elif ratio >= 0.93:
        was_amended = False
        amendment_note = "No amendments listed on NELIS; enacting body text is nearly identical."
    elif ratio >= 0.80:
        was_amended = True
        amendment_note = (
            "No amendments listed on NELIS, but the enacting body text differs enough "
            "to suggest changes before enrollment."
        )
    else:
        was_amended = True
        amendment_note = (
            "No amendments listed on NELIS; enrolled enacting body differs substantially "
            "from the introduced body (or PDF extraction differs)."
        )

    if not was_amended:
        narrative = (
            "Enrolled substance matches the introduced bill. "
            + amendment_note
        )
    elif ratio >= 0.85:
        narrative = (
            "The enrolled bill is close to the introduced version, with limited changes. "
            + amendment_note
        )
    else:
        narrative = (
            "The enrolled bill differs from the introduced version before it reached "
            "the Governor. "
            + amendment_note
        )

    return {
        "similarity_ratio": round(ratio, 4),
        "body_similarity_ratio": round(ratio, 4),
        "was_textually_amended": was_amended,
        "narrative": narrative,
        "introduced_summary": intro_summary,
        "enrolled_act_clause": enrol_act,
        "enrolled_legislative_counsel_digest": enrol_digest,
        "notable_additions": added[:max_chunks],
        "notable_removals": removed[:max_chunks],
    }


def process_bill(
    session: requests.Session,
    *,
    progress_row: dict,
    session_path: str,
    bill_key_id: str,
    text_cache: dict,
    refresh: bool,
) -> dict:
    key = bill_key(progress_row["session"], progress_row["bill_identifier"])
    if key in text_cache and text_cache[key].get("status") == "ok" and not refresh:
        return text_cache[key]

    docs, amendments = fetch_text_docs(session, session_path, bill_key_id)
    introduced = pick_version(docs, "as introduced", "introduced")
    enrolled = pick_version(docs, "as enrolled", "enrolled")
    if not introduced or not enrolled:
        row = {
            "session": progress_row["session"],
            "bill_identifier": progress_row["bill_identifier"],
            "status": "missing_versions",
            "documents": docs,
            "amendments_listed": amendments,
            "error": "Could not find both As Introduced and As Enrolled PDFs",
            "collected_at": now(),
        }
        text_cache[key] = row
        return row

    dest_dir = RAW / progress_row["session"] / progress_row["bill_identifier"]
    intro_bytes = download_pdf(
        session, introduced["url"], dest_dir / "as_introduced.pdf"
    )
    enrol_bytes = download_pdf(
        session, enrolled["url"], dest_dir / "as_enrolled.pdf"
    )
    intro_text = pdf_text(intro_bytes)
    enrol_text = pdf_text(enrol_bytes)
    summary = summarize_diff(
        intro_text, enrol_text, amendments_listed=amendments
    )
    # If NELIS only published Introduced + Enrolled (no reprints/amendment PDFs),
    # treat as not amended even when PDF formatting makes text similarity look low.
    labels = {(d.get("label") or "").lower() for d in docs}
    has_middle_versions = any(
        "reprint" in label or label.startswith("amendment") for label in labels
    )
    if not amendments and not has_middle_versions:
        summary["was_textually_amended"] = False
        summary["narrative"] = (
            "No amendments or reprints appear on NELIS for this bill. "
            "The enrolled PDF may look different from the introduced PDF due to "
            "formatting, but there is no evidence the substance was amended before "
            "it reached the Governor."
        )

    row = {
        "session": progress_row["session"],
        "bill_identifier": progress_row["bill_identifier"],
        "title": progress_row.get("title"),
        "status": "ok",
        "governor_bound": True,
        "amendments_listed": amendments,
        "introduced": {
            "label": introduced["label"],
            "url": introduced["url"],
            "local_path": str(dest_dir / "as_introduced.pdf"),
            "char_count": len(intro_text),
        },
        "enrolled": {
            "label": enrolled["label"],
            "url": enrolled["url"],
            "local_path": str(dest_dir / "as_enrolled.pdf"),
            "char_count": len(enrol_text),
        },
        "all_text_documents": docs,
        **summary,
        "collected_at": now(),
    }
    text_cache[key] = row
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    progress = load_json(PROGRESS, [])
    actions = load_json(ACTIONS, [])
    abstract_cache = load_json(ABSTRACT_CACHE, {})
    nelis_cache = load_json(NELIS_CACHE, {})
    text_cache = {} if args.refresh else load_json(TEXT_CACHE, {})

    targets = governor_bound_keys(progress, actions)
    rows = [p for p in progress if bill_key(p["session"], p["bill_identifier"]) in targets]
    rows = sorted(rows, key=lambda r: (r["session"], r["bill_identifier"]))
    if args.limit:
        rows = rows[: args.limit]

    print(f"Governor-bound bills to compare: {len(rows)}")
    client = requests.Session()
    client.headers.update(UA)

    results = []
    failures = []
    for index, row in enumerate(rows, start=1):
        key = bill_key(row["session"], row["bill_identifier"])
        print(f"[{index}/{len(rows)}] {key}")
        ids = nelis_ids(abstract_cache, row, nelis_cache)
        if not ids:
            failures.append({"bill": key, "error": "missing_nelis_ids"})
            continue
        try:
            result = process_bill(
                client,
                progress_row=row,
                session_path=ids[0],
                bill_key_id=ids[1],
                text_cache=text_cache,
                refresh=args.refresh,
            )
            results.append(result)
            save_json(TEXT_CACHE, text_cache)
            print(
                f"  status={result.get('status')} amended={result.get('was_textually_amended')} "
                f"similarity={result.get('similarity_ratio')}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED: {exc}")
            failures.append({"bill": key, "error": str(exc)})

    payload = {
        "collected_at": now(),
        "note": (
            "As Introduced vs As Enrolled comparison for bills enrolled/delivered "
            "to the Governor or signed into law."
        ),
        "bill_count": len(results),
        "ok_count": sum(1 for r in results if r.get("status") == "ok"),
        "amended_count": sum(1 for r in results if r.get("was_textually_amended")),
        "failures": failures,
        "bills": results,
    }
    save_json(OUT, payload)
    print(f"Wrote {OUT} ({payload['ok_count']} ok, {payload['amended_count']} amended)")


if __name__ == "__main__":
    main()
