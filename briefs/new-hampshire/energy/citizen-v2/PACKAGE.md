# Package — NH1 Energy Legislative Brief v1.0

The Forum · 2026-08-12 · built on the New Hampshire lege-brief template
(`briefs/new-hampshire/public-education/citizen-v2/` is the exemplar)

This folder holds the combined New Hampshire energy legislative brief in the
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
| `NH1-Energy-Lege-Brief.docx` | **The deliverable.** 8 pages, LibreOffice-verified: brief → policy spotlights (the five NH1 energy grid proposals) → glossary (own page) → legislative process glossary (own page); template separator rules incl. the navy rule above Policy Spotlights; real Word footer ("NH1 Energy Legislative Brief v1.0" + page number, verified on one line without the footer-tab fix — this label is shorter than the education packet's) |
| `lege-brief.md` | Source markdown (edit this, then rebuild) |
| `appendices/` | Appendices A–I (A bills · B themes · C votes · D sponsors · E paths · F limits · G bill-by-bill grid · H HB2 sections · I sources & both certifications) as markdown, plus `appendices-print.html` and `appendices.docx` (201 pp in LibreOffice) |
| `appendices/NH1-Energy-Master-Appendix.docx` | **Master Appendix** — all appendices in one Word document (title page + A–I; 202 pp in LibreOffice) |
| `appendices/NH1-Energy-Master-Appendix.pdf` | **Master Appendix (PDF)** — same content in the Phase 2 print styling with a table of contents (161 pages) |
| `citizen-brief-print.css` | Print CSS used by the appendices HTML |

## Document architecture (matches NV1 v1.6 exactly)

1. Title + dek
2. WHAT THIS BRIEF COVERS + 4-cell stat-card table
3. ALSO IN THE BUDGET BILL (HB2) — NH-specific content section, same modules
4. CLOSEST TO LAW: BILLS THAT PASSED BOTH CHAMBERS (vetoed / died between chambers)
5. PROVEN SUPPORT: CLEARED A CHAMBER OR A COMMITTEE
6. ALREADY LAW — AND THE OPENINGS AROUND IT (new laws / willing to go further)
7. LITTLE TRACTION YET: STOPPED EARLY (all five proposals have been filed —
   the untraveled ground is their harder versions)
8. WHERE THERE IS MOVEMENT — AND WHERE THERE IS NONE
9. FEDERAL OVERLAP: WHAT WASHINGTON ALREADY COVERS (heavy here: FERC and
   ISO-New England wholesale markets, federal siting/licensing, clean-energy
   tax credits, LIHEAP, the federal Weatherization Assistance Program —
   descriptive only)
10. Policy Spotlights — the five proposals from the NH1 Phase 2 constituent
    grid (Energy Cost, Sourcing, and Reliability section, editable revision),
    each with viability-grouped bullet lists
11. GLOSSARY (two-column, NH energy terms only)
12. LEGISLATIVE PROCESS GLOSSARY (two-column; shared across NH briefs —
    identical to the public-education brief's except the four issue-example
    clauses, which describe this record's vetoes, deadline deaths,
    appointments, and sponsor patterns instead of the education record's)

## Content provenance

- Record: the certified 375-bill policy set (see `appendices/I-sources-and-review-notes.md`,
  including the full-universe completeness certifications for BOTH universes:
  the 5,467-bill 2020–2024 bulk mirror and the 2,234-bill 2025–2026 SQL
  legislation table).
- Proposals: `config/issues/new-hampshire-energy.yaml` →
  `constituent_proposals` (encoded from the grid document; this grid section
  carries no ★ markers).
- Automated checks on this document (`working/new-hampshire/energy/scan-lege-brief.py`):
  no advice language; all 101 cited bills exist in the evidence pack; every
  vote pair matches the official record (one documented committee-vote
  exception, labeled as such in the brief: HR16's 21–0 committee report
  ahead of its consent-calendar adoption, resolved from House Journal No. 3,
  February 16, 2022 — a GenCourt docket-mirror gap).

## Rebuild

```bash
python3 collectors/export_docx_lege_brief.py \
  --source briefs/new-hampshire/energy/citizen-v2/lege-brief.md \
  --out briefs/new-hampshire/energy/citizen-v2/NH1-Energy-Lege-Brief.docx \
  --footer "NH1 Energy Legislative Brief v1.0" --polish-breaks
# --polish-breaks (documented per-issue knob in the exporter; default off):
#   template separator rules (navy double rule above Policy Spotlights, gray
#   rules over the appendix pointer and closing the spotlights), template-
#   faithful glossary section structure, each glossary on its own single
#   page, keep-with-next headings and widow control
# The footer-tab fix (fix-footer-tabs.py in the education packet) is NOT
# needed here: "NH1 Energy Legislative Brief v1.0" is short enough that the
# page number stays on one line with the template's ten tabs (verified
# visually in the LibreOffice render).

python3 working/new-hampshire/energy/build-appendices-nh.py
python3 collectors/build_appendices_print.py --brief-dir briefs/new-hampshire/energy/citizen-v2 [...flags in git history]
python3 collectors/export_docx.py --brief-dir briefs/new-hampshire/energy/citizen-v2
python3 working/new-hampshire/energy/build-master-appendix.py   # run Chrome in tmux — it can hang on exit
```

The format authority is `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`;
never restyle by hand — change the template file if the format itself changes.
