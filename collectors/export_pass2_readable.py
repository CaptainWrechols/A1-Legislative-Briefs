#!/usr/bin/env python3
"""Export Pass 2 progress + votes to Markdown / HTML / CSV for human review.

  python collectors/export_pass2_readable.py
"""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

PROCESSED = Path("sources/nevada/water-scarcity/processed")
OUT = PROCESSED / "readable"

PROGRESS = PROCESSED / "bill-legislative-progress.json"
VOTES = PROCESSED / "bill-votes.json"
CORE = PROCESSED / "bills-core.json"
TEXT_CHANGES = PROCESSED / "bill-text-changes.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def load_obj(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def yn(value: bool) -> str:
    return "Yes" if value else "No"


def write_progress_md(rows: list[dict], abstracts: dict[str, str] | None = None) -> None:
    abstracts = abstracts or {}
    lines = [
        "# Nevada water bills — legislative progress (Pass 2)",
        "",
        f"Total bills: **{len(rows)}**",
        "",
        "Each bill shows **what it does** (NELIS digest), then the yes/no path through "
        "committee, floor, crossover, and enactment.",
        "",
    ]
    for i, row in enumerate(rows, start=1):
        m = row.get("milestones") or {}
        key = f"{row.get('session')}:{row.get('bill_identifier')}"
        abstract = abstracts.get(key) or row.get("abstract") or row.get("what_the_bill_does") or ""
        lines.extend(
            [
                f"## {i}. {row.get('session')}:{row.get('bill_identifier')}",
                "",
                f"- **Title:** {row.get('title') or '—'}",
                f"- **Origin chamber:** {row.get('origin_chamber_label') or '—'}",
                f"- **Final disposition:** {row.get('final_disposition') or '—'}",
                f"- **Most recent action:** {row.get('most_recent_action') or '—'}",
                "",
                "### What the bill does",
                "",
                abstract.strip() or "_(no abstract)_",
                "",
                "| Milestone | Result |",
                "|---|---|",
                f"| Seen in committee (origin) | {yn(m.get('seen_in_committee_origin'))} |",
                f"| Passed out of committee (origin) | {yn(m.get('passed_out_of_committee_origin'))} |",
                f"| Floor vote (origin) | {yn(m.get('floor_vote_origin_chamber'))} |",
                f"| Passed origin chamber | {yn(m.get('passed_origin_chamber'))} |",
                f"| Crossed over | {yn(m.get('crossed_over'))} |",
                f"| Seen in committee (other chamber) | {yn(m.get('seen_in_committee_second_chamber'))} |",
                f"| Passed out of committee (other chamber) | {yn(m.get('passed_out_of_committee_second_chamber'))} |",
                f"| Floor vote (other chamber) | {yn(m.get('floor_vote_second_chamber'))} |",
                f"| Passed other chamber | {yn(m.get('passed_second_chamber'))} |",
                f"| Signed into law | {yn(m.get('signed_into_law'))} |",
                f"| Vetoed | {yn(m.get('vetoed'))} |",
                f"| Failed | {yn(m.get('failed'))} |",
                "",
            ]
        )
        if row.get("nelis_url"):
            lines.append(f"[NELIS page]({row['nelis_url']})")
            lines.append("")
        lines.append("---")
        lines.append("")
    path = OUT / "progress-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def write_progress_csv(
    rows: list[dict], abstracts: dict[str, str] | None = None
) -> None:
    abstracts = abstracts or {}
    milestone_fields = [
        "seen_in_committee_origin",
        "passed_out_of_committee_origin",
        "floor_vote_origin_chamber",
        "passed_origin_chamber",
        "crossed_over",
        "seen_in_committee_second_chamber",
        "passed_out_of_committee_second_chamber",
        "floor_vote_second_chamber",
        "passed_second_chamber",
        "signed_into_law",
        "vetoed",
        "failed",
    ]
    fields = [
        "session",
        "bill_identifier",
        "title",
        "abstract",
        "origin_chamber_label",
        "final_disposition",
        "most_recent_action",
        *milestone_fields,
        "nelis_url",
    ]
    path = OUT / "progress-readable.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            m = row.get("milestones") or {}
            key = f"{row.get('session')}:{row.get('bill_identifier')}"
            out = {
                "session": row.get("session"),
                "bill_identifier": row.get("bill_identifier"),
                "title": row.get("title"),
                "abstract": abstracts.get(key)
                or row.get("abstract")
                or row.get("what_the_bill_does")
                or "",
                "origin_chamber_label": row.get("origin_chamber_label"),
                "final_disposition": row.get("final_disposition"),
                "most_recent_action": row.get("most_recent_action"),
                "nelis_url": row.get("nelis_url"),
            }
            for field in milestone_fields:
                out[field] = yn(bool(m.get(field)))
            writer.writerow(out)
    print(f"Wrote {path}")


