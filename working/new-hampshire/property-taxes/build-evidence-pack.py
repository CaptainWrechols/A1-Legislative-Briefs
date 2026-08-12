#!/usr/bin/env python3
"""Assemble the NH property-taxes evidence pack (Evidence Curator v2.2, NH shapes).

Deterministic merge of:
  - working/.../curation-map.json      (plain topics, themes, relevance, dispositions)
  - processed/bill-votes.json          (SQL roll calls + per-member ballots)
  - pass1/bills.json                   (sponsors: SQL for 2025-2026, bulk sponsorships 2020-2024)
  - working/.../dispositions.json      (stages)
  - working/.../hb2-sections.json      (curated HB2 tax/revenue sections)

Only computes counts and shapes JSON; the judgment lives in curation-map.json
and the HB2 analysis. Nothing here invents votes, parties, or sponsors.

Run from repo root:
  python3 working/new-hampshire/property-taxes/build-evidence-pack.py
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

W = Path("working/new-hampshire/property-taxes")
SRC = Path("sources/new-hampshire/property-taxes")

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
        # sponsors (SQL shape for 2025-2026; normalized bulk shape for 2020-2024)
        if p1.get("sponsors"):
            rec["sponsors"] = [
                {"name": s.get("name"), "party": s.get("party"),
                 "body": {"H": "House", "S": "Senate"}.get(s.get("body"), s.get("body")),
                 "prime": bool(s.get("prime")) or str(s.get("primary")).lower() in ("true", "primary"),
                 "source": s.get("source") or "sql_sponsors"}
                for s in p1["sponsors"]]
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
            "search over every title, plus a certification-sweep supplement, "
            "with every excluded wide-net candidate reviewed and categorized "
            "(see working/.../certification-report.json). 2025-2026 comes "
            "complete from the official state database."),
    }

    # --- theme buckets ---
    themes = []
    for t in cur["themes"]:
        if t.startswith("Context"):
            continue
        tb = [b for b in policy if b["theme"] == t]
        if not tb:
            continue
        n_en = sum(1 for b in tb if b["disposition"] == "enacted")
        stops = Counter(b["disposition"] for b in tb if b["disposition"] != "enacted")
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
        if b["disposition"] in ("enacted", "passed"):
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
            "Sponsors come from the SQL sponsors table (2025-2026, with party) "
            "and the OpenStates bulk sponsorship files (2020-2024, no party "
            "labels; first-listed treated as prime where the file carries no "
            "flag). Cross-party counts therefore understate the true number."),
        "frequent_primary_sponsors": [
            {"name": n, "party": prime_party.get(n), "bills": c}
            for n, c in prime_counter.most_common(12) if c >= 3],
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
        {"bill_key": "2020:HB623", "hb2": "91:109-110",
         "note": "Standalone BPT/BET rate bills died in 2020; the 2021 trailer then cut both rates (BPT 7.7 to 7.6, BET 0.675 to 0.55)."},
        {"bill_key": "2022:HB568", "hb2": "79:85-88",
         "note": "Standalone bills to repeal the interest and dividends tax early (HB568 2022) died; the 2023 trailer accelerated the repeal to January 1, 2025 anyway."},
        {"bill_key": "2021:SB99", "hb2": "91:112",
         "note": "SB99's push to raise the towns' meals-and-rooms share died on the Senate table; the 2021 trailer rewrote the distribution and created the municipal revenue fund."},
        {"bill_key": "2025:HB255", "hb2": "141:132-133",
         "note": "HB255/HB318 would have RAISED the education trust fund's share of the business taxes; both died while the 2025 trailer CUT the share from 41 to 39 percent."},
        {"bill_key": "2026:HB728", "hb2": "141:26",
         "note": "The standalone video lottery terminal bill died in 2026 - the 2025 trailer had already legalized VLTs; SB83 (2025) carried the companion exemption-reimbursement fund into law."},
        {"bill_key": "2025:SB277", "hb2": "141:335-340",
         "note": "SB277's utility-property/SWEPT fix died at the Senate deadline but was enacted as standalone HB696 the same year (not via HB2); listed here because the BTLA quorum section (141:340) interlocks with the same appeals machinery."},
    ]

    # --- data limits ---
    data_limits = [
        "Bill discovery is certified complete for the issue vocabulary: "
        "2020-2024 was collected from the OpenStates bulk CSVs, a full mirror "
        "of the official docket (5,467 bills), and every bill in those five "
        "sessions was additionally swept with a wide-net tax/revenue "
        "vocabulary; all matches were either included or individually "
        "reviewed and categorized as out of scope (certification-report.json). "
        "2025-2026 comes complete from the official state database. A tax "
        "bill could be absent only if its title avoids the entire wide-net "
        "vocabulary.",
        "Bills that span a biennium (e.g. filed 2023, decided 2024) appear "
        "once per year in the annual files; first-year records are marked "
        "carryover duplicates and counted once.",
        "Sponsor names exist for nearly every bill (SQL for 2025-2026, "
        "OpenStates bulk sponsorship files for 2020-2024); party labels exist "
        "only on the 2025-2026 layer, so cross-party counts understate the "
        "true number.",
        "NH kills most bills by voice vote or on the consent calendar; a bill "
        "with no roll call is not necessarily uncontroversial.",
        "Committee votes appear only where a committee report recorded them "
        "(e.g. 'Vote 12-7; RC' in the docket); there is no complete "
        "committee-vote table.",
        "Roll-call party splits use the legislators table; a few older "
        "ballots have no party on record (shown as '?').",
        "HB2 votes are on the whole budget trailer; they are never "
        "attributable to a single tax or revenue section.",
        "The three HB2 bill records themselves (2021, 2023, 2025) are kept in "
        "the collected set as context so the trailer's sections (analyzed in "
        "Appendix H) are not double-counted in bill totals.",
    ]

    pack = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issue": "new-hampshire-02-property-taxes",
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
    md = ["# Evidence pack — Property Taxes and Revenue Needs in New Hampshire", ""]
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
               f"{c['core_sections']} core + {c['adjacent_sections']} adjacent tax/revenue sections"]
    for t in hb2_tieins:
        md += [f"- Tie-in {t['bill_key']} ↔ HB2 {t['hb2']}: {t['note']}"]
    md += ["", "## Data limits", ""]
    for d in data_limits:
        md += [f"- {d}"]
    (W / "evidence-pack.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(inventory, indent=1)[:900])
    print("themes:", len(themes), "| high-support:", len(high_support),
          "| cross-party:", people["cross_party_count"])


if __name__ == "__main__":
    main()
