# Political-Reality Map — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · reality-mapper v2.2 · 2026-07-17
- **Input:** `evidence-pack.json` — 108 policy bills (of 189 collected), sessions 2019–2025
- **For:** citizen working groups sharpening the three Phase 2 water proposals
- **Coverage:** keyword search + full LCB subject-index harvest (incl. Tahoe, rivers, flood, sewage headings after a recall audit); all six 2020–2025 special sessions checked — no water or data-center bills there

## The headline

The ten most common citizen statements on water (Phase 2 RAG dataset) sort
into three groups when checked against the 2019–2025 record:

| Group | Citizen statements |
|---|---|
| **Never filed as a bill** | Data-center water/cooling rules · statewide metering · water-waste fines · reimbursement-style tax incentives · bring-your-own-water |
| **Tried, but stalled** | Statewide expert water body (2019 SB499, 2025 SB143) · records/audit funding (2025 AB485) · statewide-science standards (2019 AB51, 2023 AB387) · conditions on tax breaks (0-for-5) |
| **Partly done / precedent exists** | Grass ban (2021 AB356) and land-split water dedication (2019 SB250) for growth limits · well meters + loss audits (2019 AB95, 2023 SB113, 2023 AB191) · water agency database money (2025 AB577) |

## Statement reality cards (ten)

Full structured cards live in `reality-map.json → proposal_reality_cards`.
Summary:

1. **Statewide expert water body** — *tried, stalled.* 2019 SB499 died in first committee; 2025 SB143 passed the Senate 21–0, died in the Assembly. No Economic-Forum-style water body exists in statute.
2. **Data-center guardrails** — *never filed.* Helping large users went 4-for-4 (2019 SB547, 2019 AB400, 2021 AB66, 2023 AB261); restraining their tax deals went 0-for-5; the one cooling bill (2025 AB385) pushed the other way and died. Cooling rules are local today — the county-by-county race citizens described is real.
3. **Audit / digitize water records** — *tried, stalled; partly done.* 2025 AB485 (basin budgets + monitoring + digitization + adjudication staff) died in first committee — matching citizens' "keeps getting shut down in committee." Enacted nearby: 2019 AB95 basin studies, 2023 SB113 critical-management areas, 2025 AB577 database money, 2025 SB36 buy-and-retire.
4. **Metering** — *never filed statewide.* Enacted edges: domestic-well meters in stressed basins (2019 AB95 → 2023 SB113), supplier water-loss audits (2023 AB191), leak plans (2019 AB163). Flat-rate billing is a utility/city matter today.
5. **Waste enforcement / fines** — *never filed.* Nearest law: 2019 AB537 raised environmental civil penalties (pollution, public water systems) — not lawn-watering waste. Enforcement funding, citizens' own complaint, has never been taken up.
6. **Incentives for heavy users** — *thin record.* 2021 SB283 lets improvement districts finance water-efficiency projects; 2023 AB261 added water efficiency to the state economic development plan. No dedicated incentive program.
7. **Conditional (reimbursement) tax incentives** — *direction failed 5 times.* 2025 AB77, 2023 SB394 (Senate 14–7, died in Assembly Revenue), 2023 SB429 (vetoed), 2021 AB449, 2025 SB364. The reimbursement-at-the-end design itself has never been filed.
8. **Growth restrictions** — *precedent exists, mixed.* 2021 AB356 grass ban passed 21–0/42–0 (southern Nevada only); 2019 SB250 land-split dedication passed 39–0; but 2023 SB169 (master-plan conservation) was vetoed and 2025 SB143 died. Watering days and moratoriums remain local rules.
9. **Fairness / no carve-outs** — *tried, stalled.* 2019 AB51 (manage all water together) died in first committee; 2023 AB387 (best available science) passed the Assembly 26–14, died in the Senate. The enacted record is regional by design.
10. **Bring your own water** — *never filed statewide.* 2019 SB250 is the nearest statute; northern Nevada already requires dedication + an 11% drought reserve, but by water-authority rule, not state law.

## Theme scorecards (baskets)

| Theme | Bills | Enacted | Basket | Certainty |
|---|---|---|---|---|
| Money for water projects | 17 | 14 | Often moved before | high |
| Water permits / State Engineer rules | 16 | 9 | Often moved before | high |
| Water utilities and districts | 11 | 8 | Often moved before | medium |
| Clean water and pollution | 13 | 10 | Often moved before | medium |
| Using less water | 6 | 4 | Often moved before | medium |
| Colorado River, planning, new supply | 13 | 5 | Mixed | medium |
| Groundwater, wells, over-pumped basins | 12 | 4 | Mixed (strong unfinished streak) | high |
| Buying, banking, retiring water rights | 3 | 1 | Unfinished → recently done (83:SB36) | low |
| Courts and oversight of water decisions | 6 | 0 | Rarely moved before | high |
| Data centers, big users, tax deals | 11 | 4 | Rarely moved (in the restraint direction) | high |

Inference lines and per-theme stop stages are in `reality-map.json`.

## People and process signals (facts only)

- 58 of 108 policy bills were committee-sponsored; 50 came from named lawmakers.
- Sen. Pete Goicoechea (R) is the most frequent person sponsor (14 bills; groundwater, districts, rights retirement). Asm. Howard Watts (D), Sen. Chris Brooks (D), and Asm. Sarah Peters (D) each carried 5.
- Cross-party sponsor teams: 5 bills; 4 became law.
- Of 27 first-committee deaths, **15 were in a Natural Resources committee**; Assembly Revenue stopped both abatement-restraint bills.
- **The governor is a live stop:** 3 vetoes in 2023 (82:AB97, 82:SB169, 82:SB429).

## High-support non-enactments (top of the list)

82:SB180 (41–0 + unanimous, groundwater boards), 83:SB143 (21–0, water-saving
review), 82:SJR3 (42–0 resolution), 82:AB97 (42–0 then vetoed), 82:SB394
(Senate 14–7, abatement cap), 82:AB387 (26–14, best available science),
80:AB30 (31–9, monitoring plans), 83:SB31 (15–6), 83:SB324 (16–4), 82:SB169
(18–3 then vetoed). Full list in JSON. These are possible timing/process
deaths — not proof of popularity.

## Recently done (2025) — don't assume a blank slate

83:SB36 (buy-and-retire water rights account), 83:SB6 (cloud seeding again),
83:SB442 (shut-off protections), 83:SB276 (pollution-permit notice,
cross-party), 83:AB449 + 83:SB326 (small-utility rates), 83:AB104 (grant
rules).

## Deliberation prompts

1. No desalination or pipeline bill has ever been filed. Unrealistic — or just never asked? What would a funded study cost?
2. Why did cloud seeding move twice, unanimously, when no other new-supply idea was tried?
3. For data centers: is the real lever the tax deal, the water law, or the local permit?
4. Was 82:SB394's Assembly death a "no" or a calendar death?
5. What has to change for the groundwater-boards idea (82:SB180 → 83:AB363) to finish on the third try?
6. Oversight bills are 0-for-6 but gaining floor wins. Growing support or a permanent second-house wall?
7. Three 2023 deaths were vetoes. How should groups weigh the governor's desk?
8. Who sits on the Natural Resources committees now — the place where 15 of 27 early deaths happened?

## Data limits carried forward

Keyword + subject-index discovery (broad, not provably complete) · the record
shows where, never why · committee Yeas partly inferred (marked) · party from
official rosters (100% matched) · the 2026 interim study is context, not
bill record.

> Reality Mapper finished. Run **Citizen Brief Writer** (and **Appendix Builder** in parallel).
