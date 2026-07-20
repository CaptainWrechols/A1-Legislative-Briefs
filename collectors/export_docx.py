#!/usr/bin/env python3
"""Export the citizen brief + appendices to Word (.docx) via pandoc.

Creates (once) a branded pandoc reference document mirroring the Phase 2
Issue Brief system — Arial 9pt body with compact spacing, navy #1A2D4F
title/H1, terracotta #C0392B ALL-CAPS H2, 0.6in margins — then converts:

  {BRIEF_DIR}/citizen-brief.md              -> {BRIEF_DIR}/citizen-brief.docx
  {BRIEF_DIR}/appendices/*.md (A-... order) -> {BRIEF_DIR}/appendices/appendices.docx

Usage:
  python collectors/export_docx.py --brief-dir briefs/nevada/water-scarcity/citizen-v1
  python collectors/export_docx.py --brief-dir ... --rebuild-reference

Requires pandoc (https://pandoc.org). If pandoc is missing, this prints
manual conversion instructions and exits non-zero.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REFERENCE = Path("templates/citizen-brief/forum-reference.docx")

NAVY = "1A2D4F"
NAVY2 = "2E4A78"
TERRACOTTA = "C0392B"
BODY_GRAY = "444444"

MANUAL_STEPS = """\
pandoc is not installed. Manual ways to get a Word document:
  1. Open the packaged HTML (citizen-brief.html) in Microsoft Word directly
     (File > Open), then Save As .docx; or
  2. Upload citizen-brief.md to Google Docs (File > Open > Upload), then
     File > Download > Microsoft Word (.docx); or
  3. Install pandoc and re-run this script:
     pandoc citizen-brief.md -o citizen-brief.docx
"""


def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        sys.stderr.write(MANUAL_STEPS)
        raise SystemExit(2)


def _restyle(styles_xml: str) -> str:
    """Apply Phase 2 tokens and compact spacing to pandoc's default styles."""
    xml = styles_xml

    # Arial everywhere a font is set — including theme-based rFonts, which is
    # what pandoc's docDefaults use (otherwise the body stays a serif theme font).
    xml = re.sub(r"<w:rFonts [^/]*/>", '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial" />', xml)
    xml = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', r'w:\1="Arial"', xml)

    # Document defaults: 9pt gray body, compact paragraph spacing.
    xml = re.sub(
        r"(<w:rPrDefault>\s*<w:rPr>.*?)<w:sz w:val=\"\d+\" />\s*<w:szCs w:val=\"\d+\" />",
        rf'\1<w:color w:val="{BODY_GRAY}" /><w:sz w:val="18" /><w:szCs w:val="18" />',
        xml,
        flags=re.S,
    )
    xml = re.sub(
        r"<w:pPrDefault>\s*<w:pPr>\s*<w:spacing [^/]*/>",
        '<w:pPrDefault><w:pPr><w:spacing w:after="80" w:line="252" w:lineRule="auto" />',
        xml,
    )

    def edit_style(xml: str, style_id: str, rpr_add: str = "", ppr_add: str = "",
                   color: str | None = None, size_half_pts: int | None = None) -> str:
        pattern = re.compile(
            r'(<w:style [^>]*w:styleId="%s".*?</w:style>)' % re.escape(style_id), re.S
        )
        m = pattern.search(xml)
        if not m:
            return xml
        block = m.group(1)
        new = block
        if color is not None:
            if "<w:color" in new:
                new = re.sub(r'<w:color w:val="[^"]*"', f'<w:color w:val="{color}"', new)
            else:
                new = new.replace("</w:rPr>", f'<w:color w:val="{color}"/></w:rPr>', 1)
        if size_half_pts is not None:
            if "<w:sz " in new:
                new = re.sub(r'<w:sz w:val="\d+"', f'<w:sz w:val="{size_half_pts}"', new)
                new = re.sub(r'<w:szCs w:val="\d+"', f'<w:szCs w:val="{size_half_pts}"', new)
            else:
                new = new.replace(
                    "</w:rPr>",
                    f'<w:sz w:val="{size_half_pts}"/><w:szCs w:val="{size_half_pts}"/></w:rPr>',
                    1,
                )
        if rpr_add:
            new = new.replace("</w:rPr>", f"{rpr_add}</w:rPr>", 1)
        if ppr_add:
            if "<w:spacing" in new:
                new = re.sub(r"<w:spacing [^/]*/>", ppr_add, new, count=1)
            elif "</w:pPr>" in new:
                new = new.replace("</w:pPr>", f"{ppr_add}</w:pPr>", 1)
        return xml.replace(block, new)

    # Body Text / First Paragraph: compact spacing (pandoc uses these, with
    # their own w:spacing that overrides docDefaults).
    xml = re.sub(
        r'(<w:style w:type="paragraph" w:styleId="BodyText">.*?)<w:spacing [^/]*/>',
        r'\1<w:spacing w:before="0" w:after="80" w:line="252" w:lineRule="auto" />',
        xml,
        flags=re.S,
    )
    # Title (if used): big navy.
    xml = edit_style(xml, "Title", color=NAVY, size_half_pts=40,
                     ppr_add='<w:spacing w:before="0" w:after="60"/>')
    # H1 = document title style: navy, 18pt, thick feel.
    xml = edit_style(xml, "Heading1", color=NAVY, size_half_pts=36,
                     ppr_add='<w:spacing w:before="0" w:after="40"/>')
    # H2 = terracotta ALL-CAPS section header, 11pt, letter-spaced.
    xml = edit_style(
        xml, "Heading2", color=TERRACOTTA, size_half_pts=22,
        rpr_add='<w:caps/><w:spacing w:val="20"/>',
        ppr_add='<w:spacing w:before="140" w:after="40"/>',
    )
    # H3/H4: secondary navy, small.
    xml = edit_style(xml, "Heading3", color=NAVY2, size_half_pts=20,
                     ppr_add='<w:spacing w:before="100" w:after="30"/>')
    xml = edit_style(xml, "Heading4", color=NAVY2, size_half_pts=18)
    # Compact lists and table text.
    xml = edit_style(xml, "Compact",
                     ppr_add='<w:spacing w:before="0" w:after="40"/>')
    return xml


