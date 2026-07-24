# Evidence Pack — Housing Affordability in Nevada

- **Issue:** `nevada-01-housing-affordability` · built 2026-07-24 by evidence-curator v2.2
- **Machine pack:** `evidence-pack.json` (assembled by `collectors/build_evidence_pack.py` from `curation-map.json` + processed Pass 2 data)
- **Sessions:** 2019 (80th), 2021 (81st), 2023 (82nd), 2025 (83rd)

## How this set was built

Discovery combined NELIS keyword search (housing, affordable/attainable
housing, rent, landlord, tenant, eviction, accessory dwelling, tiny house,
manufactured home, impact fee, inclusionary, corporate investor, down
payment, starter home, and related terms) with a full harvest of the LCB
official Subject Index of Bills under the housing heading family
(AFFORDABLE/ATTAINABLE HOUSING, HOUSING and its bodies, LANDLORD AND TENANT,
EVICTION, LEASES, MANUFACTURED/MOBILE/TINY HOMES, ZONING, LAND USE PLANNING,
SUBDIVISION OF LAND, IMPACT FEES, RESIDENTIAL CONSTRUCTION TAX, REAL
PROPERTY TRANSFER TAXES, REAL ESTATE INVESTMENT TRUSTS, BUILDING
CODES/PERMITS, HOMELESS PERSONS).

- **431 bills collected**, tiered by relevance after reading every digest:
  - **93 core** (housing affordability, renting, or housing programs are the point of the bill)
  - **56 adjacent** (a real but partial housing angle)
  - **282 context** (found by broad terms or omnibus indexing; kept for audit,
    excluded from headline counts)
- **Policy set (core + adjacent): 149 bills** — the basis for all headline
  numbers.
- All six 2020–2025 special sessions were checked by hand
  (`sources/nevada/housing-affordability/verification/special-sessions.json`).
  Three housing-relevant special-session bills exist: 32nd (2020) SB1
  (COVID eviction stays, enacted), 36th (2025) SB6 (Windsor Park act revision,
  enacted), and 36th (2025) SB10 (corporate-investor purchase cap — passed the
  Senate 18–0, then recorded **Lost** in the Assembly at 27–10 because the
  bill's fee provisions required a two-thirds majority, 28 of 42).

## Inventory (policy set, 149 bills)

| Disposition | Count |
|---|---|
| Enacted | 63 |
| Failed | 70 |
| Vetoed | 16 |

By session: 2019 — 35 bills (22 enacted); 2021 — 27 (14, 1 vetoed); 2023 —
39 (12, **9 vetoed**); 2025 — 48 (15, 6 vetoed). 2025 had the most housing
bills and the worst pass rate in the record (15 of 48); 2023 is the veto
wave (9 of 39 bills in the set vetoed).

## Themes (policy bills)

| Theme | Bills | Enacted | Where the rest usually stopped |
|---|---|---|---|
| Evictions, discrimination, renter protections | 37 | 16 | first committee (9), **vetoed (8)** |
| Money/tax breaks/financing for affordable housing | 24 | 11 | first committee (7), origin floor (3) |
| Rent levels, fees, deposits | 20 | 5 | first committee (8), **vetoed (4)** |
| Zoning, density, ADUs | 19 | 6 | first committee (6), second house (5) |
| Homelessness → housing | 16 | 10 | first committee (5) |
| Manufactured/mobile/tiny homes | 10 | 6 | scattered |
| Corporate and investor buying of homes | 7 | 2 | second house (2), vetoed (1), first committee (2) |
| Developer fees and obligations | 6 | 1 | first committee (3), after both chambers (1) |
| Buying and keeping a home | 5 | 2 | scattered |
| Housing data, studies, state bodies | 5 | 4 | second house (1) |

## Constituent-proposal crosswalk (headline)

| Phase 2 proposal | Matched bills | Reading |
|---|---|---|
| Corporate ownership limits | 7 | Passed twice, stopped twice at the finish line: 2023 SB395 vetoed; 2025-special SB10 lost needing two-thirds; 2025 SB391 died in the second house. A study of taxing corporate landlords (2025 AB457) is law. |
| Down payment / first-time buyer | 3 | 2025 SB193 rate buy-down pilot died in the Assembly; matched-savings accounts (2021 SB188) are law. |
| Developers fund infrastructure | 5 | 2025 SB99 linkage fee passed both houses, delivered to the governor, never signed. In-lieu funds died in first committee twice (2021). |
| Inclusionary mandates | 0 | Never filed as a percentage mandate. The fight has been over local *authority* (2023 SB371 vetoed; 2025 SB289 died in committee). |
| Rent guardrails | 6 | General caps never reached a floor vote; the one that passed (2023 SB275, manufactured home parks) was vetoed. Rent-control *bans* also died (2025 SB123, AB443). |
| Rental fee limits/transparency | 9 | The most-passed, most-vetoed idea in the set: 4 vetoes (2023 AB218, AB298, SB78; 2025 AB280). Precedent in law: 2019 SB151 5% late-fee cap, 2021 AB308, 2023 SB381 (21–0/42–0), 2025 AB121 all-in pricing. |
| ADUs / density / infill | 4 | 2025 enacted the core asks: AB396 (ADUs) and AB241 (by-right multifamily on commercial land). |
| Starter/tiny/modular homes | 3 | Tiny homes zoning is law (2021 SB150); the starter-home incentive design (2025 SB430) died in its first committee. |
| Workforce buyer subsidies | 1 | Never filed as loan-forgiveness-for-housing; teacher housing (2023 SB47) died on the Senate floor; the rural health loan-repayment model exists in statute. |
| Builders-citizens-legislators working group | 7 | A statutory Advisory Committee on Housing exists (2019 AB476, 38–2 and 20–0, cross-party). |

## People signals

- 114 of 149 policy bills came from named lawmakers; 35 from committees.
- Frequent primaries: Sen. Julia Ratti (D) 12; Sen. Dina Neal (D) 10;
  Sen. Dallas Harris (D) 9; Sen. Pat Spearman (D) 8; Sen. Fabian Doñate (D) 7.
- 16 bills had sponsors from both major parties; 13 of the 16 became law.
- Party labels: official NELIS rosters; 97.8% of ballot rows matched
  (unmatched rows are minutes-parsing name fragments, kept unlabeled).

## Data limits

See `evidence-pack.json → data_limits` and Appendix F. Committee Yeas are
partly inferred (membership minus recorded Nay/Absent); the record shows
where each bill stopped, never why; OpenStates was unavailable (no API key),
so all history, votes, and parties come from NELIS and official rosters.
