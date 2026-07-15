#!/usr/bin/env python3
"""Export pass1/bills.json to Markdown, HTML, and CSV for human review."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS1 = ROOT / "sources" / "nevada" / "water-scarcity" / "pass1"
BILLS_JSON = PASS1 / "bills.json"


def load_bills() -> list[dict]:
    data = json.loads(BILLS_JSON.read_text(encoding="utf-8"))
    return list(data.get("bills") or [])


def write_markdown(bills: list[dict]) -> None:
    lines = [
        "# Nevada water bills — Pass 1 review list",
        "",
        f"Total bills: **{len(bills)}**",
        "",
        "Each entry shows the bill number, short title, and full abstract/digest from NELIS.",
        "",
    ]
    for i, bill in enumerate(bills, start=1):
        sid = f"{bill.get('session')}:{bill.get('identifier')}"
        strong = "yes" if bill.get("passes_water_title_filter") else "no"
        sources = []
        if bill.get("in_nelis"):
            sources.append("NELIS")
        if bill.get("in_openstates"):
            sources.append("OpenStates")
        lines.extend(
            [
                f"## {i}. {sid}",
                "",
                f"- **Title:** {bill.get('title') or ''}",
                f"- **Sources:** {', '.join(sources) or '—'}",
                f"- **Strong water-title match:** {strong}",
            ]
        )
        if bill.get("nelis_url"):
            lines.append(f"- **NELIS link:** {bill['nelis_url']}")
        if bill.get("openstates_url"):
            lines.append(f"- **OpenStates link:** {bill['openstates_url']}")
        lines.extend(
            [
                "",
                "### Abstract",
                "",
                (bill.get("abstract") or "").strip() or "_(no abstract)_",
                "",
                "---",
                "",
            ]
        )
    out = PASS1 / "bills-readable.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


def write_html(bills: list[dict]) -> None:
    parts = [
        "<!DOCTYPE html>",
        "<html><head><meta charset=\"utf-8\">",
        "<title>Nevada water bills</title>",
        "<style>",
        "body{font-family:Georgia,serif;max-width:800px;margin:2rem auto;"
        "padding:0 1rem;line-height:1.45}",
        "h1{font-size:1.6rem}",
        "h2{font-size:1.2rem;margin-top:2rem;border-top:1px solid #ccc;padding-top:1rem}",
        ".meta{color:#333;font-size:0.95rem}",
        "a{color:#0645ad}",
        "</style></head><body>",
        "<h1>Nevada water bills — Pass 1 review list</h1>",
        f"<p>Total bills: <strong>{len(bills)}</strong></p>",
    ]
    for i, bill in enumerate(bills, start=1):
        sid = html.escape(f"{bill.get('session')}:{bill.get('identifier')}")
        title = html.escape(bill.get("title") or "")
        strong = "yes" if bill.get("passes_water_title_filter") else "no"
        sources = []
        if bill.get("in_nelis"):
            sources.append("NELIS")
        if bill.get("in_openstates"):
            sources.append("OpenStates")
        abstract = html.escape((bill.get("abstract") or "").strip() or "(no abstract)")
        parts.append(f"<h2>{i}. {sid}</h2>")
        parts.append('<p class="meta">')
        parts.append(f"<strong>Title:</strong> {title}<br>")
        parts.append(f"<strong>Sources:</strong> {html.escape(', '.join(sources) or '—')}<br>")
        parts.append(f"<strong>Strong water-title match:</strong> {strong}<br>")
        if bill.get("nelis_url"):
            url = html.escape(bill["nelis_url"])
            parts.append(f'<strong>NELIS:</strong> <a href="{url}">{url}</a><br>')
        if bill.get("openstates_url"):
            url = html.escape(bill["openstates_url"])
            parts.append(f'<strong>OpenStates:</strong> <a href="{url}">{url}</a><br>')
        parts.append("</p>")
        parts.append(f"<p>{abstract}</p>")
    parts.append("</body></html>")
    out = PASS1 / "bills-readable.html"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out}")


def write_csv(bills: list[dict]) -> None:
    fields = [
        "session",
        "identifier",
        "title",
        "abstract",
        "passes_water_title_filter",
        "in_nelis",
        "in_openstates",
        "nelis_url",
        "openstates_url",
    ]
    out = PASS1 / "bills-readable.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for bill in bills:
            writer.writerow({k: bill.get(k, "") for k in fields})
    print(f"Wrote {out}")


def main() -> None:
    bills = load_bills()
    write_markdown(bills)
    write_html(bills)
    write_csv(bills)


if __name__ == "__main__":
    main()
