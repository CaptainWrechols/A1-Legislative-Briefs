# Citizen Reviewer report — Growth, Infrastructure, and Roads in South Carolina (citizen-v2.1)

Citizen Reviewer v2.3 · 2026-09-01, re-reviewed 2026-09-04 · Verdict: **READY FOR HUMAN REVIEW**

Package reviewed: `briefs/south-carolina/growth-infrastructure-roads/citizen-v2/`
(combined citizen brief, standalone proposal spotlights, appendices A–I,
HTML + Word renders). Working inputs: `evidence-pack.json`,
`reality-map.{json,md}`, `curation-map.json`, `proviso-curated.json`,
`explainer-log.md`.

## A. Purpose fit — PASS

| ID | Result | Notes |
|---|---|---|
| A1 | PASS | The brief reports what was filed, where it stopped, and what finished; no passage tells readers or lawmakers what to pick. |
| A2 | PASS | Proposals grouped by record status: "Where something finished" (the green-space penny, SCDOT Modernization), "Got support but didn't finish" (shortline credit, RIA package, concurrency), and "Rarely moved before" (impact fees, transit, gas-tax bills, planning); spotlights use the viability groups (already law / got support / stopped early / never filed). |
| A4 | PASS | No pursue/adapt/avoid commands anywhere in citizen-facing text (automated scan + read-through). One "should pay" in Appendix H's restatement of a citizen proposal was rewritten to "make developers pay" during review. |
| A5 | PASS | All five constituent proposals of the FINAL grid ("SC1 - Growth Infrastructure Roads", received 2026-09-04) covered with [P-…] labels in the front brief and spotlights: local-funding-tools, state-master-planning, fix-roads-first, no-new-taxes, contractor-accountability. The final grid's frequency/consensus/tradeoff descriptions are carried verbatim in substance (Appendix H). |
| A6 | PASS | No how-to-use section, no discussion questions, no cautions or meta-commentary, no source keys in the front brief (all reviewer material is in Appendix I). |

## B. Reading level & explainers — PASS

| ID | Result | Notes |
|---|---|---|
| B1 | PASS | Plain prose; specialized terms (proviso, penny tax, impact fee, concurrency, "C" funds, design-build, infrastructure maintenance fee) are explained inline at first use and again in the appended glossaries — the combined format approved for the three earlier SC briefs. The explainer log (`working/.../explainer-log.md`) maps each term to where it is explained. |
| B2 | PASS | Policy terms are used naturally in the text; the glossaries are appended companion pages (pages 4–6), not front-brief apparatus. |
| B3 | PASS | Bill descriptions are single-sentence plain summaries verified against full text ("A BILL TO..." long titles were read for every ambiguous candidate); no legal training needed. |

## C. Length & layout — PASS

| ID | Result | Notes |
|---|---|---|
| C1 | PASS | Front brief renders in 2 letter pages in **both** renders (re-verified 2026-09-04 after the fact-check corrections): HTML→PDF (headless Chrome — the front brief fills page 2 exactly; the spotlights header starts page 3) and DOCX→PDF (LibreOffice — spotlights header at the end of page 2). Combined document: 6 pages in both renders. |
| C2 | PASS | Page 1 carries the landscape, the key numbers, the required proviso callout, and the start of the where-something-finished basket — verified by text extraction in both renders. |
| C3 | PASS | Bill-by-bill depth lives in the spotlights and appendices; the front brief cites only the load-bearing measures. |

## D. Evidence integrity — PASS

