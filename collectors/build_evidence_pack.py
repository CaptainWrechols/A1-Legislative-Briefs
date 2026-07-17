#!/usr/bin/env python3
"""Assemble working/{...}/evidence-pack.json (Evidence Curator v2.2 assembler).

Deterministic merge of:
  - processed/bills-core.json          (titles, digests, sponsors, milestones)
  - processed/bill-votes.json          (floor + committee votes with party)
  - working/curation-map.json          (hand-written plain topics, themes, relevance)
  - config/issues/{issue}.yaml         (constituent_proposals)

The plain-language judgment lives in curation-map.json (written by the
Evidence Curator agent); this script only computes counts and shapes JSON,
so the pack never contains invented votes or parties.

  python collectors/build_evidence_pack.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

SOURCES = Path("sources/nevada/water-scarcity")
WORKING = Path("working/nevada/water-scarcity")
CONFIG = Path("config/issues/nevada-water-scarcity.yaml")

YEARS = {"80": "2019", "81": "2021", "82": "2023", "83": "2025"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def stage_of(milestones: dict, disposition: str) -> str:
    if milestones.get("signed_into_law"):
        return "enacted"
    if milestones.get("vetoed"):
        return "vetoed"
    if milestones.get("passed_second_chamber"):
        return "after_both_chambers"
    if milestones.get("passed_origin_chamber"):
        return "second_chamber"
    if milestones.get("passed_out_of_committee_origin"):
        return "origin_floor"
    if milestones.get("seen_in_committee_origin"):
        return "origin_committee"
    return "introduced"


def main() -> None:
    core = load(SOURCES / "processed" / "bills-core.json")["bills"]
    votes = load(SOURCES / "processed" / "bill-votes.json")
    curation = load(WORKING / "curation-map.json")
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    votes_by_bill: dict[str, list[dict]] = {}
    for v in votes:
        votes_by_bill.setdefault(f"{v['session']}:{v['bill_identifier']}", []).append(v)

    bills = []
    for b in core:
        key = f"{b['session']}:{b['identifier']}"
        cur = curation["bills"].get(key) or {}
        milestones = b.get("milestones") or {}
        disposition = b.get("final_disposition") or "Unknown"

        best_pct = None
        best_yes_no = None
        for v in votes_by_bill.get(key, []):
            motion = (v.get("motion") or "").lower()
            if "final passage" not in motion:
                continue
            c = v.get("counts") or {}
            yes = c.get("yes") or 0
            no = c.get("no") or 0
            if yes + no == 0:
                continue
            pct = round(100.0 * yes / (yes + no), 1)
            if best_pct is None or pct > best_pct:
                best_pct = pct
                best_yes_no = f"{yes}-{no}"

        primary = [
            {"name": s.get("name"), "party": s.get("party"), "entity_type": s.get("entity_type")}
            for s in (b.get("primary_sponsors") or [])
        ]
        cos = [
            {"name": s.get("name"), "party": s.get("party"), "entity_type": s.get("entity_type")}
            for s in (b.get("co_sponsors") or [])
        ]
        bills.append(
            {
                "bill_key": key,
                "session": b["session"],
                "session_year": YEARS.get(b["session"], b["session"]),
                "identifier": b["identifier"],
                "title": b.get("title"),
                "plain_topic": cur.get("plain_topic") or (b.get("title") or ""),
                "theme": cur.get("theme") or "context",
                "relevance": cur.get("relevance") or "context",
                "disposition": disposition,
                "death_or_success_stage": stage_of(milestones, disposition),
                "primary_sponsors": primary,
                "co_sponsors": cos,
                "best_floor_yes_pct": best_pct,
                "best_floor_yes_no": best_yes_no,
                "nelis_url": b.get("nelis_url"),
                "strong_title_match": bool(b.get("passes_water_title_filter")),
            }
        )

    policy = [b for b in bills if b["relevance"] in ("core", "adjacent")]
    ctx = [b for b in bills if b["relevance"] == "context"]

    def disp_counts(rows):
        out: dict[str, int] = {}
        for r in rows:
            out[r["disposition"]] = out.get(r["disposition"], 0) + 1
        return out

    themes: dict[str, dict] = {}
    for b in policy:
        t = themes.setdefault(
            b["theme"],
            {
                "theme_id": b["theme"],
                "label": curation["themes"].get(b["theme"], b["theme"]),
                "bills": [],
            },
        )
        t["bills"].append(b["bill_key"])
    for t in themes.values():
        rows = [b for b in policy if b["bill_key"] in t["bills"]]
        enacted = [b for b in rows if b["disposition"] == "Enacted"]
        t["bill_count"] = len(rows)
        t["enacted_count"] = len(enacted)
        t["enactment_rate_pct"] = round(100.0 * len(enacted) / len(rows), 1) if rows else 0.0
        stops: dict[str, int] = {}
        for b in rows:
            if b["disposition"] not in ("Enacted",):
                stops[b["death_or_success_stage"]] = stops.get(b["death_or_success_stage"], 0) + 1
        t["stop_stages_when_not_enacted"] = stops

    # High-support non-enactments (floor >50% yes but not law)
    high_support = [
        {
            "bill_key": b["bill_key"],
            "plain_topic": b["plain_topic"],
            "best_floor_yes_pct": b["best_floor_yes_pct"],
            "best_floor_yes_no": b["best_floor_yes_no"],
            "stage": b["death_or_success_stage"],
            "disposition": b["disposition"],
        }
        for b in policy
        if b["disposition"] != "Enacted"
        and b["best_floor_yes_pct"] is not None
        and b["best_floor_yes_pct"] > 50.0
    ]

    # People signals
    sponsor_counts: dict[str, dict] = {}
    committee_sponsored = 0
    person_sponsored = 0
    cross_party = []
    for b in policy:
        people = [s for s in b["primary_sponsors"] if s.get("entity_type") != "organization"]
        orgs = [s for s in b["primary_sponsors"] if s.get("entity_type") == "organization"]
        if orgs and not people:
            committee_sponsored += 1
        elif people:
            person_sponsored += 1
        parties = {
            s.get("party")
            for s in b["primary_sponsors"] + b["co_sponsors"]
            if s.get("party") in ("Democratic", "Republican")
        }
        if len(parties) == 2:
            cross_party.append(b["bill_key"])
        for s in people:
            row = sponsor_counts.setdefault(
                s["name"], {"name": s["name"], "party": s.get("party"), "bill_count": 0, "bills": []}
            )
            row["bill_count"] += 1
            row["bills"].append(b["bill_key"])
    frequent = sorted(sponsor_counts.values(), key=lambda r: -r["bill_count"])[:12]

    # Constituent proposal crosswalk
    crosswalk = []
    for prop in cfg.get("constituent_proposals") or []:
        terms = [t.lower() for t in prop.get("match_terms") or []]
        matched = []
        near_miss = []
        for b in bills:
            blob = " ".join(
                [b.get("plain_topic") or "", b.get("title") or ""]
            ).lower()
            hit = any(t in blob for t in terms) or (
                b["theme"] == "big-users" and prop["id"] == "regulate-data-centers"
            )
            if not hit:
                continue
            if b["relevance"] == "context":
                near_miss.append(b["bill_key"])
            else:
                matched.append(b["bill_key"])
        crosswalk.append(
            {
                "proposal_id": prop["id"],
                "title": prop["title"],
                "matched_bills": matched,
                "near_miss_bills": near_miss,
                "coverage": (
                    "none" if not matched else "thin" if len(matched) <= 2 else "partial"
                ),
            }
        )

    sessions_snapshot = {}
    for sid, year in YEARS.items():
        rows = [b for b in policy if b["session"] == sid]
        sessions_snapshot[year] = {
            "bills_in_set": len(rows),
            "dispositions": disp_counts(rows),
        }

    pack = {
        "issue_id": cfg["issue_id"],
        "issue_title": cfg["issue_title"],
        "built_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "evidence-curator v2.2 (curation-map + build_evidence_pack.py)",
        "inventory": {
            "total_bills_collected": len(bills),
            "policy_bills": len(policy),
            "core_bills": sum(1 for b in bills if b["relevance"] == "core"),
            "adjacent_bills": sum(1 for b in bills if b["relevance"] == "adjacent"),
            "context_bills": len(ctx),
            "dispositions_policy": disp_counts(policy),
            "sessions": sessions_snapshot,
            "discovery_note": (
                "Set discovered via NELIS keyword search + the LCB official Subject "
                "Index of Bills (WATER, WATER RIGHTS, STATE ENGINEER, DROUGHT, DATA "
                "CENTERS and related headings) for 2019-2025. Keyword-plus-index "
                "discovery is strong but still not a proven complete universe."
            ),
        },
        "themes": sorted(themes.values(), key=lambda t: -t["bill_count"]),
        "high_support_non_enactments": sorted(
            high_support, key=lambda r: -(r["best_floor_yes_pct"] or 0)
        ),
        "people_signals": {
            "committee_sponsored_policy_bills": committee_sponsored,
            "person_sponsored_policy_bills": person_sponsored,
            "frequent_primary_sponsors": frequent,
            "cross_party_sponsored_bills": cross_party,
        },
        "constituent_proposal_crosswalk": crosswalk,
        "data_limits": [
            "The set was found by keyword search plus the official subject index; it is broad but not guaranteed complete.",
            "The record shows where each bill stopped — never why.",
            "Committee Yea votes are inferred (membership minus recorded Nay/Absent) because Nevada minutes usually list only No and Absent votes; these rows are marked in the source data.",
            "No OpenStates data in this refresh; party labels come from official NELIS legislator directories (100% of ballot rows matched).",
            "Context bills (found by broad search terms or omnibus indexing) are kept for audit but excluded from headline counts.",
        ],
        "bills": bills,
    }
    out = WORKING / "evidence-pack.json"
    out.write_text(json.dumps(pack, indent=2), encoding="utf-8")
    print(
        f"Wrote {out}: bills={len(bills)} policy={len(policy)} themes={len(themes)} "
        f"high_support={len(high_support)} crosswalk={len(crosswalk)}"
    )


if __name__ == "__main__":
    main()
