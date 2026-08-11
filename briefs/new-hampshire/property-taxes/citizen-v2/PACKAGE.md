# Package — NH1 Property Taxes Legislative Brief v1.0

The Forum · 2026-08-11 · built on the New Hampshire lege-brief template
(`briefs/new-hampshire/housing-affordability/citizen-v2/` is the exemplar)

This folder holds the combined New Hampshire property-taxes legislative brief
in the **finalized, working-group-approved format** — cloned from
`templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`, the actual document
used with the Nevada water working group. Format (fonts, sizes, colors,
section architecture, stat-card table, square-bullet spotlights, two-column
glossaries, footer) is identical by construction: the exporter reuses the
approved file's styles, numbering, theme, and section-break structure and
regenerates only the content.

## What's in this folder

| File | What it is |
|---|---|
| `NH1-Property-Taxes-Lege-Brief.docx` | **The deliverable.** 8 pages, LibreOffice-verified: brief → policy spotlights (six NH1 grid proposals) → glossary → legislative process glossary; real Word footer ("NH1 Property Taxes Legislative Brief v1.0" + page number) |
| `lege-brief.md` | Source markdown (edit this, then rebuild) |
| `appendices/` | Appendices A–I (A bills · B themes · C votes · D sponsors · E paths · F limits · G bill-by-bill grid · H HB2 sections · I sources & certification) as markdown, plus `appendices-print.html` and `appendices.docx` (213 pp) |
| `appendices/NH1-Property-Taxes-Master-Appendix.docx` | **Master Appendix** — all appendices in one Word document (title page + A–I; 212 pp in LibreOffice) |
| `appendices/NH1-Property-Taxes-Master-Appendix.pdf` | **Master Appendix (PDF)** — same content in the Phase 2 print styling with a table of contents (171 pages) |
| `citizen-brief-print.css` | Print CSS used by the appendices HTML |

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
10. Policy Spotlights — the six proposals from the NH1 Phase 2 constituent
    grid (Property Taxes and Revenue Needs section, editable .docx revision),
    each with viability-grouped bullet lists
11. GLOSSARY (two-column, NH tax terms only)
12. LEGISLATIVE PROCESS GLOSSARY (two-column; shared across NH briefs —
    identical to the housing brief's except the four issue-example clauses,
    which describe this record's vetoes, deadline deaths, appointments, and
    sponsor patterns instead of housing's)

## Content provenance

- Record: the certified 445-bill policy set (see `appendices/I-sources-and-review-notes.md`,
  including the full-universe completeness certification).
- Proposals: `config/issues/new-hampshire-property-taxes.yaml` →
  `constituent_proposals` (encoded from the grid .docx).
- Automated checks on this document (`working/new-hampshire/property-taxes/scan-lege-brief.py`):
  no advice language; all 85 cited bills exist in the evidence pack; every
  vote pair matches the official record (HB675's 170–185 reconsideration is a
  division-vote tally from the official docket, labeled as such).

## Rebuild

```bash
python3 collectors/export_docx_lege_brief.py \
  --source briefs/new-hampshire/property-taxes/citizen-v2/lege-brief.md \
  --out briefs/new-hampshire/property-taxes/citizen-v2/NH1-Property-Taxes-Lege-Brief.docx \
  --footer "NH1 Property Taxes Legislative Brief v1.0"

python3 working/new-hampshire/property-taxes/build-appendices-nh.py
python3 collectors/build_appendices_print.py --brief-dir briefs/new-hampshire/property-taxes/citizen-v2 [...flags in git history]
python3 collectors/export_docx.py --brief-dir briefs/new-hampshire/property-taxes/citizen-v2
python3 working/new-hampshire/property-taxes/build-master-appendix.py
```

The format authority is `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`;
never restyle by hand — change the template file if the format itself changes.
