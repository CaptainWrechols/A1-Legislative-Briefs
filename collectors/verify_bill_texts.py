#!/usr/bin/env python3
"""Verify that every relevant bill has authentic, downloadable full text.

Gates analysis readiness:
- each NELIS stub/bill has at least one downloaded official PDF
- identifier appears in URL/filename and/or extracted PDF preview
- OpenStates bills likewise have downloaded version/document files when links exist
- when both sources share the same URL, SHA-256 fingerprints must match

Exits non-zero when critical failures remain (so CI can block bad corpora).
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from water_relevance import normalize_bill_identifier

NELIS_DIR = Path("sources/nevada/water-scarcity/nelis")
OPENSTATES_DIR = Path("sources/nevada/water-scarcity/openstates")
OUT_DIR = Path("sources/nevada/water-scarcity/verification")


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def bill_key(session: object, identifier: object) -> str:
    return f"{session}:{normalize_bill_identifier(str(identifier or ''))}"


def index_texts(rows: list[dict], session_map: dict[str, str] | None = None) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        session = row.get("session")
        if session_map and session in session_map:
            session = session_map[session]
        key = bill_key(session, row.get("bill_identifier"))
        out.setdefault(key, []).append(row)
    return out


def has_good_download(rows: list[dict]) -> bool:
    return any(r.get("local_path") and not r.get("download_error") and r.get("sha256") for r in rows)


def main() -> int:
    session_map = {
        "80th2019": "80",
        "81st2021": "81",
        "82nd2023": "82",
        "83rd2025": "83",
    }

    nelis_bills = load_json(NELIS_DIR / "bills.json", []) or load_json(
        NELIS_DIR / "bills-search-stubs.json", []
    )
    openstates_bills = load_json(OPENSTATES_DIR / "bills.json", [])
    nelis_texts = index_texts(load_json(NELIS_DIR / "bill-texts.json", []), session_map)
    openstates_texts = index_texts(load_json(OPENSTATES_DIR / "bill-texts.json", []))

    nelis_issues = []
    for bill in nelis_bills:
        key = bill_key(bill.get("openstates_session") or session_map.get(bill.get("session", "")), bill.get("identifier"))
        rows = nelis_texts.get(key, [])
        if not rows:
            nelis_issues.append({"key": key, "issue": "no_text_links"})
            continue
        if not has_good_download(rows):
            nelis_issues.append({"key": key, "issue": "no_successful_pdf_download", "links": len(rows)})
            continue
        if not any(r.get("identifier_match") for r in rows if r.get("local_path")):
            nelis_issues.append(
                {
                    "key": key,
                    "issue": "identifier_not_found_in_pdf_preview_or_path",
                    "note": "Manual open of PDF recommended; OCR bills may fail text extract.",
                }
            )

    openstates_issues = []
    for bill in openstates_bills:
        key = bill_key(bill.get("session"), bill.get("identifier"))
        rows = openstates_texts.get(key, [])
        version_rows = [r for r in rows if r.get("kind") in {"version", "document"} and r.get("url")]
        if not version_rows:
            openstates_issues.append({"key": key, "issue": "no_version_or_document_links"})
            continue
        if not has_good_download(version_rows):
            openstates_issues.append(
                {"key": key, "issue": "no_successful_text_download", "links": len(version_rows)}
            )

    # Same-URL fingerprint agreement across sources.
    hash_conflicts = []
    nelis_by_url = {
        r["url"]: r
        for rows in nelis_texts.values()
        for r in rows
        if r.get("url") and r.get("sha256")
    }
    for rows in openstates_texts.values():
        for r in rows:
            url = r.get("url")
            if not url or not r.get("sha256"):
                continue
            other = nelis_by_url.get(url)
            if other and other.get("sha256") != r.get("sha256"):
                hash_conflicts.append(
                    {
                        "url": url,
                        "nelis_sha256": other.get("sha256"),
                        "openstates_sha256": r.get("sha256"),
                    }
                )

    nelis_ok = len(nelis_bills) - len([i for i in nelis_issues if i["issue"] != "identifier_not_found_in_pdf_preview_or_path"])
    # identifier_not_found is warning (scanned PDFs), hard fails are missing downloads
    hard_nelis = [i for i in nelis_issues if i["issue"] != "identifier_not_found_in_pdf_preview_or_path"]
    hard_os = openstates_issues
    warnings = [i for i in nelis_issues if i["issue"] == "identifier_not_found_in_pdf_preview_or_path"]

    openstates_present = len(openstates_bills) > 0
    missing_openstates = not openstates_present
    analysis_ready = (
        len(nelis_bills) > 0
        and len(hard_nelis) == 0
        and openstates_present
        and len(hard_os) == 0
        and len(hash_conflicts) == 0
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "nelis_bill_count": len(nelis_bills),
            "openstates_bill_count": len(openstates_bills),
            "nelis_hard_failures": len(hard_nelis),
            "openstates_hard_failures": len(hard_os),
            "openstates_package_missing": missing_openstates,
            "identifier_warnings": len(warnings),
            "same_url_hash_conflicts": len(hash_conflicts),
            "analysis_ready": analysis_ready,
        },
        "nelis_hard_failures": hard_nelis,
        "openstates_hard_failures": hard_os,
        "identifier_warnings": warnings[:100],
        "same_url_hash_conflicts": hash_conflicts,
        "authority_rule": (
            "Prefer NELIS Session PDF marked canonical_for_analysis (enrolled/reprint when present). "
            "OpenStates versions should match the same official URL/hash when available. "
            "Both sources must provide downloaded bill text before analysis begins."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "bill-text-integrity.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Bill Text Integrity",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        f"- Analysis ready: **{report['summary']['analysis_ready']}**",
        f"- NELIS bills: {report['summary']['nelis_bill_count']} (hard failures: {report['summary']['nelis_hard_failures']})",
        f"- OpenStates bills: {report['summary']['openstates_bill_count']} (hard failures: {report['summary']['openstates_hard_failures']})",
        f"- Identifier extract warnings: {report['summary']['identifier_warnings']}",
        f"- Same-URL hash conflicts: {report['summary']['same_url_hash_conflicts']}",
        "",
        report["authority_rule"],
        "",
    ]
    (OUT_DIR / "bill-text-integrity.md").write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Bill text integrity: analysis_ready={report['summary']['analysis_ready']} "
        f"nelis_hard={len(hard_nelis)} openstates_hard={len(hard_os)} "
        f"hash_conflicts={len(hash_conflicts)}"
    )
    if not report["summary"]["analysis_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
