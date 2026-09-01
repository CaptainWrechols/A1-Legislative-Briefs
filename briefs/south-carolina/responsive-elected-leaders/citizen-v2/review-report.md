# Citizen Reviewer report — Responsive Elected Leaders in South Carolina (citizen-v2.0)

Citizen Reviewer v2.3 · 2026-08-28 · Verdict: **READY FOR HUMAN REVIEW**

Package reviewed: `briefs/south-carolina/responsive-elected-leaders/citizen-v2/`
(combined citizen brief, standalone proposal spotlights, appendices A–I,
HTML + Word renders). Working inputs: `evidence-pack.json`,
`reality-map.{json,md}`, `curation-map.json`, `proviso-curated.json`,
`explainer-log.md`.

## A. Purpose fit — PASS

| ID | Result | Notes |
|---|---|---|
| A1 | PASS | The brief reports what was filed, where it stopped, and what finished; no passage tells readers or lawmakers what to pick. |
| A2 | PASS | Proposals grouped by record status: "Where something finished" (disclosure, civics) and "Rarely moved before: the proposals aimed at the State House itself" (term limits, campaign finance, RCV, redistricting); spotlights use the viability groups (adopted / already law / got support / stopped early / never filed). |
| A4 | PASS | No pursue/adapt/avoid commands anywhere in citizen-facing text (automated scan + read-through). |
| A5 | PASS | All six constituent proposals covered with [P-…] labels in the front brief and spotlights: term-limits, campaign-finance-reform, ranked-choice-voting, independent-redistricting, financial-disclosure, voter-civics-education. |
| A6 | PASS | No how-to-use section, no discussion questions, no cautions or meta-commentary, no source keys in the front brief (all reviewer material is in Appendix I). |

## B. Reading level & explainers — PASS

| ID | Result | Notes |
|---|---|---|
| B1 | PASS | Plain prose; specialized terms (proviso, statement of economic interests, Article V application, motion to continue) are explained inline at first use and again in the appended glossaries — the combined format approved for the SC slow-wage-growth brief. |
| B2 | PASS | Policy terms are used naturally in the text; the glossaries are appended companion pages (pages 4–5), not front-brief apparatus. |
| B3 | PASS | Bill descriptions are single-sentence plain summaries verified against full text; no legal training needed. |

## C. Length & layout — PASS

| ID | Result | Notes |
|---|---|---|
| C1 | PASS | Front brief renders in 2 letter pages in **both** renders: HTML→PDF (headless Chrome, front section = 2 pages exactly) and DOCX→PDF (LibreOffice, the spotlights section header falls at the end of page 2). Combined document: 5 pages HTML / 5 pages Word. |
| C2 | PASS | Page 1 carries the landscape, the stat strip, the required proviso callout, and the where-something-finished basket. |
| C3 | PASS | Bill-by-bill depth lives in the spotlights and appendices; the front brief cites only the load-bearing measures. |

## D. Evidence integrity — PASS

| ID | Result | Notes |
|---|---|---|
| D1 | PASS | Automated check: every bill number cited in the front brief and spotlights exists in the curated evidence pack (Appendix A). Zero unmatched ids. |
| D2 | PASS | Automated check: every vote pair cited (102–0, 40–0, 23–86, 53–45, 39–2, 109–4, 45–0, 91–12, 29–7, 29–14, 24–16, 67–41, 24–14, 68–30, 37–7, 74–37, 26–18, 96–14, 43–1, 41–2, 74–35, 68–36) matches a verbatim roll call in the pack. The two procedural votes used (H3570 non-concurrence 23–86; H5683 motion to continue 26–18) are labeled as procedural in place. No committee tallies stated or implied. No party labels anywhere. |
| D3 | PASS | Appendix F states the limits plainly (keyword scope, no committee tallies, no party labels, resolutions vs. laws, collection date, proviso-year gap). |
| D4 | PASS | Not applicable — no committee Yeas exist in South Carolina data and none are shown. |

## E. Forum fairness — PASS

| ID | Result | Notes |
|---|---|---|
| E1 | PASS | Automated scan: no should/must/recommend/urge directed at citizens or the legislature. All "must" hits describe what bills or laws require (e.g., "who must file"). |
| E2 | PASS | No party blame; the packet makes no party claims at all (no roster join was fetched, disclosed in Appendix F). |
| E3 | PASS | People signals are counts and bill lists (who led how many bills); no moral scorecards. |
| E4 | PASS | The recent-enactments section reports S70, H3008, and the FY 2026-27 provisos without praising or shaming further action. |

## F. Package completeness — PASS

| ID | Result | Notes |
|---|---|---|
| F1 | PASS | `citizen-brief.html` + `citizen-brief-print.css` present. |
| F2 | PASS | Appendices A–I plus README present. |
| F3 | PASS | `PACKAGE.md` present with rebuild commands and print steps. |
| F3b | PASS | Word exports present: `citizen-brief.docx` (5 pp, front brief on pp 1–2), `proposal-spotlights.docx`, `appendices/appendices.docx` (55 pp) — all LibreOffice-verified. |
| F7 | PASS | Claim-to-source map and collection notes live in Appendix I only. |
| F4 | PASS | Phase 2 tokens only (white page, navy `#1A2D4F`, terracotta `#C0392B`, Arial); no purple/gold/cream anywhere. |
| F5 | PASS | Masthead, terracotta ALL-CAPS section headers, and navy-bar stat strip present; no tables in the front brief. |
| F6 | PASS | No Phase 2 sample headings, kicker text, or body text copied — module shapes and tokens only. |

## Fixes made during review (logged per the small-fix rule)

1. Neutralized one editorial phrase in the proviso callout: "the watched
   keeping approval power over the watchdog's tools" → "changes to the
   watchdog's disclosure site need sign-off from the legislature's own
   ethics committees."
2. "The bigger prize came within days of passing" → "The bigger change
   came within days of passing" (removed evaluative word).
3. Corrected two bill years during fact-check against introduction dates:
   H4591 is 2024 (not 2023) and H5360 is 2026 (not 2025); propagated to
   the evidence pack's crosswalk note.
4. Removed two externally-sourced claims from working documents before
   they reached citizen-facing text (a federal-lawsuit reference on the
   Act 118 map; an overseas-ballot implementation detail) — the packet now
   contains only claims traceable to the local record.

## SC-specific checks (workflow requirements)

- Page-1 "Also in the state budget (provisos)" callout: present, names
  FY 2026-27 provisos 117.219, 117.145, and 110.1 with the one-year-rule
  explainer and the whole-bill-vote rule. The FY 2020-21 no-enacted-Part-IB
  gap is stated in Appendix G.
- No implied committee tallies: verified (D2).
- No invented sponsors or votes: sponsor lines verbatim in Appendix D;
  votes verbatim in Appendix C.
- History baskets only: "Often moved / Got support but didn't finish /
  Rarely moved" framing used in the brief and Appendix B; no advice.

## Verdict

**READY FOR HUMAN REVIEW.** Status lines updated in `citizen-brief.md`
(front matter), `citizen-brief.html` (meta), and `proposal-spotlights.*`.
Suggested human reviewers: Ryan Echols, Jodi Stephens, Ashley Lovell.
