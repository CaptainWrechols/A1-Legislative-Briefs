# Citizen Reviewer Report — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · citizen-v1.0 · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.1 on 2026-07-17
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief-print.css`, `appendices/` (README + A–G + print HTML), `PACKAGE.md`, `working/nevada/water-scarcity/reality-map.md` + `.json`, `evidence-pack.json`, `explainer-log.md`, rendered pages 1–2 (headless Chrome, US Letter, 0.6in margins)

## Status: READY FOR HUMAN REVIEW

All checklist items pass. One small accuracy fix was applied in-pass (logged below).

## Checklist results

### A. Purpose fit

| ID | Result | Evidence |
|----|--------|----------|
| A1 | PASS | Brief presents history baskets and open questions; explicitly states "This sheet does not pick for you." No path is endorsed. |
| A2 | PASS | All three baskets present: "Often moved before," "Got support but didn't finish," "Rarely moved before," each with real example bills. |
| A3 | PASS | Six deliberation questions, all open-ended (what/who/is-that framing); none steer toward a conclusion. |
| A4 | PASS | No pursue/adapt/avoid commands anywhere in the brief (regex scan of md + html). |

### B. Reading level & explainers

| ID | Result | Evidence |
|----|--------|----------|
| B1 | PASS | Flesch-Kincaid grade ≈ 7.6 (795 words, ~15 words/sentence; list items inflate this — prose sentences are shorter). All ten policy terms explained inline at first use per explainer-log.md; verified against the text. |
| B2 | PASS | No glossary. All explainers are in-section parentheticals or bordered explainer blocks (session, bill, committee, floor vote, water rights, groundwater, State Engineer, water banking, sponsor). |
| B3 | PASS | Plain topics readable without legal training ("Banned decorative grass that uses Colorado River water," "a state account to buy water rights ... and retire them for good"). Jargon deliberately avoided (origin committee → "first committee," enactment → "became law"). |
| B4 | PASS | "How a bill moves" primer with the start → committee → floor → other house → governor line is on page 1 (verified on rendered page 1). |

### C. Length & layout

| ID | Result | Evidence |
|----|--------|----------|
| C1 | PASS | Re-rendered with headless Chrome after the fix: exactly 2 US Letter pages at 0.6in margins. |
| C2 | PASS | Page 1 carries the essential map: stat strip, bill-path primer, all three history baskets (cards + table), and the data caution. |
| C3 | PASS | Detail lives in appendices A–G (~48 pages); front brief points to them in "Where to look next." |

### D. Evidence integrity

| ID | Result | Evidence |
|----|--------|----------|
| D1 | PASS | All 24 bill keys cited in the brief's source-key table resolve in `evidence-pack.json` (88-bill set), and every example bill has a row in Appendix A. |
| D2 | PASS (after fix) | Every vote count checked against the evidence pack: SB180 41-0/21-0; SB143 Senate 21-0; AB387 Assembly 26-14; AB30 Assembly 31-9; SB31 Senate 15-6. No invented counts or parties. Question 4's original wording was imprecise (see fix log). |
| D3 | PASS | "One fair caution" states the keyword-search limit, the 88-bill scope, and "where each bill stopped — never why." Appendix F carries the full limits list. |
| D4 | PASS (n/a) | No committee vote counts (inferred or otherwise) appear in the brief; the underlying data mostly lacks committee roll calls and the brief does not fabricate any. |

### E. Forum fairness

| ID | Result | Evidence |
|----|--------|----------|
| E1 | PASS | No should/must/recommend/urge directed at citizens or the legislature (regex scan). Appendix uses "must" only when describing what a bill itself required. |
| E2 | PASS | Party labels appear only descriptively (sponsor party tags, cross-party counts). No blame framing. |
| E3 | PASS | People signals are counts and dates with the explicit line "Facts only. No judgment about anyone is implied." |
| E4 | PASS | "Passed recently (2025)" is framed as "facts, not endorsements"; saturation is raised only as an open question elsewhere, not as shaming. |

### F. Package completeness

| ID | Result | Evidence |
|----|--------|----------|
| F1 | PASS | `citizen-brief.html` and `citizen-brief-print.css` exist and render. |
| F2 | PASS | Appendices A–F all exist (plus G and README, and `appendices-print.html`). |
| F3 | PASS | `PACKAGE.md` exists with export instructions and module mapping. |
| F4 | PASS | CSS tokens match `config/forum-brand.yaml`: white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial body, Georgia only in quote cards. Retired purple/gold/cream website palette absent (verified in CSS and in rendered pages 1–2). |
| F5 | PASS | All Phase 2 modules present: eyebrow header (THE FORUM bar + navy rule + kicker), terracotta all-caps section headers, navy-bar stat strip, quote-style history example cards, navy-header baskets table, info card pair, numbered question grid. |
| F6 | PASS | 6-word shingle comparison against the Phase 2 sample PDF text found no shared headings or body text. The only overlap is the issue title "Growth, Water Scarcity, and Long-Term Supply in Nevada," which is the official issue title from `config/issues/nevada-water-scarcity.yaml`, not copied sample copy. |

## Fixes made in-pass

1. **Question 4 accuracy fix** (`citizen-brief.md` and `citizen-brief.html`). Original: "The newest two won big floor votes first." Among the six State Engineer oversight bills, the two newest are both from 2025 (SB31 and AB419), and AB419 died after its origin committee with no floor vote. The two bills that actually won floor votes were 2023 AB387 (Assembly 26-14) and 2025 SB31 (Senate 15-6) — solid majorities, but "big" overstated 65% and 71% margins. Rewritten to: "Two recent ones (2023, 2025) won floor votes in one house before dying in the other." Matches the evidence pack and reality map exactly. Re-rendered: still exactly 2 pages.

## Notes for human reviewers (no action required)

- The page-1 stat strip shows 88 bills / 45 became law / 40 did not finish. The remaining 3 are enrolled joint resolutions ("in progress") that do not become statutes; this is documented in Appendix F (item 9) and the appendices README, but not on the front pages. A citizen doing the arithmetic may ask; the appendix answer exists.
- Rendered page images were refreshed after the fix (`/opt/cursor/artifacts/citizen-brief-page-1.png`, `-2.png`); both are in the Phase 2 visual family (navy/terracotta on white, Arial).

## Handoff

> Citizen Reviewer finished. Open a Pull Request for human review: Ryan Echols, Jodi Stephens, Ashley Lovell.
