# Appendix I — Sources and review notes

This appendix holds the reviewer-facing material that does not belong in the
front brief: the claim-to-source mapping, data-collection notes, and review
status.

## How this record was assembled

Bills were discovered two ways for the 2019, 2021, 2023, and 2025 sessions:
NELIS full-text search (housing, affordable housing, attainable housing,
rent, landlord, tenant, eviction, accessory dwelling, tiny house,
manufactured home, impact fee, inclusionary, corporate investor,
institutional investor, down payment, starter home, student loan, and
related terms) and a full harvest of the Legislative Counsel Bureau's
official Subject Index of Bills (the HOUSING heading family — AFFORDABLE
HOUSING, ATTAINABLE HOUSING, HOUSING AUTHORITIES, HOMELESSNESS TO HOUSING —
plus LANDLORD AND TENANT, EVICTION, LEASES, DWELLINGS, APARTMENT HOUSES,
MANUFACTURED/MOBILE/TINY HOMES, HOMELESS PERSONS, ZONING, LAND USE PLANNING,
PLANNING COMMISSIONS, REGIONAL PLANNING, PLANNED UNIT DEVELOPMENTS,
SUBDIVISION OF LAND, IMPACT FEES FOR NEW DEVELOPMENT, RESIDENTIAL
CONSTRUCTION TAX, REAL PROPERTY TRANSFER TAXES, REAL ESTATE INVESTMENT
TRUSTS, and BUILDING CODES/PERMITS, with entry-level keywords such as
accessory dwelling, down payment, inclusionary, rent control, corporate
investor, and starter home).

All six 2020–2025 special sessions were checked by hand; unlike the water
issue, housing bills exist there. Three matter and are documented with full
history and votes in
`sources/nevada/housing-affordability/verification/special-sessions.json`:
the 32nd (2020) Special Session SB1 (court stays of evictions, enacted),
the 36th (2025) Special Session SB6 (Windsor Park act revision, enacted),
and the 36th (2025) Special Session SB10 (corporate-investor purchase cap
and registry), which passed the Senate 18–0 and was recorded **Lost** in the
Assembly at Yeas 27, Nays 10 — the bill's face is printed "REQUIRES
TWO-THIRDS MAJORITY VOTE (§ 2)," and 27 is one vote short of two-thirds of
42. These special-session facts come from the verification file, not the
regular pipeline, and the front brief marks them by naming the special
session.

The search yielded 431 bills, hand-curated (every NELIS digest read) into
149 policy bills — the basis for all headline numbers — and 282 context
bills kept for audit. This is broad, double-source coverage but not a
provably complete universe; the record shows where each bill stopped, never
why (no veto messages or floor debate). Committee Yea votes are partly
inferred (committee membership minus recorded Nay/Absent) because Nevada
minutes usually list only No and Absent votes; those rows are marked in the
source data. Party labels come from official NELIS legislator rosters
(97.8% of roll-call ballot rows matched; the unmatched rows are
minutes-parsing name fragments left unlabeled, and sponsor party coverage is
99.6%). One generated provenance string inside `evidence-pack.json`
(`discovery_note`) was corrected after the build to describe the housing
headings actually harvested; all counts are untouched pipeline output.
Every factual claim in the reality map and front brief was checked
programmatically against the evidence pack before writing
(`working/nevada/housing-affordability/fact-check-reality-map.py`, all
claims verified).

## Claim-to-source mapping (front brief)

Bill keys are `session:identifier` (80=2019, 81=2021, 82=2023, 83=2025;
special-session bills named in text). Machine sources live in
`working/nevada/housing-affordability/evidence-pack.json` and
`reality-map.json`.

