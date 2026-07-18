# Package — Growth, Water Scarcity, and Long-Term Supply in Nevada (citizen-v3.0)

Design Packager v2.2 · 2026-07-17 · The Nevada Forum

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the 2-page front brief |
| `citizen-brief.html` | Print-ready front brief (verified 2 US Letter pages) |
| `citizen-brief.docx` | Word version of the front brief |
| `citizen-brief-print.css` | Shared Phase 2 print CSS |
| `appendices/` | Appendices A–G (markdown), `appendices-print.html`, `appendices.docx` |
| `review-report.md` / `.json` | Citizen Reviewer output |

## Print to PDF

1. Open `citizen-brief.html` in Chrome or Edge.
2. Print → Destination: *Save as PDF* → Paper: **Letter** → Margins: **Default** → **Background graphics: on** → no headers/footers.
3. Result should be exactly **2 pages** (verified with headless Chrome at 0.6in margins).
4. Repeat with `appendices/appendices-print.html` for the long appendix PDF (many pages; tables repeat their header rows across breaks).

## Word (.docx)

`citizen-brief.docx` and `appendices/appendices.docx` are generated with:

```bash
python collectors/export_docx.py --brief-dir briefs/nevada/water-scarcity/citizen-v1
```

They use the branded pandoc reference document
`templates/citizen-brief/forum-reference.docx` (Arial body, navy `#1A2D4F`
title/H1/H3, terracotta `#C0392B` H2). The Word files carry the same words as
the markdown; the HTML remains the layout-faithful print artifact.

**If you need Word and cannot run the script** (no pandoc installed):

1. Easiest: open `citizen-brief.html` in Microsoft Word directly
   (File → Open → select the .html file), then File → Save As → `.docx`.
   Word keeps the tables and most of the styling.
2. Or: upload `citizen-brief.md` to Google Docs (File → Open → Upload), then
   File → Download → Microsoft Word (.docx).
3. Or install pandoc ([pandoc.org/installing](https://pandoc.org/installing.html))
   and run the command above.

## Visual system

Tokens come from `config/forum-brand.yaml`, extracted from the Phase 2 sample
`templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`:
white page, navy `#1A2D4F`, secondary navy `#2E4A78`, terracotta `#C0392B`
ALL-CAPS section headers, soft tint `#E8D5D3`, Arial body (~9pt), Georgia serif
only inside quote-style history cards. No purple/gold/cream website palette.

Modules used: eyebrow header, terracotta H2s, navy-bar stat strip, process
line, navy-header comparison tables (proposals table on page 1 is the
centerpiece; baskets table on page 2), quote-style history cards, info card
pair, numbered question grid, footline.

## v3.0 layout notes

- Page 1 = statement-first: stat strip, bill-path primer, and rows 1–8 of
  "The ten things Nevadans said most, checked against the record."
- Page 2 = table rows 9–10 (navy header repeats across the break), compact
  three-basket prose, people/process signals, passed recently, question
  grid, caution footline.
- The ten statements come from the Forum's RAG constituent-voice dataset
  ("NV1 - RAG - Phase 2 Constituent Input", Water sheet); fuller wording is
  preserved in `config/issues/nevada-water-scarcity.yaml`.
- Appendix H carries the full statement-by-statement crosswalk (bill
  tables, venue notes, open questions per statement).
- Fit notes: ten-statement table renders at 7.6pt with tightened cell
  padding; basket cards became labeled prose lines. No facts were dropped
  from the packet — detail lives in Appendices B, C, and H.
