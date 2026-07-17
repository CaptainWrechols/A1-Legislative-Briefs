# Citizen Reviewer Report — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · **citizen-v3.0** · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.2 on 2026-07-17
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief.docx`, `citizen-brief-print.css`, `appendices/` (README + A–H + print HTML + docx), `PACKAGE.md`, `working/…/reality-map.{md,json}`, `evidence-pack.{json,md}`, `curation-map.json`, `explainer-log.md`, rendered pages (headless Chrome, US Letter, 0.6in margins)

## Status: READY FOR HUMAN REVIEW

## What changed from v2.0

v3.0 replaces the three-proposal page 1 with **all ten** of the most common
citizen statements on water from the Phase 2 RAG constituent-voice dataset
("NV1 - RAG - Phase 2 Constituent Input", Water sheet). Each statement is a
row in the page-1 table: what Nevadans proposed · tried? · what the record
shows. A new **Appendix H** carries the full statement-by-statement
crosswalk with bill tables, venue notes, and open questions per statement.
The evidence base is unchanged (189 bills collected, 108 policy bills) —
the crosswalk in `evidence-pack.json` now maps all ten statements.

## Checklist results

### A. Purpose fit

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | Brief reports history per statement; "This sheet reports history; it does not pick for you." No path endorsed. |
| A2 | PASS | Three baskets present on page 2 (compact prose form) with real examples. |
| A3 | PASS | Six open questions, each tied to a specific record finding; none steer to a conclusion. |
| A4 | PASS | Regex scan of md + html: no should/must/recommend/urge/pursue/avoid as commands. |
| A5 | PASS | All **ten** citizen statements from the constituent-input dataset have a row on page 1 and a full card in Appendix H / reality-map.json. |

### B. Reading level & explainers

| ID | Result | Evidence |
|----|--------|----------|
| B1 | PASS | Flesch-Kincaid ≈ 8.3 on prose (excluding table rows); sentences ≈ 15 words. |
| B2 | PASS | No glossary. Explainers inline at first use (see `working/…/explainer-log.md`). "Abatement," "preemption," "adjudication" avoided in favor of plain words. Citizens' own terms (closed-loop, moratorium, Economic Forum) kept with plain context, since readers coined them. |
| B3 | PASS | Plain topics readable without legal training; "Never filed" explicitly defined ("it means nobody has asked yet"). |
| B4 | PASS | Bill-path primer on page 1 with committee and floor vote explained inline. |

### C. Length & layout

| ID | Result | Evidence |
|----|--------|----------|
| C1 | PASS | Headless Chrome render: exactly **2** US Letter pages at 0.6in margins (ten-statement table flows rows 9–10 onto page 2 with its navy header repeated). |
| C2 | PASS | Page 1 carries the essential map: stat strip, primer, and statements 1–8 of the table. |
| C3 | PASS | Depth lives in appendices A–H (64 rendered pages), including the full crosswalk (H). |

### D. Evidence integrity

| ID | Result | Evidence |
|----|--------|----------|
| D1 | PASS | 28/28 disposition+stage checks and 6/6 floor-vote-count checks of the table's bill claims pass against `evidence-pack.json`. |
| D2 | PASS | No invented votes or parties; party labels from NELIS rosters (100% of ballot rows matched). |
| D3 | PASS | Data limits in footline + Appendix F; "where, never why" on both pages. |
| D4 | PASS | Inferred committee Yeas flagged in appendices README, Appendix C intro, and print TOC note. |

### E. Forum fairness

| ID | Result | Evidence |
|----|--------|----------|
| E1 | PASS | No advice verbs directed at citizens or the legislature. |
| E2 | PASS | No party blame; the 4-for-4 / 0-for-5 data-center pattern is stated by bill direction, not party. |
| E3 | PASS | People signals descriptive. |
| E4 | PASS | "Passed recently" framed as facts; SB36's earlier failures noted as history. |

### F. Package completeness

| ID | Result | Evidence |
|----|--------|----------|
| F1 | PASS | `citizen-brief.html` + print CSS present. |
| F2 | PASS | Appendices A–H + README + `appendices-print.html` (64 pages with TOC). |
| F3 | PASS | `PACKAGE.md` with print steps. |
| F3b | PASS | Word exports regenerated for v3.0 (`citizen-brief.docx`, `appendices/appendices.docx` incl. Appendix H) plus no-pandoc fallback steps. |
| F4 | PASS | Only Phase 2 tokens (navy `#1A2D4F`, `#2E4A78`, terracotta `#C0392B`, tint `#E8D5D3`, Arial; Georgia only in quote-card style). |
| F5 | PASS | Modules: eyebrow header, terracotta H2s, stat strip, process line, navy-header table (ten-statement centerpiece), info pair, question grid, footline. Basket cards rendered as compact labeled prose to hold 2 pages. |
| F6 | PASS | No Phase 2 sample headings/kicker/body text copied. |

## Notes for human reviewers (Ryan Echols, Jodi Stephens, Ashley Lovell)

1. The ten statements and their consensus/trade-off summaries come verbatim
   from the Forum's own RAG dataset (Water sheet). The brief paraphrases them
   at grade 8; the config (`config/issues/nevada-water-scarcity.yaml`)
   preserves fuller detail with the dataset's framing.
2. The strongest editorial judgment in v3.0 is the "Tried?" status column
   (never filed / tried-stalled / precedent exists). Statuses are derived
   from the crosswalk and are documented per statement in Appendix H —
   please gut-check the two borderline calls: row 4 (metering: "never filed
   statewide" despite well-meter laws) and row 8 (growth restrictions:
   "precedent exists" on the strength of AB356 + SB250).
3. Row 10's northern-Nevada dedication practice (rights + 11% drought
   reserve) is sourced to the LCB data-centers memo (S25) and is a
   water-authority rule, not statute — the brief says so explicitly.
4. Cross-cutting citizen themes (transparency, "legislature meets every
   other year") are noted in the issue config and reality map but not on
   page 1 — flag if you want them surfaced in the brief.
