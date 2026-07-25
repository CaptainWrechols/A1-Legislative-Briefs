# Political-Reality Map — Housing Affordability in Nevada

- **Issue:** `nevada-01-housing-affordability` · reality-mapper v2.2 · 2026-07-24
- **Input:** `evidence-pack.json` — 149 policy bills (of 431 collected), sessions 2019–2025
- **For:** citizen working groups sharpening the ten Phase 2 housing proposals
- **Coverage:** NELIS keyword search + full LCB subject-index harvest (housing heading family); all six 2020–2025 special sessions checked by hand — three housing-relevant special-session bills found (32nd SB1 eviction stays, enacted; 36th SB6 Windsor Park, enacted; 36th SB10 corporate purchase cap, lost by one vote under the two-thirds rule)
- **Fact-check:** every card claim below verified programmatically against the pack (`fact-check-reality-map.py`, all claims verified 2026-07-24)

## The headline

Housing is the rare issue where citizens' proposals have mostly **already
been written as bills** — and the record's central fact is *where they die*.
Since 2023 the chokepoint has moved from committees to the finish line: nine
housing bills were vetoed in 2023 and six more in 2025, and the
corporate-purchase cap lost in the November 2025 special session by a single
vote under the constitutional two-thirds rule.

| Group | Citizen proposals |
|---|---|
| **Never filed as such** | Inclusionary percentage mandates · loan-forgiveness/homebuying subsidies for professions |
| **Tried, but stalled** | Corporate ownership caps (vetoed 2023; one vote short 2025) · rent guardrails (park version vetoed) · developer linkage fee (died unsigned at the desk 2025) · rate buy-down pilot (died in second house) · starter-home incentives (died in first committee) |
| **Partly done / precedent exists** | Rental-fee caps and transparency (four laws, four vetoes) · ADUs/density (2025 AB396 + AB241 now law) · tiny/factory-built homes (2021 SB150, 2025 AB38) · statutory Advisory Committee on Housing (2019 AB476) |

## Statement reality cards (ten)

Full structured cards live in `reality-map.json → proposal_reality_cards`. Summary:

1. **Corporate ownership limits** — *tried, stopped at the finish line three different ways.* 2023 SB395 (1,000-home annual cap) passed 14–6 and 28–14, vetoed. 2025 SB391 (100-home cap) passed the Senate 13–8, died in the Assembly. 36th (2025) Special Session SB10 passed the Senate 18–0 and recorded **Lost** at 27–10 in the Assembly — its fee provisions required a two-thirds majority (28 of 42). What is law: 2025 AB457's interim study of taxing corporate rental owners.
2. **Down payment assistance** — *tried, stalled late.* 2025 SB193 (state pilot buying down mortgage rates for first-home borrowers) passed the Senate 14–5 and died in the Assembly. Enacted edge: 2021 SB188 matched-savings accounts (failed 2019, passed 2021 36–5/21–0).
3. **Developers fund infrastructure** — *tried, died unsigned.* 2025 SB99 (local linkage fee on developers for affordable housing) passed 14–6 and 27–15, was delivered to the governor May 27, 2025, and the record ends with no signature — not law. In-lieu funds (2021 AB331/AB334) and school impact fees (2019 SB471) died in Government Affairs committees. The enacted bill runs the other way: 2019 SB103 lets localities *reduce* fees for affordable projects.
4. **Inclusionary mandates** — *never filed as such.* The fight is over local authority: 2023 SB371 (confirm local power over affordable-housing ordinances) passed and was vetoed; 2025 SB289 died in committee.
5. **Rent guardrails** — *tried, stalled exactly as citizens predicted.* General caps died in Commerce and Labor (2023 AB362) and on the Senate floor (2023 SB426); the manufactured-home-park cap passed both houses (13–8, 28–14) and was vetoed (2023 SB275); the 2025 retry died in committee. Rent-control *bans* also died twice (2025 SB123, AB443).
6. **Rental fee limits and transparency** — *the most-passed, most-vetoed idea in the set; real precedent in statute.* Law now: 5% late-fee cap (2019 SB151), 3-day grace (2021 AB308), no fees for the landlord's own repair duties (2023 SB381, 21–0/42–0), all-in advertised rent (2025 AB121). Vetoed: 2023 AB218, AB298 (36–6!), SB78; 2025 AB280. Landlord registries died in first committee twice.
7. **ADUs / density / infill** — *recently done, in part.* 2025 AB396 (ADUs must be allowed in big jurisdictions) and 2025 AB241 (by-right multifamily on commercial land) are law; 2021 SB150 (tiny houses) preceded them. The ADU property-tax incentive died twice (2023 AB416; 2025 AB131 — Assembly 42–0, died in Senate).
8. **Starter/tiny/modular incentives** — *tried once, died in first committee.* 2025 SB430 (tax credits for at-cost starter homes with corporate-investor resale protections) died in Senate Revenue without a vote. Legal-status precedent exists (SB150 tiny homes; AB38 factory-built code, 40–2/17–3).
9. **Workforce buyer subsidies** — *never filed as such.* The rural-medicine loan-repayment template exists in statute and was expanded twice in 2025 (AB269, SB266) — never extended to housing. Nearest attempts: 2023 SB47 (school-district employee housing) died on the Senate floor; 2025 SB193 targeted income, not profession.
10. **Builders–citizens–legislators working group** — *precedent exists.* 2019 AB476 (cross-party) recreated the statutory Advisory Committee on Housing (38–2, 20–0) with an annual needs report and one bill draft per session. Study/body bills are the most reliably enacted kind in the record (4 of 5). Open question: whether the Committee's composition matches the three-legged table citizens described.

