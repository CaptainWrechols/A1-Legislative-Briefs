# Package — Responsive Elected Leaders in South Carolina (citizen-v2.1)

Design Packager v2.1 · 2026-09-04 · The Forum

**v2.1 (2026-09-04): reworked around the FINAL proposal grid** ("SC1 —
Responsive Elected Leaders"), which carries two proposals forward — the
independent/nonpartisan redistricting commission and better voter
education/civics — and frames the issue around leaders who fail to respond
to constituent priorities "whether because of unlimited terms or other weak
accountability mechanisms." The brief, spotlights, and Appendix H now center
on those two proposals, with each proposal's reported frequency, consensus,
and concerns (process input) answered by record facts; the four lanes from
the earlier six-proposal Phase 2 v2 grid appear as the wider accountability
record. **The legislative record — curation, dispositions, and every vote
count — is unchanged from v2.0.**

The second South Carolina citizen brief, produced on the SC foundation
(certified 123rd–126th universe + prebuilt issue artifacts). Follows the
NV/NH combined citizen-brief product (the NV citizen-v4 format, as applied
to SC by the approved slow-wage-growth package): the two-page Phase 2 front
brief, the proposal spotlights, the glossary, and the legislative process
glossary in **one document**, plus a standalone spotlights companion and
long appendices — with the SC-specific page-1 **"Also in the state budget
(provisos)"** callout required by `docs/sc-issue-chat-workflow.md`.

## What's in this folder

| File | What it is |
|---|---|
| `SC1-Responsive-Elected-Leaders-Lege-Brief.docx` | **THE DELIVERABLE** — the finalized, working-group-approved lege-brief format, cloned from `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx` (identical to SC1-Slow-Wage-Growth-Lege-Brief): brief organized by distance to law → policy spotlights → glossary (own page) → legislative process glossary (own page), stat-card table, square-bullet spotlights, two-column glossaries, real Word footer ("SC1 Responsive Elected Leaders Legislative Brief v1.0" + page number). 7 pages, LibreOffice-verified |
| `SC1-Responsive-Elected-Leaders-Lege-Brief.pdf` | PDF export of the deliverable (LibreOffice) |
| `lege-brief.md` | Source markdown of the deliverable (edit this, then rebuild) |
| `citizen-brief.md` | Combined-format source (front brief → spotlights → glossaries) |
| `citizen-brief.html` | Print-ready Phase 2 HTML — **5 letter pages**, front brief on pages 1–2 (Chrome print-to-PDF verified) |
| `citizen-brief.docx` | Word version — **5 pages**, front brief on pages 1–2 (LibreOffice-verified), direct-formatted for cross-app fidelity |
| `proposal-spotlights.md` / `.html` / `.docx` | Standalone policy spotlights: the two final-grid proposals as bulleted bill lists grouped by viability (already law / got support / stopped early / never filed), each opening with the proposal's reported frequency, consensus, and concerns, plus a wider-record background section — 2 pages HTML, 2 pages Word |
| `citizen-brief-print.css` | Phase 2 print tokens (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial) |
| `appendices/A…I-*.md` | Nine appendices (see `appendices/README.md`) |
| `appendices/appendices-print.html` | Combined print HTML with TOC — 57 letter pages (Chrome-verified) |
| `appendices/appendices.docx` | Word version of the combined appendices — 55 pages (LibreOffice-verified) |
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
  landscape, key numbers, the proviso callout, and the redistricting
  proposal; page 2 carries the civics proposal, the wider accountability
  record, political terrain, and the latest-session section. The companion
  sections — the two proposal spotlights, glossary, legislative process
  glossary — follow on pages 3–5, matching the combined format.
- Front-brief-on-two-pages and totals verified in **both** renders
  (HTML→PDF via headless Chrome; DOCX→PDF via LibreOffice). No content was
  cut to fit.

## Rebuild

```bash
# THE DELIVERABLE — lege-brief docx from the approved NV1 v1.6 template
python3 collectors/export_docx_lege_brief.py \
  --source briefs/south-carolina/responsive-elected-leaders/citizen-v2/lege-brief.md \
  --out briefs/south-carolina/responsive-elected-leaders/citizen-v2/SC1-Responsive-Elected-Leaders-Lege-Brief.docx \
  --footer "SC1 Responsive Elected Leaders Legislative Brief v1.0" --polish-breaks
# PDF: soffice --headless --convert-to pdf SC1-Responsive-Elected-Leaders-Lege-Brief.docx

# HTML combined document (Phase 2 shell)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/responsive-elected-leaders/citizen-v2

# Standalone policy spotlights (prose layout, HTML + Word)
python3 collectors/export_brief_html.py --brief-dir briefs/south-carolina/responsive-elected-leaders/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC2 Responsive Elected Leaders Policy Spotlights v2.1"
python3 collectors/export_docx_brief.py --brief-dir briefs/south-carolina/responsive-elected-leaders/citizen-v2 \
  --file proposal-spotlights --layout prose --footer "SC2 Responsive Elected Leaders Policy Spotlights v2.1"

# Combined appendices print HTML (TOC descriptions + SC data note)
python3 collectors/build_appendices_print.py --brief-dir briefs/south-carolina/responsive-elected-leaders/citizen-v2 \
  --title "Responsive Elected Leaders in South Carolina" \
  --kicker "SOUTH CAROLINA · 2019–2026" \
  --dek "Detail behind the two-page front brief: bills, votes, sponsors, budget provisos, and sources, 2019–2026." \
  --note "South Carolina publishes committee outcomes but never committee vote tallies; no committee vote counts appear anywhere in these appendices. Floor roll-call counts are verbatim from the chamber vote histories. Party labels are intentionally absent (no roster join was fetched). 'Adopted (resolution)' marks measures adopted by both chambers that never go to the governor." \
  --footline "The Forum · Citizen Brief citizen-v2.1 · Responsive Elected Leaders in South Carolina · September 2026" \
  --descriptions '{"A":"Every curated bill: plain topic, theme, tier, result, where it stopped","B":"Theme scorecards with history baskets and certainty labels","C":"Passage/adoption-type floor votes, verbatim; high-support non-enactments","D":"Frequent lead sponsors; verbatim sponsor line per policy bill","E":"Milestone paths for the 15 measures the front brief leans on","F":"What this data can and cannot say","G":"Ethics and elections provisos in each state budget year","H":"The two final citizen proposals matched against the record","I":"Claim-to-source mapping, collection notes, review status"}'

# Word exports (front brief via direct writer; appendices via pandoc + branded reference doc)
python3 collectors/export_docx.py --brief-dir briefs/south-carolina/responsive-elected-leaders/citizen-v2
```

Print to PDF: open either HTML in a browser → Print → Save as PDF (Letter,
default margins — the CSS sets 0.6in). If pandoc is unavailable for the
appendices: open `appendices-print.html` in Word directly, or upload the
markdown to Google Docs and download as .docx.

## Data provenance (short)

Everything derives from the certified SC universe and prebuilt issue
artifacts on `main` — no new scraping. Working chain:
`build-curation.py` → `curation-map.json` (189 kept: 185 of 5,548 Pass 1
hits + 4 universe adds) → `build-evidence-pack.py` → `evidence-pack.json` →
`reality-map.{json,md}` → this package. Proviso picks:
`build-proviso-curation.py` → `proviso-curated.json` (32 provisos, six
enacted cycles + the FY 2020-21 explicit gap). Gate:
`python3 -m collectors.sc.verify_completeness --strict` =
PASS_WITH_WARNINGS (the one warning — advice-style words inside five quoted
official bill titles — is disclosed in Appendix I).
