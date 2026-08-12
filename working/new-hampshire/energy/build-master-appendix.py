#!/usr/bin/env python3
"""Build the Master Appendix: all appendices A-I as one document.

  NH1-Energy-Master-Appendix.docx  (title page + A-I, branded
                                            pandoc reference conversion)
  NH1-Energy-Master-Appendix.pdf   (the Phase 2 print styling with
                                            TOC: headless-Chrome print of
                                            appendices-print.html)

Run from repo root after build-appendices-nh.py and build_appendices_print.py.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "collectors")
import export_docx  # noqa: E402

DIR = Path("briefs/new-hampshire/energy/citizen-v2/appendices")

TITLE_MD = """# NH1 Energy — Master Appendix

**Energy Cost, Sourcing, and Reliability in New Hampshire — the complete appendix record**

The Forum · NH1 Energy Legislative Brief v1.0 · August 2026

This document collects Appendices A–I behind the NH1 Energy
Legislative Brief: every bill in the certified 2020–2026 set, theme
scorecards, every recorded roll call with party splits, sponsors, bill paths,
data limits, the bill-by-bill vote grid, the HB2 budget-trailer sections, and
the claim-to-source map. Votes on HB2 are on the whole trailer, never on a
single section.
"""


def main() -> None:
    export_docx.ensure_pandoc()
    export_docx.build_reference_doc(rebuild=False)
    with tempfile.TemporaryDirectory() as td:
        title = Path(td) / "00-title.md"
        title.write_text(TITLE_MD, encoding="utf-8")
        md_files = sorted(p for p in DIR.glob("*.md")
                          if p.name[0].isupper() and p.name != "README.md")
        export_docx.convert([title] + md_files,
                            DIR / "NH1-Energy-Master-Appendix.docx",
                            "NH1 Energy Master Appendix")
    subprocess.run([
        "google-chrome", "--headless=new", "--no-sandbox",
        "--user-data-dir=/tmp/chrome-master",
        f"--print-to-pdf={DIR / 'NH1-Energy-Master-Appendix.pdf'}",
        "--no-pdf-header-footer",
        str(DIR / "appendices-print.html"),
    ], check=True)
    print(f"Wrote {DIR / 'NH1-Energy-Master-Appendix.pdf'}")


if __name__ == "__main__":
    main()
