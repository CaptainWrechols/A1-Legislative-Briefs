# Package — Housing Affordability in New Hampshire (citizen-v2.0)

Design Packager v2.3 · 2026-08-10 · The Forum

citizen-v2.0 is the combined legislative brief prepared for working-group and
legislator distribution, matching the **Nevada citizen-v4.0 format** (the
"Lege Brief" layout): the citizen brief, the proposal spotlights, the topic
glossary, and the legislative process glossary in one document. The brief
body carries the certified v1.2 record (289 policy bills, 59 laws; see
`../citizen-v1/review-report.md` and the completeness certification in
`../citizen-v1/appendices/I-sources-and-review-notes.md`). The spotlights
cover the five housing proposals from the **NH1 Phase 2 constituent proposal
grid** (June–July 2026 Community Conversations), now also encoded in
`config/issues/new-hampshire-housing-affordability.yaml` under
`constituent_proposals`. `citizen-v1/` is untouched for side-by-side
comparison and still holds Appendices A–I.

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the combined document |
| `citizen-brief.docx` | Word version — the primary deliverable (5 pages, LibreOffice-verified) |
| `citizen-brief.html` | Print-ready HTML companion (5 pages, Chrome-verified) |
| `proposal-spotlights.md` / `.docx` / `.html` | Standalone policy spotlights: each grid proposal as bulleted bill lists grouped by viability (already law / survived a repeal / proven support / stopped early / never filed), single column at 1.15 line spacing, editable Word footer (3 pages — five proposals vs. Nevada's four) |

## v2.0 format notes (mirroring NV v4.0)

- **One combined document**: brief → proposal spotlights → glossary →
  legislative process glossary, single column throughout.
- **Real Word footer** ("NH1 Housing Legislative Brief v2.0" plus an automatic
  page number) — an actual footer object, editable via Insert → Footer.
- No "THE FORUM" masthead block, per the internal team's format.
- Type: 18pt title, 12.5pt section headers, nothing below 10pt.
- The glossaries are New Hampshire-specific: the topic glossary defines only
  terms the brief and spotlights actually use; the process glossary covers NH
  practice (Inexpedient to Legislate, consent calendar, tabling, interim
  study, Rule 3-23, HB2 budget trailer, division vs. roll-call votes,
  Governor and Executive Council).
- "Never filed" statements rest on the certified complete 2020–2024 universe
  (see `working/.../certification-report.json`).
- Glossary entries state legal requirements ("a bill must pass both
  chambers") — descriptive uses of "must", not advice, matching the NV v4
  glossary convention.

## Rebuild

```bash
python collectors/export_docx_brief.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v2 \
  --no-masthead --footer "NH1 Housing Legislative Brief v2.0"
python collectors/export_brief_html.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v2 \
  --no-masthead --footer "NH1 Housing Legislative Brief v2.0"
```

## Rebuild the policy spotlights

```bash
python collectors/export_docx_brief.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v2 \
  --file proposal-spotlights --layout prose --no-masthead --footer "NH1 Housing Policy Spotlights v2.0"
python collectors/export_brief_html.py --brief-dir briefs/new-hampshire/housing-affordability/citizen-v2 \
  --file proposal-spotlights --layout prose --no-masthead --footer "NH1 Housing Policy Spotlights v2.0"
```
