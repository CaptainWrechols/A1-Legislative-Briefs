# Legislative Brief — NELIS Preliminary Package

| Field | Value |
|-------|-------|
| State | nevada |
| Issue ID | nevada-04-water-scarcity |
| Variant | **nelis-preliminary** (NELIS only) |
| Purpose | Preview of a completed brief package; assembly viability context |
| Status | DRAFT |
| Citation style | Chicago notes-bibliography |

## Files in this package

| File | Description |
|------|-------------|
| executive-summary.md | Issue Brief–style overview (GitHub-readable Markdown) |
| executive-summary.html | Visual layout matching Phase 2 Issue Brief v1.5 |
| executive-summary.pdf | Printable letter-size PDF (3 pages) |
| appendix-a-bills.md | Bill master table (147 NELIS bills) |
| appendix-b-bill-actions.md | Actions — INSUFFICIENT DATA |
| appendix-c-votes.md | Votes — INSUFFICIENT DATA |
| appendix-d-statutes.md | Statute chapter links |
| appendix-e-agency-documents.md | Agency / LCB documents |
| appendix-f-data-gaps.md | Gap inventory |
| sources-registry.json | Chicago note + bibliography entries |
| final-review-report.md | Automated review status |

## Isolation rule

Do **not** merge OpenStates data into this folder. When OpenStates enrichment is ready, build a separate clean Version 0 at `briefs/nevada/water-scarcity/version-0/` (or a new dated folder).


## Format reference

Phase 2 Issue Brief PDF (canonical path):

`briefs/phase-2/nevada/water-scarcity/issue-brief-v1.5.pdf`

Upload typo path (also present):

`briefs/phasse-2/nevada/water-scarcity/`


## Printable PDF

```bash
pip install weasyprint
python collectors/render_nelis_brief_pdf.py
```

Then open `executive-summary.pdf` and print.
