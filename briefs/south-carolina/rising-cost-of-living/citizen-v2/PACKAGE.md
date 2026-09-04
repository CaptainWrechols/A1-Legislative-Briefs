# Package — Rising Cost of Living in South Carolina (citizen-v2.1)

Design Packager v2.1 · 2026-08-27, reworked 2026-09-04 (v2.1: brief re-centered on the final proposal grid; child care assistance section added for the reported legislator-discussion topic) · The Forum

The third South Carolina citizen brief, produced on the SC foundation
(certified 123rd–126th universe + prebuilt issue artifacts). Follows the
NV/NH combined citizen-brief product (the NV citizen-v4 format, as shipped
for SC slow-wage-growth): the two-page Phase 2 front brief, the proposal
spotlights, the glossary, and the legislative process glossary in **one
document**, plus a standalone spotlights companion and long appendices —
with the SC-specific page-1 **"Also in the state budget (provisos)"**
callout required by `docs/sc-issue-chat-workflow.md`.

## What's in this folder

| File | What it is |
|---|---|
| `SC1-Rising-Cost-of-Living-Lege-Brief.docx` | **THE DELIVERABLE** — the finalized, working-group-approved lege-brief format, cloned from `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx` (same format as SC1-Slow-Wage-Growth-Lege-Brief and the NH lege briefs): brief organized by distance to law → policy spotlights with reported grid cells and viability groups (incl. the childcare-topic spotlight) → glossary (own page) → legislative process glossary (own page), stat-card table, square-bullet spotlights, real Word footer ("SC1 Rising Cost of Living Legislative Brief v1.0" + page number). 10 pages, LibreOffice-verified |
| `SC1-Rising-Cost-of-Living-Lege-Brief.pdf` | PDF export of the deliverable (LibreOffice) |
| `lege-brief.md` | Source markdown of the deliverable (edit this, then rebuild) |
| `citizen-brief.md` | Combined-format source (front brief → spotlights → glossaries), kept alongside |
| `citizen-brief.html` | Print-ready Phase 2 HTML — **5 letter pages**, front brief on pages 1–2 (Chrome print-to-PDF verified) |
| `citizen-brief.docx` | Word version — **5 pages**, front brief on pages 1–2 (LibreOffice-verified), direct-formatted for cross-app fidelity |
| `proposal-spotlights.md` / `.html` / `.docx` | Standalone policy spotlights: each Phase 2 proposal as bulleted bill lists grouped by viability (already law / proven support / stopped early / never filed), single column, incl. the childcare-topic section — **4 pages** in both renders |
| `citizen-brief-print.css` | Phase 2 print tokens (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial) |
| `appendices/A…I-*.md` | Nine appendices (see `appendices/README.md`) |
| `appendices/appendices-print.html` | Combined print HTML with TOC — 81 letter pages |
| `appendices/appendices.docx` | Word version of the combined appendices — 83 pages (LibreOffice-verified) |
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

- Front brief (pages 1–2 of the combined document, v2.1): page 1 carries the
  landscape, key numbers, the proviso callout, and the utility-transparency
  and market-competition proposal sections; page 2 carries financial
  education, property/vehicle taxes, the childcare-topic section, political
  terrain, and the latest-session section. Each proposal section opens with
  the final grid's reported cells (labeled process input) and closes with
  the record. The companion sections — spotlights, glossaries — follow on
  pages 3–5.
- Front-brief-on-two-pages and 5-page totals verified in **both** renders
  (HTML→PDF via headless Chrome; DOCX→PDF via LibreOffice). Trims to fit
  moved detail into the spotlights/appendices — no facts were cut.

## Rebuild

```bash
# THE DELIVERABLE — lege-brief docx from the approved NV1 v1.6 template
python3 collectors/export_docx_lege_brief.py \
  --source briefs/south-carolina/rising-cost-of-living/citizen-v2/lege-brief.md \
  --out briefs/south-carolina/rising-cost-of-living/citizen-v2/SC1-Rising-Cost-of-Living-Lege-Brief.docx \
  --footer "SC1 Rising Cost of Living Legislative Brief v1.0" --polish-breaks
# PDF: soffice --headless --convert-to pdf SC1-Rising-Cost-of-Living-Lege-Brief.docx

# HTML combined document (Phase 2 shell)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2

# Word front brief (direct writer, cross-app safe)
python3 collectors/export_docx_brief.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2

# Standalone policy spotlights (prose layout, HTML + Word)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Rising Cost of Living Policy Spotlights v2.1"
python3 collectors/export_docx_brief.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Rising Cost of Living Policy Spotlights v2.1"

# Combined appendices print HTML (TOC descriptions + SC data note)
python3 collectors/build_appendices_print.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2 \
  --title "Rising Cost of Living in South Carolina" \
  --kicker "SOUTH CAROLINA · 2019–2026" \
  --dek "Detail behind the two-page front brief: bills, votes, sponsors, budget provisos, and sources, 2019–2026." \
  --note "South Carolina publishes committee outcomes but never committee vote tallies; no committee vote counts appear anywhere in these appendices. Floor roll-call counts are verbatim from the chamber vote histories. Party labels are intentionally absent (no roster join was fetched)." \
  --footline "The Forum · Citizen Brief citizen-v2.1 · Rising Cost of Living in South Carolina · September 2026" \
  --descriptions '{"A":"Every curated bill: plain topic, theme, tier, result, where it stopped","B":"Theme scorecards with history baskets and certainty labels","C":"Passage-type floor votes, verbatim; high-support non-enactments","D":"Frequent lead sponsors; verbatim sponsor line per policy bill","E":"Milestone paths for the 22 bills the front brief leans on","F":"What this data can and cannot say","G":"Cost-of-living provisos in each state budget year, incl. childcare vouchers and 4K","H":"The final grid proposals with reported cells, matched against the record; childcare addendum","I":"Claim-to-source mapping, collection notes, review status"}'

# Word exports (appendices via pandoc + branded reference doc)
python3 collectors/export_docx.py --brief-dir briefs/south-carolina/rising-cost-of-living/citizen-v2
```

Print to PDF: open either HTML in a browser → Print → Save as PDF (Letter,
default margins — the CSS sets 0.6in). If pandoc is unavailable for the
appendices: open `appendices-print.html` in Word directly, or upload the
markdown to Google Docs and download as .docx.

## Data provenance (short)

Everything derives from the certified SC universe and prebuilt issue
artifacts on `main` — no new scraping (one out-of-record verification: the
personal-finance graduation regulation's effective status, checked against
the State Register; see Appendix F item 8). Working chain:
`build-curation.py` → `curation-map.json` (271 of 6,814 Pass 1 hits, plus 3
universe adds, incl. the 17-bill childcare theme added 2026-09-04) → `build-evidence-pack.py` → `evidence-pack.json` →
`reality-map.{json,md}` → this package. Proviso picks:
`build-proviso-curation.py` → `proviso-curated.json` (43 provisos, 6 enacted
cycles + the FY 2020-21 gap). Gate: `python3 -m
collectors.sc.verify_completeness --strict` = PASS_WITH_WARNINGS (21/1/0;
the warning is the optional OpenStates mirror, disclosed in Appendix I).
