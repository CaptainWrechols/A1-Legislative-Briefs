# Appendix I — Sources and review notes

Reviewer-facing material: where every kind of claim in the packet comes
from, and how the data was assembled. Nothing here appears in the front
brief by design.

## Claim-to-source map

| Claim type in the front brief | Source |
|---|---|
| Bill identities, titles, sponsor lines, action histories, act numbers | Official SC State House per-bill pages, mirrored in the certified universe (`sources/south-carolina/_universe/`, sessions 123–126) and the issue extract (`sources/south-carolina/responsive-elected-leaders/processed/bills-core.json`) |
| What each bill would do (plain topics; term caps; disclosure designs) | Latest-version full bill text in the universe JSONL, read during curation (`working/south-carolina/responsive-elected-leaders/build-curation.py` documents each verification) |
| Floor vote counts (e.g. 102–0, 40–0, 53–45, 29–14, 26–18) | Chamber vote-history tables, verbatim (`processed/bill-votes.json`; universe `rollcalls.json` for the REACH Act family); passage/adoption-type motions only, with the two decisive procedural votes (H3570 concurrence 23–86, H5683 continue 26–18) labeled as procedural |
| "Died in its first committee," "died in conference," "shelved on a motion to continue," "died on the Senate calendar" | Computed from official action histories (`build-evidence-pack.py`), with hand-verified stage overrides for the six unusual paths (H3570, H5683, S133, H3676, H3125, H4492) |
| Committee-tally absence | SC publishes committee outcomes without tallies; asserted as a data limit, never bridged with estimates |
| Budget proviso claims (ethics filing rule, election-litigation power, lobbying bans, civic-education money) | Part IB full texts per enacted cycle (`working/south-carolina/responsive-elected-leaders/provisos/{year}/`), hand-curated in `proviso-curated.json` with caption checks |
| "The constitution assigns reapportionment to the General Assembly," "two-thirds plus referendum" | The constitutional-amendment procedure recited in the joint resolutions' own texts (e.g. S6, H3044) and the S.C. Constitution provisions they amend |
| Citizen proposals and consensus notes ([P-…]) | Phase 2 Community Conversations dataset "SC1 – Phase 2 Constituent Proposals – Grid View for Legislators v2" via the issue config — process input, not verified fact |

## Collection and verification notes

- Universe: every instrument of the 123rd–126th General Assemblies with
  full action histories, sponsor lines, latest-version texts, and all
  chamber roll calls; certified in
  `sources/south-carolina/_universe/verification/universe-certification.md`.
- Issue gate: `python3 -m collectors.sc.verify_completeness --strict` passed
  (PASS 21 / WARN 1 / FAIL 0). The warning is benign and disclosed: five
  official bill *titles* contain advice-style words (quoted titles, not
  Forum language).
- Curation: keep-all Pass 1 (5,548 hits) hand-reviewed to 189 bills
  (139 core / 38 adjacent / 12 context); exclusion rules and per-bill plain
  topics in `working/south-carolina/responsive-elected-leaders/curation-map.json`.
  Ambiguous bills were verified against latest-version full text before
  tier assignment. Four REACH Act civics bills were hand-added from the
  certified universe (their text contains none of the issue's search
  terms) and are marked `source: universe` in the curation map.
- Provisos: term-matched candidates (191–234 per cycle) hand-curated to 32
  entries across six enacted cycles plus the FY 2020-21 explicit gap;
  every entry's caption is checked verbatim against the source file at
  build time (`build-proviso-curation.py`).
- Vote discipline: only passage/reading/ratification/adoption motions count
  as support signals; tabling, amendment, and continue motions are
  excluded, and the two decisive procedural votes the brief mentions are
  described as procedural in place.
- No party labels anywhere: the roster/ballot join was not fetched for
  this brief (see Appendix F).
- External-source discipline: the packet contains no claims sourced outside
  the repository's local record (no news accounts, no litigation status,
  no counts of other states' Article V applications).

## Review status

- Citizen Reviewer verdict: see `review-report.md` / `review-report.json`
  in the package root.
- Suggested human reviewers: Ryan Echols, Jodi Stephens, Ashley Lovell.
