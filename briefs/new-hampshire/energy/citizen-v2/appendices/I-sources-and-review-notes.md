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
| S6 | GenCourt legacy bill-status archive (`bill_docket.aspx` by LSR) and the official House Journals (`calendars_journals` viewer) — used for the two hand-researched docket-mirror gaps |

## Claim-to-source map (brief)

| Brief claim | Source |
|---|---|
| 375 energy bills; 103 became law; 38 laws in 2025–2026 | S5 counts over S1/S4 (discovery, dockets) — `evidence-pack.json` inventory |
| 28 core energy sections in the last three trailers; the trailer contents (Department of Energy 91:187, PUC rebuild 91:204/91:206, consumer advocate 91:211, utility assessments 91:243–245, rate reduction bonds to 2027 91:98, group-host net metering 91:234, renewable energy fund 91:240, RGGI fund 91:293, offshore wind office 91:285–286, energy data platform 91:292, utility assessment rewrite 79:119–122, EV surcharge 79:475, Regional Energy Advocacy Fund 79:123, fuel-assistance cliff study 79:581, renewable-fund sweep and diversion 141:140–142) | S2/S3 HB2 texts — curated in `hb2-sections.json`; Appendix H |
| HB2 2025 passed the House 184–183 (Senate 16–8); HB2 2021 House 198–181, Senate 14–10; HB2 2023 House concur 326–53 | S1 roll calls (`hb2/{year}/hb2-votes.json`) |
| The 7 vetoes and their override tallies (SB159 227–128 then 207–130; HB466 201–120 then 199–139; SB124 214–141 then Senate 14–10; SB122 212–140 then Senate 14–10; HB142 269–109 then 194–159; SB79 194–179 then 0–23; HB221 no override action recorded as of collection) | S1 roll calls; S1/S4 dockets ("Vetoed by Governor") |
| Died-between-chambers bills (HB342 concurrence failed 154–195 then House non-concur by voice; HB710; SB78; HB624) | S1 roll calls + S1/S4 dockets; HB342's non-concur row hand-staged (`manual-resolutions.json` — the docket spells it "Non-Concurs") |
| Proven-support votes (SB109 Senate 24–0 three times, then tabled; HB351 House 198–179; HB1218 House 215–125; HB1542 189–157; HB219 175–152; SB603 Senate 13–11; HB1496 House 180–101) | S1 roll calls + dockets |
| HR16 (2022) unanimous 21–0 committee report and consent-calendar adoption | S6: GenCourt archive docket (LSR 2317, "Committee Report: Ought to Pass HR0016 (Vote 21-0; CC)") + House Journal No. 3, 02/16/2022 (consent calendar and Third Reading/Final Passage) — labeled as a committee vote; the floor row is a documented GenCourt docket-mirror gap |
| 2025–2026 law votes (HB1775 House 198–153; HB682 206–163; HB690 200–155; HB672 concur 185–151; SB4 Senate 23–0; HB723 201–160 on the carryover record) | S1 roll calls |
| Efficiency-settlement votes (HB549 House 343–0; HB2023 Senate 23–0 on the remainder; SB269 interim study 182–152; HB96 tabled 199–135) | S1 roll calls |
| Net-metering and aggregation votes (SB228 killed 190–151; SB449 killed 181–158; SB106 postponed 172–152; HB1402 interim study 188–148) | S1 roll calls |
| TOU/data-layer votes (HB631 killed 192–180) and climate votes (HR17 adopted 178–159; HB524 OTP failed 181–186; HCR4 adopted 195–149) | S1 roll calls |
| Rate/EV votes (HB504 204–165; HB189 206–148; HB1623 184–168; SB272 killed 195–163) | S1 roll calls |
| 38 laws of 2025–2026 listed in "Already law" | S1 dockets ("Signed by Governor ... Chapter N") |
| "1 of 5 citizen proposals already substantially law" (community power: HB315 2021, SB265 2022, HB385 2023, HB1600 2024, SB590 and HB1742 2026) | S1/S4 dockets; grid proposal list in `config/issues/new-hampshire-energy.yaml` |
| Sponsor counts and 41 cross-party bills | S1 sponsors (2025–2026) + S4 bulk sponsorships (2020–2024) — `evidence-pack.json` people signals |
| Federal overlap statements (FERC/ISO-New England wholesale markets, interstate transmission and pipeline licensing, NRC licensing and nuclear waste, Gulf of Maine offshore leasing, LIHEAP, the federal Weatherization Assistance Program, clean-energy tax credits, RGGI as an interstate program) | Descriptive statements of federal law and programs; the NH bills cited (HR15 2025, HR16 2022, HCR4 2025, HB690 2025, SB102 2023) are in the pack |
| "Geothermal has never had a New Hampshire bill in either universe" | Both certification sweeps: the word-bounded wide net (incl. `geothermal`) over all 5,467 + 2,234 titles returned zero geothermal bills; the term also scored zero in calibration |

