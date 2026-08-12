# Appendix I — Sources and review notes

Reviewer-facing material: where every brief claim comes from, how the record
was collected, and what to re-check. Nothing in this appendix appears in the
citizen-facing brief.

## Source keys

| Key | Source |
|---|---|
| S1 | New Hampshire General Court public SQL database (`NHLegislatureDB`): `rollcallsummary` / `rollcallhistory` (all years), `legislation`, `legislationtext`, `sponsors`, `docket` (2025–2026 biennium) |
| S2 | gc.nh.gov official bill texts: HB2 2021 chaptered final (Chapter 91) |
| S3 | Legislative Budget Assistant chapter-law PDF for HB2 2023 (Laws of 2023, Chapter 79); SQL `legislationtext` for HB2 2025 (Chapter 141) |
| S4 | OpenStates bulk session CSVs (complete per-session mirrors of the official GenCourt docket, 2020–2024; committed under `sources/new-hampshire/_bulk/`) — bill lists, sponsors, actions, votes |
| S5 | Derived working files in this repository: `evidence-pack.json`, `curation-map.json`, `dispositions.json`, `hb2-sections.json`, `certification-report.json`, `certification-current.json` (all fact-checked layers over S1–S4) |

## Claim-to-source map (brief)

| Brief claim | Source |
|---|---|
| 894 education bills; 224 became law; 555 killed; 83 laws in 2025–2026 | S5 counts over S1/S4 (discovery, dockets) — `evidence-pack.json` inventory |
| 46 core education sections in the last three trailers; the trailer contents (EFA creation 91:431, divisive-concepts ban 91:298, $100M SWEPT cut 91:322, $4,100 base 79:150, 3.5x catastrophic threshold 79:141, DEI prohibition 141:322, fiscal capacity disparity aid 141:225, 41%→39% trust-fund shares 141:132–133, $20M surplus sweep 141:80, cell-phone mandate 141:455, authority declaration 141:389) | S2/S3 HB2 texts — curated in `hb2-sections.json`; Appendix H |
| HB2 2025 passed the House 184–183; HB2 2021 House 198–181, Senate 14–10; HB2 2023 House concur 326–53 | S1 roll calls (`hb2/{year}/hb2-votes.json`) |
| HB242 (2021) House 198–149, Senate 13–9, override failed 165–182 | S1 roll calls |
| The 18 vetoes and their override tallies (HB324 183–167; HB319 182–173; HB446 181–170; HB356 177–174; HB1093 160–172; HB1454 193–140; HB115 1–347; HB781 28–322; HB667 159–190; HB35 0–350) | S1 roll calls; S1/S4 dockets ("Vetoed by Governor"); 2026 vetoes labeled "no override action recorded as of collection" |
| Conference/concurrence deaths (HB1431 CofC rejected 171–176; HB1311 House 194–180 then non-concur; SB33, SB72, SB96, SB206, SB578, SB209, SB513, HB1639 183–164, HB1695 192–173, HB1665, HB1195, HB468, SB532) | S1 roll calls + S1/S4 dockets |
| HB675 (2025) OTPA 190–185; killed Jan 2026, reconsideration failed 170–185 | S1 roll call (190–185); S1 docket division-vote tally ("Reconsider ITL: MF DV 170-185 01/08/2026 HJ 2") — labeled as a division vote |
| SB523 (2024) Senate 14–10; House motion to consider failed 187–193 | S1 roll call (14–10); S4 docket division-vote tally ("Shall House Consider: MF DV 187-193 lacking necessary two-thirds vote 04/11/2024 HJ 11") — labeled as a division vote |
| HB765 (2025) unanimous 18–0 Inexpedient to Legislate committee report, killed by voice vote | S1 docket ("Committee Report: Inexpedient to Legislate 03/17/2025 (Vote 18-0; CC) HC 17") — labeled as a committee vote |
| Open-enrollment votes (HB741 198–174; SB101 14–10 then 168–184; HB709 182–159; SB97 199–165; HB771 205–169; HB1817 179–156) | S1 roll calls + dockets |
| Funding-bill votes (HB1815 188–162 and 16–8; SB420 21–1 and 261–71; HB1799 185–159; HB491 195–157; HB503 345–27; HB651 190–155; SB582 16–8; HB1557 184–157; SB584 16–8) | S1 roll calls |
| Choice and content votes (SB295 House 188–176; HB367 187–184; HB1683 189–166; SB432 14–9; HB1716 194–166; HB320 208–141; HB1323 187–139; SB213 201–175; SB272 14–10 then postponed 195–190; SB211 16–8; HB1312 186–185; SB341 postponed 185–176; SB430 193–163; HB10 2025 212–161; HB10 2023 OTP failed 189–195) | S1 roll calls |
| Meals votes (HB665 189–158; SB204 183–161; HB703 202–173) and CTE votes (SB99 House 206–167) | S1 roll calls |
| 83 laws of 2025–2026 listed in "Already law" | S1 dockets ("Signed by Governor ... Chapter N") |
| "1 of 6 citizen proposals already law in its own words" (the special-education cost commission, SB57 2025, Chapter 220) | S1 docket + `legislationtext`; grid proposal list in `config/issues/new-hampshire-public-education.yaml` |
| Sponsor counts and 62 cross-party bills | S1 sponsors (2025–2026) + S4 bulk sponsorships (2020–2024) — `evidence-pack.json` people signals |
| Federal overlap statements (ESSA annual testing, IDEA, Title I, USDA meals/Summer EBT, FERPA, Perkins) | Descriptive statements of federal law; the NH bills cited (HCR10 2024, HB601 2024, HB665 2026, HB1727 2026, HB1019 2024, SB303 2025) are in the pack |

