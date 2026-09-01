# Package — Growth, Infrastructure, and Roads in South Carolina (citizen-v2.0)

Design Packager v2.1 · 2026-09-01 · The Forum

The third South Carolina citizen brief, produced on the SC foundation
(certified 123rd–126th universe + prebuilt issue artifacts). Follows the
NV/NH combined citizen-brief product (the NV citizen-v4 format, as applied
to SC by the approved slow-wage-growth, responsive-elected-leaders, and
rising-cost-of-living packages): the two-page Phase 2 front brief, the
proposal spotlights, the glossary, and the legislative process glossary in
**one document**, plus a standalone spotlights companion and long
appendices — with the SC-specific page-1 **"Also in the state budget
(provisos)"** callout required by `docs/sc-issue-chat-workflow.md`.

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Combined-format source (front brief → spotlights → glossaries) |
| `citizen-brief.html` | Print-ready Phase 2 HTML — **6 letter pages**, front brief on pages 1–2 (Chrome print-to-PDF verified; the proviso callout renders on page 1) |
| `citizen-brief.docx` | Word version — **6 pages**, front brief on pages 1–2 (LibreOffice-verified), direct-formatted for cross-app fidelity |
| `proposal-spotlights.md` / `.html` / `.docx` | Standalone policy spotlights: each of the seven Phase 2 proposals as bulleted bill lists grouped by viability (already law / got support / stopped early / never filed), single column — 5 pages HTML, 4 pages Word |
| `citizen-brief-print.css` | Phase 2 print tokens (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial) |
| `appendices/A…I-*.md` | Nine appendices (see `appendices/README.md`) |
| `appendices/appendices-print.html` | Combined print HTML with TOC — 60 letter pages (Chrome-verified) |
| `appendices/appendices.docx` | Word version of the combined appendices — 56 pages (LibreOffice-verified) |
| `review-report.md` / `.json` | Citizen Reviewer v2.3 gate results |

## Visual system

Tokens from `config/forum-brand.yaml`, mirroring the Phase 2 Issue Brief
sample (`templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`)
— module shapes and tokens only, no sample text. Modules used: eyebrow
masthead, terracotta ALL-CAPS section headers, navy-bar stat strip,
bold-lead prose paragraphs, muted footline. No tables in the front brief;
appendix tables use the navy-header comparison style with repeating headers
across page breaks.

## Page discipline

- Front brief (pages 1–2 of the combined document): page 1 carries the
  landscape, key numbers, the required proviso callout, and the start of
  the where-something-finished basket; page 2 carries got-support,
  rarely-moved, political terrain, and the latest-session section, with
  the spotlights header falling at the end of page 2. The companion
  sections — proposal spotlights, glossary, legislative process glossary —
  follow on pages 3–6, matching the combined format.
- Front-brief-on-two-pages and totals verified in **both** renders
  (HTML→PDF via headless Chrome; DOCX→PDF via LibreOffice). No content was
  cut to fit.

## Rebuild

```bash
# HTML combined document (Phase 2 shell)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/growth-infrastructure-roads/citizen-v2

# Standalone policy spotlights (prose layout, HTML + Word)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/growth-infrastructure-roads/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Growth, Infrastructure, and Roads Policy Spotlights v2.0"
python3 collectors/export_docx_brief.py --brief-dir briefs/south-carolina/growth-infrastructure-roads/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC1 Growth, Infrastructure, and Roads Policy Spotlights v2.0"

# Combined appendices print HTML (TOC descriptions + SC data note)
python3 collectors/build_appendices_print.py --brief-dir briefs/south-carolina/growth-infrastructure-roads/citizen-v2 \
  --title "Growth, Infrastructure, and Roads in South Carolina" \
  --kicker "SOUTH CAROLINA · 2019–2026" \
  --dek "Detail behind the two-page front brief: bills, votes, sponsors, budget provisos, and sources, 2019–2026." \
  --note "South Carolina publishes committee outcomes but never committee vote tallies; no committee vote counts appear anywhere in these appendices. Floor roll-call counts are verbatim from the chamber vote histories. Party labels are intentionally absent (no roster join was fetched). Many bills show no roll calls at all: South Carolina uses voice votes heavily, and an empty vote history is a real answer." \
  --footline "The Forum · Citizen Brief citizen-v2.0 · Growth, Infrastructure, and Roads in South Carolina · September 2026" \
  --descriptions '{"A":"Every curated bill: plain topic, theme, tier, result, where it stopped","B":"Theme scorecards with history baskets and certainty labels","C":"Passage/adoption-type floor votes, verbatim; high-support non-enactments","D":"Frequent lead sponsors; verbatim sponsor line per policy bill","E":"Milestone paths for the 15 measures the front brief leans on","F":"What this data can and cannot say","G":"Roads and growth provisos in each state budget year","H":"The seven Phase 2 citizen proposals matched against the record","I":"Claim-to-source mapping, collection notes, review status"}'

# Word exports (front brief via direct writer; appendices via pandoc + branded reference doc)
python3 collectors/export_docx.py --brief-dir briefs/south-carolina/growth-infrastructure-roads/citizen-v2
```

Print to PDF: open either HTML in a browser → Print → Save as PDF (Letter,
default margins — the CSS sets 0.6in). If pandoc is unavailable for the
appendices: open `appendices-print.html` in Word directly, or upload the
markdown to Google Docs and download as .docx.

## Data provenance (short)

Everything derives from the certified SC universe and prebuilt issue
artifacts on `main` — no new scraping. Working chain:
`build-curation.py` → `curation-map.json` (178 kept: 169 of 5,618 Pass 1
hits + 9 universe adds) → `build-evidence-pack.py` → `evidence-pack.json` →
`reality-map.{json,md}` → this package. Proviso picks:
`build-proviso-curation.py` → `proviso-curated.json` (18 provisos, six
enacted cycles + the FY 2020-21 explicit gap). Gate:
`python3 -m collectors.sc.verify_completeness --strict` =
PASS_WITH_WARNINGS (both warnings — the zero-hit exact-phrase "penny tax"
server search, and advice-style words inside five quoted official bill
titles — are disclosed in Appendix I).
