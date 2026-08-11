#!/usr/bin/env python3
"""Assemble the NH housing evidence pack (Evidence Curator v2.2, NH shapes).

Deterministic merge of:
  - working/.../curation-map.json      (plain topics, themes, relevance, dispositions)
  - processed/bill-votes.json          (SQL roll calls + per-member ballots)
  - pass1/bills.json                   (sponsors for the current biennium)
  - working/.../dispositions.json      (stages + sponsor lines for 2020-2021)
  - working/.../hb2-sections.json      (curated HB2 housing sections)

Only computes counts and shapes JSON; the judgment lives in curation-map.json
and the HB2 analysis. Nothing here invents votes, parties, or sponsors.

Run from repo root:
  python3 working/new-hampshire/housing-affordability/build-evidence-pack.py
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")
SRC = Path("sources/new-hampshire/housing-affordability")

ENACTED = {"enacted"}
KILLED = {"killed_floor", "killed_committee", "killed_deadline", "died_on_table",
          "died_between_chambers", "died_other"}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def norm_disposition(b: dict) -> str:
    d = b["disposition"]
    if d == "resolved_manually":
        s = b["stage"].lower()
        if "became" in s and "chapter" in s and "hb2" not in s:
            return "enacted"
        if "enacted through hb2" in s:
            return "content_enacted_via_hb2"
        if "vetoed" in s:
            return "vetoed"
        if "died" in s or "killed" in s or "table" in s:
            return "killed"
    if d in KILLED:
        return "killed"
    if d in ENACTED:
        return "enacted"
    return d  # vetoed | interim_study | passed | carryover_duplicate


def party_split(ballots, seq):
    c = defaultdict(Counter)
    for x in ballots:
        if x["voteSequenceNumber"] != seq:
            continue
        p = (x.get("Party") or "?").upper()
        if x["vote"] == 1:
            c[p]["yea"] += 1
        elif x["vote"] == 2:
            c[p]["nay"] += 1
    return {p: dict(v) for p, v in sorted(c.items())}


def parse_sponsor_line(line: str) -> list[dict]:
    out = []
    for part in re.split(r";", line or ""):
        part = part.strip()
        m = re.match(r"(Rep|Sen)\.\s+([^,]+)", part)
        if m:
            out.append({"name": m.group(2).strip(),
                        "body": "House" if m.group(1) == "Rep" else "Senate",
                        "party": None, "prime": len(out) == 0,
                        "source": "gencourt_final_text"})
    return out


def main() -> None:
    cur = load(W / "curation-map.json")
    disp = {f"{b['session_year']}:{b['bill_no']}": b for b in load(W / "dispositions.json")["bills"]}
    votes = {(v["session_year"], v["bill_no"]): v for v in load(SRC / "processed" / "bill-votes.json")["bills"]}
    pass1 = {(b["session_year"], b["bill_no"]): b for b in load(SRC / "pass1" / "bills.json")["bills"]}
    hb2 = load(W / "hb2-sections.json")

    bills = []
    for c in cur["bills"]:
        key = (c["session_year"], c["bill_no"])
        p1 = pass1[key]
        d = disp[c["bill_key"]]
        nd = norm_disposition(c | {"stage": d["stage"]})
        rec = {
            "bill_key": c["bill_key"],
            "session_year": c["session_year"],
            "identifier": c["bill_no"],
            "title": c["title"],
            "plain_topic": c["plain_topic"],
            "theme": c["theme"],
            "relevance": c["relevance"],
            "disposition": nd,
            "stage": d["stage"],
            "found_by_terms": p1.get("found_by_terms", []),
        }
        if d.get("citations"):
            rec["stage_citations"] = d["citations"]
        # sponsors
        if p1.get("sponsors"):
            rec["sponsors"] = [
                {"name": s.get("name"), "party": s.get("party"),
                 "body": {"H": "House", "S": "Senate"}.get(s.get("body"), s.get("body")),
                 "prime": bool(s.get("prime")) or str(s.get("primary")).lower() in ("true", "primary"),
                 "source": s.get("source") or "sql_sponsors"}
                for s in p1["sponsors"]]
        elif d.get("sponsors_line"):
            rec["sponsors"] = parse_sponsor_line(d["sponsors_line"])
        elif p1.get("os_sponsors"):
            rec["sponsors"] = [
                {"name": s.get("name"), "party": None, "body": None,
                 "prime": str(s.get("primary")).lower() in ("true", "primary", "1"),
                 "source": "openstates_bulk"}
                for s in p1["os_sponsors"]]
        # roll calls with party splits
        v = votes.get(key, {})
        rcs = []
        for r in v.get("roll_calls", []):
            yeas, nays = r.get("yeas") or 0, r.get("nays") or 0
            rc = {"body": {"H": "House", "S": "Senate"}.get(r["legislativeBody"], r["legislativeBody"]),
                  "date": str(r["voteDate"])[:10],
                  "motion": r.get("question_Motion"),
                  "yeas": yeas, "nays": nays,
                  "yes_pct": round(100 * yeas / (yeas + nays), 1) if (yeas + nays) else None}
            if v.get("ballots"):
                rc["party_split"] = party_split(v["ballots"], r["voteSequenceNumber"])
            rcs.append(rc)
        rec["roll_calls"] = rcs
        best = max((r for r in rcs if r["yes_pct"] is not None),
                   key=lambda r: r["yes_pct"], default=None)
        rec["best_floor_yes_pct"] = best["yes_pct"] if best else None
        bills.append(rec)

    policy = [b for b in bills if b["relevance"] != "context"
              and b["disposition"] != "carryover_duplicate"]
    core = [b for b in policy if b["relevance"] == "core"]

    # --- inventory ---
    inventory = {
        "collected_total": len(bills),
        "policy_set": len(policy),
        "core": len(core),
        "adjacent": sum(1 for b in policy if b["relevance"] == "adjacent"),
        "context_excluded": sum(1 for b in bills if b["relevance"] == "context"),
        "carryover_duplicates": sum(1 for b in bills if b["disposition"] == "carryover_duplicate"),
        "by_session": dict(sorted(Counter(b["session_year"] for b in policy).items())),
        "by_disposition": dict(Counter(b["disposition"] for b in policy).most_common()),
        "keyword_discovered_note": (
            "2020-2024 discovery is certified against the complete OpenStates "
            "bulk universe (5,467 bills across the five sessions): keyword "
            "search over every title, plus index-based and certification-sweep "
            "supplements, with every excluded wide-net candidate reviewed and "
            "categorized (see working/.../certification-report.json). "
            "2025-2026 comes complete from the official state database."),
    }

    # --- theme buckets ---
    themes = []
    for t in cur["themes"]:
        if t.startswith("Context"):
            continue
        tb = [b for b in policy if b["theme"] == t]
        if not tb:
            continue
        n_en = sum(1 for b in tb if b["disposition"] in ("enacted", "content_enacted_via_hb2"))
        stops = Counter(b["disposition"] for b in tb if b["disposition"] not in ("enacted", "content_enacted_via_hb2"))
        themes.append({
            "theme": t,
            "bills": len(tb),
            "enacted": n_en,
            "enactment_rate_pct": round(100 * n_en / len(tb), 1),
            "typical_stop": stops.most_common(1)[0][0] if stops else None,
            "stops": dict(stops),
            "bill_keys": [b["bill_key"] for b in tb],
        })

    # --- high-support non-enactments ---
    high_support = []
    for b in policy:
        if b["disposition"] in ("enacted", "content_enacted_via_hb2", "passed"):
            continue
        wins = [r for r in b["roll_calls"]
                if r["yes_pct"] and r["yes_pct"] > 50
                and re.search(r"OTP|Ought to Pass|Concur|Adopt", r.get("motion") or "")]
        if wins:
            top = max(wins, key=lambda r: r["yes_pct"])
            high_support.append({
                "bill_key": b["bill_key"], "plain_topic": b["plain_topic"],
                "vote": f"{top['body']} {top['yeas']}-{top['nays']} ({top['motion']})",
                "outcome": b["stage"]})

    # --- people signals ---
    def norm_name(n):
        n = re.sub(r"\s+[A-Z]\.(?=\s)", "", n or "")
        return re.sub(r"\s+", " ", n).strip()

    prime_counter = Counter()
    prime_party = {}
    cross_party = []
    with_sponsors = 0
    for b in policy:
        sp = b.get("sponsors") or []
        if sp:
            with_sponsors += 1
        primes = [s for s in sp if s.get("prime")]
        for s in primes:
            nm = norm_name(s["name"])
            prime_counter[nm] += 1
            if s.get("party"):
                prime_party[nm] = s["party"]
        parties = {s.get("party") for s in sp if s.get("party")}
        if {"R", "D"} <= parties:
            cross_party.append(b["bill_key"])
    people = {
        "bills_with_sponsor_data": with_sponsors,
        "sponsor_data_note": (
            "Sponsors come from the SQL sponsors table (current biennium) and "
            "gc.nh.gov final-text pages (2020-2021). Sponsor names for most "
            "2022-2024 bills are not in the collected record."),
        "frequent_primary_sponsors": [
            {"name": n, "party": prime_party.get(n), "bills": c}
            for n, c in prime_counter.most_common(12) if c >= 2],
        "cross_party_sponsored_bills": cross_party,
        "cross_party_count": len(cross_party),
    }

    # --- HB2 crosswalk ---
    hb2_summary = []
    for cyc in hb2["cycles"]:
        coresec = [s for s in cyc["relevant_sections"] if s["category"] == "core"]
        hb2_summary.append({
            "session_year": cyc["session_year"],
            "laws_citation": cyc["laws_citation"],
            "core_sections": len(coresec),
            "adjacent_sections": len(cyc["relevant_sections"]) - len(coresec),
            "headline_items": [f"{s['cite']} - {s['plain_language']}" for s in coresec],
            "whole_bill_final_votes": cyc["whole_bill_final_votes"],
        })
    hb2_tieins = [
        {"bill_key": "2023:SB145", "hb2": "79:462-466",
         "note": "Housing Champion program passed the Senate 21-3 as SB145, then was enacted through HB2 2023."},
        {"bill_key": "2023:SB203", "hb2": "79:301",
         "note": "SB203 tried to restructure the Board of Manufactured Housing and died between the chambers; HB2 2023 repealed the board outright."},
        {"bill_key": "2021:SB152", "hb2": "91:376",
         "note": "SB152's Affordable Housing Fund money died in the House as a standalone bill; the 2021 budget carried a $25M appropriation instead."},
        {"bill_key": "2023:SB231", "hb2": "79:39-43, 79:564",
         "note": "SB231's InvestNH, Affordable Housing Fund, and shelter appropriations were enacted through HB2 2023 while the standalone bill went no further."},
        {"bill_key": "2026:HB572", "hb2": "141:212",
         "note": "The Partners in Housing program moved through HB2 2025 while the standalone bill sat in the House."},
    ]

    # --- data limits ---
    data_limits = [
        "Bill discovery is certified complete for the issue vocabulary: "
        "2020-2024 was collected from the OpenStates bulk CSVs, a full mirror "
        "of the official docket (5,467 bills), and every bill in those five "
        "sessions was additionally swept with a wide-net housing vocabulary; "
        "all matches were either included or individually reviewed and "
        "categorized as out of scope (certification-report.json). 2025-2026 "
        "comes complete from the official state database. A housing bill could "
        "be absent only if its title avoids the entire wide-net vocabulary.",
        "Bills that span a biennium (e.g. filed 2023, decided 2024) appear "
        "once per year in the annual files; first-year records are marked "
        "carryover duplicates and counted once.",
        "Sponsor names now exist for most bills (SQL for 2025-2026, official "
        "final texts for 2020-2021, bulk files for 2022-2024); party labels "
        "are only on the SQL and final-text layers, so cross-party counts "
        "understate the true number.",
        "NH kills most bills by voice vote or on the consent calendar; a bill with "
        "no roll call is not necessarily uncontroversial.",
        "Committee votes appear only where a committee report recorded them "
        "(e.g. 'Vote 10-8; RC' in the docket); there is no complete committee-vote table.",
        "Roll-call party splits use the legislators table; a few older ballots "
        "have no party on record (shown as '?').",
        "Dispositions for eight older bills rest on archived dockets or cited "
        "news/official research rather than the SQL database; each such record "
        "carries its citations in dispositions.json.",
        "HB2 votes are on the whole budget trailer; they are never attributable "
        "to a single housing section.",
    ]

    pack = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issue": "new-hampshire-01-housing-affordability",
        "sessions": [2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "inventory": inventory,
        "themes": themes,
        "high_support_non_enactments": high_support,
        "people_signals": people,
        "hb2_crosswalk": {"cycles": hb2_summary, "standalone_bill_tieins": hb2_tieins},
        "data_limits": data_limits,
        "bills": bills,
    }
    (W / "evidence-pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")

    # ---- human skim ----
    md = ["# Evidence pack — Housing Affordability in New Hampshire", ""]
    md += [f"*{inventory['collected_total']} bills collected; "
           f"{inventory['policy_set']} in the policy set "
           f"({inventory['core']} core / {inventory['adjacent']} adjacent); "
           f"{inventory['context_excluded']} context bills excluded from counts.*", ""]
    md += ["## Dispositions (policy set)", ""]
    for k, v in inventory["by_disposition"].items():
        md += [f"- {k}: {v}"]
    md += ["", "## Bills by session (policy set)", ""]
    md += ["- " + ", ".join(f"{y}: {n}" for y, n in inventory["by_session"].items()), ""]
    md += ["## Themes", ""]
    for t in themes:
        md += [f"- **{t['theme']}** — {t['bills']} bills, {t['enacted']} enacted "
               f"({t['enactment_rate_pct']}%); stops: {t['stops']}"]
    md += ["", "## High-support non-enactments", ""]
    for h in high_support:
        md += [f"- {h['bill_key']}: {h['plain_topic']} — {h['vote']} → {h['outcome']}"]
    md += ["", "## People signals", ""]
    for s in people["frequent_primary_sponsors"]:
        md += [f"- {s['name']} ({s['party'] or '?'}) — prime sponsor on {s['bills']} bills"]
    md += [f"- Cross-party sponsor teams: {people['cross_party_count']} bills", ""]
    md += ["## HB2 crosswalk", ""]
    for c in hb2_summary:
        md += [f"- HB2 {c['session_year']} ({c['laws_citation']}): "
               f"{c['core_sections']} core + {c['adjacent_sections']} adjacent housing sections"]
    for t in hb2_tieins:
        md += [f"- Tie-in {t['bill_key']} ↔ HB2 {t['hb2']}: {t['note']}"]
    md += ["", "## Data limits", ""]
    for d in data_limits:
        md += [f"- {d}"]
    (W / "evidence-pack.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(inventory, indent=1)[:800])
    print("themes:", len(themes), "| high-support:", len(high_support),
          "| cross-party:", people["cross_party_count"])


if __name__ == "__main__":
    main()