## Completeness certification (2020–2024 and 2025–2026)

The five OpenStates bulk session archives are complete mirrors of the official
docket: 5,467 bills. `working/.../certify-universe.py` verified that (1) every
collected 2020–2024 bill exists in that universe, (2) no bill in the set is
missing votes the mirror knows about (the one bulk-vote/SQL mismatch is 2022
HB1670's table motion — a division vote, MA DV 188–163 in the official docket,
which the SQL roll-call table does not carry by design), and (3) every one of
the 5,467 titles was swept with a 48-pattern wide-net education vocabulary far
broader than the issue's search terms — bare school/educat stems, students,
teachers, testing, choice, CTE, sports, and library-materials vocabulary. All
291 wide-net matches not already in the set were reviewed by hand: 138 were
added (tagged `supplement:universe-certification`) and 153 were excluded with
per-bill categories (higher education, driver training, child care, public
libraries, occupational licensing, housing, and similar) recorded in
`working/.../certification-report.json` and summarized in
`certification-report.md`. A 2020–2024 K-12 education bill could be absent
from this record only if its title avoids that entire vocabulary.

The same net was then applied to the complete current biennium
(`certify-current-biennium.py`): all 2,234 bills in the official SQL
legislation table for 2025–2026 were swept, 49 real misses were added (tagged
`supplement:universe-certification-current` — including the education
financing bills HB1815 and SB659, whose titles carry none of the seed
vocabulary), and 77 candidates were excluded with categories in
`certification-current.json` / `certification-current.md`. One docket-mirror
gap is documented: 2024 HB1378 has only its introduction row in every official
mirror (GenCourt's own archived docket for that LSR returns a server error);
its resolution — withdrawn after introduction — is hand-researched and cited
in `manual-resolutions.json`.

## Collection and review notes

- Votes come exclusively from the state's `rollcallsummary` table; where the
  brief cites a division or committee tally, it is quoted from the official
  docket text and labeled as such (three instances, whitelisted in
  `scan-lege-brief.py` with their docket citations).
- Dispositions are docket-derived for all 1,049 bills, zero unresolved; seven
  manual resolutions carry citations (`manual-resolutions.json`).
- Biennium carryovers (72 first-year records) are counted once, in their
  decision year, after verifying terminal actions in the first-year docket.
- HB2 votes are on the whole trailer and are never attributed to a section.
- The automated review gates: `scan-lege-brief.py` (advice language, cited
  bills, vote pairs) and `fact-check-reality-map.py` (every reality-map claim
  against the evidence pack) — both PASS on the shipped revision.