## Theme scorecards (baskets)

| Theme | Bills | Enacted | Basket | Certainty |
|---|---|---|---|---|
| Housing data, studies, state bodies | 5 | 4 | Often moved before | low |
| Homelessness → housing | 16 | 10 | Often moved before | medium |
| Manufactured/mobile/tiny homes | 10 | 6 | Often moved before | medium |
| Money/tax breaks/financing | 24 | 11 | Often moved before | medium |
| Evictions, discrimination, renter protections | 37 | 16 | Mixed (veto wall since 2023) | high |
| Zoning, density, ADUs | 19 | 6 | Mixed → moved in 2025 | medium |
| Buying and keeping a home | 5 | 2 | Mixed | low |
| Rent levels, fees, deposits | 20 | 5 | Got support but didn't finish | high |
| Corporate/investor buying of homes | 7 | 2 | Got support but didn't finish | high |
| Developer fees and obligations | 6 | 1 | Got support but didn't finish (recent), rarely moved (early) | medium |

Inference lines and per-theme stop stages are in `reality-map.json`.

## People and process signals (facts only)

- 114 of 149 policy bills came from named lawmakers; 35 from committees.
- Sen. Julia Ratti (D) is the most frequent primary sponsor (12 bills — the 2019 baseline: eviction rewrite, fee caps, Housing Crisis Response System). Sen. Dina Neal (D) carries the corporate-cap and finance line (10). Sens. Dallas Harris (D, 9), Pat Spearman (D, 8), Fabian Doñate (D, 7) follow.
- Cross-party sponsor teams: 16 bills; **13 became law** — rare and unusually successful.
- Of 43 first-committee deaths: 11 in Assembly Commerce and Labor (rent/landlord-tenant), 14 in the Government Affairs committees (local powers, developer fees, registries), 5 in tax committees.
- **The governor's desk is the live stop:** 16 vetoes (1 in 2021, 9 in 2023, 6 in 2025), concentrated on renter-cost, eviction-procedure, discrimination, and corporate-cap bills. 2025 AB121 (all-in rent pricing) is the exception that was signed. 2025 SB99 was delivered to the desk and the record simply ends.

## High-support non-enactments (top of the list)

83:AB131 (42–0 Assembly, ADU tax break), 83:AB37 (42–0, Housing Liaison),
82:AB298 (36–6 + 12–8, vetoed), special-36th SB10 (18–0 Senate; 27–10
Assembly, Lost under the two-thirds rule), 82:SB395 (vetoed), 83:SB99
(delivered, never signed), 83:SB193 (14–5 Senate), 83:SB393 (both houses,
died; enacted three months later as special-session SB6). Full list in JSON.
These are possible timing/process deaths — not proof of popularity.

## Recently done (2025) — don't assume a blank slate

83:AB540 ($133M Attainable Housing Account, 42–0/15–6), 83:AB396 (ADU
mandate), 83:AB241 (by-right multifamily), 83:AB121 (all-in rent pricing),
83:AB211 (forced repairs at neglected apartment properties, 41–0), 83:AB475
(eviction-diversion money, 42–0/19–1), 83:AB457 (corporate-landlord tax
study, reports for 2027), and — in the November special session — SB6
(Windsor Park) and the one-vote loss of SB10.

## Deliberation prompts

1. The corporate cap failed three different ways — veto, second house, one vote short of two-thirds. Which obstacle is the one worth solving?
2. Fee-transparency bills passed five times; four were vetoed and the fifth became law. What was different about 2025 AB121?
3. Rent guardrails died in committee as citizens predicted — but the seniors-focused park version reached the desk. Is narrower scope the tested path?
4. The 2025 session enacted the ADU and by-right density mandates participants thought nobody had touched. Which proposals still need a bill at all?
5. SB99 passed both houses and was delivered to the governor; the record ends there. What would a group need to learn before a retry?
6. Study and advisory-body bills almost always pass. Is a working group a cheap early win, or does the Advisory Committee on Housing already occupy the space?
7. Only 16 of 149 policy bills had cross-party sponsors — and 13 passed. Which of the ten proposals could plausibly attract one?
8. The veto pattern hits renter-cost bills hardest; money, studies, and supply mandates historically escape it. Which proposals are exposed?

## Data limits carried forward

The set is broad but not a proven complete universe; the record shows where
bills stopped, never why (no veto messages or floor debate in the dataset);
committee Yeas are partly inferred and marked; party labels are 97.8%
matched from official rosters; special-session facts come from a manual
verification file, with SB10's two-thirds requirement printed on the bill face.
