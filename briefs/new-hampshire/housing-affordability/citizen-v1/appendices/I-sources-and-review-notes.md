# Appendix I — Sources and review notes

Reviewer-facing material: where every front-brief claim comes from, how the
record was collected, and what to re-check. Nothing in this appendix appears
in the citizen-facing front brief.

## Source keys

| Key | Source |
|---|---|
| S1 | New Hampshire General Court public SQL database (`NHLegislatureDB`): `rollcallsummary` / `rollcallhistory` (all years), `legislation`, `legislationtext`, `sponsors`, `docket` (2025–2026 biennium) |
| S2 | gc.nh.gov official bill texts: `/legislation/{year}/{bill}.html` (latest/chaptered versions, 2020–2021; HB2 2021 Chapter 91) |
| S3 | Legislative Budget Assistant chapter-law PDF for HB2 2023 (Laws of 2023, Chapter 79) |
| S4 | Internet Archive snapshots of openstates.org and legiscan.com bill pages — mirrors of the official GenCourt docket, used only for 2022–2024 action histories; each record stores its snapshot URL |
| S5 | Cited public reporting and agency documents for six bills whose final stage the snapshots could not fully resolve (NH Office of Planning and Development legislation matrix, NH Bulletin, InDepthNH, NHMA legislative bulletin, NHHA newsletter, Housing Action NH, TrackBill/MyRepTracker docket mirrors); per-bill citations in `working/.../dispositions.json` and `older-bill-status.json` |
| S6 | Derived working files in this repository: `evidence-pack.json`, `curation-map.json`, `dispositions.json`, `hb2-sections.json` (all fact-checked layers over S1–S5) |

## Claim-to-source map (front brief)

| Front-brief claim | Source |
|---|---|
| 135 housing bills; 30 became law (one via HB2); 101 bills and 22 laws in 2025–2026; 67 kills and 11 interim studies in the biennium; 51 kills in 2026 | S6 counts over S1 (discovery, dockets) — `evidence-pack.json` inventory |
| HB2 carried 22 core housing sections; dollar figures ($25M AHF 2021 and 2023, $5M Housing Champion, $10M shelter 2023, $5M/yr opioid shelter 2025); Board of Manufactured Housing repeal; Housing Appeals Board restructure | S1 (HB2 2025 text), S2 (HB2 2021), S3 (HB2 2023) — curated in `hb2-sections.json`; Appendix H |
| HB2 2025 passed the House 184–183 | S1 roll calls (`hb2/2025/hb2-votes.json`) |
| HB631 (2025): kill motion rejected 128–211; became law (Chapter 201) | S1 (roll call + docket) |
| HB1010 (2026) Chapter 319; HB1588 (2026) conference report 185–171, Chapter 329 | S1 |
| HB577 (2025) detached ADUs, Chapter 197; analysis text quoted from chaptered final | S1 (`legislationtext`) |
| HB1079 (2026) Chapter 210; HB1012, HB1662 died; HB604 interim study | S1 |
| SB126 (2021) Senate 24–0, Chapter 152; HB1598 (2026) Chapter 308 | S1 (votes), S2 (chapter header) |
| HB92 (2025) Chapter 108; HB1359 (2024) Chapter 130; board-training deaths 2020/2021/2022/2026 | S1, S4 (2022 SB400, 2024 HB1359 histories) |
| SB166 (2025) Chapter 244; HB1681 (2026) 242–102, Chapter 330 | S1 |
| HB1291 (2024) House 220–143 (150 D + 67 R yes), Senate amendment failed 8–16, indefinitely postponed | S1 (roll calls + ballots with party), S5 (NH Bulletin / Housing Action NH for the Senate voice vote) |
| SB538 (2024) killed 188–173; SB84 (2025) Senate 13–10, interim study; HB1008/HB1713 died | S1 |
| SB152 (2021) Senate 24–0, House ITL; $25M via 2021 budget | S1 (roll call), S5 (NHBR, Citizens Count), S2 (HB2 91:376) |
| HB530/SB81 deadline deaths; SB419 interim study 16–8; HB1786 tabled (remove failed 100–235); HB1707 died | S1 (dockets + roll calls) |
| SB415 (2022) tabled 13–11; SB113 (2025) 23–0 then deadline death | S1 (roll calls + docket), S5 (InDepthNH, TrackBill) |
| HB1196 (2026) House 185–166 (party split), Senate killed the repeal | S1 (roll call + ballots + docket) |
| Voucher bills: HB1291 (2022) tabled 179–148; HB469 (2023); HB628 (2025) | S1 (roll calls), S4 (2022/2023 archived dockets) |
| HB95 (2023) 301–63; HB567, HB558, HB1371, HB1375, HB1612, HB1553, HB1143 died; HB309 (2025) Chapter 176 | S1, S4 |
| HB1336 (2026) passed both chambers, vetoed, override pending | S1 (docket: veto recorded, no override action as of collection) |
| HB112 (2023) 175–199; HB444 (2025) died | S1 |
| 42 cross-party bills; sponsor counts (Alexander 7, Read 6, Murphy 5) | S1 sponsors + S2 sponsor lines — `evidence-pack.json` people signals |
| SB86 (2021) House 208–167 with 196 R / 164 D pattern | S1 ballots joined to the legislators roster |
| Three vetoes (HB1247 2020 override failed 187–148; SB318 2024; HB1336 2026) | S1 (roll calls), S2 (HB1247 final version), S4 (SB318 history) |
| Rule 3-23 deadline deaths of five 2025 Senate bills | S1 dockets (`Inexpedient to Legislate, Senate Rule 3-23, 10/31/2025`) |

## Collection notes

- Discovery: 40 search terms over SQL bill titles (current biennium) and roll-call
  titles (all years); every hit kept and hand-curated. `ADUs` was added after a
  known 2025 ADU law (HB577) was found missing — documented in the issue config.
- 2020–2024 completeness is limited to floor-voted bills plus HB2; no
  OpenStates/LegiScan key was available in this environment, so committee- and
  voice-vote-killed bills from those years are absent. The strict completeness
  checker passed with this gap documented in
  `sources/new-hampshire/housing-affordability/data-gaps.json`. Re-running the
  `collect-nh` GitHub Actions workflow (which holds an `OPENSTATES_API_KEY`
  secret) would backfill them.
- Every reality-map claim was verified programmatically against the evidence
  pack (`fact-check-reality-map.py`; run passes).
- The completeness fact-checker verdict was PASS_WITH_WARNINGS (empty search
  terms with no NH hits, plus one resolution title containing the word
  "should" — HR30, quoted nowhere in the brief).

## Review status

- Automated review: see `review-report.md` / `review-report.json`.
- Human review: pending — this packet is the citizen-v1 draft for that review.
