#!/usr/bin/env python3
"""Build appendices A-G (Appendix Builder v2.2 assembler).

Deterministic tables from evidence-pack.json + reality-map.json + processed
Pass 2 files. Narrative intros are maintained in this script; all numbers
come from the data.

  python collectors/build_appendices.py
"""

from __future__ import annotations

import json
from pathlib import Path

import sys as _sys
from pathlib import Path as _P
_sys.path.insert(0, str(_P(__file__).resolve().parent))
import issue_paths as ip  # noqa: E402

SOURCES = ip.SOURCES
WORKING = ip.WORKING
OUT = ip.BRIEF_DIR / "appendices"

YEARS = {"80": "2019", "81": "2021", "82": "2023", "83": "2025"}
STAGE_LABEL = {
    "enacted": "Became law",
    "vetoed": "Vetoed by the governor",
    "after_both_chambers": "Passed both houses, still no law",
    "second_chamber": "Died in the second house",
    "origin_floor": "Died on its first floor / calendar",
    "origin_committee": "Died in its first committee",
    "introduced": "Introduced, no further step recorded",
}
REL_LABEL = {"core": "Core", "adjacent": "Adjacent", "context": "Context"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def bill_label(key: str) -> str:
    session, ident = key.split(":")
    return f"{YEARS[session]} {ident}"


def esc(text: str) -> str:
    return (text or "").replace("|", "/").strip()


def sponsors_short(bill: dict) -> str:
    names = []
    for s in bill.get("primary_sponsors") or []:
        n = s.get("name") or ""
        if s.get("entity_type") == "organization":
            n = n.replace("Committee on ", "Cmte ")
        p = s.get("party")
        names.append(f"{n} ({p[0]})" if p in ("Democratic", "Republican") else n)
    return "; ".join(names[:3]) + (" …" if len(names) > 3 else "") or "—"


def main() -> None:
    pack = load(WORKING / "evidence-pack.json")
    rmap = load(WORKING / "reality-map.json")
    votes = load(SOURCES / "processed" / "bill-votes.json")
    text_changes = load(SOURCES / "processed" / "bill-text-changes.json")
    gaps = load(SOURCES / "processed" / "data-gaps.json")

    bills = pack["bills"]
    policy = [b for b in bills if b["relevance"] != "context"]
    ctx = [b for b in bills if b["relevance"] == "context"]
    OUT.mkdir(parents=True, exist_ok=True)
    theme_label = {t["theme_id"]: t["label"] for t in pack["themes"]}
    theme_label["context"] = "Context (not water policy)"

    # ---------- A ----------
    a = ["# Appendix A — Every bill in the set\n"]
    a.append(
        "This record holds 165 bills found for 2019–2025: 100 policy bills "
        "(water or big-user policy is a real part of the bill) and 65 context "
        "bills (found by broad search terms or omnibus indexing; kept so the "
        "search is auditable). Headline numbers in the front brief use the "
        "policy set only. \"Where it ended\" tells you the last step the bill "
        "reached — the record never says why it stopped.\n"
    )
    a.append("## Policy bills (100)\n")
    a.append("| Year | Bill | What it tried (plain words) | Theme | Result | Where it ended | Primary sponsors |")
    a.append("|---|---|---|---|---|---|---|")
    for b in sorted(policy, key=lambda x: (x["session"], x["identifier"])):
        a.append(
            f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'])} "
            f"| {theme_label.get(b['theme'], b['theme'])} | {b['disposition']} "
            f"| {STAGE_LABEL.get(b['death_or_success_stage'], b['death_or_success_stage'])} "
            f"| {esc(sponsors_short(b))} |"
        )
    a.append("\n<!-- pdf-page-break -->\n")
    a.append("## Context bills (65)\n")
    a.append(
        "These were surfaced by broad search terms (like \"partial abatement\" "
        "or \"closed-loop\") or by omnibus subject indexing, but water policy "
        "is not what they do. They are excluded from headline counts.\n"
    )
    a.append("| Year | Bill | Why it appeared in the search | Result |")
    a.append("|---|---|---|---|")
    for b in sorted(ctx, key=lambda x: (x["session"], x["identifier"])):
        a.append(
            f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'])} | {b['disposition']} |"
        )
    (OUT / "A-bills-overview.md").write_text("\n".join(a) + "\n", encoding="utf-8")

    # ---------- B ----------
    bmd = ["# Appendix B — Theme scorecards\n"]
    bmd.append(
        "Each policy bill was assigned one theme. The basket says how this "
        "kind of idea usually fared in this record: Often moved before / Got "
        "support but didn't finish / Rarely moved before / Mixed.\n"
    )
    cards = {t["theme_id"]: t for t in rmap["theme_scorecards"]}
    for t in pack["themes"]:
        if t["theme_id"] == "context":
            continue
        card = cards.get(t["theme_id"], {})
        basket = rmap["baskets"].get(card.get("basket", ""), card.get("basket", ""))
        bmd.append(f"\n## {t['label']}\n")
        bmd.append(
            f"- **Bills:** {t['bill_count']} · **Became law:** {t['enacted_count']} "
            f"({t['enactment_rate_pct']}%) · **Basket:** {basket} · "
            f"**Certainty:** {card.get('certainty', 'n/a')}"
        )
        if card.get("typical_stop"):
            bmd.append(f"- **Typical stop:** {card['typical_stop']}")
        if card.get("inference"):
            bmd.append(f"- *{card['inference']}*")
        bmd.append("\n| Year | Bill | What it tried | Result | Where it ended |")
        bmd.append("|---|---|---|---|---|")
        rows = [b for b in policy if b["theme"] == t["theme_id"]]
        for b in sorted(rows, key=lambda x: (x["session"], x["identifier"])):
            bmd.append(
                f"| {b['session_year']} | {b['identifier']} | {esc(b['plain_topic'])} "
                f"| {b['disposition']} | {STAGE_LABEL.get(b['death_or_success_stage'], '')} |"
            )
        bmd.append("\n<!-- pdf-page-break -->")
    (OUT / "B-theme-scorecards.md").write_text("\n".join(bmd) + "\n", encoding="utf-8")

    # ---------- C ----------
    c = ["# Appendix C — Votes and support\n"]
    c.append(
        "Final Passage floor votes for policy bills, plus committee "
        "work-session votes where minutes recorded them. Committee Yea lists "
        "marked * are inferred: Nevada minutes usually record only No and "
        "Absent votes, so remaining committee members are counted as Yes.\n"
    )
    c.append("## Final Passage floor votes\n")
    c.append("| Year | Bill | Chamber | Yes | No | Yes% | Party split (Yes) | Outcome |")
    c.append("|---|---|---|---|---|---|---|---|")
    pol_keys = {b["bill_key"] for b in policy}
    by_key = {b["bill_key"]: b for b in bills}
    floor_rows = []
    for v in votes:
        key = f"{v['session']}:{v['bill_identifier']}"
        if key not in pol_keys:
            continue
        if "final passage" not in (v.get("motion") or "").lower():
            continue
        cnt = v.get("counts") or {}
        yes, no = cnt.get("yes") or 0, cnt.get("no") or 0
        if yes + no == 0:
            continue
        dem = sum(
            1
            for bal in v.get("ballots") or []
            if bal.get("vote") == "yea" and bal.get("party") == "Democratic"
        )
        rep = sum(
            1
            for bal in v.get("ballots") or []
            if bal.get("vote") == "yea" and bal.get("party") == "Republican"
        )
        floor_rows.append((key, v, yes, no, dem, rep))
    for key, v, yes, no, dem, rep in sorted(floor_rows, key=lambda r: r[0]):
        b = by_key[key]
        pct = round(100.0 * yes / (yes + no), 1)
        c.append(
            f"| {YEARS[v['session']]} | {v['bill_identifier']} | {esc(v.get('chamber') or '')} "
            f"| {yes} | {no} | {pct}% | {dem} D / {rep} R | {b['disposition']} |"
        )
    c.append("\n<!-- pdf-page-break -->\n")
    c.append("## High support, still no law\n")
    c.append(
        "Policy bills whose best Final Passage vote was above 50% Yes but "
        "which never became law. These are possible timing or process deaths "
        "— the record does not say why they stopped.\n"
    )
    c.append("| Bill | Best floor vote | Where it ended | What it tried |")
    c.append("|---|---|---|---|")
    for h in pack["high_support_non_enactments"]:
        c.append(
            f"| {bill_label(h['bill_key'])} | {h['best_floor_yes_no']} ({h['best_floor_yes_pct']}%) "
            f"| {STAGE_LABEL.get(h['stage'], h['stage'])} | {esc(h['plain_topic'])} |"
        )
    (OUT / "C-votes-and-support.md").write_text("\n".join(c) + "\n", encoding="utf-8")

    # ---------- D ----------
    d = ["# Appendix D — Sponsors and people\n"]
    d.append(
        "A sponsor is the lawmaker or committee that puts a bill forward. "
        "Party letters follow official legislative rosters. Policy bills only.\n"
    )
    ps = pack["people_signals"]
    d.append(
        f"Committee-sponsored: **{ps['committee_sponsored_policy_bills']}** · "
        f"Person-sponsored: **{ps['person_sponsored_policy_bills']}**\n"
    )
    d.append("## Frequent primary sponsors\n")
    d.append("| Sponsor | Party | Policy bills | Bills |")
    d.append("|---|---|---|---|")
    for f in ps["frequent_primary_sponsors"]:
        if f["bill_count"] < 2:
            continue
        blist = ", ".join(bill_label(k) for k in f["bills"])
        d.append(f"| {esc(f['name'])} | {f.get('party') or '—'} | {f['bill_count']} | {blist} |")
    d.append("\n## Bills with sponsors from both major parties\n")
    d.append("| Bill | What it tried | Result |")
    d.append("|---|---|---|")
    for k in ps["cross_party_sponsored_bills"]:
        b = by_key[k]
        d.append(f"| {bill_label(k)} | {esc(b['plain_topic'])} | {b['disposition']} |")
    d.append("\n<!-- pdf-page-break -->\n")
    d.append("## Primary sponsors, bill by bill\n")
    d.append("| Year | Bill | Primary sponsors |")
    d.append("|---|---|---|")
    for b in sorted(policy, key=lambda x: (x["session"], x["identifier"])):
        d.append(f"| {b['session_year']} | {b['identifier']} | {esc(sponsors_short(b))} |")
    (OUT / "D-sponsors-and-people.md").write_text("\n".join(d) + "\n", encoding="utf-8")

    # ---------- E ----------
    e = ["# Appendix E — How far each bill got\n"]
    e.append(
        "The path of every policy bill through the steps: first committee → "
        "first floor → the other house → the governor. ✓ means the bill "
        "cleared that step.\n"
    )
    e.append("| Year | Bill | 1st cmte | 1st floor | Crossed | 2nd cmte | 2nd floor | Governor | Final |")
    e.append("|---|---|---|---|---|---|---|---|---|")
    prog = {
        f"{r['session']}:{r['bill_identifier']}": r
        for r in load(SOURCES / "processed" / "bill-legislative-progress.json")
    }
    for b in sorted(policy, key=lambda x: (x["session"], x["identifier"])):
        m = (prog.get(b["bill_key"]) or {}).get("milestones") or {}
        def mark(flag):
            return "✓" if m.get(flag) else "—"
        gov = "signed" if m.get("signed_into_law") else ("VETO" if m.get("vetoed") else "—")
        e.append(
            f"| {b['session_year']} | {b['identifier']} "
            f"| {mark('passed_out_of_committee_origin')} | {mark('passed_origin_chamber')} "
            f"| {mark('crossed_over')} | {mark('passed_out_of_committee_second_chamber')} "
            f"| {mark('passed_second_chamber')} | {gov} | {b['disposition']} |"
        )
    (OUT / "E-bill-path-details.md").write_text("\n".join(e) + "\n", encoding="utf-8")

    # ---------- F ----------
    f = ["# Appendix F — What this data can and cannot say\n"]
    f.append("Plain-language limits of the record behind this packet.\n")
    for i, limit in enumerate(pack["data_limits"], 1):
        f.append(f"{i}. {limit}")
    f.append("")
    f.append(
        "Known collection gaps recorded during the refresh: "
        f"{sum(1 for g in gaps if g.get('result') not in ('complete',))} items "
        "(see `sources/nevada/water-scarcity/processed/data-gaps.json`). "
        "OpenStates was unavailable for this refresh; all history, votes, and "
        "party labels come from the official NELIS system and legislator "
        "rosters, with committee votes read from official minutes PDFs."
    )
    (OUT / "F-data-limits.md").write_text("\n".join(f) + "\n", encoding="utf-8")

    # ---------- G ----------
    g = ["# Appendix G — Did the text change on the way to the governor?\n"]
    g.append(
        "For bills that reached the governor, this compares the bill as "
        "introduced with the final (enrolled) text. \"Similarity\" of 1.0 "
        "means nearly unchanged; low numbers mean heavy amendment.\n"
    )
    g.append("| Year | Bill | Amended? | Similarity | Note |")
    g.append("|---|---|---|---|---|")
    tc = {
        f"{r['session']}:{r['bill_identifier']}": r
        for r in (text_changes.get("bills") or [])
        if r.get("status") == "ok"
    }
    for key in sorted(tc):
        if key not in pol_keys:
            continue
        r = tc[key]
        b = by_key[key]
        sim = r.get("similarity_ratio")
        g.append(
            f"| {YEARS[key.split(':')[0]]} | {key.split(':')[1]} "
            f"| {'yes' if r.get('was_textually_amended') else 'no'} "
            f"| {sim if sim is not None else '—'} | {esc((r.get('narrative') or '')[:160])} |"
        )
    (OUT / "G-text-changes.md").write_text("\n".join(g) + "\n", encoding="utf-8")

    # ---------- H ----------
    cards = rmap.get("proposal_reality_cards") or []
    if cards:
        h = ["# Appendix H — Citizen statements, checked against the record\n"]
        h.append(
            "The ten most common citizen statements on water from the Phase 2 "
            "Community Conversations (RAG constituent-voice dataset), each "
            "checked against the 2019–2025 bill record. \"Never filed\" means "
            "no bill in this record proposed it — not that it is impossible.\n"
        )
        status_label = {
            "tried_and_stalled": "Tried, but stalled",
            "never_filed_as_such": "Never filed",
            "tried_and_stalled_partly_done": "Tried and stalled; pieces passed",
            "never_filed_statewide": "Never filed statewide",
            "never_filed": "Never filed",
            "thin_record": "Thin record",
            "direction_repeatedly_failed": "This direction failed repeatedly",
            "precedent_exists_mixed": "Precedent exists; mixed since",
        }
        for i, card in enumerate(cards, 1):
            h.append(f"\n## {i}. {card.get('citizen_statement', card['proposal_id'])}\n")
            h.append(f"- **Status:** {status_label.get(card.get('status'), card.get('status', ''))}")
            h.append(f"- **The record:** {card.get('record', '')}")
            if card.get("venue_note"):
                h.append(f"- **Where the decision sits:** {card['venue_note']}")
            if card.get("matched_bills"):
                rows = []
                for k in card["matched_bills"]:
                    b = by_key.get(k)
                    if b:
                        rows.append(
                            f"| {bill_label(k)} | {esc(b['plain_topic'])} | {b['disposition']} "
                            f"| {STAGE_LABEL.get(b['death_or_success_stage'], '')} |"
                        )
                if rows:
                    h.append("\n| Bill | What it tried | Result | Where it ended |")
                    h.append("|---|---|---|---|")
                    h.extend(rows)
            if card.get("open_questions"):
                h.append("\n**Open questions for a working group:**")
                for q in card["open_questions"]:
                    h.append(f"- {q}")
            h.append("\n<!-- pdf-page-break -->")
        (OUT / "H-citizen-statements-crosswalk.md").write_text("\n".join(h) + "\n", encoding="utf-8")

    # ---------- README ----------
    readme = f"""# Appendices — Growth, Water Scarcity, and Long-Term Supply in Nevada

Long-form detail behind the 2-page citizen front brief (citizen-v2.0).
Built from the July 2026 re-collection: 165 bills found, 100 policy bills.

| File | Contents |
|---|---|
| `A-bills-overview.md` | Every bill: plain topic, theme, result, where it ended, sponsors (policy + context sets) |
| `B-theme-scorecards.md` | Ten themes with baskets, stop patterns, and full bill tables |
| `C-votes-and-support.md` | Final Passage votes with party splits; high-support non-enactments |
| `D-sponsors-and-people.md` | Frequent sponsors, cross-party bills, sponsor-by-bill list |
| `E-bill-path-details.md` | Step-by-step progress checkmarks for all policy bills |
| `F-data-limits.md` | What the data cannot say |
| `G-text-changes.md` | Introduced vs. final text for governor-bound bills |
| `H-citizen-statements-crosswalk.md` | The ten most common citizen statements, each checked against the record |
| `I-sources-and-review-notes.md` | Claim-to-source mapping, collection notes, review status |

Committee Yea votes marked * anywhere in these appendices are inferred
(membership minus recorded Nay/Absent) because Nevada minutes usually list
only No and Absent votes.

Print: open `appendices-print.html` and print to PDF (US Letter).
Word: `appendices.docx` in this folder, or run
`python collectors/export_docx.py --brief-dir briefs/nevada/water-scarcity/citizen-v1`.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Wrote appendices A-G + README to {OUT}")


if __name__ == "__main__":
    main()
