# Package — Slow Wage Growth in South Carolina (citizen-v2.0)

Design Packager v2.1 · 2026-08-26 · The Forum

The first South Carolina citizen brief, produced on the SC foundation
(certified 123rd–126th universe + prebuilt issue artifacts). Follows the
NV/NH citizen-brief product: two-page Phase 2 front brief + long appendices,
with the SC-specific page-1 **"Also in the state budget (provisos)"**
callout required by `docs/sc-issue-chat-workflow.md`.

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the front brief |
| `citizen-brief.html` | Print-ready Phase 2 HTML — **2 letter pages** (Chrome print-to-PDF verified) |
| `citizen-brief.docx` | Word version — **2 pages** (LibreOffice-verified), direct-formatted for cross-app fidelity |
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

- Front brief: page 1 carries the landscape, key numbers, the proviso
  callout, and the two strongest history baskets; page 2 carries the
  rarely-moved basket, political terrain, and the latest-session section.
- Verified ≤2 pages in **both** renders (HTML→PDF via headless Chrome;
  DOCX→PDF via LibreOffice). No content was cut to fit.

## Rebuild

```bash
# HTML front brief (Phase 2 shell)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/slow-wage-growth/citizen-v2

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
