"""LegiScan bulk-dataset adapter for complete New Hampshire bill data.

Why LegiScan: GenCourt only serves the current biennium for bill
identity/metadata/text (see ``docs/nh-data-sources.md``), so older sessions
(2020-2024) need an outside mirror. OpenStates works but its per-bill API is
rate-limited. **LegiScan's bulk dataset API avoids that entirely**: one
``getDataset`` call returns a single ZIP containing *every* bill, roll call,
and person for a whole session as JSON -- including bills that died in
committee. Mirroring all of NH 2020-2026 is roughly:

    1x getDatasetList(state=NH)  +  1x getDataset per session  ~= 8 queries

against a free 30,000-queries/month public key. Rate limits are a non-issue.

    https://api.legiscan.com/?key=KEY&op=getDatasetList&state=NH
    https://api.legiscan.com/?key=KEY&op=getDataset&id=SESSION_ID&access_key=KEY2

Full bill *text* is referenced in each bill's ``texts`` array; the bytes come
from ``getBillText`` (base64), which we fetch only for the issue-relevant bills
and for HB2 -- still a handful of calls.

Requires ``LEGISCAN_API_KEY`` (free: https://legiscan.com/legiscan). This module
is self-contained and does not touch the Nevada collectors.
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
import zipfile

import requests

API = "https://api.legiscan.com/"


class NoApiKey(RuntimeError):
    pass


def available() -> bool:
    return bool(os.environ.get("LEGISCAN_API_KEY"))


def _key() -> str:
    key = os.environ.get("LEGISCAN_API_KEY")
    if not key:
        raise NoApiKey(
            "LEGISCAN_API_KEY is not set. Get a free key at "
            "https://legiscan.com/legiscan and add it as a Cloud Agent secret."
        )
    return key


def _call(op: str, **params) -> dict:
    """One LegiScan API call with backoff. Returns the parsed JSON envelope."""
    q = {"key": _key(), "op": op, **params}
    last = None
    for i in range(6):
        r = requests.get(API, params=q, timeout=120)
        if r.status_code in {429, 500, 502, 503, 504}:
            time.sleep(min(60, 5 * (2 ** i)))
            last = r
            continue
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "OK":
            raise RuntimeError(f"LegiScan {op} returned status {data.get('status')}: "
                               f"{data.get('alert') or data}")
        return data
    raise RuntimeError(f"LegiScan {op} failed after retries ({last})")


def dataset_list(year_min: int | None = None) -> list[dict]:
    """NH session datasets (session_id + access_key + year_start/end)."""
    data = _call("getDatasetList", state="NH")
    out = data.get("datasetlist", [])
    if year_min is not None:
        out = [d for d in out if int(d.get("year_end", 0)) >= year_min]
    return out


def fetch_dataset(session_id: int, access_key: str) -> dict[str, list[dict]]:
    """Download one session's ZIP and return parsed bills/people/votes.

    The ZIP holds one JSON file per bill/person/rollcall under
    ``<state>/<session>/{bill,people,vote}/*.json``; each file wraps its record
    under a top-level key ("bill" / "person" / "roll_call").
    """
    data = _call("getDataset", id=session_id, access_key=access_key)
    raw = base64.b64decode(data["dataset"]["zip"])
    out: dict[str, list[dict]] = {"bill": [], "person": [], "vote": []}
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for name in zf.namelist():
            if not name.endswith(".json"):
                continue
            try:
                rec = json.loads(zf.read(name))
            except json.JSONDecodeError:
                continue
            if "bill" in rec:
                out["bill"].append(rec["bill"])
            elif "person" in rec:
                out["person"].append(rec["person"])
            elif "roll_call" in rec:
                out["vote"].append(rec["roll_call"])
    return out


def _relevant(bill: dict, rel_terms: list[str]) -> bool:
    blob = f"{bill.get('title','')} {bill.get('description','')}".lower()
    return any(t in blob for t in rel_terms)


def discover_session(dataset: dict[str, list[dict]], search_terms: list[str],
                     rel_terms: list[str]) -> list[dict]:
    """Filter a session's bills to those matching the issue, keeping full
    metadata (sponsors, history, status, text refs) from the bulk record.
    """
    terms = [t.lower() for t in search_terms]
    rel = [t.lower() for t in (rel_terms or search_terms)]
    hits = []
    for bill in dataset["bill"]:
        blob = f"{bill.get('title','')} {bill.get('description','')}".lower()
        matched = [t for t in terms if t in blob]
        if not matched or not _relevant(bill, rel):
            continue
        hits.append({
            "bill_no": (bill.get("bill_number") or "").replace(" ", ""),
            "title": bill.get("title") or "",
            "description": bill.get("description") or "",
            "status": bill.get("status"),
            "status_date": bill.get("status_date"),
            "bill_id": bill.get("bill_id"),
            "sponsors": [
                {"name": s.get("name"), "party": s.get("party"),
                 "role": s.get("role"), "sponsor_type_id": s.get("sponsor_type_id")}
                for s in (bill.get("sponsors") or [])
            ],
            "history": bill.get("history") or [],
            "texts": [
                {"doc_id": t.get("doc_id"), "type": t.get("type"),
                 "mime": t.get("mime"), "url": t.get("state_link") or t.get("url")}
                for t in (bill.get("texts") or [])
            ],
            "legiscan_url": bill.get("url"),
            "found_by_terms": matched,
        })
    return sorted(hits, key=lambda b: b["bill_no"])


def bill_text(doc_id: int) -> dict:
    """Full text of one document (base64-decoded). Use sparingly (per doc)."""
    data = _call("getBillText", id=doc_id)
    doc = data["text"]
    decoded = base64.b64decode(doc["doc"]) if doc.get("doc") else b""
    return {"doc_id": doc_id, "mime": doc.get("mime"),
            "type": doc.get("type"), "bytes": decoded}


if __name__ == "__main__":
    for d in dataset_list(year_min=2020):
        print(d.get("session_id"), d.get("year_start"), "-", d.get("year_end"),
              d.get("session_name"))
