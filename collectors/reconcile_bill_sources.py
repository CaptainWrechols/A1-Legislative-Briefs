#!/usr/bin/env python3
"""Cross-reference NELIS and OpenStates bill packages for consistency checks.

Matches bills by OpenStates session id + identifier (AB19 / session 82).
Compares title tokens, sponsor name sets, vote yea/nay counts, and enactment
signals. Writes a machine-readable report plus a short markdown summary for
reviewers.

NELIS is treated as the Nevada-official surface for history text and hearing
recommendations; OpenStates is treated as a structured API mirror that may lag
or omit fields when detail enrichment fails.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

NELIS_DIR = Path("sources/nevada/water-scarcity/nelis")
OPENSTATES_DIR = Path("sources/nevada/water-scarcity/openstates")
OUT_DIR = Path("sources/nevada/water-scarcity/crossref")

SESSION_PATH_TO_ID = {
    "80th2019": "80",
    "81st2021": "81",
    "82nd2023": "82",
    "83rd2025": "83",
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def norm_name(value: str | None) -> str:
    text = (value or "").lower()
    text = re.sub(r"\b(assemblyman|assemblywoman|assemblymember|senator)\b", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_tokens(value: str | None) -> set[str]:
    stop = {"the", "a", "an", "of", "to", "and", "for", "in", "on", "relating", "provisions"}
    tokens = re.findall(r"[a-z0-9]+", (value or "").lower())
    return {t for t in tokens if len(t) > 2 and t not in stop}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def nelis_match_key(bill: dict) -> str:
    session = bill.get("openstates_session") or SESSION_PATH_TO_ID.get(bill.get("session", ""), "")
    identifier = (bill.get("identifier") or "").upper()
    return f"{session}:{identifier}"


def openstates_match_key(bill: dict) -> str:
    return f"{bill.get('session')}:{(bill.get('identifier') or '').upper()}"


def index_rows(rows: list[dict], session_field_map=None) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        session = row.get("session")
        if session_field_map and session in session_field_map:
            session = session_field_map[session]
        key = f"{session}:{(row.get('bill_identifier') or '').upper()}"
        out.setdefault(key, []).append(row)
    return out


def signed_from_nelis(bill: dict, actions: list[dict]) -> bool | None:
    recent = (bill.get("most_recent_history_action") or "").lower()
    if "chapter" in recent or "approved by the governor" in recent:
        return True
    blob = " ".join((a.get("description") or "").lower() for a in actions)
    if "approved by the governor" in blob or re.search(r"\bchapter\s+\d+", blob):
        return True
    if actions:
        return False
    return None


def signed_from_openstates(bill: dict, progress_row: dict | None) -> bool | None:
    if progress_row and "signed_into_law" in progress_row:
        return bool(progress_row["signed_into_law"])
    latest = (bill.get("latest_action_description") or "").lower()
    if "approved by the governor" in latest or "chapter" in latest:
        return True
    return None


def compare_bill(key: str, nelis: dict | None, openstates: dict | None, ctx: dict) -> dict:
    row = {
        "key": key,
        "in_nelis": bool(nelis),
        "in_openstates": bool(openstates),
        "checks": {},
        "warnings": [],
        "conflicts": [],
    }
    if not nelis or not openstates:
        if nelis and not openstates:
            row["warnings"].append("present_only_in_nelis")
        if openstates and not nelis:
            row["warnings"].append("present_only_in_openstates")
        return row

    n_title = nelis.get("title") or ""
    o_title = openstates.get("title") or ""
    title_score = jaccard(title_tokens(n_title), title_tokens(o_title))
    row["checks"]["title_similarity"] = round(title_score, 3)
    if title_score < 0.25:
        row["conflicts"].append(
            {
                "field": "title",
                "nelis": n_title,
                "openstates": o_title,
                "similarity": title_score,
            }
        )

    n_sponsors = {norm_name(s.get("name")) for s in ctx["nelis_sponsors"].get(key, []) if s.get("name")}
    o_sponsors = {
        norm_name(s.get("name")) for s in ctx["openstates_sponsors"].get(key, []) if s.get("name")
    }
    # Drop empty norms
    n_sponsors = {s for s in n_sponsors if s}
    o_sponsors = {s for s in o_sponsors if s}
    sponsor_score = jaccard(n_sponsors, o_sponsors)
    row["checks"]["sponsor_overlap"] = round(sponsor_score, 3)
    row["checks"]["nelis_sponsor_count"] = len(n_sponsors)
    row["checks"]["openstates_sponsor_count"] = len(o_sponsors)
    if n_sponsors and o_sponsors and sponsor_score < 0.34:
        row["conflicts"].append(
            {
                "field": "sponsors",
                "nelis_only": sorted(n_sponsors - o_sponsors),
                "openstates_only": sorted(o_sponsors - n_sponsors),
                "overlap": sponsor_score,
            }
        )
    elif not n_sponsors or not o_sponsors:
        row["warnings"].append("sponsor_data_missing_on_one_source")

    n_votes = ctx["nelis_votes"].get(key, [])
    o_votes = ctx["openstates_votes"].get(key, [])
    row["checks"]["nelis_vote_events"] = len(n_votes)
    row["checks"]["openstates_vote_events"] = len(o_votes)
    if n_votes and not o_votes:
        row["warnings"].append("votes_only_in_nelis")
    if o_votes and not n_votes:
        row["warnings"].append("votes_only_in_openstates")

    # Compare aggregate yea/nay when both have final-passage-like events.
    def vote_fingerprint(votes: list[dict], source: str) -> set[tuple]:
        fps = set()
        for vote in votes:
            if source == "nelis":
                yea = vote.get("counts", {}).get("Yea")
                if yea is None:
                    yea = len(vote.get("yea_voters") or [])
                nay = vote.get("counts", {}).get("Nay")
                if nay is None:
                    nay = len(vote.get("nay_voters") or [])
                chamber = (vote.get("chamber_label") or "").split("(")[0].strip().lower()
                fps.add((chamber, int(yea or 0), int(nay or 0)))
            else:
                counts = {c.get("option"): c.get("value") for c in (vote.get("counts") or []) if isinstance(c, dict)}
                yea = counts.get("yes")
                if yea is None:
                    yea = vote.get("yes_count")
                nay = counts.get("no")
                if nay is None:
                    nay = vote.get("no_count")
                org = (vote.get("organization") or "").lower()
                chamber = "assembly" if "assembly" in org or "lower" in org else (
                    "senate" if "senate" in org or "upper" in org else org
                )
                fps.add((chamber, int(yea or 0), int(nay or 0)))
        return fps

    if n_votes and o_votes:
        n_fp = vote_fingerprint(n_votes, "nelis")
        o_fp = vote_fingerprint(o_votes, "openstates")
        overlap = jaccard({str(x) for x in n_fp}, {str(x) for x in o_fp})
        row["checks"]["vote_count_fingerprint_overlap"] = round(overlap, 3)
        if overlap == 0:
            row["conflicts"].append(
                {
                    "field": "vote_counts",
                    "nelis": sorted(n_fp),
                    "openstates": sorted(o_fp),
                }
            )

    n_signed = signed_from_nelis(nelis, ctx["nelis_actions"].get(key, []))
    o_signed = signed_from_openstates(openstates, ctx["openstates_progress"].get(key))
    row["checks"]["nelis_signed_into_law"] = n_signed
    row["checks"]["openstates_signed_into_law"] = o_signed
    if n_signed is not None and o_signed is not None and n_signed != o_signed:
        row["conflicts"].append(
            {
                "field": "signed_into_law",
                "nelis": n_signed,
                "openstates": o_signed,
            }
        )

    n_actions = len(ctx["nelis_actions"].get(key, []))
    o_actions = len(ctx["openstates_actions"].get(key, []))
    row["checks"]["nelis_action_count"] = n_actions
    row["checks"]["openstates_action_count"] = o_actions
    if n_actions and not o_actions:
        row["warnings"].append("actions_only_in_nelis")
    if o_actions and not n_actions:
        row["warnings"].append("actions_only_in_openstates")

    return row


def main() -> None:
    nelis_bills = load_json(NELIS_DIR / "bills.json", [])
    if not nelis_bills:
        nelis_bills = load_json(NELIS_DIR / "bills-search-stubs.json", [])
    openstates_bills = load_json(OPENSTATES_DIR / "bills.json", [])
    if not openstates_bills:
        openstates_bills = load_json(OPENSTATES_DIR / "bills-combined.json", [])

    nelis_by_key = {nelis_match_key(b): b for b in nelis_bills if nelis_match_key(b).count(":") == 1 and not nelis_match_key(b).startswith(":")}
    openstates_by_key = {openstates_match_key(b): b for b in openstates_bills}

    ctx = {
        "nelis_actions": index_rows(
            load_json(NELIS_DIR / "bill-actions.json", []), SESSION_PATH_TO_ID
        ),
        "nelis_votes": index_rows(load_json(NELIS_DIR / "bill-votes.json", []), SESSION_PATH_TO_ID),
        "nelis_sponsors": index_rows(
            load_json(NELIS_DIR / "bill-sponsors.json", []), SESSION_PATH_TO_ID
        ),
        "openstates_actions": index_rows(load_json(OPENSTATES_DIR / "bill-actions.json", [])),
        "openstates_votes": index_rows(load_json(OPENSTATES_DIR / "bill-votes.json", [])),
        "openstates_sponsors": index_rows(load_json(OPENSTATES_DIR / "bill-sponsors.json", [])),
        "openstates_progress": {
            f"{row.get('session')}:{(row.get('bill_identifier') or '').upper()}": row
            for row in load_json(OPENSTATES_DIR / "bill-legislative-progress.json", [])
        },
    }

    all_keys = sorted(set(nelis_by_key) | set(openstates_by_key))
    comparisons = [
        compare_bill(key, nelis_by_key.get(key), openstates_by_key.get(key), ctx)
        for key in all_keys
    ]

    both = [c for c in comparisons if c["in_nelis"] and c["in_openstates"]]
    conflicts = [c for c in comparisons if c["conflicts"]]
    warnings = [c for c in comparisons if c["warnings"]]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "nelis_bill_count": len(nelis_by_key),
            "openstates_bill_count": len(openstates_by_key),
            "matched_both": len(both),
            "nelis_only": sum(1 for c in comparisons if c["in_nelis"] and not c["in_openstates"]),
            "openstates_only": sum(1 for c in comparisons if c["in_openstates"] and not c["in_nelis"]),
            "conflict_bill_count": len(conflicts),
            "warning_bill_count": len(warnings),
        },
        "authority_notes": {
            "nelis": "Official Nevada Legislature site for bill text PDFs, history wording, hearings/recommendations, floor vote member lists.",
            "openstates": "Structured API mirror for actions/votes/sponsorships; useful for machine joins and party fields, but detail enrichment can fail (429/5xx).",
            "crosscheck_rule": "Flag conflicts for human review. Prefer NELIS wording for citations; use OpenStates when NELIS detail scrape failed and OpenStates enrichment succeeded.",
        },
        "bills": comparisons,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "bill-match-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# NELIS ↔ OpenStates Cross-Reference",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- NELIS bills: **{report['summary']['nelis_bill_count']}**",
        f"- OpenStates bills: **{report['summary']['openstates_bill_count']}**",
        f"- In both: **{report['summary']['matched_both']}**",
        f"- NELIS only: **{report['summary']['nelis_only']}**",
        f"- OpenStates only: **{report['summary']['openstates_only']}**",
        f"- Bills with field conflicts: **{report['summary']['conflict_bill_count']}**",
        f"- Bills with warnings: **{report['summary']['warning_bill_count']}**",
        "",
        "## How to use this",
        "",
        "1. Collect NELIS search + details.",
        "2. Collect OpenStates search + detail enrichment.",
        "3. Run this reconciler.",
        "4. Investigate every bill listed under Conflicts before citing vote/sponsor/enactment facts.",
        "",
        "## Conflicts",
        "",
    ]
    if not conflicts:
        lines.append("_None. No hard field conflicts detected._")
    else:
        for item in conflicts[:100]:
            lines.append(f"### `{item['key']}`")
            for conflict in item["conflicts"]:
                lines.append(f"- `{conflict['field']}`: `{json.dumps(conflict, default=str)[:300]}`")
            lines.append("")

    lines.extend(["## Coverage warnings (first 50)", ""])
    if not warnings:
        lines.append("_None._")
    else:
        for item in warnings[:50]:
            lines.append(f"- `{item['key']}`: {', '.join(item['warnings'])}")

    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"Cross-ref complete: both={report['summary']['matched_both']} "
        f"conflicts={report['summary']['conflict_bill_count']} -> {OUT_DIR}"
    )


if __name__ == "__main__":
    main()
