# Appendix I — Sources and review notes

Reviewer-facing material: where every kind of claim in the packet comes
from, and how the data was assembled. Nothing here appears in the front
brief by design.

## Claim-to-source map

| Claim type in the front brief | Source |
|---|---|
| Bill identities, titles, sponsor lines, action histories, act numbers | Official SC State House per-bill pages, mirrored in the certified universe (`sources/south-carolina/_universe/`, sessions 123–126) and the issue extract (`sources/south-carolina/rising-cost-of-living/processed/bills-core.json`) |
| What each bill would do (plain topics; exemption amounts; who a ban covers) | Latest-version full bill text in the universe JSONL, read during curation (`working/south-carolina/rising-cost-of-living/build-curation.py` documents the review; headline bills verified individually) |
| Floor vote counts (e.g. 105–1, 118–0, 44–0, 64–47) | Chamber vote-history tables, verbatim (`processed/bill-votes.json`); passage-type motions only; every pair cited in the brief was re-matched programmatically against the tables |
| "Died in its first committee," "died in conference," "recommitted" | Computed from official action histories (`build-evidence-pack.py`) |
| Committee-tally absence | SC publishes committee outcomes without tallies; asserted as a data limit, never bridged with estimates |
| Budget proviso claims (extra homestead exemption, tax-rate suspension, personal-finance order, Santee Cooper oversight funding) | Part IB full texts per enacted cycle (`working/south-carolina/rising-cost-of-living/provisos/{year}/`), hand-curated in `proviso-curated.json` |
| The personal-finance graduation requirement being in force (Reg. 43-234 / Doc. 5130, eff. May 26, 2023; Class of 2027) | State Register (SCSR 47-5, Doc. 5130) and the State Board of Education's published regulation — the one claim verified outside the bill record, because a stalled approval resolution does not stop a regulation from taking effect |
| Homestead exemption ($50,000, §12-37-250), Act 388 school-tax swap (§11-11-156), assessment ratios, SEI disclosures (ethics law) | Statutory context cited by section number; provisions referenced in the curated bill texts and proviso texts |
| Citizen proposals, reported frequency/consensus/tradeoff cells, and legislator notes ([P-…]) | The final proposal grid ("SC1 – Rising Cost of Living", 2026-09-04) via the issue config — process input, not verified fact. Provenance caveat (also Appendix F item 11): the final-grid document did not transfer into this workspace; cells are the Phase 2 grid lines ("Grid View for Legislators v2"), which the final grids carry forward verbatim per the slow-wage-growth final grid. Confirm against the original. |
| Child care assistance topic and record scan | Reported legislator discussions (2026-09-04 request; not part of the record); scan method and findings in `working/south-carolina/rising-cost-of-living/childcare-assistance-scan.md`, built on this issue's Pass 1 childcare hits and the slow-wage-growth full-universe scan; proviso facts verified against `_universe/part1b/{year}/` |

## Collection and verification notes

- Universe: all 15,817 instruments of the 123rd–126th General Assemblies
  with full action histories, sponsor lines, latest-version texts, and all
  chamber roll calls; certified in `verification/universe-certification.md`.
- Issue gate: `python3 -m collectors.sc.verify_completeness --strict` passed
  before curation — PASS_WITH_WARNINGS (21 pass / 1 warn / 0 fail). The one
  warning is benign and disclosed: the optional OpenStates bulk-CSV mirror
  (an external cross-check) is not on disk; completeness is certified from
  the official surfaces (enumeration + chamber vote lists + ratification
  sheets + full-text search joins).
- Curation: keep-all Pass 1 (6,814 hits) hand-reviewed to 271 bills (121
  core / 136 adjacent / 14 context, incl. the 17-bill childcare theme added
  2026-09-04); exclusion rules and per-bill plain topics in
  `working/south-carolina/rising-cost-of-living/curation-map.json`. Headline
  and ambiguous bills verified against latest-version full text before tier
  assignment. Three bills matched no Pass 1 term and were added from hand
  full-text scans of the universe (2019-20 H4149 and 2021-22 H3116,
  personal finance; 2023-24 H5205, childcare), marked with a `source` field.
- Provisos: term-matched candidates (434–564 per cycle) hand-curated to 43
  provisos across six enacted cycles (`build-proviso-curation.py` →
  `proviso-curated.json`), each verified by reading caption and text. The
  FY 2020-21 no-enacted-Part-IB gap is stated explicitly.
- Vote integrity: every vote pair cited in the front brief and spotlights
  was programmatically matched to the corresponding bill's passage-vote
  table (zero unmatched). No committee tallies appear or are implied
  anywhere. No party labels appear anywhere (no roster join fetched).
- Pipeline: `build-curation.py` → `curation-map.json` →
  `build-evidence-pack.py` → `evidence-pack.json` → `reality-map.{json,md}`
  → this package. All working files live under
  `working/south-carolina/rising-cost-of-living/`.

## Review status

Citizen Reviewer v2.3 gate results are in `review-report.md` /
`review-report.json` at the package root. Reviewers for the PR:
Ryan Echols, Jodi Stephens, Ashley Lovell.
