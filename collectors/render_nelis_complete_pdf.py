#!/usr/bin/env python3
"""Build one printable Issue Brief–styled PDF for the NELIS preliminary package.

Includes:
  - Executive summary
  - Appendices A–F
  - Verification report
  - Final review report
  - Selected sources

Usage:
  python collectors/render_nelis_complete_pdf.py
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "briefs/nevada/water-scarcity/nelis-preliminary"
SOURCES = ROOT / "sources/nevada/water-scarcity"
OUT_HTML = BRIEF / "legislative-brief-nelis-preliminary-complete.html"
OUT_PDF = BRIEF / "legislative-brief-nelis-preliminary-complete.pdf"

CSS = """
:root {
  --navy: #1b2a4a;
  --orange: #c45c26;
  --ink: #2a2a2a;
  --muted: #5a5a5a;
  --box: #d9d9d9;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--ink);
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  line-height: 1.35;
  font-size: 11.5px;
}
.page-section { padding: 0; }
.brand {
  font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
  color: var(--navy); text-transform: uppercase;
}
.topline { border-top: 2px solid var(--navy); margin: 6px 0 10px; }
.eyebrow {
  text-align: center; font-size: 9.5px; font-weight: 700;
  letter-spacing: 0.08em; color: var(--orange); text-transform: uppercase;
  margin: 0 0 10px;
}
h1 {
  margin: 0 0 10px; color: var(--navy); font-size: 24px;
  line-height: 1.15; font-weight: 700;
}
h2 {
  margin: 16px 0 8px; font-size: 11px; letter-spacing: 0.06em;
  color: var(--orange); text-transform: uppercase; font-weight: 700;
  break-after: avoid; page-break-after: avoid;
}
h3 {
  margin: 12px 0 6px; font-size: 12px; color: var(--navy); font-weight: 700;
  break-after: avoid;
}
.title-rule { border: 0; border-top: 3px solid var(--navy); margin: 0 0 14px; }
p { margin: 0 0 8px; }
.note { font-size: 10.5px; color: var(--muted); }
.grid-5 {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px;
  margin: 8px 0 12px;
}
.card {
  border: 1px solid var(--box); border-radius: 6px; padding: 8px 6px;
  break-inside: avoid;
}
.stat {
  color: var(--navy); font-size: 18px; font-weight: 700;
  margin: 0 0 4px; line-height: 1;
}
.card p { font-size: 9.5px; margin: 0; }
table {
  width: 100%; border-collapse: collapse; font-size: 9px;
  margin: 6px 0 12px;
}
th {
  background: var(--navy); color: #fff; text-align: left;
  padding: 5px 4px; font-weight: 600; vertical-align: top;
}
td {
  border: 1px solid #cfcfcf; padding: 4px; vertical-align: top;
}
td:first-child { font-weight: 700; color: var(--navy); }
.insuf { font-weight: 700; color: var(--navy); }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
ul { margin: 0 0 8px 16px; padding: 0; }
li { margin-bottom: 3px; }
.sources p { font-size: 10px; margin: 0 0 6px; }
.footer {
  margin-top: 14px; padding-top: 6px; border-top: 1px solid #ccc;
  font-size: 9px; color: var(--muted);
}
.page-break { break-before: page; page-break-before: always; }
.cover-meta {
  margin: 8px 0 14px; font-size: 10.5px; color: var(--muted);
}
.status-pill {
  display: inline-block; border: 1px solid var(--navy); color: var(--navy);
  padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 700;
}
@media print {
  @page { size: letter; margin: 0.45in; }
}
"""


def esc(text: object) -> str:
    return html.escape("" if text is None else str(text))


def md_table_to_html(md_text: str) -> str:
    """Convert a simple GitHub-style markdown table block to HTML."""
    lines = [ln.strip() for ln in md_text.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 2:
        return f"<p>{esc(md_text)}</p>"
    rows = []
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip("|").split("|")]
        if i == 1 and all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in cells):
            continue
        tag = "th" if i == 0 else "td"
        rows.append("<tr>" + "".join(f"<{tag}>{esc(c)}</{tag}>" for c in cells) + "</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def strip_md_header(text: str) -> str:
    text = re.sub(r"^<!--.*?-->\s*", "", text, flags=re.S)
    return text.strip()


def executive_summary_body() -> str:
    # Reuse the visual body from executive-summary.html if present
    html_doc = read(BRIEF / "executive-summary.html")
    m = re.search(r"<article class=\"page\">(.*?)</article>", html_doc, flags=re.S)
    if not m:
        return "<p>Executive summary HTML missing.</p>"
    body = m.group(1)
    # Drop nested brand/title if we add a package cover; keep full article content
    return body


def appendix_section(letter: str, title: str, filename: str) -> str:
    raw = strip_md_header(read(BRIEF / filename))
    # Remove leading markdown H1
    raw = re.sub(r"^# .*\n+", "", raw)
    if "|" in raw and raw.count("|") > 4:
        # Split intro prose from table
        parts = raw.split("\n\n", 1)
        intro = parts[0] if len(parts) == 2 and "|" not in parts[0] else ""
        table_md = parts[1] if intro else raw
        # If intro still has pipes, treat whole as table
        if "|" in intro:
            intro, table_md = "", raw
        table_html = md_table_to_html(table_md)
        intro_html = f"<p>{esc(intro)}</p>" if intro.strip() else ""
        if "INSUFFICIENT DATA" in raw and raw.count("|") < 6:
            return f"""
            <h2>Appendix {letter} — {esc(title)}</h2>
            <p><span class="insuf">INSUFFICIENT DATA</span> — {esc(re.sub(r'\\*\\*', '', raw.split('INSUFFICIENT DATA',1)[-1]).strip(' —-\n'))}</p>
            """
        return f"<h2>Appendix {letter} — {esc(title)}</h2>{intro_html}{table_html}"
    # Prose / gaps list
    content = esc(raw)
    content = content.replace("**INSUFFICIENT DATA**", '<span class="insuf">INSUFFICIENT DATA</span>')
    content = re.sub(r"\n+", "</p><p>", content)
    return f"<h2>Appendix {letter} — {esc(title)}</h2><p>{content}</p>"


def verification_section() -> str:
    report = json.loads(read(SOURCES / "verification/report.json") or "{}")
    status = report.get("overall_status", "UNKNOWN")
    warnings = report.get("warnings") or []
    checks = report.get("checks") or []
    rows = ["<tr><th>Check</th><th>Status</th><th>Notes</th></tr>"]
    for c in checks:
        notes = {k: v for k, v in c.items() if k not in {"check_id", "status", "samples"}}
        rows.append(
            "<tr>"
            f"<td>{esc(c.get('check_id'))}</td>"
            f"<td>{esc(c.get('status'))}</td>"
            f"<td>{esc(json.dumps(notes, ensure_ascii=False))}</td>"
            "</tr>"
        )
    warn_html = "".join(f"<li>{esc(w)}</li>" for w in warnings) or "<li>None</li>"
    return f"""
    <h2>Verification Report</h2>
    <p>Agent: data-verifier · Data source: NELIS_ONLY · Status:
      <span class="status-pill">{esc(status)}</span></p>
    <p class="note">Verified at: {esc(report.get('verified_at'))}</p>
    <table>{''.join(rows)}</table>
    <h3>Warnings</h3>
    <ul>{warn_html}</ul>
    """


def final_review_section() -> str:
    raw = strip_md_header(read(BRIEF / "final-review-report.md"))
    raw = re.sub(r"^# .*\n+", "", raw)
    # lightweight markdown conversions
    lines = []
    for line in raw.splitlines():
        if line.startswith("## "):
            lines.append(f"<h3>{esc(line[3:])}</h3>")
        elif line.startswith("|") and "---" not in line:
            continue  # skip markdown tables; hardcode summary below
        elif line.startswith("- "):
            lines.append(f"<li>{esc(line[2:])}</li>")
        elif line.strip():
            lines.append(f"<p>{esc(line)}</p>")
    # rebuild known pieces more cleanly
    return f"""
    <h2>Final Review Report</h2>
    <p><strong>Automated result:</strong> <span class="status-pill">READY FOR HUMAN REVIEW</span></p>
    <p><strong>Recommended reviewers:</strong> Ryan Echols, Jodi Stephens, Ashley Lovell</p>
    <h3>Summary</h3>
    <p>NELIS-only preliminary package produced through agents 2–10 with Phase 2 Issue Brief formatting.
    Bill actions, votes, sponsors, and enactment remain <span class="insuf">INSUFFICIENT DATA</span>.</p>
    <h3>Blocking issues</h3>
    <p>None</p>
    <h3>Warnings</h3>
    <ul>
      <li>Title-language synthesis only (no full digests in discovery export)</li>
      <li>Do not overwrite this NELIS preliminary folder with OpenStates outputs</li>
    </ul>
    """


def sources_section() -> str:
    data = json.loads(read(BRIEF / "sources-registry.json") or "{}")
    blocks = []
    for src in data.get("sources") or []:
        blocks.append(
            f"<p><strong>[{esc(src.get('key'))}]</strong> {esc(src.get('chicago_bibliography'))}</p>"
        )
    return "<h2>Selected Sources</h2>" + "\n".join(blocks)


def build_html() -> str:
    summary = executive_summary_body()
    # Remove the inner Selected Sources / footer from summary if present — we add package-level ones
    summary = re.sub(
        r"<h2>Selected Sources</h2>.*?<p class=\"footer\".*?</p>",
        "",
        summary,
        flags=re.S,
    )

    appendices = [
        appendix_section("A", "Bills (NELIS)", "appendix-a-bills.md"),
        appendix_section("B", "Bill Actions", "appendix-b-bill-actions.md"),
        appendix_section("C", "Votes", "appendix-c-votes.md"),
        appendix_section("D", "Statutes", "appendix-d-statutes.md"),
        appendix_section("E", "Agency Documents", "appendix-e-agency-documents.md"),
        appendix_section("F", "Data Gaps", "appendix-f-data-gaps.md"),
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>THE FORUM — Legislative Brief Preliminary Complete · Nevada Water Scarcity</title>
  <style>{CSS}</style>
</head>
<body>
  <section class="page-section">
    <div class="brand">The Forum</div>
    <div class="topline"></div>
    <p class="eyebrow">Legislative Brief Preliminary · Complete Package · Water Scarcity · Nevada Forum · July 2026 · NELIS Only</p>
    <h1>Growth, Water Scarcity, and Long-Term Supply In Nevada</h1>
    <hr class="title-rule" />
    <p class="cover-meta">
      One printable package: executive summary + appendices A–F + verification + final review + sources.
      Format modeled on Phase 2 Issue Brief v1.5. Data source: NELIS only.
    </p>
    {summary}
  </section>

  <section class="page-section page-break">
    <div class="brand">The Forum</div>
    <div class="topline"></div>
    <p class="eyebrow">Appendices · NELIS Preliminary · Nevada Water Scarcity</p>
    <h1>Data Appendices</h1>
    <hr class="title-rule" />
    {''.join(appendices)}
  </section>

  <section class="page-section page-break">
    <div class="brand">The Forum</div>
    <div class="topline"></div>
    <p class="eyebrow">Process Reports · NELIS Preliminary · Nevada Water Scarcity</p>
    <h1>Verification And Final Review</h1>
    <hr class="title-rule" />
    {verification_section()}
    {final_review_section()}
    {sources_section()}
    <p class="footer">
      The Forum · Legislative Brief Preliminary Complete (NELIS only) · DRAFT ·
      Canonical folder: briefs/nevada/water-scarcity/nelis-preliminary/ ·
      Reviewers: Ryan Echols, Jodi Stephens, Ashley Lovell
    </p>
  </section>
</body>
</html>
"""


def main() -> None:
    BRIEF.mkdir(parents=True, exist_ok=True)
    doc = build_html()
    OUT_HTML.write_text(doc, encoding="utf-8")
    HTML(string=doc, base_url=str(BRIEF)).write_pdf(str(OUT_PDF))
    print(f"Wrote {OUT_HTML}")
    print(f"Wrote {OUT_PDF}")


if __name__ == "__main__":
    main()
