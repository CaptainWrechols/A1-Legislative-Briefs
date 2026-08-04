# Citizen Reviewer report — Housing Affordability in New Hampshire (citizen-v1)

**Status: READY FOR HUMAN REVIEW**

Re-reviewed 2026-08-04 (citizen-v1.1: 2020–2024 supplement of 23 bills from
year-end official indexes; headline numbers now 158 policy bills / 48 laws) by
citizen-reviewer v2.3 (automated pass; agent spec
`agents/citizen-reviewer/AGENT.md`). Machine scans ran against
`working/new-hampshire/housing-affordability/evidence-pack.json`; the reality
map behind the brief passed its own programmatic fact-check
(`fact-check-reality-map.py`).

## A. Purpose fit

| ID | Result | Notes |
|---|---|---|
| A1 | PASS | Brief reports the record; no directives to readers. Automated advice-verb scan (should/must/recommend/urge/need to/pursue/avoid): zero hits in the front brief. |
| A2 | PASS | Content grouped by record status: "Where new law exists" / "Ideas that reached the Legislature and stalled" / "Ideas that have not passed either chamber". |
| A4 | PASS | No pursue/adapt/avoid commands. |
| A5 | N/A | No `constituent_proposals` exist for New Hampshire (no Phase 2 constituent dataset for this state); the brief is organized around the record's recurring housing ideas instead, per the issue mission. |
| A6 | PASS | No how-to-use, no discussion questions, no civics primer, no cautions/meta-commentary, no source keys in the front brief. One fix applied in-pass: a mid-brief appendix pointer inside the HB2 callout was removed (pointers are reserved for the single closing line). The HB2 whole-trailer-vote sentence is retained as a factual constraint required by `docs/nh-hb2-section-workflow.md`, not a caution. |

## B. Reading level & explainers

| ID | Result | Notes |
|---|---|---|
| B1 | PASS | Adult professional prose; no reading-level scaffolding; common civic terms unexplained. |
| B2 | PASS | No glossary; policy terms used naturally; in-context appositions logged in `working/.../explainer-log.md`. |
| B3 | PASS | Bill descriptions are plain-language (verified against curation-map plain topics). |

## C. Length & layout

| ID | Result | Notes |
|---|---|---|
| C1 | PASS | `citizen-brief.html` renders exactly 2 US Letter pages in headless Chrome; `citizen-brief.docx` renders exactly 2 pages in LibreOffice (re-verified after the v1.1 revision). |
| C2 | PASS | Page 1: landscape, Key numbers stat strip, HB2 budget-bill callout (mission requirement), and the enacted-law map. |
| C3 | PASS | Bill-by-bill detail, all roll calls, sponsors, HB2 sections, and limits live in Appendices A–I. |

## D. Evidence integrity

| ID | Result | Notes |
|---|---|---|
| D1 | PASS | All 27 bills cited in the front brief exist in Appendix A / the evidence pack (automated scan; zero missing). |
| D2 | PASS | Every vote pair cited in the brief matches a roll call in the official record or an HB2 whole-bill vote, except SB454's 180–176 tabling, which is a division-vote tally recorded in the official docket (House Journal 12, p. 86) and described as such in the brief. Party-split claims (SB86 2021, HB1291 2024, HB44 2023, HB1196 2026) match the ballot-level party tallies. |
| D3 | PASS | Data limits stated in Appendix F, including the 2020–2024 roll-call-only coverage gap. |
| D4 | N/A | No inferred committee Yeas are presented. |

## E. Forum fairness

| ID | Result | Notes |
|---|---|---|
| E1 | PASS | No should/must/recommend/urge directed at citizens or the Legislature. |
| E2 | PASS | Every party characterization carries a concrete cited vote (SB86 208–167 with party counts; HB1291 220–143; HB1196 185–166). |
| E3 | PASS | Sponsor mentions are counts of bills filed, not scorecards. |
| E4 | PASS | The new-law recap reports without shaming repeats; the interim studies are reported neutrally. |

## F. Package completeness

| ID | Result | Notes |
|---|---|---|
| F1 | PASS | `citizen-brief.html` + `citizen-brief-print.css` present. |
| F2 | PASS | Appendices A–F present, plus H (HB2 sections) and I (sources); G intentionally absent (no text-diff data) and documented in the appendices README. |
| F3 | PASS | `PACKAGE.md` present with export and print steps. |
| F3b | PASS | Word exports exist for brief and appendices; brief verified 2 pages. |
| F7 | PASS | Claim-to-source map and collection notes live in Appendix I only. |
| F4 | PASS | Phase 2 tokens only (white page, navy #1A2D4F, terracotta #C0392B, Arial body); no purple/gold/cream. |
| F5 | PASS | Masthead, terracotta section headers, and stat strip present; zero tables in the front brief (markdown table scan: 0). |
| F6 | PASS | No Phase 2 sample headings/titles/body text copied; kicker and section names are original. |

## Fixes applied during review

1. Removed "Appendix H has the section-by-section detail." from the HB2
   callout (A6) and re-exported HTML/Word; both renders remained 2 pages.

## Blocking issues

None.

## Notes for human reviewers

- 2020–2024 coverage combines roll-call discovery with a documented supplement
  of 23 bills from year-end official indexes (NHMA, OPD, NH Housing, NH
  Bulletin), each resolved against archived official dockets. Major enacted
  laws and prominent failures are covered; low-profile older bills that died
  quietly by voice vote may still be missing. Running the `collect-nh` GitHub
  Actions workflow (which holds the repo's OpenStates secret) remains the way
  to make the older years provably complete; headline framing scopes claims to
  "in this record".
- HB1336 (2026) is described as "override pending this fall" based on the
  docket showing a veto with no override action as of collection; re-check
  before any reprint after October 2026.
