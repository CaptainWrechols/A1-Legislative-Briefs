# Package — NH1 Public Education Legislative Brief v1.0

The Forum · 2026-08-12 · built on the New Hampshire lege-brief template
(`briefs/new-hampshire/property-taxes/citizen-v2/` is the exemplar)

This folder holds the combined New Hampshire public-education legislative
brief in the **finalized, working-group-approved format** — cloned from
`templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`, the actual document
used with the Nevada water working group. Format (fonts, sizes, colors,
section architecture, stat-card table, square-bullet spotlights, two-column
glossaries, footer) is identical by construction: the exporter reuses the
approved file's styles, numbering, theme, and section-break structure and
regenerates only the content.

## What's in this folder

| File | What it is |
|---|---|
| `NH1-Public-Education-Lege-Brief.docx` | **The deliverable.** 8 pages, LibreOffice-verified: brief → policy spotlights (six NH1 grid proposals) → glossary (own page) → legislative process glossary (own page); template separator rules incl. the navy rule above Policy Spotlights; real Word footer ("NH1 Public Education Legislative Brief v1.0" + page number) |
| `lege-brief.md` | Source markdown (edit this, then rebuild) |
| `appendices/` | Appendices A–I (A bills · B themes · C votes · D sponsors · E paths · F limits · G bill-by-bill grid · H HB2 sections · I sources & both certifications) as markdown, plus `appendices-print.html` and `appendices.docx` (410 pp in LibreOffice) |
| `appendices/NH1-Public-Education-Master-Appendix.docx` | **Master Appendix** — all appendices in one Word document (title page + A–I; 410 pp in LibreOffice) |
| `appendices/NH1-Public-Education-Master-Appendix.pdf` | **Master Appendix (PDF)** — same content in the Phase 2 print styling with a table of contents (328 pages) |
| `citizen-brief-print.css` | Print CSS used by the appendices HTML |

## Document architecture (matches NV1 v1.6 exactly)

1. Title + dek
2. WHAT THIS BRIEF COVERS + 4-cell stat-card table
3. ALSO IN THE BUDGET BILL (HB2) — NH-specific content section, same modules
4. CLOSEST TO LAW: BILLS THAT PASSED BOTH CHAMBERS (vetoed / died between chambers)
5. PROVEN SUPPORT: CLEARED A CHAMBER OR A COMMITTEE
6. ALREADY LAW — AND THE OPENINGS AROUND IT (new laws / willing to go further)
7. LITTLE TRACTION YET: STOPPED EARLY (all six proposals have been filed — the
   contrast with the tax packet's "never filed" framing is the record's)
8. WHERE THERE IS MOVEMENT — AND WHERE THERE IS NONE
9. FEDERAL OVERLAP: WHAT WASHINGTON ALREADY COVERS
10. Policy Spotlights — the six proposals from the NH1 Phase 2 constituent
    grid (K-12 Public Education Outcomes section, editable revision),
    each with viability-grouped bullet lists
11. GLOSSARY (two-column, NH education terms only)
12. LEGISLATIVE PROCESS GLOSSARY (two-column; shared across NH briefs —
    identical to the property-taxes brief's except the four issue-example
    clauses, which describe this record's vetoes, deadline deaths,
    appointments, and sponsor patterns instead of the tax record's)

## Content provenance

- Record: the certified 894-bill policy set (see `appendices/I-sources-and-review-notes.md`,
  including the full-universe completeness certifications for BOTH universes:
  the 5,467-bill 2020–2024 bulk mirror and the 2,234-bill 2025–2026 SQL
  legislation table).
- Proposals: `config/issues/new-hampshire-public-education.yaml` →
  `constituent_proposals` (encoded from the grid document).
- Automated checks on this document (`working/new-hampshire/public-education/scan-lege-brief.py`):
  no advice language; all 109 cited bills exist in the evidence pack; every
  vote pair matches the official record (three documented docket-tally
  exceptions, labeled as such in the brief: HB675's 170–185 division-vote
  reconsideration, SB523's 187–193 division vote lacking two-thirds, and
  HB765's 18–0 recorded committee vote).

## Rebuild

```bash
python3 collectors/export_docx_lege_brief.py \
  --source briefs/new-hampshire/public-education/citizen-v2/lege-brief.md \
  --out briefs/new-hampshire/public-education/citizen-v2/NH1-Public-Education-Lege-Brief.docx \
  --footer "NH1 Public Education Legislative Brief v1.0" --polish-breaks
# --polish-breaks (documented per-issue knob in the exporter; default off):
#   template separator rules (navy double rule above Policy Spotlights, gray
#   rules over the appendix pointer and closing the spotlights), template-
#   faithful glossary section structure, each glossary on its own single
#   page, keep-with-next headings and widow control

python3 working/new-hampshire/public-education/fix-footer-tabs.py   # keeps the page number on one line for this longer footer label
python3 working/new-hampshire/public-education/build-appendices-nh.py
python3 collectors/build_appendices_print.py --brief-dir briefs/new-hampshire/public-education/citizen-v2 [...flags in git history]
python3 collectors/export_docx.py --brief-dir briefs/new-hampshire/public-education/citizen-v2
python3 working/new-hampshire/public-education/build-master-appendix.py   # run Chrome in tmux — it can hang on exit
```

The format authority is `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`;
never restyle by hand — change the template file if the format itself changes.
