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

**The data is already collected on the foundation branch.** The full state
universe (every bill, vote, ratification, and latest-version text for the
123rd–126th sessions) lives under `sources/south-carolina/_universe/`
(certified: `verification/universe-certification.md`), and each issue's
artifact set is prebuilt:

- `sources/south-carolina/{slug}/pass1/bills.json` — keep-all discovery
  (server full-text search + local full-text/title scans over the universe)
- `sources/south-carolina/{slug}/processed/bills-core.json` — full records
  (actions, sponsors, governor actions, version URLs)
- `sources/south-carolina/{slug}/processed/bill-votes.json` — every floor
  roll call per discovered bill, counts verbatim
- `sources/south-carolina/{slug}/data-gaps.json` — explicit gaps
- `working/south-carolina/{slug}/provisos/{year}/` — Part IB matches per
  enacted cycle (full proviso sets shared at `_universe/part1b/{year}/`)

So an issue chat:

1. `export ISSUE_CONFIG=config/issues/south-carolina-{slug}.yaml`
2. **Gate first** — `python3 -m collectors.sc.verify_completeness --strict`.
3. **Curate** — prune `pass1/bills.json` by `relevance_flag` + hand review
   (nothing was dropped upstream); prune `proviso-relevant.json` per cycle.
4. **On-demand fetches only** — ballot PDFs (+ roster party join) for votes
   the brief will cite (`ballot_pdf_key` is recorded per roll call); earlier
   bill versions via the recorded `versions[].url` when amendment history
   matters; re-run `collect_issue` only if terms change.
5. Curate → map → write → package → review per the canonical pipeline.

Committee votes: South Carolina publishes committee *outcomes* in bill
histories, never tally tables — briefs must not imply counted committee votes.

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