def write_votes_md(votes: list[dict]) -> None:
    floor = [v for v in votes if v.get("vote_kind", "floor_final_passage") == "floor_final_passage"]
    committee = [
        v
        for v in votes
        if v.get("vote_kind") in {"committee_work_session", "committee_hearing"}
        or v.get("source") in {"nelis_committee_minutes", "nelis_meetings"}
    ]
    lines = [
        "# Nevada water bills — vote roll calls (Pass 2)",
        "",
        f"Floor Final Passage events: **{len(floor)}**",
        f"Committee hearing / work-session events: **{len(committee)}**",
        "",
        "Floor votes come from the NELIS Votes tab (full Yea/Nay rolls).",
        "Committee votes come from committee **minutes PDFs** (NO/ABSENT by name) plus "
        "inferred **Yea** votes = that committee’s session membership minus Nay/Absent.",
        "",
        "## Floor votes (Final Passage)",
        "",
    ]

    def append_vote(vote: dict, index: int) -> None:
        counts = vote.get("counts") or {}
        kind = vote.get("vote_kind") or "floor_final_passage"
        lines.extend(
            [
                f"### {index}. {vote.get('session')}:{vote.get('bill_identifier')} — "
                f"{vote.get('motion') or vote.get('recommendation') or 'Vote'}",
                "",
                f"- **Kind:** {kind}",
                f"- **Chamber / committee:** {vote.get('chamber') or vote.get('committee') or '—'}",
                f"- **Date:** {vote.get('date') or '—'}",
                f"- **Result:** {vote.get('result') or '—'}",
                f"- **Counts:** Yea {counts.get('yes') if counts.get('yes') is not None else '—'}; "
                f"Nay {counts.get('no') if counts.get('no') is not None else '—'}; "
                f"Absent {counts.get('absent') if counts.get('absent') is not None else '—'}; "
                f"Excused {counts.get('excused') if counts.get('excused') is not None else '—'}",
                "",
            ]
        )
        if vote.get("minutes_url"):
            lines.append(f"- **Minutes:** {vote['minutes_url']}")
            lines.append("")
        if vote.get("note"):
            lines.append(f"_{vote['note']}_")
            lines.append("")
        if vote.get("yea_inference_note"):
            lines.append(f"_{vote['yea_inference_note']}_")
            lines.append("")
        by_option: dict[str, list[str]] = {}
        for ballot in vote.get("ballots") or []:
            option = (ballot.get("vote") or "other").title()
            party = ballot.get("party")
            label = ballot.get("name") or "—"
            if party:
                label = f"{label} ({party[0] if party in {'Democratic', 'Republican'} else party})"
            if ballot.get("inferred") and option == "Yea":
                label = f"{label}*"
            by_option.setdefault(option, []).append(label)
        for option in ("Yea", "Nay", "Not Voting", "Absent", "Excused"):
            names = by_option.get(option) or []
            if not names:
                continue
            lines.append(f"#### {option} ({len(names)})")
            lines.append("")
            lines.append(", ".join(names))
            lines.append("")
        if vote.get("excerpt") and not vote.get("ballots"):
            lines.append("#### Minutes excerpt")
            lines.append("")
            lines.append(vote["excerpt"])
            lines.append("")
        lines.append("---")
        lines.append("")

    for i, vote in enumerate(floor, start=1):
        append_vote(vote, i)
    lines.append("## Committee votes / hearings")
    lines.append("")
    if not committee:
        lines.append("No committee vote/hearing rows were collected.")
        lines.append("")
    for i, vote in enumerate(committee, start=1):
        append_vote(vote, i)

    path = OUT / "votes-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def write_votes_csv(votes: list[dict]) -> None:
    path = OUT / "votes-readable.csv"
    fields = [
        "session",
        "bill_identifier",
        "vote_kind",
        "chamber_or_committee",
        "motion",
        "date",
        "result",
        "voter_name",
        "vote",
        "party",
        "party_source",
        "minutes_url",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for vote in votes:
            chamber = vote.get("chamber") or vote.get("committee") or ""
            base = {
                "session": vote.get("session"),
                "bill_identifier": vote.get("bill_identifier"),
                "vote_kind": vote.get("vote_kind") or "floor_final_passage",
                "chamber_or_committee": chamber,
                "motion": vote.get("motion") or vote.get("recommendation"),
                "date": vote.get("date"),
                "result": vote.get("result"),
                "minutes_url": vote.get("minutes_url") or "",
            }
            if not vote.get("ballots"):
                writer.writerow({**base, "voter_name": "", "vote": "", "party": "", "party_source": ""})
                continue
            for ballot in vote.get("ballots") or []:
                writer.writerow(
                    {
                        **base,
                        "voter_name": ballot.get("name"),
                        "vote": ballot.get("vote"),
                        "party": ballot.get("party"),
                        "party_source": ballot.get("party_source"),
                    }
                )
    print(f"Wrote {path}")


def write_html(progress: list[dict], votes: list[dict]) -> None:
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>Nevada water bills — Pass 2</title>",
        "<style>",
        "body{font-family:Georgia,serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.45}",
        "h1{font-size:1.7rem} h2{font-size:1.25rem;margin-top:2rem;border-top:1px solid #ccc;padding-top:1rem}",
        "table{border-collapse:collapse;width:100%;margin:0.75rem 0} td,th{border:1px solid #ddd;padding:0.35rem 0.5rem;text-align:left}",
        "th{background:#f4f4f4}.yes{color:#0a5}.no{color:#555}.meta{color:#333}",
        "nav a{margin-right:1rem}",
        "</style></head><body>",
        "<h1>Nevada water bills — Pass 2 review</h1>",
        "<nav><a href='#progress'>Progress</a><a href='#votes'>Votes</a></nav>",
        f"<p class='meta'>{len(progress)} bills · {len(votes)} vote events</p>",
        "<h2 id='progress'>Legislative progress</h2>",
    ]
    for i, row in enumerate(progress, start=1):
        m = row.get("milestones") or {}
        parts.append(f"<h3>{i}. {html.escape(str(row.get('session')))}:{html.escape(str(row.get('bill_identifier')))}</h3>")
        parts.append(f"<p class='meta'><strong>Title:</strong> {html.escape(row.get('title') or '—')}<br>")
        parts.append(f"<strong>Disposition:</strong> {html.escape(row.get('final_disposition') or '—')}<br>")
        parts.append(f"<strong>Latest:</strong> {html.escape(row.get('most_recent_action') or '—')}</p>")
        parts.append("<table><tr><th>Milestone</th><th>Result</th></tr>")
        for label, key in [
            ("Seen in committee (origin)", "seen_in_committee_origin"),
            ("Passed out of committee (origin)", "passed_out_of_committee_origin"),
            ("Floor vote (origin)", "floor_vote_origin_chamber"),
            ("Passed origin chamber", "passed_origin_chamber"),
            ("Crossed over", "crossed_over"),
            ("Seen in committee (other chamber)", "seen_in_committee_second_chamber"),
            ("Passed out of committee (other chamber)", "passed_out_of_committee_second_chamber"),
            ("Floor vote (other chamber)", "floor_vote_second_chamber"),
            ("Passed other chamber", "passed_second_chamber"),
            ("Signed into law", "signed_into_law"),
        ]:
            val = yn(bool(m.get(key)))
            cls = "yes" if val == "Yes" else "no"
            parts.append(f"<tr><td>{label}</td><td class='{cls}'>{val}</td></tr>")
        parts.append("</table>")

    parts.append("<h2 id='votes'>Vote roll calls</h2>")
    for i, vote in enumerate(votes, start=1):
        counts = vote.get("counts") or {}
        parts.append(
            f"<h3>{i}. {html.escape(str(vote.get('session')))}:{html.escape(str(vote.get('bill_identifier')))} — "
            f"{html.escape(vote.get('motion') or 'Vote')}</h3>"
        )
        parts.append(
            f"<p class='meta'><strong>Chamber:</strong> {html.escape(vote.get('chamber') or '—')} · "
            f"<strong>Yea/Nay:</strong> {counts.get('yes')}/{counts.get('no')}</p>"
        )
        by_option: dict[str, list[str]] = {}
        for ballot in vote.get("ballots") or []:
            option = (ballot.get("vote") or "other").title()
            label = ballot.get("name") or "—"
            if ballot.get("party"):
                party = ballot["party"]
                short = party[0] if party in {"Democratic", "Republican"} else party
                label = f"{label} ({short})"
            by_option.setdefault(option, []).append(html.escape(label))
        for option in ("Yea", "Nay"):
            names = by_option.get(option) or []
            if names:
                parts.append(f"<p><strong>{option} ({len(names)}):</strong> {', '.join(names)}</p>")

    parts.append("</body></html>")
    path = OUT / "pass2-readable.html"
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {path}")


