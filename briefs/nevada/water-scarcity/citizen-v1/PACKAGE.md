# Package — Growth, Water Scarcity, and Long-Term Supply in Nevada (citizen-v4.0)

Design Packager v2.3 · 2026-07-20 · The Nevada Forum

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

## v4.0 layout notes

- Adult, prose-only front brief for working groups: title + subtitle,
  legislative landscape, Key numbers stat strip, proposal paragraphs grouped
  by record status (no bill on record / stalled / precedent exists),
  political terrain, new 2025 law, and one pointer line to the appendices.
- Removed per Forum direction (2026-07-20): version/kicker subtitle,
  how-to-use section, bill-path primer, all tables, discussion questions,
  data cautions, and the source-keys section (now Appendix I).
- Word export restyled to the Phase 2 system: Arial 9pt compact body, navy
  #1A2D4F title/H1, terracotta #C0392B ALL-CAPS section headers, 0.6-inch
  margins. `citizen-brief.docx` verified at 2 pages (LibreOffice render).
- Appendix I (Sources and review notes) holds the claim-to-source map and
  collection notes formerly in the front brief.
