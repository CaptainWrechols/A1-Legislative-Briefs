#!/usr/bin/env python3
"""Build appendices-print.html from appendix markdown (Design Packager helper).

Uses pandoc for md->html body conversion, then wraps everything in the Phase 2
visual system (citizen-brief-print.css): navy-header tables, terracotta
section headers, TOC card, page breaks at <!-- pdf-page-break --> markers.

  python collectors/build_appendices_print.py --brief-dir briefs/nevada/water-scarcity/citizen-v1
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

APPENDIX_DESCRIPTIONS = {
    "A": "Every bill: plain topic, theme, result, where it ended, sponsors",
    "B": "Theme scorecards with baskets and stop patterns",
    "C": "Final Passage votes, party splits, high-support non-enactments",
    "D": "Sponsors and people",
    "E": "Step-by-step progress for every policy bill",
    "F": "What this data can and cannot say",
    "G": "Introduced vs. final text for governor-bound bills",
}


def md_to_body(md_path: Path) -> str:
    out = subprocess.run(
        ["pandoc", str(md_path), "-f", "markdown+pipe_tables", "-t", "html"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    out = out.replace("<table>", '<table class="cmp">')
    out = re.sub(r"<h1[^>]*>(.*?)</h1>", r'<h2 class="appendix-title">\1</h2>', out, flags=re.S)
    out = re.sub(r"<h2 id=", '<h3 class="sub" id=', out)
    out = out.replace("</h2>\n", "</h2>\n")  # no-op guard
    out = re.sub(r"</h2>(?!\n)", "</h2>", out)
    out = re.sub(r"<h2(?! class)", '<h3 class="sub"', out)
    out = out.replace("</h2>", "</h2>")
    out = out.replace("<!-- pdf-page-break -->", '<div class="page-break"></div>')
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-dir", required=True)
    args = parser.parse_args()
    appendix_dir = Path(args.brief_dir) / "appendices"
    files = sorted(
        p for p in appendix_dir.glob("*.md") if p.name != "README.md" and p.name[0].isupper()
    )

    toc_items = []
    bodies = []
    for p in files:
        letter = p.name[0]
        anchor = f"appendix-{letter.lower()}"
        title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        toc_items.append(
            f'<li><a href="#{anchor}">{title}</a> '
            f'<span class="toc-desc">— {APPENDIX_DESCRIPTIONS.get(letter, "")}</span></li>'
        )
        body = md_to_body(p)
        bodies.append(f'<div class="page-break"></div>\n<section id="{anchor}">\n{body}\n</section>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Appendices — Growth, Water Scarcity, and Long-Term Supply in Nevada</title>
<link rel="stylesheet" href="../citizen-brief-print.css">
</head>
<body>

<header class="masthead">
  <div class="forum">The&nbsp;Forum</div>
  <hr class="navy-rule">
  <div class="kicker"><span class="k-lead">Citizen Brief · Appendices</span> · citizen-v2.0 · Water in Nevada · The Nevada Forum · July 2026</div>
  <h1 class="title">Growth, Water Scarcity, and Long-Term Supply in Nevada — Appendices</h1>
  <p class="dek">Long-form detail behind the two-page citizen brief. 165 bills found for 2019–2025; 100 policy bills carry the headline numbers.</p>
</header>

<div class="toc">
  <div class="toc-title">Contents</div>
  <ol>
    {chr(10).join(toc_items)}
  </ol>
  <p class="note">Committee Yea votes marked * are inferred (committee membership minus recorded Nay/Absent), because Nevada minutes usually list only No and Absent votes.</p>
</div>

{chr(10).join(bodies)}

<p class="footline">The Nevada Forum · Citizen Brief citizen-v2.0 appendices · July 2026 · Sources: NELIS (leg.state.nv.us), LCB Subject Index of Bills, official committee minutes</p>
</body>
</html>
"""
    out = appendix_dir / "appendices-print.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