def write_core_md(core_bills: list[dict]) -> None:
    lines = [
        "# Nevada water bills — core review set (Pass 2)",
        "",
        f"Total bills: **{len(core_bills)}**",
        "",
        "Each bill includes the **full abstract** (what the bill does), legislative milestones, "
        "and — for Governor-bound bills — an introduced vs enrolled change summary.",
        "",
    ]
    for i, bill in enumerate(core_bills, start=1):
        m = bill.get("milestones") or {}
        lines.extend(
            [
                f"## {i}. {bill.get('session')}:{bill.get('identifier')}",
                "",
                f"- **Title:** {bill.get('title') or '—'}",
                f"- **Disposition:** {bill.get('final_disposition') or '—'}",
                f"- **Latest action:** {bill.get('most_recent_action') or '—'}",
                "",
                "### Sponsors",
                "",
            ]
        )
        primaries = bill.get("primary_sponsors") or [
            s for s in (bill.get("sponsors") or []) if s.get("classification") == "primary"
        ]
        cos = bill.get("co_sponsors") or [
            s for s in (bill.get("sponsors") or []) if s.get("classification") == "cosponsor"
        ]
        if primaries:
            lines.append(
                "- **Primary:** "
                + "; ".join(
                    f"{s.get('name')}" + (f" ({s['party']})" if s.get("party") else "")
                    for s in primaries
                )
            )
        else:
            lines.append("- **Primary:** —")
        if cos:
            lines.append(
                "- **Co-sponsors:** "
                + "; ".join(
                    f"{s.get('name')}" + (f" ({s['party']})" if s.get("party") else "")
                    for s in cos
                )
            )
        else:
            lines.append("- **Co-sponsors:** —")
        lines.extend(
            [
                "",
                "### What the bill does (NELIS digest)",
                "",
                (bill.get("abstract") or bill.get("what_the_bill_does") or "_(no abstract)_").strip(),
                "",
                "### Path through the legislature",
                "",
                f"- Seen in committee (origin): {yn(bool(m.get('seen_in_committee_origin')))}",
                f"- Passed out of committee (origin): {yn(bool(m.get('passed_out_of_committee_origin')))}",
                f"- Floor vote / passed origin chamber: {yn(bool(m.get('floor_vote_origin_chamber')))} / {yn(bool(m.get('passed_origin_chamber')))}",
                f"- Crossed over: {yn(bool(m.get('crossed_over')))}",
                f"- Other chamber committee / floor / passed: "
                f"{yn(bool(m.get('seen_in_committee_second_chamber')))} / "
                f"{yn(bool(m.get('floor_vote_second_chamber')))} / "
                f"{yn(bool(m.get('passed_second_chamber')))}",
                f"- Signed into law: {yn(bool(m.get('signed_into_law')))}",
                "",
            ]
        )
        text = bill.get("text_changes")
        if text and text.get("status") == "ok":
            lines.extend(
                [
                    "### Introduced vs enrolled (Governor-bound)",
                    "",
                    f"- **Textually amended:** {yn(bool(text.get('was_textually_amended')))}",
                    f"- **Similarity:** {text.get('similarity_ratio')}",
                    f"- **Amendments listed on NELIS:** {', '.join(text.get('amendments_listed') or []) or '—'}",
                    f"- **Summary:** {text.get('narrative') or '—'}",
                    "",
                ]
            )
            if text.get("enrolled_legislative_counsel_digest"):
                lines.extend(
                    [
                        "**Legislative Counsel’s Digest (as enrolled):**",
                        "",
                        text["enrolled_legislative_counsel_digest"],
                        "",
                    ]
                )
            elif text.get("enrolled_act_clause"):
                lines.extend(
                    [
                        "**Enrolled act clause:**",
                        "",
                        text["enrolled_act_clause"],
                        "",
                    ]
                )
        elif bill.get("governor_bound"):
            lines.append("_Governor-bound, but introduced/enrolled comparison not available._")
            lines.append("")
        if bill.get("nelis_url"):
            lines.append(f"[NELIS page]({bill['nelis_url']})")
            lines.append("")
        lines.append("---")
        lines.append("")
    path = OUT / "bills-core-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def _format_sponsor_list(sponsors: list[dict]) -> str:
    return "; ".join(
        f"{s.get('name')}" + (f" ({s['party']})" if s.get("party") else "")
        for s in sponsors
    )


