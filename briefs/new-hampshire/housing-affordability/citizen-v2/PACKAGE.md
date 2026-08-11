# Package — NH1 Housing Legislative Brief v1.0

The Forum · 2026-08-11 · **the template for all New Hampshire lege briefs**

This folder holds the combined New Hampshire housing legislative brief in the
**finalized, working-group-approved format** — cloned from
`templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`, the actual document
used with the Nevada water working group. Format (fonts, sizes, colors,
section architecture, stat-card table, square-bullet spotlights, two-column
glossaries, footer) is identical by construction: the exporter reuses the
approved file's styles, numbering, theme, and section-break structure and
regenerates only the content.

## What's in this folder

| File | What it is |
|---|---|
| `NH1-Housing-Lege-Brief.docx` | **The deliverable.** 7 pages, LibreOffice-verified: brief → policy spotlights → glossary → legislative process glossary; real Word footer ("NH1 Housing Legislative Brief v1.0" + page number) |
| `lege-brief.md` | Source markdown (edit this, then rebuild) |
| `appendices/` | Appendices A–I (A bills · B themes · C votes · D sponsors · E paths · F limits · H HB2 sections · I sources & certification) as markdown, plus `appendices-print.html` (77 print pages) and `appendices.docx` |
| `appendices/NH1-Housing-Master-Appendix.docx` | **Master Appendix** — all appendices in one Word document (title page + A–I, 86 pages) |
| `appendices/NH1-Housing-Master-Appendix.pdf` | **Master Appendix (PDF)** — same content in the Phase 2 print styling with a table of contents (77 pages) |
| `citizen-brief-print.css` | Print CSS used by the appendices HTML |

The review record (review-report, completeness certification) remains in `../citizen-v1/`.

## Document architecture (matches NV1 v1.6 exactly)

1. Title + dek
2. WHAT THIS BRIEF COVERS + 4-cell stat-card table
3. ALSO IN THE BUDGET BILL (HB2) — NH-specific content section, same modules
4. CLOSEST TO LAW: BILLS THAT PASSED BOTH CHAMBERS (vetoed / died between chambers)
5. PROVEN SUPPORT: CLEARED A CHAMBER OR A COMMITTEE
6. ALREADY LAW — AND THE OPENINGS AROUND IT (new laws / willing to go further)
7. LITTLE TRACTION YET: NEVER FILED OR STOPPED EARLY
8. WHERE THERE IS MOVEMENT — AND WHERE THERE IS NONE
9. FEDERAL OVERLAP: WHAT WASHINGTON ALREADY COVERS
10. Policy Spotlights — the five proposals from the NH1 Phase 2 constituent
    grid (editable .docx revision), each with viability-grouped bullet lists
11. GLOSSARY (two-column, NH-specific terms only)
12. LEGISLATIVE PROCESS GLOSSARY (two-column; reusable verbatim for every NH brief)

## Content provenance

- Record: the certified 289-bill policy set (see `../citizen-v1/appendices/I-sources-and-review-notes.md`,
  including the full-universe completeness certification).
- Proposals: `config/issues/new-hampshire-housing-affordability.yaml` →
  `constituent_proposals` (encoded from the grid .docx).
- Automated checks re-run on this document: no advice language; all 54 cited
  bills exist in the evidence pack; every vote pair matches the official
  record (SB454's 180–176 tabling is a division-vote tally from the docket;
  SB203's 19–0 is its recorded House committee vote).

## Rebuild

```bash
python collectors/export_docx_lege_brief.py \
  --source briefs/new-hampshire/housing-affordability/citizen-v2/lege-brief.md \
  --out briefs/new-hampshire/housing-affordability/citizen-v2/NH1-Housing-Lege-Brief.docx \
  --footer "NH1 Housing Legislative Brief v1.0"
```

## Reusing this as the template for other NH briefs

1. Copy `lege-brief.md` for the new issue; keep the section architecture and
   the LEGISLATIVE PROCESS GLOSSARY verbatim; replace the topic content,
   spotlights, and topic glossary.
2. Rebuild with the exporter, setting `--footer "NH1 <Issue> Legislative Brief v1.0"`.
3. The format authority is `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`;
   never restyle by hand — change the template file if the format itself changes.
