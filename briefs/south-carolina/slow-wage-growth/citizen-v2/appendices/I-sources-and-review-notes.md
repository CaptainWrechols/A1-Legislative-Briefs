# Appendix I — Sources and review notes

Reviewer-facing material: where every kind of claim in the packet comes
from, and how the data was assembled. Nothing here appears in the front
brief by design.

## Claim-to-source map

| Claim type in the front brief | Source |
|---|---|
| Bill identities, titles, sponsor lines, action histories, act numbers | Official SC State House per-bill pages, mirrored in the certified universe (`sources/south-carolina/_universe/`, sessions 123–126) and the issue extract (`sources/south-carolina/slow-wage-growth/processed/bills-core.json`) |
| What each bill would do (plain topics; dollar amounts in minimum-wage bills) | Latest-version full bill text in the universe JSONL, read during curation (`working/south-carolina/slow-wage-growth/build-curation.py` documents each verification) |
| Floor vote counts (e.g. 121–0, 16–27, 105–1) | Chamber vote-history tables, verbatim (`processed/bill-votes.json`); passage-type motions only |
| "Died in its first committee," "died in conference," "ran out of Senate calendar" | Computed from official action histories (`build-evidence-pack.py`) |
| Committee-tally absence | SC publishes committee outcomes without tallies; asserted as a data limit, never bridged with estimates |
| Budget proviso claims (lead apprenticeship agency, WINS amounts, employee raises) | Part IB full texts per enacted cycle (`working/south-carolina/slow-wage-growth/provisos/{year}/`), hand-curated in `proviso-curated.json` |
| "No state minimum wage; local minimums preempted" | Bill texts amending S.C. Code §6-1-130 (scope of authority to set minimum wage) and the issue config's code-section notes (§41-1-110) |
| Citizen proposals and consensus notes ([P-…]) | Phase 2 Community Conversations dataset "SC1 – Phase 2 Constituent Proposals – Grid View for Legislators v2" via the issue config — process input, not verified fact |
| Federal youth training wage ($4.25 / first 90 days) | Federal FLSA background noted for venue context; not an SC-record claim |

## Collection and verification notes

- Universe: all 15,817 instruments of the 123rd–126th General Assemblies
  with full action histories, sponsor lines, latest-version texts, and all
  8,879 chamber roll calls; certified in
  `verification/universe-certification.md` and independently audited
  (per-bill vote endpoints reconciled against chamber-wide lists; all 975
  Act List rows 2019–2026 joined to enumerated bills).
- Issue gate: `python3 -m collectors.sc.verify_completeness --strict` passed
  (20 pass / 2 warn / 0 fail). The two warnings are benign and disclosed:
  four search terms have zero hits statewide ("youth wage," "training
  wage," "tip credit," "wage theft" — itself a finding used in the brief),
  and five official bill *titles* contain advice-style words (e.g.
  "Sentencing Reform"), which are quoted titles, not Forum language.
- Curation: keep-all Pass 1 (5,744 hits) hand-reviewed to 133 bills
  (54 core / 52 adjacent / 27 context); exclusion rules and per-bill plain
  topics in `working/south-carolina/slow-wage-growth/curation-map.json`.
  Ambiguous bills were verified against latest-version full text before
  tier assignment.
- Provisos: term-matched candidates (566–674 per cycle) hand-curated to 46
  wage/workforce provisos across six enacted cycles; FY 2020-21 none-found
  gap stated explicitly.
- No new scraping was performed for this brief; ballot-PDF/roster party
  joins were deliberately not fetched, so the packet contains no party
  claims.

## Review

- Automated gate: citizen-reviewer v2.3 — see `review-report.md` /
  `review-report.json` in this folder.
- Human reviewers for the PR: Ryan Echols, Jodi Stephens, Ashley Lovell.