| ID | Result | Notes |
|---|---|---|
| D1 | PASS | Automated check: every bill number cited in the front brief (103 ids) and spotlights (124 ids) exists in the curated evidence pack. Zero unmatched ids. |
| D2 | PASS | Automated check: every vote pair cited (30 distinct pairs, including 37–1, 114–0, 112–2, 43–0, 43–1, 41–3, 67–28, 81–18, 40–2, 91–14, 106–3, 65–46, 112–0, 106–4, 42–2, 44–1, 65–35, 108–2, 32–6, 104–1, 34–2, 87–15, 44–0, 102–10, 38–0, 108–0, 103–0, 110–2, 107–0, 90–15) matches a verbatim passage/reading/adoption roll call in the pack; a strict second pass confirmed all remaining hyphenated numbers are year ranges, not vote counts. No committee tallies stated or implied. No party labels anywhere. |
| D3 | PASS | Appendix F states the limits plainly (keyword scope, no committee tallies, no party labels, voice votes, one-year provisos, whole-bill votes, collection date, FY 2020-21 gap). |
| D4 | PASS | Not applicable — no committee Yeas exist in South Carolina data and none are shown. |
| D5 | PASS | Proviso citations verified: every proviso number cited in citizen-facing text (84.8, 84.9, 84.12, 84.15, 84.16, 84.18, 86.1, 117.96, 118.18, 118.19, 118.21, 118.22) matches the hand-curated set or its verified renumbering across years; dollar figures ($200,000,000 / $100,000,000 / $117,401,000 / $175,000,000 / $50,000,000 / $133,636,230) are verbatim from enacted Part IB text. |

## E. Forum fairness — PASS

| ID | Result | Notes |
|---|---|---|
| E1 | PASS | Automated scan: no should/must/recommend/urge directed at citizens or the legislature. All "must" hits describe what bills, laws, or provisos require (e.g., "SCDOT must publish"). |
| E2 | PASS | No party blame; the packet makes no party claims at all (no roster join was fetched, disclosed in Appendix F). |
| E3 | PASS | People signals are counts and bill lists (who led how many bills); no moral scorecards. |
| E4 | PASS | The recent-enactments section reports Act 177, Act 244, Act 203, Act 222, and the FY 2026-27 provisos without praising or shaming further action. Both sides of the tax split are reported symmetrically (the suspension bills and the increase bill died in the same committees). |

## F. Package completeness — PASS

| ID | Result | Notes |
|---|---|---|
| F1 | PASS | `citizen-brief.html` + `citizen-brief-print.css` present. |
| F2 | PASS | Appendices A–I plus README present. |
| F3 | PASS | `PACKAGE.md` present with rebuild commands and print steps. |
| F3b | PASS | Word exports present: `citizen-brief.docx` (6 pp, front brief on pp 1–2), `proposal-spotlights.docx` (4 pp), `appendices/appendices.docx` (56 pp) — all LibreOffice-verified. |
| F7 | PASS | Claim-to-source map and collection notes live in Appendix I only. |
| F4 | PASS | Phase 2 tokens only (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial); no purple/gold/cream anywhere. |
| F5 | PASS | Masthead, terracotta ALL-CAPS section headers, and navy-bar stat strip present; no tables in the front brief. |
| F6 | PASS | No Phase 2 sample headings, kicker text, or body text copied — module shapes and tokens only. |

## Fixes made during review (logged per the small-fix rule)

1. Corrected four bill-year citations against introduction dates: S227,
   S288, and H4050 were introduced in 2025 (cited as 2026 because their
   decisive activity was 2026 — now "filed 2025", with the 2026 floor
   events still dated 2026); H4597 was introduced May 2019 (cited as
   2020). Propagated to the internal reality map.
2. Rewrote Appendix H's restatement of the developer-pays proposal from
   "developers should pay" to "make developers pay" (removes a bare
   "should" even in attributed process input).
3. All renders (HTML, DOCX, appendices print) rebuilt after the fixes and
   page boundaries re-verified in both engines.
4. Post-review source cross-check (2026-09-01): the seven [P-…] proposal
   descriptions were verified against the uploaded "SC1 – Phase 2
   Constituent Proposals – Grid View for Legislators v2" document. Six of
   seven match in substance; one faithful detail was added to Appendix H
   and the internal reality map (state master planning was a consensus
   recommendation at the Charleston conversation). Exception flagged for
   human review: the developer-pays-growth detail table
   (frequency/tradeoffs/consensus) is blank in the v2 document, so its
   attributes ("very high frequency, all events; high consensus") rest on
   the issue config's proposal block alone (disclosed in Appendices H
   and I).

## SC-specific checks (workflow requirements)

