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

## Send / print this file

**`legislative-brief-nelis-preliminary-complete.pdf`**

One Issue Brief–styled document with:

1. Executive summary  
2. Appendices A–F  
3. Verification report  
4. Final review report  
5. Selected sources  

Direct link (branch `cursor/nevada-brief-pipeline-a39c`):

https://github.com/CaptainWrechols/A1-Legislative-Briefs/blob/cursor/nevada-brief-pipeline-a39c/briefs/nevada/water-scarcity/nelis-preliminary/legislative-brief-nelis-preliminary-complete.pdf

## Files in this package

| File | Description |
|------|-------------|
| **legislative-brief-nelis-preliminary-complete.pdf** | **Full package PDF (use this)** |
| legislative-brief-nelis-preliminary-complete.html | Same full package in HTML |
| executive-summary.md / .html / .pdf | Summary only |
| appendix-a-bills.md … appendix-f-data-gaps.md | Individual appendices |
| sources-registry.json | Chicago-keyed sources |
| final-review-report.md | Final Reviewer checklist |
| edit-log.md / tone-edit-log.md | Pipeline edit logs |

## Regenerate the complete PDF

```bash
pip install weasyprint
python collectors/render_nelis_complete_pdf.py
```

Summary-only PDF:

```bash
python collectors/render_nelis_brief_pdf.py
```

## Isolation rule

Do **not** merge OpenStates data into this folder. Build OpenStates Version 0 elsewhere.
