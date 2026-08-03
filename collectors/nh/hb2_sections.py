"""Split NH HB2 (the omnibus budget policy trailer) into its numbered sections.

HB2 is the companion to HB1 in every budget biennium (2021, 2023, 2025 ...).
Unlike a single-subject bill it bundles dozens or hundreds of unrelated policy
changes, so it must be analysed **section by section**: for a given issue we
want only the handful of sections that touch that issue, not the whole bill.

In the gc.nh.gov inline bill text each operative section is marked by an
anchor ``<a name="Chapt{N}"></a>`` immediately followed by
``{N}&nbsp;{Heading}.&nbsp;{operative text}`` (e.g.
``9  New Paragraph; Water Management and Protection; Fill and Dredge In
Wetlands. Amend RSA 482-A:3 ...``). We split on those anchors, which is stable
across the 2021/2023/2025 texts.

Output (see ``docs/nh-hb2-section-workflow.md``):

  working/new-hampshire/{issue}/hb2-sections.json   # machine-readable
  working/new-hampshire/{issue}/hb2-sections.md     # human review

This module only parses HTML that a caller already fetched (via
``gencourt_web.fetch_version_text``); it does no network I/O and is fully
state-agnostic.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

_ANCHOR_RE = re.compile(r'<a name="Chapt(\d+)"></a>')


def _plain(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    fragment = fragment.replace("\xa0", " ")
    return re.sub(r"\s+", " ", fragment).strip()


def extract_sections(bill_html: str) -> list[dict]:
    """Return one record per HB2 section: number, heading, RSAs, full text."""
    anchors = list(_ANCHOR_RE.finditer(bill_html))
    sections: list[dict] = []
    for i, m in enumerate(anchors):
        number = int(m.group(1))
        start = m.end()
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(bill_html)
        body_html = bill_html[start:end]
        text = _plain(body_html)
        # Strip a leading "{N} " if present, then split heading (up to the
        # first period) from the operative text.
        text = re.sub(r"^\s*%d\s+" % number, "", text)
        heading, _, remainder = text.partition(". ")
        rsas = sorted(set(re.findall(r"RSA\s+[0-9A-Za-z:\-]+", text)))
        sections.append(
            {
                "section": number,
                "heading": heading.strip().rstrip("."),
                "affected_rsas": rsas,
                "text": text,
            }
        )
    return sections


def match_sections(sections: list[dict], terms: list[str]) -> list[dict]:
    """Sections whose heading/text/RSA mention any issue term (case-insensitive)."""
    lowered = [t.lower() for t in terms]
    hits = []
    for sec in sections:
        blob = (sec["heading"] + " " + sec["text"]).lower()
        matched = [t for t in lowered if t in blob]
        if matched:
            hits.append({**sec, "matched_terms": matched})
    return hits


def write_outputs(sections: list[dict], out_dir: Path, meta: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "note": (
            "HB2 is the omnibus budget policy trailer. Each section is an "
            "independent policy change; review only the sections relevant to "
            "the issue. Vote counts are NOT included here -- pull those from "
            "gencourt_sql.rollcall_summaries so nothing is invented."
        ),
        **meta,
        "section_count": len(sections),
        "sections": sections,
    }
    (out_dir / "hb2-sections.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    lines = [
        f"# HB2 sections - {meta.get('session_year', '?')} ({meta.get('bill_no', 'HB2')})",
        "",
        f"Source: {meta.get('source_url', 'gc.nh.gov billinfo linkv postback')}  ",
        f"Version: {meta.get('version_label', 'Introduced')}  ",
        f"Sections: {len(sections)}",
        "",
        "> HB2 bundles many unrelated policy changes. For a citizen brief, "
        "review only the sections relevant to your issue.",
        "",
    ]
    for sec in sections:
        lines.append(f"## Section {sec['section']} - {sec['heading']}")
        if sec["affected_rsas"]:
            lines.append(f"*Affects:* {', '.join(sec['affected_rsas'])}")
        lines.append("")
        lines.append(sec["text"])
        lines.append("")
    (out_dir / "hb2-sections.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Extract HB2 sections from saved HTML")
    p.add_argument("html_file", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--session-year", type=int, default=0)
    args = p.parse_args()

    secs = extract_sections(args.html_file.read_text(encoding="utf-8"))
    write_outputs(secs, args.out, {"bill_no": "HB2", "session_year": args.session_year})
    print(f"Extracted {len(secs)} sections -> {args.out}")
