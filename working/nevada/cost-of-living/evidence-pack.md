# Evidence Pack — The Rising Cost of Living in Nevada: Health Care

- **Issue:** `nevada-02-cost-of-living` · built 2026-07-26 by evidence-curator v2.2
- **Machine pack:** `evidence-pack.json` (assembled by `collectors/build_evidence_pack.py` from `curation-map.json` + processed Pass 2 data)
- **Sessions:** 2019 (80th), 2021 (81st), 2023 (82nd), 2025 (83rd)

## How this set was built

Discovery combined NELIS keyword search (health care, health insurance,
prior authorization, pharmacy benefit, physician, nurse, licensure compact,
medical education, residency, loan repayment, Medicaid, reimbursement,
urgent care, telehealth, medical debt, balance billing, and related terms)
with a full harvest of the LCB official Subject Index of Bills under the
healthcare heading family (INSURANCE and INSURANCE COMPANIES/ADMINISTRATORS,
HEALTH CARE PROVIDERS, HEALTH CARE — RESTRAINING COSTS OF, HEALTH
MAINTENANCE ORGANIZATIONS, MANAGED CARE ORGANIZATIONS, NONPROFIT
HOSPITAL/MEDICAL/DENTAL SERVICE CORPORATIONS, PUBLIC OPTION HEALTH BENEFIT
PLAN, SILVER STATE HEALTH INSURANCE EXCHANGE, PATIENT PROTECTION COMMISSION,
PATIENTS, PHARMACY BENEFIT MANAGERS, PHARMACISTS AND PHARMACY,
PRESCRIPTIONS, MEDICAID, MEDICARE, MEDICAL BILLS, MEDICAL DEBT, HOSPITALS,
TELEHEALTH, PHYSICIANS, PHYSICIAN ASSISTANTS, OSTEOPATHIC PHYSICIANS, NURSES
AND NURSING, MEDICAL EDUCATION COUNCIL, HEALTH SERVICE CORPS, EMERGENCY
MEDICAL SERVICES), plus entry-level keywords (licensure compact, prior
authorization, graduate medical education, credentialing, urgent care,
reimbursement rate, public option).

- **772 bills collected**, tiered by relevance after reading every digest:
  - **276 core** (healthcare cost, coverage, access, provider supply, or
    regulation of insurers/providers toward patients is the point of the bill)
  - **133 adjacent** (a real but partial healthcare cost/access angle)
  - **363 context** (found by broad terms or omnibus indexing; kept for
    audit, excluded from headline counts)
- **Policy set (core + adjacent): 409 bills** — the basis for all headline
  numbers.
- All six 2020–2025 special sessions were checked by hand
  (`sources/nevada/cost-of-living/verification/special-sessions.json`).
  Two healthcare-relevant special-session bills exist: 31st (2020) AB3
  (the pandemic budget bill that cut FY2020–2021 appropriations, including
  Department of Health and Human Services budgets; enacted 36–6 / 21–0) and
  36th (2025) SB5, which created the Statewide Health Care Access and
  Recruitment Grant Program under the new Nevada Health Authority (enacted
  15–6 / 37–0, Chapter 12) — the same program the regular session's SB434
  passed 18–2 and 42–0 and then lost in the end-of-session amendment
  shuttle.

## Inventory (policy set, 409 bills)

| Disposition | Count |
|---|---|
| Enacted | 221 |
| Failed | 172 |
| Vetoed | 15 |
| Adopted resolution (recorded Unknown by the milestone machine) | 1 |

By session: 2019 — 82 bills (47 enacted); 2021 — 82 (46); 2023 — 112 (61,
**8 vetoed**); 2025 — 133 (67, **7 vetoed**). Volume grew every cycle;
2025 had the most healthcare-cost bills in the record. Every veto in the
set falls in 2023 or 2025.

## Themes (policy bills)

