# Package — K-12 Educational Outcomes in Nevada (citizen-v4.0)

Design Packager v2.3 · 2026-07-30 · The Nevada Forum

citizen-v4.0 is the combined legislative brief prepared for working-group
distribution, matching the internal team's format (the "NV1 Lege Brief"
layout): the citizen brief, the proposal spotlights, the glossary, and the
legislative process glossary in one document. Content carries the
plain-language wording from the 2026-07-29 review. `citizen-v1/` through
`citizen-v3/` are untouched for side-by-side comparison.

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the combined document |
| `citizen-brief.docx` | Word version — the primary deliverable (5 pages, LibreOffice-verified) |
| `citizen-brief.html` | Print-ready HTML companion |

## v4.0 format notes

- **One combined document**: brief → proposal spotlights → glossary →
  legislative process glossary, single column throughout.
- **Real Word footer** ("NV1 K-12 Education Legislative Brief v4.0" plus an automatic page number) — an
  actual footer object, editable via Insert → Footer in Word; not body text.
- No "THE FORUM" masthead block, per the internal team's format.
- Spotlight sections appear without the "Working-group proposal" note lines,
  per the internal team's format.
- Type: 18pt title, 12.5pt section headers, nothing below 10pt (footer text
  is intentionally small and freely editable).
- Appendices A–I remain in `../citizen-v3/appendices/`.

## Rebuild

```bash
python collectors/export_docx_brief.py --brief-dir briefs/nevada/k-12_educational_outcomes/citizen-v4 \
  --no-masthead --footer "NV1 K-12 Education Legislative Brief v4.0"
python collectors/export_brief_html.py --brief-dir briefs/nevada/k-12_educational_outcomes/citizen-v4 \
  --no-masthead --footer "NV1 K-12 Education Legislative Brief v4.0"
```
