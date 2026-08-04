"""Split NH HB2 (the omnibus budget policy trailer) into its numbered sections.

HB2 is the companion to HB1 in every budget biennium (2021, 2023, 2025 ...).
Unlike a single-subject bill it bundles dozens or hundreds of unrelated policy
changes, so it must be analysed **section by section**: for a given issue we
want only the handful of sections that touch that issue, not the whole bill.

Supported source formats (auto-detected):

1. **Introduced / engrossed HTML** from `billinfo` / SQL ``legislationtext`` —
   sections anchored by ``<a name="Chapt{N}"></a>``.
2. **Chaptered final HTML** (e.g. ``gc.nh.gov/legislation/2021/HB0002.html``) —
   sections labelled ``{chapter}:{N}`` (Laws of 2021 Chapter 91 → ``91:12``).
3. **Chaptered final PDF plain text** (e.g. LBA HB2 Chapter Law PDF for 2023) —
   same ``{chapter}:{N}`` labels after ``pypdf`` extraction.

Output (see ``docs/nh-hb2-section-workflow.md``):

  working/new-hampshire/{issue}/hb2/{year}/hb2-sections.json
  working/new-hampshire/{issue}/hb2/{year}/hb2-sections.md
  working/new-hampshire/{issue}/hb2/{year}/hb2-relevant.json

This module only parses text a caller already fetched; it does no network I/O.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

_ANCHOR_RE = re.compile(r'<a name="Chapt(\d+)"></a>')
_CHAPTERED_RE_TMPL = r"(?:^|[\n>])\s*{chapter}:(\d+)\s+"


def _plain(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = html.unescape(fragment)
    fragment = fragment.replace("\xa0", " ")
    return re.sub(r"\s+", " ", fragment).strip()


def _record(number: int, text: str, *, chapter: int | None = None) -> dict:
    text = re.sub(r"^\s*%d\s+" % number, "", text)
    if chapter is not None:
        text = re.sub(rf"^\s*{chapter}:{number}\s+", "", text)
    heading, _, _ = text.partition(". ")
    rsas = sorted(set(re.findall(r"RSA\s+[0-9A-Za-z:\-]+", text)))
    rec = {
        "section": number,
        "heading": heading.strip().rstrip("."),
        "affected_rsas": rsas,
        "text": text,
    }
    if chapter is not None:
        rec["chapter_cite"] = f"{chapter}:{number}"
    return rec


def extract_sections_chaptered(text: str, chapter: int) -> list[dict]:
    """Split chaptered final text on ``{chapter}:{N}`` labels."""
    pat = re.compile(_CHAPTERED_RE_TMPL.format(chapter=chapter))
    matches = list(pat.finditer(text))
    # Deduplicate by section number, keeping the first occurrence (the
    # analysis summary at the top of some PDFs re-lists section numbers).
    seen: set[int] = set()
    ordered: list[re.Match] = []
    for m in matches:
        n = int(m.group(1))
        if n in seen:
            continue
        seen.add(n)
        ordered.append(m)
    sections: list[dict] = []
    for i, m in enumerate(ordered):
        number = int(m.group(1))
        start = m.end()
        end = ordered[i + 1].start() if i + 1 < len(ordered) else len(text)
        body = text[start:end]
        # Strip HTML if present.
        body_plain = _plain(body) if "<" in body else re.sub(r"\s+", " ", body).strip()
        sections.append(_record(number, f"{chapter}:{number} {body_plain}", chapter=chapter))
    return sections


def extract_sections_anchored(bill_html: str) -> list[dict]:
    """Split introduced/engrossed HTML on ``<a name="Chapt{N}">`` anchors."""
    anchors = list(_ANCHOR_RE.finditer(bill_html))
    # Skip empty/duplicate anchors (chaptered HTML sometimes stacks them).
    usable: list[re.Match] = []
    seen: set[int] = set()
    for m in anchors:
        n = int(m.group(1))
        # Peek ahead: if the next chars are another Chapt anchor, skip this one.
        nxt = bill_html[m.end(): m.end() + 40]
        if re.match(r'\s*<a name="Chapt\d+"', nxt):
            continue
        if n in seen:
            continue
        seen.add(n)
        usable.append(m)
    sections: list[dict] = []
    for i, m in enumerate(usable):
        number = int(m.group(1))
        start = m.end()
        end = usable[i + 1].start() if i + 1 < len(usable) else len(bill_html)
        text = _plain(bill_html[start:end])
        sections.append(_record(number, text))
    return sections


def detect_chapter(text: str) -> int | None:
    """Infer the Laws-of-NH chapter number from dense ``N:M`` labels."""
    counts: dict[int, int] = {}
    for ch, _sec in re.findall(r"(?:^|[\n>])\s*(\d{1,3}):(\d+)\s+[A-Z]", text):
        counts[int(ch)] = counts.get(int(ch), 0) + 1
    if not counts:
        return None
    best = max(counts, key=counts.get)
    return best if counts[best] >= 10 else None


def extract_sections(bill_text: str, *, chapter: int | None = None) -> list[dict]:
    """Auto-detect format and return one record per HB2 section."""
    # Prefer explicit chaptered labels when present (more reliable than anchors
    # on chaptered HTML, where anchors can be stacked/misnumbered).
    ch = chapter if chapter is not None else detect_chapter(bill_text)
    if ch is not None:
        secs = extract_sections_chaptered(bill_text, ch)
        if len(secs) >= 10:
            return secs
    if "<a name=\"Chapt" in bill_text:
        secs = extract_sections_anchored(bill_text)
        if secs:
            return secs
    if ch is not None:
        return extract_sections_chaptered(bill_text, ch)
    return []


def extract_sections_from_plain(plain: str, *, chapter: int) -> list[dict]:
    return extract_sections_chaptered(plain, chapter)


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
        f"Source: {meta.get('source_url', meta.get('url', ''))}  ",
        f"Version: {meta.get('version_label', 'unknown')}  ",
        f"Sections: {len(sections)}",
        "",
        "> HB2 bundles many unrelated policy changes. For a citizen brief, "
        "review only the sections relevant to your issue.",
        "",
    ]
    for sec in sections:
        cite = sec.get("chapter_cite") or str(sec["section"])
        lines.append(f"## Section {cite} - {sec['heading']}")
        if sec["affected_rsas"]:
            lines.append(f"*Affects:* {', '.join(sec['affected_rsas'])}")
        lines.append("")
        lines.append(sec["text"])
        lines.append("")
    (out_dir / "hb2-sections.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Extract HB2 sections from saved HTML/text")
    p.add_argument("text_file", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--session-year", type=int, default=0)
    p.add_argument("--chapter", type=int, default=None)
    args = p.parse_args()

    raw = args.text_file.read_text(encoding="utf-8", errors="replace")
    secs = extract_sections(raw, chapter=args.chapter)
    write_outputs(secs, args.out, {"bill_no": "HB2", "session_year": args.session_year,
                                   "chapter": args.chapter})
    print(f"Extracted {len(secs)} sections -> {args.out}")
