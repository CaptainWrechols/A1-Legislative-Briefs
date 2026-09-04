# Package — Slow Wage Growth in South Carolina (citizen-v2.0)

Design Packager v2.1 · 2026-08-27 · The Forum

The first South Carolina citizen brief, produced on the SC foundation
(certified 123rd–126th universe + prebuilt issue artifacts). Follows the
NV/NH combined citizen-brief product (the NV citizen-v4 format): the
two-page Phase 2 front brief, the proposal spotlights, the glossary, and
the legislative process glossary in **one document**, plus a standalone
spotlights companion and long appendices — with the SC-specific page-1
**"Also in the state budget (provisos)"** callout required by
`docs/sc-issue-chat-workflow.md`.

## What's in this folder

| File | What it is |
|---|---|
| `SC1-Slow-Wage-Growth-Lege-Brief.docx` | **THE DELIVERABLE (v1.1)** — the finalized, working-group-approved lege-brief format, cloned from `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx` (same format as NH1-Energy/Housing/Property-Taxes/Public-Education-Lege-Brief): brief → policy spotlights → glossary (own page) → legislative process glossary (own page), stat-card table, square-bullet spotlights, two-column glossaries, real Word footer ("SC1 Slow Wage Growth Legislative Brief v1.1" + page number). 8 pages, LibreOffice-verified. **v1.1 (2026-09-04) is reworked around the FINAL proposal grid** ("SC1 – Slow Wage Growth", three proposals): the standalone raise-minimum-wage item is folded into the age-bracketed proposal per the grid, and each spotlight carries the grid's frequency/consensus/concerns with record facts addressed to them (who the enacted programs reach, the awareness provisos, tax credit vs. never-filed direct bonus) |
| `SC1-Slow-Wage-Growth-Lege-Brief.pdf` | PDF export of the deliverable (LibreOffice) |
| `lege-brief.md` | Source markdown of the deliverable (edit this, then rebuild) |
| `citizen-brief.md` | Earlier combined-format source (front brief → spotlights → glossaries), kept for provenance; predates the final grid |
| `proposal-spotlights.md`/`.html`/`.docx` | Standalone spotlights from the Phase 2 four-proposal set — superseded by the final-grid spotlights inside the lege brief; kept for provenance |
| `citizen-brief.html` | Print-ready Phase 2 HTML — **4 letter pages**, front brief on pages 1–2 (Chrome print-to-PDF verified) |
| `citizen-brief.docx` | Word version — **4 pages**, front brief on pages 1–2 (LibreOffice-verified), direct-formatted for cross-app fidelity |
| `proposal-spotlights.md` / `.html` / `.docx` | Standalone policy spotlights: each Phase 2 proposal as bulleted bill lists grouped by viability (already law / proven support / stopped early / never filed), single column — **2 pages** in both renders |
| `citizen-brief-print.css` | Phase 2 print tokens (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial) |
| `appendices/A…I-*.md` | Nine appendices (see `appendices/README.md`) |
| `appendices/appendices-print.html` | Combined print HTML with TOC — 44 letter pages |
| `appendices/appendices.docx` | Word version of the combined appendices — 41 pages (LibreOffice-verified) |
| `review-report.md` / `.json` | Citizen Reviewer v2.3 gate results |

## Visual system

Tokens from `config/forum-brand.yaml`, mirroring the Phase 2 Issue Brief
sample (`templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`)
— module shapes and tokens only, no sample text. Modules used: eyebrow
masthead, terracotta ALL-CAPS section headers, navy-bar stat strip
(4 cards + 1 long stat as a highlighted bullet), bold-lead prose paragraphs,
muted footline. No tables in the front brief; appendix tables use the
navy-header comparison style with repeating headers across page breaks.

## Page discipline

- Front brief (pages 1–2 of the combined document): page 1 carries the
  landscape, key numbers, the proviso callout, and the two strongest
  history baskets; page 2 carries the rarely-moved basket, political
  terrain, and the latest-session section. The companion sections —
  proposal spotlights, glossary, legislative process glossary — follow on
  pages 3–4, matching the NV citizen-v4 combined format.
- Front-brief-on-two-pages and 4-page totals verified in **both** renders
  (HTML→PDF via headless Chrome; DOCX→PDF via LibreOffice). No content was
  cut to fit.

## Rebuild

```bash
# THE DELIVERABLE — lege-brief docx from the approved NV1 v1.6 template
python3 collectors/export_docx_lege_brief.py \
  --source briefs/south-carolina/slow-wage-growth/citizen-v2/lege-brief.md \
  --out briefs/south-carolina/slow-wage-growth/citizen-v2/SC1-Slow-Wage-Growth-Lege-Brief.docx \
  --footer "SC1 Slow Wage Growth Legislative Brief v1.1" --polish-breaks
# PDF: soffice --headless --convert-to pdf SC1-Slow-Wage-Growth-Lege-Brief.docx

# HTML combined document (Phase 2 shell)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2

# Standalone policy spotlights (prose layout, HTML + Word)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Slow Wage Growth Policy Spotlights v2.0"
python3 collectors/export_docx_brief.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Slow Wage Growth Policy Spotlights v2.0"

# Combined appendices print HTML (TOC descriptions + SC data note)
python3 collectors/build_appendices_print.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2 \
  --title "Slow Wage Growth in South Carolina" \
  --kicker "SOUTH CAROLINA · 2019–2026" \
  --dek "Detail behind the two-page front brief: bills, votes, sponsors, budget provisos, and sources, 2019–2026." \
  --note "South Carolina publishes committee outcomes but never committee vote tallies; no committee vote counts appear anywhere in these appendices. Floor roll-call counts are verbatim from the chamber vote histories. Party labels are intentionally absent (no roster join was fetched)." \
  --footline "The Forum · Citizen Brief citizen-v2.0 · Slow Wage Growth in South Carolina · August 2026" \
  --descriptions '{"A":"Every curated bill: plain topic, theme, tier, result, where it stopped","B":"Theme scorecards with history baskets and certainty labels","C":"Passage-type floor votes, verbatim; high-support non-enactments","D":"Frequent lead sponsors; verbatim sponsor line per policy bill","E":"Milestone paths for the 15 bills the front brief leans on","F":"What this data can and cannot say","G":"Wage and workforce provisos in each state budget year","H":"The four Phase 2 citizen proposals matched against the record","I":"Claim-to-source mapping, collection notes, review status"}'

# Word exports (front brief via direct writer; appendices via pandoc + branded reference doc)
python3 collectors/export_docx.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2
```

Print to PDF: open either HTML in a browser → Print → Save as PDF (Letter,
default margins — the CSS sets 0.6in). If pandoc is unavailable for the
appendices: open `appendices-print.html` in Word directly, or upload the
markdown to Google Docs and download as .docx.

## Data provenance (short)

Everything derives from the certified SC universe and prebuilt issue
artifacts on `main` — no new scraping. Working chain:
`build-curation.py` → `curation-map.json` (133 of 5,744 Pass 1 hits) →
`build-evidence-pack.py` → `evidence-pack.json` → `reality-map.{json,md}` →
this package. Proviso picks: `build-proviso-curation.py` →
`proviso-curated.json`. Gate: `python3 -m collectors.sc.verify_completeness
--strict` = PASS_WITH_WARNINGS (both warnings disclosed in Appendix I).
