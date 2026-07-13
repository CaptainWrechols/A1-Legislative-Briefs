# Legislative Brief — NELIS Preliminary Package

| Field | Value |
|-------|-------|
| State | nevada |
| Issue ID | nevada-04-water-scarcity |
| Variant | **nelis-preliminary** (NELIS only) |
| Pipeline | Agents 2–10 (Agent 1 skipped; collection complete) |
| Verification | PASS_WITH_WARNINGS |
| Purpose | Preliminary assembly-viability briefing package |
| Status | DRAFT |
| Citation style | Chicago bibliography entries keyed [S#] |
| Format reference | `briefs/phase-2/nevada/water-scarcity/issue-brief-v1.5.pdf` |

## Files in this package

| File | Description |
|------|-------------|
| executive-summary.md | GitHub-readable Issue Brief–style overview |
| executive-summary.html | Visual layout matching Phase 2 Issue Brief v1.5 |
| executive-summary.pdf | Printable letter-size PDF |
| appendix-a-bills.md | 147 NELIS bills |
| appendix-b-bill-actions.md | INSUFFICIENT DATA |
| appendix-c-votes.md | INSUFFICIENT DATA |
| appendix-d-statutes.md | NRS 533 / 534 links |
| appendix-e-agency-documents.md | Agency / LCB documents |
| appendix-f-data-gaps.md | Gap inventory |
| sources-registry.json | Chicago-keyed sources |
| edit-log.md | Editor changes |
| tone-edit-log.md | Tone Editor changes |
| final-review-report.md | Final Reviewer checklist |
| legislative-brief-nelis-preliminary-complete.md | Concatenated package |

## Working files

`working/nevada/water-scarcity/nelis-preliminary/` — synthesis + analysis outputs from agents 3–4.

## Isolation rule

Do **not** merge OpenStates data into this folder. Build OpenStates Version 0 elsewhere.

## Printable PDF

```bash
pip install weasyprint
python collectors/render_nelis_brief_pdf.py
```