| Front-brief claim | Evidence |
|---|---|
| 149 policy bills; 63 enacted; 16 vetoes (9 in 2023, 6 in 2025); 43 first-committee deaths; 2025 pass rate 15 of 48 | `evidence-pack.json → inventory`; per-committee counts in `reality-map.json → people_and_process_signals` |
| 2 of 10 proposals never filed as a bill | `evidence-pack.json → constituent_proposal_crosswalk` (inclusionary-requirements: 0 matches); statuses in `reality-map.json → proposal_reality_cards` |
| Corporate cap: vetoed, died in second house, lost by one vote | `82:SB395` (14–6, 28–14, vetoed), `83:SB391` (13–8, died in Assembly), special-36th SB10 (18–0; Lost 27–10; two-thirds printed on bill face — verification file); study `83:AB457` (enacted 27–15, 14–7) |
| Rent guardrails | `82:AB362` (first committee), `82:SB426` (Senate floor), `82:SB275` (13–8, 28–14, vetoed), `83:SB151` (first committee); preemption deaths `83:SB123`, `83:AB443` |
| Developer contributions | `83:SB99` (14–6, 27–15, delivered to Governor May 27 2025, history ends), `81:AB331`/`81:AB334` (first committee), `80:SB471` (first committee), `80:SB103` (enacted 21–0, 36–4) |
| Inclusionary never filed; local-power fight | crosswalk `inclusionary-requirements` (0 matches); `82:SB371` (12–9, 26–14, vetoed), `83:SB289` (first committee) |
| Down payment / first-time buyer | `83:SB193` (14–5, died in Assembly), `81:SB188` (36–5, 21–0, enacted), `80:SB194` (Senate floor); Housing Division bond authority described in SB193's digest |
| Workforce subsidies never filed; template exists | crosswalk `workforce-buyer-subsidies`; `82:SB47` (Senate floor), `83:AB269` + `83:SB266` (enacted health loan-repayment expansions) |
| Starter/tiny/modular | `83:SB430` (first committee), `81:SB150` (20–1, 33–8, enacted), `83:AB38` (40–2, 17–3, enacted) |
| Fee precedents and vetoes | enacted `80:SB151`, `81:AB308`, `82:SB381` (21–0, 42–0), `83:AB121` (27–15, 16–5); vetoed `82:AB298` (36–6, 12–8), `83:AB280`, `82:AB218`, `82:SB78`; registries `81:AB332`, `83:SB436` (first committee) |
| ADU / density | `83:AB396` (27–15, 14–7, enacted), `83:AB241` (28–14, 15–6, enacted), `81:SB150`; tax-side deaths `82:AB416`, `83:AB131` (42–0 Assembly, died in Senate) |
| Working group precedent | `80:AB476` (38–2, 20–0, cross-party, enacted); `83:AB37` (42–0 Assembly, died in Senate at deadline) |
| Political terrain (114 person-sponsored; Ratti 12; Neal 10; 16 cross-party, 13 enacted; committee routing 11 Commerce and Labor / 14 Government Affairs) | `evidence-pack.json → people_signals`; chokepoint counts in `reality-map.json → people_and_process_signals` |
| New 2025 law | `83:AB540` (42–0, 15–6), `83:AB396`, `83:AB241`, `83:AB121`, `83:AB211` (41–0), `83:AB475` (42–0, 19–1), `83:AB457`; special-session SB6 and SB10 from the verification file |
| Citizen proposals and quoted phrases | "NV1 - RAG - Phase 2 Constituent Input" (NV1 - Housing sheet), mirrored in `config/issues/nevada-housing-affordability.yaml → constituent_proposals` |

## Statute and agency references

Landlord-tenant law: NRS 118A
([leg.state.nv.us/NRS/NRS-118A.html](https://www.leg.state.nv.us/NRS/NRS-118A.html));
manufactured home parks: NRS 118B; planning and zoning (housing elements,
impact fees): NRS 278 and 278B; Housing Division programs and the Accounts
for Low-Income/Affordable Housing: NRS 319; Nevada Housing Division:
[housing.nv.gov](https://housing.nv.gov/). Special-session bill text for
SB10: leg.state.nv.us/Session/36th2025Special/Bills/SB/SB10.pdf.

## Review status

See `review-report.md` / `review-report.json` in the packet folder for the
automated checklist (no-advice scan, banned-section scan, fact spot-checks,
page-count renders) and the items flagged for human judgment.