def _set_margins(document_xml: str) -> str:
    """US Letter with 0.6in margins (864 twips)."""
    document_xml = re.sub(
        r'<w:pgMar [^/]*/>',
        '<w:pgMar w:top="864" w:right="864" w:bottom="864" w:left="864" '
        'w:header="432" w:footer="432" w:gutter="0"/>',
        document_xml,
    )
    document_xml = re.sub(
        r'<w:pgSz [^/]*/>',
        '<w:pgSz w:w="12240" w:h="15840"/>',
        document_xml,
    )
    return document_xml


def build_reference_doc(rebuild: bool = False) -> None:
    if REFERENCE.exists() and not rebuild:
        return
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        default = Path(td) / "default.docx"
        with default.open("wb") as fh:
            subprocess.run(
                ["pandoc", "--print-default-data-file", "reference.docx"],
                check=True,
                stdout=fh,
            )
        workdir = Path(td) / "unzipped"
        with zipfile.ZipFile(default) as zf:
            zf.extractall(workdir)
        styles_path = workdir / "word" / "styles.xml"
        styles_path.write_text(_restyle(styles_path.read_text(encoding="utf-8")), encoding="utf-8")
        doc_path = workdir / "word" / "document.xml"
        doc_path.write_text(_set_margins(doc_path.read_text(encoding="utf-8")), encoding="utf-8")
        with zipfile.ZipFile(REFERENCE, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(workdir.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(workdir))
    print(f"Built branded reference doc: {REFERENCE}")


def strip_front_matter(markdown: str) -> str:
    if markdown.startswith("---"):
        end = markdown.find("\n---", 3)
        if end != -1:
            return markdown[end + 4 :].lstrip("\n")
    return markdown


def strip_html_comments(markdown: str) -> str:
    return re.sub(r"<!--.*?-->\n?", "", markdown, flags=re.S)


def drop_trailing_hr(markdown: str) -> str:
    return re.sub(r"\n---+\n", "\n", markdown)


def convert(md_paths: list[Path], out_path: Path, title: str | None = None) -> None:
    with tempfile.TemporaryDirectory() as td:
        combined = Path(td) / "combined.md"
        chunks = []
        for p in md_paths:
            text = drop_trailing_hr(
                strip_html_comments(strip_front_matter(p.read_text(encoding="utf-8")))
            )
            chunks.append(text)
        combined.write_text("\n\n\\newpage\n\n".join(chunks), encoding="utf-8")
        cmd = [
            "pandoc",
            str(combined),
            "-f",
            "markdown+pipe_tables",
            "-t",
            "docx",
            "--reference-doc",
            str(REFERENCE),
            "-o",
            str(out_path),
        ]
        if title:
            cmd[-2:-2] = ["--metadata", f"title={title}"]
        subprocess.run(cmd, check=True)
    print(f"Wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-dir", required=True)
    parser.add_argument("--rebuild-reference", action="store_true")
    args = parser.parse_args()
    brief_dir = Path(args.brief_dir)

    ensure_pandoc()
    build_reference_doc(rebuild=args.rebuild_reference)

    brief_md = brief_dir / "citizen-brief.md"
    if brief_md.exists():
        # No pandoc title block: the markdown's own H1 is the title.
        convert([brief_md], brief_dir / "citizen-brief.docx")
    else:
        print(f"Missing {brief_md}; skipped front brief")

    appendix_dir = brief_dir / "appendices"
    if appendix_dir.exists():
        md_files = sorted(
            p
            for p in appendix_dir.glob("*.md")
            if p.name[0].isalpha() and p.name != "README.md"
        )
        readme = appendix_dir / "README.md"
        ordered = ([readme] if readme.exists() else []) + md_files
        if ordered:
            convert(ordered, appendix_dir / "appendices.docx", "Appendices")
    else:
        print(f"Missing {appendix_dir}; skipped appendices")


if __name__ == "__main__":
    main()