| Theme | Bills | Enacted | Where the rest usually stopped |
|---|---|---|---|
| Provider licensing (compacts, endorsement, scope) | 90 | 49 | first committee (22), origin floor (9) |
| Care delivery (hospitals, clinics, telehealth, rural) | 71 | 45 | first committee (14), origin floor (5) |
| Medicaid and public programs (rates, eligibility) | 60 | 36 | first committee (11), origin floor (9) |
| Coverage mandates | 50 | 25 | first committee (12), origin floor (12) |
| Drug costs, pharmacies, PBMs | 35 | 15 | first committee (10), **vetoed (3)** |
| Provider pipeline (residencies, loan repayment) | 34 | 16 | first committee (8), origin floor (7) |
| Insurer rules (prior auth, denials, networks) | 32 | 18 | first committee (8), **vetoed (3)** |
| Patient billing and medical debt | 22 | 8 | first committee (7), **vetoed (3)** |
| Insurance market (pooling, public option, exchange) | 15 | 9 | first committee (4) |

## Constituent-proposal crosswalk (headline)

| Phase 2 proposal | Matched bills | Reading |
|---|---|---|
| Licensure compacts | 23 | Compacts pass unanimously for PTs, EMS, audiologists/SLPs — but the Nurse Licensure Compact died in its first committee in 2021 (AB142), 2023 (AB108), and 2025 (inside the five-compact omnibus SB34). No physician compact bill exists in the record. |
| Increase provider supply | 18 | The 2025 flagship (SB434, statewide shortage grant program) passed 18–2 and 42–0, died awaiting concurrence, and became law three months later as special-session SB5. |
| Fund GME / residencies | 11 | A state residency grant program is law (2023 SB350, unanimous; revised 2025 SB262). The tax-credit design (Titus) died on the Senate floor twice. |
| Provider loan forgiveness | 8 | Already in statute: the Health Service Corps and the underserved-communities loan-repayment program, funded 2019/2021, expanded 2023 (AB45) and twice in 2025 (AB269, SB266). |
| Prior authorization reform | 16 | 2025 was the test: AB463 (deadlines, Medicaid+private) is law, 42–0/20–0; the AI-denial ban SB128 passed both houses and was vetoed; AB290 cleared its first committee and died after re-referral. |
| PBMs / middlemen | 20 | Transparency laws exist (2019). Full PBM regulation died four ways — including SB316 (2025), which passed 18–2 and 42–0 and died in the amendment shuttle. Enacted instead: a single state-contracted PBM for Medicaid (SB389, 2025). |
| Network accuracy / credentialing | 4 | Thinnest record of the ten: one 2019 law standardizing network-rejection letters (SB234); credentialing speed itself has never been the subject of a bill. |
| Small-business / group pooling | 6 | Precedent exists: association health plan rules (2019 SB481), public drug-purchasing pools (2021 SB396), and the Public Option (2021 SB420, 12–9 / 26–15 — the closest party-line vote in the set). |
| Reimbursement rates | 22 | Narrow Medicaid raises pass unanimously; systemic rate reform dies early (2019 AB116 study, 2023 AB99 review, 2023 SB255 / 2025 SB239 children's rates, 2025 SB366) — mostly in money committees. |
| Right-size ER vs urgent care | 21 | The split-billing model itself has never been filed. What exists: the out-of-network emergency billing law (2019 AB469), ER arbitration (2023 SB497), rural emergency hospitals (2023 AB277), telehealth parity (2021 SB5, 2023 SB119). Hospital price-setting died twice (2023 AB85, 2025 AB349). |

## People signals

- 270 of 409 policy bills came from named lawmakers; 139 from committees.
- Frequent primary sponsors: Sen. Pat Spearman (D, 21), Sen. Joseph Hardy
  (R, 19), Sen. Melanie Scheible (D, 18), Sen. Nicole Cannizzaro (D, 16),
  Sen. Roberta Lange (D, 16), Sen. Jeff Stone (R, 16), Sen. Fabian Doñate
  (D, 16), Sen. James Ohrenschall (D, 12).
- Cross-party sponsor teams: 54 policy bills; 36 became law.
- 43 policy bills earned a >50% floor vote and still did not become law.

## Data limits

- Keyword + subject-index discovery is broad but not a proven complete universe.
- The record shows where each bill stopped — never why (no veto messages or floor debate).
- Committee Yea votes are inferred (membership minus recorded Nay/Absent) and marked.
- Party labels: 97.7% of roll-call ballot rows matched to official NELIS
  rosters (the rest are minutes-parsing name fragments); sponsor party
  coverage is 100%.
- Special-session facts come from the manual verification file, not the
  regular pipeline.
