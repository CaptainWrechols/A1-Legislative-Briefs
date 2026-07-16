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


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def yn(value: bool) -> str:
    return "Yes" if value else "No"


def write_progress_md(rows: list[dict]) -> None:
    lines = [
        "# Nevada water bills — legislative progress (Pass 2)",
        "",
        f"Total bills: **{len(rows)}**",
        "",
        "Each bill shows the yes/no path through committee, floor, crossover, and enactment.",
        "",
    ]
    for i, row in enumerate(rows, start=1):
        m = row.get("milestones") or {}
        lines.extend(
            [
                f"## {i}. {row.get('session')}:{row.get('bill_identifier')}",
                "",
                f"- **Title:** {row.get('title') or '—'}",
                f"- **Origin chamber:** {row.get('origin_chamber_label') or '—'}",
                f"- **Final disposition:** {row.get('final_disposition') or '—'}",
                f"- **Most recent action:** {row.get('most_recent_action') or '—'}",
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


def write_progress_csv(rows: list[dict]) -> None:
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
            out = {
                "session": row.get("session"),
                "bill_identifier": row.get("bill_identifier"),
                "title": row.get("title"),
                "origin_chamber_label": row.get("origin_chamber_label"),
                "final_disposition": row.get("final_disposition"),
                "most_recent_action": row.get("most_recent_action"),
                "nelis_url": row.get("nelis_url"),
            }
            for key in milestone_fields:
                out[key] = yn(bool(m.get(key)))
            writer.writerow(out)
    print(f"Wrote {path}")


def write_votes_md(votes: list[dict]) -> None:
    lines = [
        "# Nevada water bills — vote roll calls (Pass 2)",
        "",
        f"Total vote events: **{len(votes)}**",
        "",
        "Each vote lists counts, then Yea/Nay names with party when matched.",
        "",
    ]
    for i, vote in enumerate(votes, start=1):
        counts = vote.get("counts") or {}
        lines.extend(
            [
                f"## {i}. {vote.get('session')}:{vote.get('bill_identifier')} — {vote.get('motion') or 'Vote'}",
                "",
                f"- **Chamber:** {vote.get('chamber') or '—'}",
                f"- **Date:** {vote.get('date') or '—'}",
                f"- **Result:** {vote.get('result') or '—'}",
                f"- **Counts:** Yea {counts.get('yes') if counts.get('yes') is not None else '—'}; "
                f"Nay {counts.get('no') if counts.get('no') is not None else '—'}; "
                f"Absent {counts.get('absent') if counts.get('absent') is not None else '—'}; "
                f"Excused {counts.get('excused') if counts.get('excused') is not None else '—'}",
                "",
            ]
        )
        by_option: dict[str, list[str]] = {}
        for ballot in vote.get("ballots") or []:
            option = (ballot.get("vote") or "other").title()
            party = ballot.get("party")
            label = ballot.get("name") or "—"
            if party:
                label = f"{label} ({party[0] if party in {'Democratic', 'Republican'} else party})"
            by_option.setdefault(option, []).append(label)
        for option in ("Yea", "Nay", "Not Voting", "Absent", "Excused"):
            names = by_option.get(option) or []
            if not names:
                continue
            lines.append(f"### {option} ({len(names)})")
            lines.append("")
            lines.append(", ".join(names))
            lines.append("")
        lines.append("---")
        lines.append("")
    path = OUT / "votes-readable.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


def write_votes_csv(votes: list[dict]) -> None:
    path = OUT / "votes-readable.csv"
    fields = [
        "session",
        "bill_identifier",
        "chamber",
        "motion",
        "date",
        "result",
        "voter_name",
        "vote",
        "party",
        "party_source",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for vote in votes:
            ballots = vote.get("ballots") or [{}]
            if not vote.get("ballots"):
                writer.writerow(
                    {
                        "session": vote.get("session"),
                        "bill_identifier": vote.get("bill_identifier"),
                        "chamber": vote.get("chamber"),
                        "motion": vote.get("motion"),
                        "date": vote.get("date"),
                        "result": vote.get("result"),
                        "voter_name": "",
                        "vote": "",
                        "party": "",
                        "party_source": "",
                    }
                )
                continue
            for ballot in ballots:
                writer.writerow(
                    {
                        "session": vote.get("session"),
                        "bill_identifier": vote.get("bill_identifier"),
                        "chamber": vote.get("chamber"),
                        "motion": vote.get("motion"),
                        "date": vote.get("date"),
                        "result": vote.get("result"),
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    progress = load(PROGRESS)
    votes = load(VOTES)
    write_progress_md(progress)
    write_progress_csv(progress)
    write_votes_md(votes)
    write_votes_csv(votes)
    write_html(progress, votes)
    print(f"Readable exports in {OUT}/")


if __name__ == "__main__":
    main()