def write_core_csv(core_bills: list[dict]) -> None:
    fields = [
        "session",
        "identifier",
        "title",
        "primary_sponsors",
        "co_sponsors",
        "abstract",
        "final_disposition",
        "most_recent_action",
        "signed_into_law",
        "governor_bound",
        "was_textually_amended",
        "similarity_ratio",
        "text_change_narrative",
        "amendments_listed",
        "nelis_url",
    ]
    path = OUT / "bills-core-readable.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for bill in core_bills:
            text = bill.get("text_changes") or {}
            m = bill.get("milestones") or {}
            primaries = bill.get("primary_sponsors") or [
                s
                for s in (bill.get("sponsors") or [])
                if s.get("classification") == "primary"
            ]
            cos = bill.get("co_sponsors") or [
                s
                for s in (bill.get("sponsors") or [])
                if s.get("classification") == "cosponsor"
            ]
            writer.writerow(
                {
                    "session": bill.get("session"),
                    "identifier": bill.get("identifier"),
                    "title": bill.get("title"),
                    "primary_sponsors": _format_sponsor_list(primaries),
                    "co_sponsors": _format_sponsor_list(cos),
                    "abstract": bill.get("abstract"),
                    "final_disposition": bill.get("final_disposition"),
                    "most_recent_action": bill.get("most_recent_action"),
                    "signed_into_law": yn(bool(m.get("signed_into_law"))),
                    "governor_bound": yn(bool(bill.get("governor_bound"))),
                    "was_textually_amended": (
                        yn(bool(text.get("was_textually_amended"))) if text else ""
                    ),
                    "similarity_ratio": text.get("similarity_ratio", ""),
                    "text_change_narrative": text.get("narrative", ""),
                    "amendments_listed": "; ".join(text.get("amendments_listed") or []),
                    "nelis_url": bill.get("nelis_url"),
                }
            )
    print(f"Wrote {path}")


