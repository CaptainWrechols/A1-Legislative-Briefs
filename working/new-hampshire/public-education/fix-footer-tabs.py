#!/usr/bin/env python3
"""Keep the footer's page number on one line for this issue's longer label.

The NV1 v1.6 template footer pushes the page number right with ten literal
tab characters. "NH1 Public Education Legislative Brief v1.0" is ~1 inch longer
than the template's label, which wraps the page number onto a second line.
This post-processes the built docx to use eight tabs instead of ten - a
per-issue knob that leaves the shared exporter and the template untouched.

Run from repo root after export_docx_lege_brief.py.
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path

DOCX = Path("briefs/new-hampshire/public-education/citizen-v2/NH1-Public-Education-Lege-Brief.docx")
TEN_TABS = "<w:tab/>" * 10
EIGHT_TABS = "<w:tab/>" * 8


def main() -> None:
    footer = zipfile.ZipFile(DOCX).read("word/footer1.xml").decode("utf-8")
    assert TEN_TABS in footer, "footer structure changed; re-check the template"
    footer = footer.replace(TEN_TABS, EIGHT_TABS)
    tmp = DOCX.with_suffix(".tmp.docx")
    with zipfile.ZipFile(DOCX) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/footer1.xml":
                zout.writestr(item, footer)
            else:
                zout.writestr(item, zin.read(item.filename))
    os.replace(tmp, DOCX)
    print(f"Footer tabs 10 -> 8 in {DOCX}")


if __name__ == "__main__":
    main()
