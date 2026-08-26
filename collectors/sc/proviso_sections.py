"""Split a SC General Appropriations Act **Part IB** into individual provisos.

Part IB ("Operation of State Government" — the *temporary provisions*) is where
South Carolina's annual budget carries its policy riders. It is organised as
one SECTION per agency, each holding numbered provisos:

    <a name="s1"><b>SECTION</a> 1 - H630 - DEPARTMENT OF EDUCATION</b>
    <b> ... 1.1. ... </b>(SDE: Appropriation Transfer Prohibition) text...<br>
    <b> ... 1.2. ... </b>(SDE: Comprehensive Health Assessment) text...<br>

So unlike New Hampshire's HB2 (bare numbered sections), every SC proviso comes
with a stable number ("1.1", "117.32") AND a parenthesised caption
("(SDE: ...)"), which makes issue matching and citation much cleaner.

This module only parses text a caller already fetched (see
:mod:`collectors.sc.proviso_fetch`); it does no network I/O.

Outputs (see docs/sc-appropriations-proviso-workflow.md):

  working/south-carolina/{issue}/proviso-sections.json   # all provisos
  working/south-carolina/{issue}/proviso-sections.md     # human review copy
  working/south-carolina/{issue}/proviso-relevant.json   # issue-matched only

Guardrails: proviso text is captured verbatim; votes are NOT attached here —
they are recorded on the whole appropriations bill, never per proviso.
"""

from __future__ import annotations

import html as htmllib
import json
import re
from pathlib import Path

# <a name="s1"> / <a name="s1a"> — agency section anchors in tap1b.htm.
_SECTION_ANCHOR_RE = re.compile(r'<a name="s([0-9]+[a-z]?)">', re.I)
# Header text after the anchor: SECTION 1 - H630 - DEPARTMENT OF EDUCATION
_SECTION_HEADER_RE = re.compile(
    r"SECTION\s+([0-9]+[A-Za-z]?)\s*-\s*([A-Z0-9]+)\s*-\s*(.+?)$"
)
# Proviso number in bold: <b> ... 1.1. ... </b>(SDE: Caption) text
_PROVISO_RE = re.compile(
    r"<b>\s*(?:&nbsp;|\s)*([0-9]+[A-Za-z]?\.[0-9]+[A-Za-z]?)\.?(?:&nbsp;|\s)*</b>",
    re.I,
)
_CAPTION_RE = re.compile(r"^\s*\(([^)]{1,160})\)")
_CODE_CITE_RE = re.compile(
    r"Section[s]?\s+(\d{1,2}-\d{1,3}-\d{1,5}(?:\([^)]*\))?)", re.I
)


def _plain(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = htmllib.unescape(fragment).replace("\xa0", " ")
    return re.sub(r"\s+", " ", fragment).strip()


def extract_provisos(part1b_html: str) -> list[dict]:
    """Return one record per proviso across all agency sections of Part IB."""
    anchors = list(_SECTION_ANCHOR_RE.finditer(part1b_html))
    provisos: list[dict] = []
    for i, anchor in enumerate(anchors):
        start = anchor.start()
        end = anchors[i + 1].start() if i + 1 < len(anchors) else len(part1b_html)
        chunk = part1b_html[start:end]

        # Parse the section header (first line of the chunk, tags stripped).
        header_plain = _plain(chunk[:400])
        hm = _SECTION_HEADER_RE.search(header_plain.split("\n")[0][:200])
        section_no = hm.group(1) if hm else anchor.group(1).upper()
        agency_code = hm.group(2) if hm else ""
        agency_name = hm.group(3).strip() if hm else header_plain[:120]

        marks = list(_PROVISO_RE.finditer(chunk))
        for j, m in enumerate(marks):
            body_end = marks[j + 1].start() if j + 1 < len(marks) else len(chunk)
            body = _plain(chunk[m.end(): body_end])
            cm = _CAPTION_RE.match(body)
            caption = cm.group(1).strip() if cm else ""
            text = body[cm.end():].strip() if cm else body
            provisos.append({
                "proviso": m.group(1),
                "section": section_no,
                "agency_code": agency_code,
                "agency_name": agency_name,
                "caption": caption,
                "text": text,
                "sc_code_cites": sorted(set(_CODE_CITE_RE.findall(text))),
            })
    return provisos


def match_provisos(provisos: list[dict], terms: list[str]) -> list[dict]:
    """Provisos whose caption/text mention any issue term (case-insensitive).

    Same philosophy as the NH HB2 workflow: err toward recall; a human prunes.
    """
    lowered = list(dict.fromkeys(          # dedupe, preserving order
        t.lower().strip() for t in terms if t and t.strip()))
    hits = []
    for p in provisos:
        blob = f"{p['caption']} {p['text']}".lower()
        matched = [t for t in lowered if t in blob]
        if matched:
            hits.append({**p, "matched_terms": matched})
    return hits


def write_outputs(provisos: list[dict], relevant: list[dict],
                  out_dir: Path, meta: dict) -> None:
    """Write proviso-sections.json/.md + proviso-relevant.json under out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    note = (
        "Part IB of the SC General Appropriations Act carries the budget's "
        "policy provisos. Each proviso is an independent temporary provision; "
        "review only those relevant to the issue. Vote counts are NOT included "
        "here -- roll calls are recorded on the whole appropriations bill "
        "(collectors.sc.scstatehouse.vote_history), never per proviso."
    )
    (out_dir / "proviso-sections.json").write_text(json.dumps({
        "note": note, **meta,
        "proviso_count": len(provisos),
        "provisos": provisos,
    }, indent=2), encoding="utf-8")

    lines = [
        f"# Part IB provisos - FY {meta.get('fiscal_year', '?')} "
        f"({meta.get('bill_no', '?')}, {meta.get('version_label', '?')})",
        "",
        f"Source: {meta.get('source_url', '')}  ",
        f"Provisos: {len(provisos)}",
        "",
        "> Part IB bundles hundreds of unrelated temporary provisions. For a "
        "citizen brief, review only the provisos relevant to your issue. "
        "Votes are on the whole appropriations bill, never on one proviso.",
        "",
    ]
    current_section = None
    for p in provisos:
        if p["section"] != current_section:
            current_section = p["section"]
            lines += [f"## SECTION {p['section']} - {p['agency_code']} - "
                      f"{p['agency_name']}", ""]
        lines.append(f"### {p['proviso']} ({p['caption']})")
        if p["sc_code_cites"]:
            lines.append(f"*Cites SC Code:* {', '.join(p['sc_code_cites'])}")
        lines += ["", p["text"], ""]
    (out_dir / "proviso-sections.md").write_text("\n".join(lines), encoding="utf-8")

    (out_dir / "proviso-relevant.json").write_text(json.dumps({
        "note": note, **meta,
        "relevant_proviso_count": len(relevant),
        "provisos": relevant,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Extract Part IB provisos from saved HTML")
    ap.add_argument("html_file", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--terms", nargs="*", default=[])
    args = ap.parse_args()
    raw = args.html_file.read_text(encoding="utf-8", errors="replace")
    provisos = extract_provisos(raw)
    relevant = match_provisos(provisos, args.terms)
    write_outputs(provisos, relevant, args.out, {"source_file": str(args.html_file)})
    print(f"{len(provisos)} provisos ({len(relevant)} matched) -> {args.out}")