def write_text_changes_md(text_payload: dict) -> None:
    bills = text_payload.get("bills") or []
    lines = [
        "# Nevada water bills — introduced vs enrolled changes",
        "",
        "Only bills that were enrolled / delivered to the Governor (or signed).",
        "",
        f"Total compared: **{len(bills)}**",
        "",
    ]
    for i, bill in enumerate(bills, start=1):
        lines.extend(
            [
                f"## {i}. {bill.get('session')}:{bill.get('bill_identifier')}",
                "",
                f"- **Title:** {bill.get('title') or '—'}",
                f"- **Status:** {bill.get('status')}",
                f"- **Textually amended:** {yn(bool(bill.get('was_textually_amended')))}",
                f"- **Similarity:** {bill.get('similarity_ratio')}",
                f"- **Amendments:** {', '.join(bill.get('amendments_listed') or []) or '—'}",
                "",
                bill.get("narrative") or "",
                "",
            ]
        )
        if bill.get("enrolled_legislative_counsel_digest"):
            lines.extend(
                [
                    "### Legislative Counsel’s Digest (enrolled)",
                    "",
                    bill["enrolled_legislative_counsel_digest"],
                    "",
                ]
            )
        if bill.get("introduced_summary"):
            lines.extend(
                [
                    "### Introduced SUMMARY line",
                    "",
                    bill["introduced_summary"],
                    "",
                ]
            )
        if bill.get("introduced"):
            lines.append(f"- Introduced PDF: {bill['introduced'].get('url')}")
        if bill.get("enrolled"):
            lines.append(f"- Enrolled PDF: {bill['enrolled'].get('url')}")
        lines.append("")
        lines.append("---")
        lines.append("")
    path = OUT / "text-changes-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def write_core_html(core_bills: list[dict]) -> None:
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>Nevada water bills — core Pass 2</title>",
        "<style>",
        "body{font-family:Georgia,serif;max-width:900px;margin:2rem auto;padding:0 1rem;line-height:1.45}",
        "h1{font-size:1.7rem} h2{font-size:1.25rem;margin-top:2rem;border-top:1px solid #ccc;padding-top:1rem}",
        ".meta{color:#333}.abstract{margin:0.75rem 0;white-space:pre-wrap}",
        ".yes{color:#0a5}.no{color:#555}",
        "</style></head><body>",
        "<h1>Nevada water bills — core review set</h1>",
        f"<p class='meta'>{len(core_bills)} bills with abstracts, progress, and Governor-bound text diffs</p>",
    ]
    for i, bill in enumerate(core_bills, start=1):
        m = bill.get("milestones") or {}
        parts.append(
            f"<h2>{i}. {html.escape(str(bill.get('session')))}:{html.escape(str(bill.get('identifier')))}</h2>"
        )
        parts.append(
            f"<p class='meta'><strong>Title:</strong> {html.escape(bill.get('title') or '—')}<br>"
            f"<strong>Disposition:</strong> {html.escape(bill.get('final_disposition') or '—')}<br>"
            f"<strong>Signed into law:</strong> "
            f"<span class='{'yes' if m.get('signed_into_law') else 'no'}'>"
            f"{yn(bool(m.get('signed_into_law')))}</span></p>"
        )
        primaries = bill.get("primary_sponsors") or [
            s for s in (bill.get("sponsors") or []) if s.get("classification") == "primary"
        ]
        cos = bill.get("co_sponsors") or [
            s for s in (bill.get("sponsors") or []) if s.get("classification") == "cosponsor"
        ]
        parts.append("<h3>Sponsors</h3>")
        parts.append(
            "<p class='meta'><strong>Primary:</strong> "
            f"{html.escape(_format_sponsor_list(primaries) or '—')}<br>"
            "<strong>Co-sponsors:</strong> "
            f"{html.escape(_format_sponsor_list(cos) or '—')}</p>"
        )
        parts.append("<h3>What the bill does</h3>")
        parts.append(
            f"<p class='abstract'>{html.escape((bill.get('abstract') or '—').strip())}</p>"
        )
        text = bill.get("text_changes")
        if text and text.get("status") == "ok":
            parts.append("<h3>Introduced vs enrolled</h3>")
            parts.append(
                f"<p class='meta'>{html.escape(text.get('narrative') or '')}<br>"
                f"Amended: {yn(bool(text.get('was_textually_amended')))} · "
                f"Similarity: {text.get('similarity_ratio')}</p>"
            )
            digest = text.get("enrolled_legislative_counsel_digest") or text.get(
                "enrolled_act_clause"
            )
            if digest:
                parts.append(f"<p class='abstract'>{html.escape(digest)}</p>")
    parts.append("</body></html>")
    path = OUT / "bills-core-readable.html"
    path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {path}")


