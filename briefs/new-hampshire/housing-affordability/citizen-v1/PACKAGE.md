# Package notes — Housing Affordability in New Hampshire (citizen-v1)

Design Packager output notes. Visual tokens come from `config/forum-brand.yaml`,
extracted from the Phase 2 Issue Brief sample
(`templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`);
module shapes only — no Phase 2 text was copied.

## Files

| File | Built by | Notes |
|---|---|---|
| `citizen-brief.md` | citizen-brief-writer v2.3 | source of truth for the front brief |
| `citizen-brief.html` | `collectors/export_brief_html.py` | Phase 2 modules: masthead, terracotta H2s, navy stat strip; verified **2 US Letter pages** in headless Chrome |
| `citizen-brief.docx` | `collectors/export_docx_brief.py` (via `export_docx.py`) | direct formatting (Arial/RGB per run); verified **2 pages** in LibreOffice |
| `citizen-brief-print.css` | shared Phase 2 print CSS | tokens: navy `#1A2D4F`, terracotta `#C0392B`, Arial ~9–10pt body, 0.6in letter margins |
| `appendices/*.md` | `working/.../build-appendices-nh.py` (A–F, H); Appendix I hand-written | Appendix H is the HB2 budget-trailer section detail; no Appendix G (no text-diff data) |
| `appendices/appendices-print.html` | `collectors/build_appendices_print.py` | 45 print pages; TOC; navy-header tables |
| `appendices/appendices.docx` | `collectors/export_docx.py` | branded reference-doc conversion |

## Export / print steps

```bash
python3 collectors/export_brief_html.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v1
python3 working/new-hampshire/housing-affordability/build-appendices-nh.py
python3 collectors/build_appendices_print.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v1 \
  --title "Housing Affordability in New Hampshire" [...see git history for full flags]
python3 collectors/export_docx.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v1

# page-count verification
google-chrome --headless=new --no-sandbox --print-to-pdf=/tmp/b.pdf --no-pdf-header-footer citizen-brief.html  # 2 pages
soffice --headless --convert-to pdf citizen-brief.docx                                                          # 2 pages
```

To print: open `citizen-brief.html` (or `appendices/appendices-print.html`) in a
browser → Print → Save as PDF, US Letter, default margins off (CSS sets 0.6in).

If pandoc is unavailable for the Word export: open `citizen-brief.html` in
Microsoft Word and Save As `.docx`, or upload `citizen-brief.md` to Google Docs
and download as Word.

## Layout decisions

- Page 1 carries: masthead, landscape paragraph, Key numbers stat strip, the
  "Also in the budget bill (HB2)" callout (mission requirement), and the
  "Where new law exists" group. Page 2: stalled ideas, never-passed ideas,
  political terrain, new-law recap, appendix pointer.
- The HB2 callout renders as a normal terracotta section on page 1 rather than
  a tinted box, keeping the exporter unmodified; content satisfies the
  "callout" requirement (short, self-contained, whole-trailer vote warning).
- No facts were trimmed to fit; both renders landed at exactly 2 pages.
