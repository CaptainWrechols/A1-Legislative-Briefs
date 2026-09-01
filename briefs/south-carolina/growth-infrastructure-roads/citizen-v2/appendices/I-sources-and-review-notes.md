# Appendix I — Sources and review notes

Reviewer-facing material: where every kind of claim in the packet comes
from, and how the data was assembled. Nothing here appears in the front
brief by design.

## Claim-to-source map

| Claim type in the front brief | Source |
|---|---|
| Bill identities, titles, sponsor lines, action histories, act numbers | Official SC State House per-bill pages, mirrored in the certified universe (`sources/south-carolina/_universe/`, sessions 123–126) and the issue extract (`sources/south-carolina/growth-infrastructure-roads/processed/bills-core.json`) |
| What each bill would do (plain topics; penny-tax designs; impact-fee changes) | Latest-version full bill text in the universe JSONL, read during curation (`working/south-carolina/growth-infrastructure-roads/build-curation.py` documents each verification; the "A BILL TO..." long titles were read for every ambiguous candidate) |
| Floor vote counts (e.g. 37–1, 114–0, 43–1, 67–28, 106–3, 112–0) | Chamber vote-history tables, verbatim (`processed/bill-votes.json`; universe `rollcalls.json` for the nine universe-added bills); passage/reading/adoption-type motions only |
| "Died in its first committee," "recommitted after floor debate stalled," "stranded on the calendar," "died without completing passage" | Computed from official action histories (`build-evidence-pack.py`), with hand-verified stage overrides for the twelve unusual paths (H5071, S227, S288, H4369, S780, S1069, S1070, H3775, H3845, H4817, H3737, H3075) |
| Committee-tally absence | SC publishes committee outcomes without tallies; asserted as a data limit, never bridged with estimates |
| Budget proviso claims (Road Buyback, the $417.4M/$200M/$225M packages, the school impact-fee prohibition, the fix-it-first rule, the dashboard) | Part IB full texts per enacted cycle (`sources/south-carolina/_universe/part1b/{year}/`, matched subsets in `working/.../provisos/{year}/`), hand-curated in `proviso-curated.json` with caption checks at build time; dollar figures verbatim |
| Background law (Act 40 of 2017 gas-tax phase-in; the 1999 Development Impact Fee Act; penny-tax chapters) | The statutes recited in the filed bills' own texts (Sections 12-28-310, 6-1-910 et seq., Title 4 Chapters 10 and 37) — described as background, not counted as record bills |
| Citizen proposals and consensus notes ([P-…]) | Phase 2 Community Conversations dataset "SC1 – Phase 2 Constituent Proposals – Grid View for Legislators v2" via the issue config — process input, not verified fact. Cross-checked against the source document itself on 2026-09-01: six of seven proposal blocks verify (frequency/tradeoffs/consensus); the developer-pays-growth detail table is blank in the v2 document, so its attributes rest on the config's proposal block alone (noted in Appendix H) |

## Collection and verification notes

- Universe: every instrument of the 123rd–126th General Assemblies with
  full action histories, sponsor lines, latest-version texts, and all
  chamber roll calls; certified in
  `sources/south-carolina/_universe/verification/universe-certification.md`.
- Issue gate: `python3 -m collectors.sc.verify_completeness --strict` passed
  (PASS 20 / WARN 2 / FAIL 0). Both warnings are benign and disclosed: the
  exact-phrase server search returned zero hits for "penny tax" (covered by
  the local scans and the hand title-scan for sales-tax phrasings), and
  five official bill *titles* contain advice-style words (quoted titles,
  not Forum language).
- Curation: keep-all Pass 1 (5,618 hits) hand-reviewed to 178 bills
  (88 core / 73 adjacent / 17 context); exclusion rules and per-bill plain
  topics in `working/south-carolina/growth-infrastructure-roads/curation-map.json`.
  Nine bills were hand-added from the certified universe via a title scan
  for "sales tax", "annexation", and "hospitality tax" phrasings the Pass 1
  terms did not cover; they are marked `source: universe` in the curation
  map.
- Provisos: term-matched candidates (246–305 per cycle) hand-curated to 18
  entries across six enacted cycles plus the FY 2020-21 explicit gap;
  every entry's caption is checked verbatim against the source file at
  build time (`build-proviso-curation.py`), and the disappearance of the
  Preventative Maintenance Credit proviso after FY 2024-25 was verified
  against the full 1,354- and 1,394-proviso sets.
- Vote discipline: only passage/reading/ratification/adoption motions count
  as support signals; tabling, amendment, and carry-over motions are
  excluded.
- No party labels anywhere: the roster/ballot join was not fetched for
  this brief (see Appendix F).
- External-source discipline: the packet contains no claims sourced outside
  the repository's local record (no news accounts, no SCDOT program data,
  no federal filings).

## Review status

- Citizen Reviewer verdict: see `review-report.md` / `review-report.json`
  in the package root.
- Suggested human reviewers: Ryan Echols, Jodi Stephens, Ashley Lovell.
