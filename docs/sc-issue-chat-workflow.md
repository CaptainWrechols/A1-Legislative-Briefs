# South Carolina issue-chat workflow

How the four South Carolina citizen-brief chats run on top of the foundation
(branch `cursor/sc-foundation-a39c`). **One agent per issue**, each on its own
branch, each producing one citizen handout package.

## The four issues

| # | Issue | slug | issue_id | branch |
|---|-------|------|----------|--------|
| 1 | Growth, Infrastructure, and Roads in South Carolina | `growth-infrastructure-roads` | `south-carolina-01-growth-infrastructure-roads` | `cursor/sc-growth-infrastructure-roads-citizen-v2-a39c` |
| 2 | Responsive Elected Leaders in South Carolina | `responsive-elected-leaders` | `south-carolina-02-responsive-elected-leaders` | `cursor/sc-responsive-elected-leaders-citizen-v2-a39c` |
| 3 | Rising Cost of Living in South Carolina | `rising-cost-of-living` | `south-carolina-03-rising-cost-of-living` | `cursor/sc-rising-cost-of-living-citizen-v2-a39c` |
| 4 | Slow Wage Growth in South Carolina | `slow-wage-growth` | `south-carolina-04-slow-wage-growth` | `cursor/sc-slow-wage-growth-citizen-v2-a39c` |

Output target per issue: `briefs/south-carolina/{issue-slug}/citizen-v2/`.

### Recommended order

1. **slow-wage-growth** — smallest, cleanest term set; minimum-wage and
   apprenticeship bills are well-bounded (14 + 13 hits in the 126th alone);
   proves the full pipeline on SC data with the least curation risk.
2. **responsive-elected-leaders** — mid-sized; ethics/elections bills are
   numerous but the proposal set (term limits, RCV, redistricting,
   disclosure) maps crisply onto bill types.
3. **growth-infrastructure-roads** — larger universe (SCDOT, impact fees,
   local-option taxes, plus budget provisos throughout).
4. **rising-cost-of-living** — broadest and most cross-cutting terms
   (housing, utilities, taxes, insurance); benefits from every lesson learned
   in the first three.

## Program context (for writers)

- Phase 2 Community Conversations (Jun–Aug 2026) produced the
  `constituent_proposals` blocks in each config — from the RAG
  constituent-voice dataset "SC1 - Phase 2 Constituent Proposals - Grid View
  for Legislators v2". They are **Forum process input**: label `[P-xxx]` in
  briefs, never present as verified fact.
- Phase 3 civic assembly: Oct 9–11, 2026, USC Law School; ~100 delegates;
  1–3 proposals ratified at ≥70% cross-partisan support.
- Phase 4 target: January 2027 legislative session (the 127th General
  Assembly's first year).

## Canonical pipeline (same as NV + NH)

    optional-collector → evidence-curator → reality-mapper
      → citizen-brief-writer + appendix-builder → design-packager → citizen-reviewer

Visual system: `config/forum-brand.yaml` + `templates/phase-2-samples/`.
Rules: ~grade 5–8 reading level; ≤2 pages front brief; long appendices;
history baskets only ("Often moved before" / "Got support but didn't finish" /
"Rarely moved before"); inline explainers; **no advice language**.

## Per-issue steps

1. `export ISSUE_CONFIG=config/issues/south-carolina-{slug}.yaml`
2. **Pass 1 discovery** — every `search_terms` entry against every session
   (123rd–126th) via `collectors.sc.scstatehouse.fulltext_search`; keep all
   hits; cross-check against OpenStates bulk CSVs if downloaded
   (`collectors.sc.openstates_bulk`). Record gaps in `data-gaps.json`.
   Remember: the site search is exact-phrase — the configs carry
   singular/plural variants where needed.
3. **Pass 2 detail on known bills only** — bill page + vote history per
   discovered bill; ballot PDFs (+ roster party join) only for votes the
   brief will cite.
4. **Provisos** — run the proviso workflow for every enacted cycle
   (2021→2026), namespaced per year
   (see [`sc-appropriations-proviso-workflow.md`](sc-appropriations-proviso-workflow.md));
   hand-prune `proviso-relevant.json` (the foundation spike ships high-recall
   matches for FY 2025-26 as a starting point).
5. **Gate** — `python3 -m collectors.sc.verify_completeness --strict` must not
   FAIL before brief writing.
6. Curate → map → write → package → review per the canonical pipeline.

## Page-1 budget callout (required)

Every SC front brief includes a short **"Also in the state budget (provisos)"**
callout on page 1:

- If issue-relevant provisos exist: name 1–3 of the most consequential (cite
  as "FY 2025-26 proviso 117.32 (caption)"), with the note that budget
  provisos are one-year rules enacted inside the annual budget bill.
- If none are found after review: say so explicitly — "We checked the state
  budget's policy provisos for [years] and found none on this issue." An
  explicit none-found is required; silence is not allowed.
- Votes cited in the callout are on the whole appropriations bill (or a named
  amendment), never on one proviso.

## Guardrails (unchanged from NV + NH)

- No advice language anywhere in citizen-facing text.
- Never invent bill numbers, sponsors, or vote counts; counts come verbatim
  from the vote-history table; party only from the roster join.
- Do not re-scrape Nevada or New Hampshire; do not modify `collectors/nh/` or
  the NELIS collectors.
- `constituent_proposals` are process input `[P-xxx]`; history baskets only;
  ≤2-page front brief; appendices carry the depth.
