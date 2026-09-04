#!/usr/bin/env python3
"""Post-process the SC1 lege-brief docx: let both glossaries flow directly
after the preceding content instead of jumping to new pages.

The exporter's --polish-breaks puts each glossary on its own page (a
pageBreakBefore on the GLOSSARY heading and a nextPage section break before
the LEGISLATIVE PROCESS GLOSSARY heading). Per reviewer direction
(2026-09-04), the SC1 brief removes both jumps so there is no large blank
gap after the Policy Spotlights or between the glossaries; making the
transitions continuous also causes the first glossary's two columns to
balance instead of filling the left column only.

Usage: python3 working/south-carolina/slow-wage-growth/fix-glossary-break.py <docx>
"""
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

path = Path(sys.argv[1])
with tempfile.TemporaryDirectory() as td:
    work = Path(td) / "unzipped"
    with zipfile.ZipFile(path) as zf:
        zf.extractall(work)
    doc = work / "word" / "document.xml"
    x = doc.read_text(encoding="utf-8")
    # remove only the pageBreakBefore whose paragraph holds the GLOSSARY heading
    n = 0
    out = []
    last = 0
    for m in re.finditer(r"<w:pageBreakBefore/>", x):
        following = x[m.end():m.end() + 2000]
        t = re.search(r"<w:t[^>]*>([^<]+)</w:t>", following)
        if t and t.group(1).strip() == "GLOSSARY":
            out.append(x[last:m.start()])
            last = m.end()
            n += 1
    out.append(x[last:])
    if n != 1:
        raise SystemExit(f"expected exactly 1 GLOSSARY pageBreakBefore, found {n}")
    x = "".join(out)
    # make the process-glossary heading section start continuous instead of
    # on a new page (it is the only nextPage sectPr in the document)
    n2 = len(re.findall(r'<w:type w:val="nextPage"/>', x))
    if n2 != 1:
        raise SystemExit(f"expected exactly 1 nextPage sectPr, found {n2}")
    x = x.replace('<w:type w:val="nextPage"/>', '<w:type w:val="continuous"/>')
    doc.write_text(x, encoding="utf-8")
    tmp_out = Path(td) / "out.docx"
    with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(work.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(work))
    shutil.move(str(tmp_out), path)
print(f"removed GLOSSARY page break in {path}")