## Completeness certification (2020–2024 and 2025–2026)

The five OpenStates bulk session archives are complete mirrors of the official
docket: 5,467 bills. `working/.../certify-universe.py` verified that (1) every
collected 2020–2024 bill exists in that universe (zero ghosts), (2) no bill in
the set is missing votes the mirror knows about (zero bulk-vote/SQL
mismatches), and (3) every one of the 5,467 titles was swept with a 51-pattern
wide-net energy vocabulary far broader than the issue's search terms — bare
energ/electric/utilit stems, word-bounded wind/oil/gas/meter/power, renewable,
solar, fuel, pipeline, kilowatt, megawatt, thermal, hydro, weatherization,
RGGI, Eversource, grid, ratepayer, nuclear, reactor, turbine, and the rest.
All 17 wide-net matches not already in the set were reviewed by hand: 3 were
added (tagged `supplement:universe-certification` — 2021 SB109's municipal
host customer generators, 2020 SB256's emergency generators, and 2020 SB429's
plastic-to-oil study, none of whose titles carry an energy/electric word) and
14 were excluded with per-bill categories (government powers, 'generation'
false positives, tear gas, waste generators, hydrology, coal grading, heating-
trade licensing) recorded in `working/.../certification-report.json` and
summarized in `certification-report.md`. A 2020–2024 energy bill could be
absent from this record only if its title avoids that entire vocabulary.

The same net was then applied to the complete current biennium
(`certify-current-biennium.py`): all 2,234 bills in the official SQL
legislation table for 2025–2026 were swept, 1 real miss was added (tagged
`supplement:universe-certification-current` — 2025 SB228, "limitations on
community customer generators", again with no energy word in the title), and
13 candidates were excluded with categories in `certification-current.json` /
`certification-current.md`. Two docket-mirror gaps are documented and
hand-researched with citations in `manual-resolutions.json`: 2022 HR16, whose
floor adoption GenCourt's own docket omits (resolved from House Journal No. 3,
February 16, 2022), and 2020 HB1355, which passed the House and died in a
Senate committee when the COVID-truncated session ended.

## Collection and review notes

- Votes come exclusively from the state's `rollcallsummary` table; where the
  brief cites a committee tally, it is quoted from the official docket text
  and labeled as such (one instance — HR16's 21–0 — whitelisted in
  `scan-lege-brief.py` with its docket citation).
- Dispositions are docket-derived for all 460 bills, zero unresolved; four
  manual resolutions carry citations (`manual-resolutions.json`): the HR16
  journal adoption, HB1355's COVID-session death, 2025 HB342's "Non-Concurs"
  spelling the classifier's pattern misses, and 2025 HB723, which the state
  database keys to BOTH years of the biennium with identical dockets — counted
  once, in 2026, per the carryover rule.
- Biennium carryovers (38 first-year records) are counted once, in their
  decision year, after verifying terminal actions in the first-year docket.
- HB2 votes are on the whole trailer and are never attributed to a section.
- The overlap rule with the sibling packets is documented in
  `build-curation.py`: the utility-property-tax / SWEPT-on-generators bills
  (HB696, SB277, and the assessing-power-generation commissions) appear in
  BOTH the property-taxes packet and this one, each from its own angle; the
  ratepayer-charge bills that packet excluded as utility regulation are core
  here, and the energy sections the sibling HB2 analyses excluded are this
  packet's Appendix H core.
- The automated review gates: `scan-lege-brief.py` (advice language, cited
  bills, vote pairs) and `fact-check-reality-map.py` (every reality-map claim
  against the evidence pack) — both PASS on the shipped revision.
