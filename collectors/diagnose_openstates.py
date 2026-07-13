#!/usr/bin/env python3
"""Diagnose OpenStates API connectivity for Nevada water-scarcity collection.

Run locally:
    export OPENSTATES_API_KEY=your-key-here
    python collectors/diagnose_openstates.py

In GitHub Actions, use the "Diagnose OpenStates Nevada" workflow.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://v3.openstates.org"
OUTPUT_DIR = Path("sources/nevada/water-scarcity/verification")
JURISDICTIONS = [
    "Nevada",
    "nevada",
    "nv",
    "ocd-jurisdiction/country:us/state:nv",
]
KNOWN_BILL = ("82", "AB19")  # water bill from 2023 session (exists on NELIS)


def get_api_key() -> str:
    key = os.environ.get("OPENSTATES_API_KEY", "").strip()
    if not key:
        print("ERROR: Set OPENSTATES_API_KEY before running.", file=sys.stderr)
        sys.exit(1)
    return key


def call(api_key: str, path: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    params["apikey"] = api_key
    headers = {"X-API-KEY": api_key}
    response = requests.get(f"{BASE}{path}", params=params, headers=headers, timeout=120)
    body: object
    if response.headers.get("content-type", "").startswith("application/json"):
        body = response.json()
    else:
        body = response.text[:500]
    return {
        "status": response.status_code,
        "url": response.url.split("apikey=")[0].rstrip("?&"),
        "body": body,
    }


def count_results(body: object) -> int | str:
    if isinstance(body, dict):
        pagination = body.get("pagination") or {}
        if pagination.get("total_items") is not None:
            return pagination["total_items"]
        if "results" in body:
            return len(body["results"])
    return "n/a"


def summarize(body: object) -> dict:
    if not isinstance(body, dict):
        return {"preview": str(body)[:200]}
    if "title" in body:
        return {
            "identifier": body.get("identifier"),
            "title": (body.get("title") or "")[:120],
            "session": body.get("session"),
        }
    return {
        "total_items": count_results(body),
        "result_count_on_page": len(body.get("results") or []),
    }


def run_diagnostic(api_key: str) -> dict:
    report: dict = {
        "diagnosed_at": datetime.now(timezone.utc).isoformat(),
        "collector": "diagnose_openstates.py",
        "tests": [],
        "interpretation": [],
    }

    meta = call(
        api_key,
        "/jurisdictions/ocd-jurisdiction/country:us/state:nv",
        {"include": "legislative_sessions"},
    )
    session_ids: list[str] = []
    if meta["status"] == 200 and isinstance(meta["body"], dict):
        sessions = meta["body"].get("legislative_sessions") or []
        session_ids = [s["identifier"] for s in sessions if s.get("identifier")]
    report["tests"].append(
        {
            "name": "jurisdiction_metadata",
            "status": meta["status"],
            "session_identifiers": session_ids[-12:],
        }
    )

    session, bill_id = KNOWN_BILL
    for juris in ["Nevada", "nv"]:
        result = call(api_key, f"/bills/{juris}/{session}/{bill_id}")
        report["tests"].append(
            {
                "name": "direct_bill_lookup",
                "jurisdiction": juris,
                "session": session,
                "bill_id": bill_id,
                "status": result["status"],
                "summary": summarize(result["body"]),
            }
        )

    for juris in JURISDICTIONS:
        result = call(
            api_key,
            "/bills",
            {"jurisdiction": juris, "session": "82", "per_page": 1, "page": 1},
        )
        report["tests"].append(
            {
                "name": "fetch_all_session_bills",
                "jurisdiction": juris,
                "session": "82",
                "status": result["status"],
                "summary": summarize(result["body"]),
            }
        )

    for juris in ["Nevada", "ocd-jurisdiction/country:us/state:nv"]:
        result = call(
            api_key,
            "/bills",
            {"jurisdiction": juris, "session": "82", "q": "water", "per_page": 5, "page": 1},
        )
        report["tests"].append(
            {
                "name": "full_text_search",
                "jurisdiction": juris,
                "session": "82",
                "query": "water",
                "status": result["status"],
                "summary": summarize(result["body"]),
            }
        )

    direct_ok = any(
        t["name"] == "direct_bill_lookup" and t["status"] == 200 for t in report["tests"]
    )
    fetch_totals = [
        t["summary"].get("total_items")
        for t in report["tests"]
        if t["name"] == "fetch_all_session_bills" and isinstance(t.get("summary"), dict)
    ]
    fetch_ok = any(isinstance(n, int) and n > 0 for n in fetch_totals)
    search_totals = [
        t["summary"].get("total_items")
        for t in report["tests"]
        if t["name"] == "full_text_search" and isinstance(t.get("summary"), dict)
    ]
    search_ok = any(isinstance(n, int) and n > 0 for n in search_totals)
    auth_failed = any(t["status"] in (401, 403) for t in report["tests"])

    if auth_failed:
        report["interpretation"].append(
            "API key rejected (HTTP 401/403). Rotate OPENSTATES_API_KEY and update the GitHub secret."
        )
    elif direct_ok and fetch_ok and not search_ok:
        report["interpretation"].append(
            "OpenStates works for Nevada via fetch-all. Full-text q= search is unreliable; keep the PR #3 collector strategy."
        )
        report["overall_status"] = "PASS_FETCH_ALL"
    elif direct_ok and fetch_ok and search_ok:
        report["interpretation"].append(
            "OpenStates works for Nevada including full-text search."
        )
        report["overall_status"] = "PASS"
    elif direct_ok and not fetch_ok:
        report["interpretation"].append(
            "Known bill exists but session listing returned zero. Check session identifier or jurisdiction string."
        )
        report["overall_status"] = "FAIL_SESSION_OR_JURISDICTION"
    else:
        report["interpretation"].append(
            "OpenStates API returned no usable Nevada bill data. File an issue at github.com/openstates/issues with this report."
        )
        report["overall_status"] = "FAIL_NO_DATA"

    return report


def format_report_text(report: dict) -> str:
    lines = [
        "OpenStates Nevada Diagnostic Report",
        "=" * 40,
        f"Status: {report.get('overall_status', 'UNKNOWN')}",
        f"Run at: {report['diagnosed_at']}",
        "",
    ]
    for test in report["tests"]:
        lines.append(f"- {test['name']}: HTTP {test['status']} {test.get('summary', '')}")
    lines.append("")
    lines.append("Interpretation:")
    for item in report["interpretation"]:
        lines.append(f"  * {item}")
    return "\n".join(lines) + "\n"


def main() -> None:
    api_key = get_api_key()
    report = run_diagnostic(api_key)
    text = format_report_text(report)

    print(text)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "openstates-diagnostic.json"
    txt_path = OUTPUT_DIR / "openstates-diagnostic.txt"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    txt_path.write_text(text, encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {txt_path}")


if __name__ == "__main__":
    main()
