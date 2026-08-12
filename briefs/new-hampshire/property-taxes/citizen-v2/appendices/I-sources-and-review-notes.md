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
| S5 | Derived working files in this repository: `evidence-pack.json`, `curation-map.json`, `dispositions.json`, `hb2-sections.json`, `certification-report.json` (all fact-checked layers over S1–S4) |

## Claim-to-source map (brief)

| Brief claim | Source |
|---|---|
| 476 tax/revenue bills; 101 became law; 306 killed; 32 laws in 2025–2026 | S5 counts over S1/S4 (discovery, dockets) — `evidence-pack.json` inventory |
| 35 core tax/revenue sections in the last three trailers; rate figures (BPT 7.7→7.6→7.5, BET 0.675→0.55, M&R 9→8.5, I&D phase-out and 1/1/2025 repeal, 41%→39% trust-fund shares, $100M SWEPT cut, VLT 31% state take) | S2/S3 HB2 texts — curated in `hb2-sections.json`; Appendix H |
| HB2 2025 passed the House 184–183; HB2 2021 House 198–181, Senate 14–10; HB2 2023 House concur 326–53 | S1 roll calls (`hb2/{year}/hb2-votes.json`) |
| HB242 (2021) House 198–149, Senate 13–9, override failed 165–182 | S1 roll calls |
| HB1417 (2022) House OTP 186–159, Senate OTP 22–2, tabled 14–10, deadline death | S1 roll calls + S4 docket |
| SB114 (2023) 23–0 then tabled; SB20 (2025) 23–0 then deadline; SB99 (2021) 24–0 then tabled; HB197 (2026) ITL 172–159 | S1 roll calls + S1/S4 dockets |
| HB1221 (2022) House 177–141, Chapter 189, one-time 7.5% municipal retirement payment | S1 roll calls + S4 docket + title/text |
| CACR1 202–171; CACR2 201–170; CACR15 183–185; CACR7 192–191 (three-fifths failures) | S1 roll calls + S4 docket ("Lacking Necessary Three-Fifths Vote") |
| HB1492 (2020) ITL 320–11; HB1478 (2022) ITL 304–40; HB1636 (2026) ITL 284–76; HB491 (2026) ITL 195–157; HB1580 (2026) ITL 284–55 | S1 roll calls |
| HB1786 (2026) tabled 189–158; remove-from-table failed 100–235 | S1 roll calls |
| HB675 (2025) OTPA 190–185; killed Jan 2026, reconsideration failed 170–185 | S1 roll call (190–185); S1 docket division-vote tally ("Reconsider ITL: MF DV 170-185 01/08/2026 HJ 2") — the one brief vote number that is not a roll call, labeled as a division vote |
| HB1699 (2020) House 172–142 then tabled; HB1160 (2020) House 174–113 then tabled; SB104 (2023) Senate 13–11 then postponed | S1 roll calls + S4 dockets |
| HB1807 (2026) House 185–150, Chapter 312; SB600 Chapter 141; HB1300, HB1331 (193–157), HB1374 (CofC 179–161) chapters | S1 roll calls + dockets |
| SB83 (2025) Chapter 16 (2026); exemption-reimbursement fund + VLT funding | S1 docket + `legislationtext`; HB2 2025 141:26 for the VLT authorization |
| Homestead-exemption tries: HB1387 (2022) killed, HB1034 (2024) interim study, HB1648 (2026) interim study | S4/S1 dockets |
| Never-filed claims (I&D restoration; consolidation incentives) | S5 `certification-report.json` (2020–2024 bulk sweep) and `certification-current.json` (2025–2026: the identical wide net over all 2,234 titles in the official SQL legislation table, every candidate human-reviewed) |
| Vetoes (HB242 2021; SB63 2023; HB1102, HB1565 2026) | S1/S4 dockets ("Vetoed by Governor") |
| 27 laws of 2025–2026 listed in "Already law" | S1 dockets ("Signed by Governor ... Chapter N") |
| Sponsor counts and 40 cross-party bills | S1 sponsors (2025–2026) + S4 bulk sponsorships (2020–2024) — `evidence-pack.json` people signals |
| Federal overlap statements (SALT deduction, IDEA/Title I, Wayfair, federal corporate tax, wire/horseracing law) | Descriptive statements of federal law; the NH bills cited (HCR10 2024, HB1097 2022, HB114/HB265 2020, HB1668 2026, SB484 2020) are in the pack |

## Completeness certification (2020–2024 and 2025–2026)

The five OpenStates bulk session archives are complete mirrors of the official
docket: 5,467 bills. `working/.../certify-universe.py` verified that (1) every
collected 2020–2024 bill exists in that universe, (2) no bill in the set is
missing votes the mirror knows about, and (3) every one of the 5,467 titles
was swept with a 46-pattern wide-net tax/revenue vocabulary far broader than
the issue's search terms. All 235 wide-net matches not already in the set were
reviewed by hand: 34 were added (tagged `supplement:universe-certification`)
and 201 were excluded with per-bill categories (cannabis bills, transportation
tolls, education testing 'assessment' false positives, condominium
assessments, right-to-know exemptions, and similar) recorded in
`working/.../certification-report.json` and summarized in
`certification-report.md`. A 2020–2024 tax or revenue bill could be absent
from this record only if its title avoids that entire vocabulary.

The same net was then applied to the complete current biennium
(`certify-current-biennium.py`): all 2,234 bills in the official SQL
legislation table for 2025–2026 were swept, 31 real misses were added
(`supplement:universe-certification-current` — including two missed laws in
the transparency and budget-cap threads, HB138 and SB105) and 86 candidates
were excluded with per-bill categories (`certification-current.json` / `.md`).

## Collection notes

- Discovery: 45 search terms over SQL bill titles (current biennium) and the
  OpenStates bulk titles+abstracts (2020–2024); every hit kept and
  hand-curated. Substring traps (bare "tax", "assessment", "homestead",
  "rooms and meals" ordering) are documented in the issue config.
- Dispositions: SQL dockets for 2025–2026 (including bills whose docket is
  keyed to the other biennium year, e.g. 2025 HB649/SB83); the bulk docket
  mirror for 2020–2024, with biennium continuation rows appended for
  first-year bills (e.g. 2021 SB128's 2022 fate). One manual resolution (2021
  SB128) documents its evidence: same-day docket rows lose intra-day order in
  the mirror.
- The three HB2 bill records (2021, 2023, 2025) are curated as context so the
  trailer's sections (Appendix H) are not double-counted in bill totals.
- HB675's January 2026 death is the only brief vote number that is not a
  roll call: the docket records the failed reconsideration as a division vote
  (170–185), and the brief labels it as such.
- Every reality-map claim was verified programmatically against the evidence
  pack (`fact-check-reality-map.py`; run passes). The brief was scanned
  programmatically (`scan-lege-brief.py`): no advice language, all 99 cited
  bills exist in the pack, every vote pair matches the official record (two
  documented docket-tally exceptions: HB675's 170–185 division vote and
  HB765's 18–0 recorded committee vote, both labeled as such).
- The strict completeness checker verdict was PASS_WITH_WARNINGS (three
  search terms with no NH hits: `revaluation`, `tax deferral`, `excise` —
  kept for future sessions and documented).

## Review status

- Automated review: `scan-lege-brief.py` and `fact-check-reality-map.py`
  both pass; LibreOffice page checks recorded in `PACKAGE.md`.
- Human review: pending — this packet is the draft for that review.
