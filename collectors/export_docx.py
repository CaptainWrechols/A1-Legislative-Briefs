#!/usr/bin/env python3
"""Export the citizen brief + appendices to Word (.docx) via pandoc.

Creates (once) a branded pandoc reference document with Forum styles —
Arial body, navy #1A2D4F titles/H1, terracotta #C0392B H2 — then converts:

  {BRIEF_DIR}/citizen-brief.md          -> {BRIEF_DIR}/citizen-brief.docx
  {BRIEF_DIR}/appendices/*.md (A-... order) -> {BRIEF_DIR}/appendices/appendices.docx

Usage:
  python collectors/export_docx.py --brief-dir briefs/nevada/water-scarcity/citizen-v1

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


def build_reference_doc() -> None:
    """Create the branded reference docx by restyling pandoc's default."""
    if REFERENCE.exists():
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
        xml = styles_path.read_text(encoding="utf-8")

        # Arial everywhere the defaults set a font.
        xml = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="[^"]*"', r'w:\1="Arial"', xml)

        def set_style_color(xml: str, style_id: str, color: str) -> str:
            pattern = re.compile(
                r'(<w:style [^>]*w:styleId="%s".*?)</w:style>' % re.escape(style_id),
                re.S,
            )
            m = pattern.search(xml)
            if not m:
                return xml
            block = m.group(0)
            if "<w:color" in block:
                block2 = re.sub(r'<w:color w:val="[^"]*"', f'<w:color w:val="{color}"', block)
            else:
                block2 = block.replace(
                    "</w:rPr>", f'<w:color w:val="{color}"/></w:rPr>', 1
                )
            return xml.replace(block, block2)

        xml = set_style_color(xml, "Title", NAVY)
        xml = set_style_color(xml, "Heading1", NAVY)
        xml = set_style_color(xml, "Heading2", TERRACOTTA)
        xml = set_style_color(xml, "Heading3", NAVY)
        xml = set_style_color(xml, "Heading4", NAVY)
        styles_path.write_text(xml, encoding="utf-8")

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


def convert(md_paths: list[Path], out_path: Path, title: str) -> None:
    with tempfile.TemporaryDirectory() as td:
        combined = Path(td) / "combined.md"
        chunks = []
        for i, p in enumerate(md_paths):
            text = strip_html_comments(strip_front_matter(p.read_text(encoding="utf-8")))
            chunks.append(text)
        combined.write_text("\n\n\\newpage\n\n".join(chunks), encoding="utf-8")
        subprocess.run(
            [
                "pandoc",
                str(combined),
                "-f",
                "markdown+pipe_tables",
                "-t",
                "docx",
                "--reference-doc",
                str(REFERENCE),
                "--metadata",
                f"title={title}",
                "-o",
                str(out_path),
            ],
            check=True,
        )
    print(f"Wrote {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-dir", required=True)
    args = parser.parse_args()
    brief_dir = Path(args.brief_dir)

    ensure_pandoc()
    build_reference_doc()

    brief_md = brief_dir / "citizen-brief.md"
    if brief_md.exists():
        convert([brief_md], brief_dir / "citizen-brief.docx", "Citizen Brief")
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
