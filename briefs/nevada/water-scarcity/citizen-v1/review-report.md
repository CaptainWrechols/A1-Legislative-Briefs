# Citizen Reviewer Report — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · **citizen-v2.0** · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.2 on 2026-07-17
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief.docx`, `citizen-brief-print.css`, `appendices/` (README + A–G + print HTML + docx), `PACKAGE.md`, `working/…/reality-map.{md,json}`, `evidence-pack.{json,md}`, `curation-map.json`, `explainer-log.md`, rendered pages (headless Chrome, US Letter, 0.6in margins)

## Status: READY FOR HUMAN REVIEW

All checklist items pass. Fit-to-two-pages trims were applied during packaging and are logged in `PACKAGE.md` (no facts dropped from the packet).

## Checklist results

### A. Purpose fit

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | Brief reports history per proposal; states "This sheet reports history; it does not pick for you." No path endorsed. |
| A2 | PASS | Three baskets present on page 2 with real examples; they support (not replace) the proposal table. |
| A3 | PASS | Six open questions, all tied to the record; none steer to a conclusion. |
| A4 | PASS | Regex scan of md + html: no should/must/recommend/urge/pursue/avoid as commands. |
| A5 | PASS | All three Phase 2 constituent proposals (desalination, interstate pipeline, regulate data centers) have a row in the page-1 table, each with tried / happened / obstacle columns. |

### B. Reading level & explainers

| ID | Result | Evidence |
|----|--------|----------|
| B1 | PASS | Flesch-Kincaid ≈ 8.7 on raw text including stat-strip and card lines (which lack terminal punctuation and inflate the score); prose sentences average ≈ 14 words. Target is ≈ grade 8. |
| B2 | PASS | No glossary. Eleven terms explained inline at first use (see `working/…/explainer-log.md`); verified against the text. "Abatement," "preemption," and "appropriation" are avoided entirely in favor of plain words. |
| B3 | PASS | Plain topics readable without legal training ("blocked local bans on big water-cooled towers," "a state account to buy water rights … and retire them for good"). |
| B4 | PASS | Bill-path primer (start → first committee → floor vote → other house → governor) is on page 1, with committee and floor vote explained inline. |

### C. Length & layout

| ID | Result | Evidence |
|----|--------|----------|
| C1 | PASS | Headless Chrome render: exactly **2** US Letter pages at 0.6in margins. |
| C2 | PASS | Page 1 carries the essential map: stat strip, primer, and the full proposal-vs-record table. |
| C3 | PASS | Depth lives in appendices A–G (49 rendered pages); front brief points to them in the footline. |

### D. Evidence integrity

| ID | Result | Evidence |
|----|--------|----------|
| D1 | PASS | All 30+ bill claims spot-checked against `evidence-pack.json` (dispositions, stages, floor counts): 20/20 programmatic checks OK, incl. 82:SB394 corrected to "passed the Senate 14–7, died in the Assembly" (an earlier draft wrongly said both houses; fixed before packaging). |
| D2 | PASS | No invented votes or parties; party labels come from NELIS rosters (100% of 6,636 ballot rows matched). |
| D3 | PASS | Data limits stated in footline + Appendix F; "where, never why" appears on both pages. |
| D4 | PASS | Inferred committee Yeas flagged in appendices README, Appendix C intro, and print TOC note. |

### E. Forum fairness

| ID | Result | Evidence |
|----|--------|----------|
| E1 | PASS | No should/must/recommend/urge directed at citizens or the legislature. |
| E2 | PASS | No party blame. The data-center 4-for-4 vs 0-for-5 pattern is stated by bill direction, not by party; SB547's sponsors are named factually in the reality map only. |
| E3 | PASS | People signals descriptive (sponsor counts, committee stops, veto counts). |
| E4 | PASS | "Passed recently" framed as facts, with SB36's prior failures noted as history, not shame. |

### F. Package completeness

| ID | Result | Evidence |
|----|--------|----------|
| F1 | PASS | `citizen-brief.html` + `citizen-brief-print.css` present. |
| F2 | PASS | Appendices A–G + README + `appendices-print.html` (renders 49 pages with TOC). |
| F3 | PASS | `PACKAGE.md` with print steps. |
| F3b | PASS | Word exports present (`citizen-brief.docx`, `appendices/appendices.docx`) plus explicit no-pandoc conversion steps in `PACKAGE.md`. |
| F4 | PASS | Only Phase 2 tokens in CSS (navy `#1A2D4F`, `#2E4A78`, terracotta `#C0392B`, tint `#E8D5D3`, Arial; Georgia only in quote cards). No purple/gold/cream. |
| F5 | PASS | Modules present: eyebrow header, terracotta H2s, stat strip, history cards, comparison tables (proposals + baskets), question grid, info pair, footline. |
| F6 | PASS | No Phase 2 sample headings/kicker/body text copied (diff against sample text). |

## Recall audit (post-review addendum, same day)

A completeness audit extended the subject-index harvest to RIVERS, DAMS,
FLOOD CONTROL, SEWAGE, TAHOE, and TRUCKEE RIVER headings plus water entries
filed under department headings, and checked all six 2020–2025 special
sessions (none contained water or data-center bills). This added 24 bills
(8 policy, 16 context). All packet numbers were rebuilt: **189 collected,
108 policy bills, 59 enacted, 27 first-committee deaths**. The proposal
crosswalk was unchanged (desalination 0, pipeline 0, data centers 11). The
front brief still renders at exactly 2 pages; fact checks re-run: 29/29 pass.

## Notes for human reviewers (Ryan Echols, Jodi Stephens, Ashley Lovell)

1. **This is a full re-collection**: 189 bills found (was 88); headline numbers use the 108-bill policy set. Context bills are listed separately in Appendix A so the search stays auditable.
2. The page-1 proposal table is the core change from v1: each Community Conversation proposal is checked against the record, including two "never filed" findings and the asymmetric data-center record (helping 4-for-4, restraining 0-for-5).
3. Venue notes (local rule vs. state statute vs. Congress) are descriptive statements of where authority sits, sourced from bill texts and the LCB data-centers memo (S25) — please gut-check the wording stays on the right side of "no advice."
4. The 2026 interim data-center study is mentioned as context ("the next real window") — flag if that reads as steering.