- Page-1 "Also in the state budget (provisos)" callout: present, names
  FY 2026-27 proviso 84.18 (Road Buyback Program), FY 2024-25 proviso
  118.22 (the $417.4M package), and FY 2021-22 proviso 117.96 (the school
  impact-fee prohibition) with the one-year-rule explainer, the FY 2020-21
  no-enacted-budget statement, and the whole-bill-vote rule.
- No implied committee tallies: verified (D2).
- No invented sponsors or votes: sponsor lines verbatim in Appendix D;
  votes verbatim in Appendix C.
- History baskets only: "Where something finished / Got support but didn't
  finish / Rarely moved before" framing used in the brief and Appendix B;
  no advice.
- Proviso analysis requirement: Appendix G covers all six enacted cycles
  plus the FY 2020-21 gap, with verbatim dollar figures and the
  renumbering trails (84.9→84.8; 84.18→84.16→84.15).

## Rework to the final proposal grid (2026-09-04)

The brief was recentered on the five proposals of the final Phase 2 grid
("SC1 - Growth Infrastructure Roads"), which supersedes the seven-proposal
draft grid the issue config originally carried. The legislative record is
unchanged. Changes: the impact-fee record now appears under
[P-local-funding-tools] (whose final title names impact fees) and the
standalone developer-pays spotlight was removed; the multimodal-transport
spotlight was removed (its bills remain in Appendices A–C and the theme
scorecards, unlabeled); all [P-…] descriptors were re-verified against the
final grid; the config's constituent_proposals block was updated to the
final grid (collection artifacts predate it and are untouched — noted in
the config); the strict gate was re-run after the config change
(PASS_WITH_WARNINGS, same two disclosed warnings). This also resolves the
2026-09-01 flag about the draft grid's blank developer-pays table: that
proposal is not in the final grid.

## Independent fact-check (2026-09-04)

A full independent verification pass was run against live scstatehouse.gov
(bill pages, vote histories, enacted Part IB budget text), the live SC Code
of Laws, and secondary web sources (SCDOR, Municipal Association of SC, SC
Council on Competitiveness): **107 of 107 automated checks pass** — every
cited vote pair, act number, proviso number, and dollar figure verified
verbatim against the live official record. One material completeness
correction resulted: the SCDOT Modernization Act (Act 177 of 2026) is an
omnibus, and the packet now reports its Pothole Mitigation Program,
design-build/CMGC contracting authority, choice-lane toll rules, P3 cap,
four-year external audit, commission-abolition date (January 1, 2027), and
"C"-funds change alongside the governance headline. Full method, findings,
and the correction log: `working/south-carolina/growth-infrastructure-roads/
fact-check-report.md` (+ `fact-check-live.{py,json}`).

## Lege Brief deliverable (2026-09-04)

The finalized working-group Lege Brief format was produced to match the
approved SC1/NH1 lege briefs exactly:
`SC1-Growth-Infrastructure-Roads-Lege-Brief.docx` / `.pdf` (9 pages; trimmed 2026-09-04 so the spotlights fill their final page and the glossary begins on the next — no near-empty page),
exported from `lege-brief.md` by `collectors/export_docx_lege_brief.py`
(format cloned from `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`,
`--polish-breaks`), footer "SC1 Growth Infrastructure Roads Legislative
Brief v1.0". Organized by distance to law (proven support → already law →
stopped early → movement map → federal overlap), with the page-1 proviso
callout, the final grid's five policy spotlights carrying each proposal's
reported frequency/consensus/concerns, and the two glossaries on their own
pages. Automated verification on the source: 108 bill ids all resolve to
the evidence pack, every vote pair matches a verbatim roll call, all
proviso ids verified, zero advice-language hits (one grid-quoted "should"
rephrased during review), zero party labels. The earlier improvised
top-level "SC1 - …" distribution copies were removed in favor of this
convention-exact deliverable.

## Verdict

**READY FOR HUMAN REVIEW.** Status lines updated in `citizen-brief.md`
(front matter), `citizen-brief.html` (meta), and `proposal-spotlights.*`.
Suggested human reviewers: Ryan Echols, Jodi Stephens, Ashley Lovell.
