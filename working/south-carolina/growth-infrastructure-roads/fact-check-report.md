# Independent fact-check — Growth, Infrastructure, and Roads citizen brief

Fact-check pass · 2026-09-04 · Result: **107 of 107 automated live checks
pass**, plus secondary-source confirmations. Two substantive completeness
corrections were made and are logged below.

## Method

The brief was built entirely from the certified local snapshot collected
2026-08-25. This pass re-verified its load-bearing claims against data
independent of that snapshot:

1. **Live scstatehouse.gov** (fetched 2026-09-04, ≥1s throttle): bill
   statuses and act numbers for all 13 enacted measures cited; the key
   non-enactment paths (S227 amended-then-died, H5071 recommitted, the
   shortline credit's two House passages, the RIA 112–0 passage, the 2020
   regulation resolutions stranded on the calendar, and negative act-number
   checks on 9 non-enacted bills); all 51 cited floor-vote pairs, verbatim,
   from the live vote-history tables; proviso numbers, captions, and
   verbatim dollar figures from the live enacted Part IB pages (FY 2021-22,
   2022-23, 2024-25, 2025-26, 2026-27), including negative checks that the
   Preventative Maintenance Credit proviso stopped appearing after
   FY 2024-25.
2. **Live SC Code of Laws**: the background-law claims — the Development
   Impact Fee Act at 6-1-910 et seq. with its repair/operation exclusion,
   the capital-project and green-space penny articles in Title 4 Ch. 10,
   the transportation penny/tolls in 4-37-30, and the Act 40 two-cents-a-
   year gas-fee phase-in in 12-28-310.
3. **Secondary sources (web)**: the SCDOT Modernization Act (SC Council on
   Competitiveness and Municipal Association of SC summaries confirm the
   governance change, the January 1, 2027 commission abolition, and the
   act's broader contents; signed May 18, 2026); the County Green Space
   Sales Tax Act (SCDOR local-tax publications and the House Legislative
   Update confirm Act 166 of 2022, up-to-1%, referendum-gated); the
   Development Impact Fee Act (Act 118 of 1999, H3641, confirmed via the
   official bill record and multiple county/municipal impact-fee studies).

Machine-readable results: `fact-check-live.json` (107 checks). The checker
itself: `fact-check-live.py` (re-runnable).

## Findings

- **Every vote count, act number, proviso number, dollar figure, committee
  stop, and background-law claim verified.** No numeric or status errors
  were found anywhere in the packet.
- **One material completeness gap, now fixed:** the brief described the
  SCDOT Modernization Act (S831, Act 177 of 2026) as a governance change
  only. The ratified act is an omnibus that also: creates the Pothole
  Mitigation Program (new Section 57-5-1800 — public pothole reporting
  including a free mobile app, a seven-day repair requirement, and
  $15,000,000 a year for full-depth repair of repeat potholes); enacts the
  phased design-build method (57-5-1710) and construction manager/general
  contractor authority (57-5-1720) — the same method whose standalone bills
  (H5312, H3560) the brief reported as dead; rewrites the toll framework
  around new-capacity "choice lanes" (renamed from turnpike facilities;
  usage charges only on capacity-adding lanes); authorizes public-private
  partnership agreements capped at sixty years (57-3-205); requires an
  independent external performance audit of SCDOT every four years; abolishes
  the commission effective January 1, 2027; and resets the county "C"-funds
  rule to a thirty-three percent state-highway share. Without these, the
  fix-roads-first and contractor-accountability narratives ("every bill
  died", "design-build died twice") were true of standalone bills but
  misleading about the enacted law. Corrected throughout the packet (front
  brief, spotlights, appendices B/H, glossary, evidence pack, reality map).
- **Verified context noted, not added to citizen text** (the packet's
  external-source discipline keeps citizen-facing claims to the legislative
  record): SCDOR publications show exactly one county (Beaufort) has used
  the Green Space penny — effective May 1, 2023, ended February 28, 2025
  after reaching its $100 million cap; no county currently imposes it. The
  brief's claim (the act created the tool) stands; implementation status is
  outside the bill record and is recorded here for human reviewers.
- **Effective-date nuance:** the governor-appointment section of Act 177 was
  effective on approval (signed May 18, 2026, per secondary sources); the
  commission abolition is effective January 1, 2027. The brief now states
  the January 1, 2027 date; it does not state the signing date (not in the
  collected action list, which records "Signed By Governor" without
  contradiction).

## Corrections applied (2026-09-04)

1. Act 177 scope added to: front brief ("Where something finished",
   maintenance bullet, "New from 2025–2026", glossary — including new
   "Choice lanes" and "Pothole Mitigation Program" entries), the standalone
   spotlights (new "Already law (inside the SCDOT Modernization Act)"
   groups for fix-roads-first and contractor-accountability; toll-provision
   bullet for local-funding-tools), Appendix B (four theme scorecards),
   Appendix H (three crosswalk entries), the curation map's S831 plain
   topic, the evidence pack's crosswalk notes, and the reality map.
2. "Every maintenance-accountability bill died" and "design-build died
   twice" phrasing qualified to "standalone" throughout, with the enacted
   Act 177 counterpart stated alongside.

All renders rebuilt after the corrections; front-brief page discipline
re-verified (see review-report).