def write_sponsors_md(sponsors: list[dict], core_bills: list[dict]) -> None:
    by_bill: dict[str, list[dict]] = {}
    for row in sponsors:
        key = f"{row.get('session')}:{row.get('bill_identifier')}"
        by_bill.setdefault(key, []).append(row)
    title_by_key = {
        f"{b.get('session')}:{b.get('identifier')}": b.get("title") or ""
        for b in core_bills
    }
    lines = [
        "# Nevada water bills — sponsors and co-sponsors",
        "",
        f"Bills with sponsor rows: **{len(by_bill)}**",
        "",
    ]
    for i, key in enumerate(sorted(by_bill), start=1):
        rows = by_bill[key]
        primaries = [r for r in rows if r.get("classification") == "primary"]
        cos = [r for r in rows if r.get("classification") == "cosponsor"]
        lines.extend(
            [
                f"## {i}. {key}",
                "",
                f"- **Title:** {title_by_key.get(key) or '—'}",
                "",
                "### Primary sponsors",
                "",
            ]
        )
        if primaries:
            for r in primaries:
                party = f" ({r['party']})" if r.get("party") else ""
                lines.append(f"- {r.get('name')}{party}")
        else:
            lines.append("- —")
        lines.extend(["", "### Co-sponsors", ""])
        if cos:
            for r in cos:
                party = f" ({r['party']})" if r.get("party") else ""
                lines.append(f"- {r.get('name')}{party}")
        else:
            lines.append("- —")
        lines.extend(["", "---", ""])
    path = OUT / "sponsors-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def write_sponsors_csv(sponsors: list[dict]) -> None:
    path = OUT / "sponsors-readable.csv"
    fields = [
        "session",
        "bill_identifier",
        "classification",
        "name",
        "party",
        "entity_type",
        "source_url",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in sponsors:
            writer.writerow({k: row.get(k, "") for k in fields})
    print(f"Wrote {path}")


def write_readme() -> None:
    text = """# Pass 2 readable exports

These files are the human-friendly view of the Nevada water bill dataset.

## Start here

1. `bills-core-readable.html` — open in a browser (Print → Save as PDF)
2. `bills-core-readable.md` — open in Word / Notes
3. `progress-readable.md` — milestones **plus full abstracts**
4. `sponsors-readable.md` / `.csv` — primary sponsors and co-sponsors
5. `votes-readable.md` — floor Final Passage rolls **and** committee work-session votes
6. `text-changes-readable.md` — introduced vs enrolled (Governor-bound only)

## Machine JSON (same folder’s parent)

- `../bills-core.json` — title + abstract + sponsors + progress + text changes
- `../bill-sponsors.json` — primary / co-sponsor rows
- `../bill-votes.json` — floor + committee vote events
- `../bill-committee-votes.json` — committee-only extract
- `../bill-text-changes.json` — introduced vs enrolled summaries

## GitHub path

`sources/nevada/water-scarcity/processed/readable/` on branch `main`
"""
    path = OUT / "README.md"
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    progress = load(PROGRESS)
    votes = load(VOTES)
    core_payload = load_obj(CORE)
    core_bills = core_payload.get("bills") or []
    abstracts = {
        f"{b.get('session')}:{b.get('identifier')}": b.get("abstract") or ""
        for b in core_bills
    }
    # Fallback to pass1 bills.json if core missing
    if not abstracts:
        pass1 = load_obj(Path("sources/nevada/water-scarcity/pass1/bills.json"))
        abstracts = {
            f"{b.get('session')}:{b.get('identifier')}": b.get("abstract") or ""
            for b in (pass1.get("bills") or [])
        }

    write_progress_md(progress, abstracts)
    write_progress_csv(progress, abstracts)
    write_votes_md(votes)
    write_votes_csv(votes)
    write_html(progress, votes)

    if core_bills:
        write_core_md(core_bills)
        write_core_csv(core_bills)
        write_core_html(core_bills)

    sponsors = load(PROCESSED / "bill-sponsors.json")
    if sponsors:
        write_sponsors_md(sponsors, core_bills)
        write_sponsors_csv(sponsors)

    text_payload = load_obj(TEXT_CHANGES)
    if text_payload.get("bills"):
        write_text_changes_md(text_payload)

    write_readme()
    print(f"Readable exports in {OUT}/")


if __name__ == "__main__":
    main()
