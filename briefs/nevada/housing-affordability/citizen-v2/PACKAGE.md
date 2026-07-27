# Package — Housing Affordability in Nevada (citizen-v1.0)

Design Packager v2.3 · 2026-07-24 · The Nevada Forum

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the 2-page front brief |
| `citizen-brief.html` | Print-ready front brief (verified 2 US Letter pages in headless Chrome) |
| `citizen-brief.docx` | Word version of the front brief (verified 2 pages in LibreOffice) |
| `citizen-brief-print.css` | Shared Phase 2 print CSS |
| `appendices/` | Appendices A–I (markdown), `appendices-print.html`, `appendices.docx` |
| `review-report.md` / `.json` | Citizen Reviewer output |

## Print to PDF

1. Open `citizen-brief.html` in Chrome or Edge.
2. Print → Destination: *Save as PDF* → Paper: **Letter** → Margins: **Default** → **Background graphics: on** → no headers/footers.
3. Result should be exactly **2 pages** (verified with headless Chrome at 0.6in margins).
4. Repeat with `appendices/appendices-print.html` for the long appendix PDF (many pages; tables repeat their header rows across breaks).

## Word (.docx)

`citizen-brief.docx` and `appendices/appendices.docx` are generated with:

```bash
ISSUE_CONFIG=config/issues/nevada-housing-affordability.yaml \
python collectors/export_docx.py --brief-dir briefs/nevada/housing-affordability/citizen-v1
```

The **front brief** is written by `collectors/export_docx_brief.py`
(python-docx) with *direct formatting on every run* — literal Arial,
explicit RGB colors, real uppercase heading text, the navy masthead rule,
and the Key-numbers stat cards. Direct formatting is the part that makes
the file look identical in Microsoft Word, Word Online, Google Docs,
LibreOffice, and Pages; style-based formatting renders differently across
those apps. Do not switch it back to style-based export.

The **appendices** use pandoc with the branded reference document
`templates/citizen-brief/forum-reference.docx` (Arial body, navy `#1A2D4F`
title/H1/H3, terracotta `#C0392B` H2) — fine for long-form tables.

**If you need Word and cannot run the script** (no pandoc installed):

1. Easiest: open `citizen-brief.html` in Microsoft Word directly
   (File → Open → select the .html file), then File → Save As → `.docx`.
2. Or: upload `citizen-brief.md` to Google Docs (File → Open → Upload), then
   File → Download → Microsoft Word (.docx).
3. Or install pandoc ([pandoc.org/installing](https://pandoc.org/installing.html)).
