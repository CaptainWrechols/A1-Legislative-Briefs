# Appendix I — Sources and review notes

This appendix holds the reviewer-facing material that does not belong in the
front brief: the claim-to-source mapping, data-collection notes, and review
status.

## How this record was assembled

Bills were discovered two ways for the 2019, 2021, 2023, and 2025 sessions:
NELIS full-text search (health care, health insurance, health benefit plan,
managed care, public option, licensure compact, licensure by endorsement,
physician, nurse, nursing, physician assistant, medical education, graduate
medical education, residency, health care workforce, loan repayment, student
loan, Health Service Corps, prior authorization, utilization review, step
therapy, pharmacy benefit, pharmacist, prescription drug, network plan,
provider network, network adequacy, credentialing, small employer, group
health, Medicaid, Medicare, reimbursement, urgent care, emergency room,
emergency department, telehealth, telemedicine, hospital, medical debt,
medical bill, balance billing, out-of-network) and a full harvest of the
Legislative Counsel Bureau's official Subject Index of Bills under the
healthcare heading family — INSURANCE (with the agent-licensing, guaranty,
and premium-tax subsets excluded), INSURANCE COMPANIES and ADMINISTRATORS,
HEALTH CARE PROVIDERS, HEALTH CARE — RESTRAINING COSTS OF, HEALTH CARE
ACCESS AND RECRUITMENT GRANT PROGRAM, HEALTH BENEFIT PLANS, HEALTH
MAINTENANCE ORGANIZATIONS, MANAGED CARE, NONPROFIT HOSPITAL/MEDICAL/DENTAL
SERVICE CORPORATIONS, PREPAID LIMITED HEALTH SERVICE ORGANIZATIONS, PUBLIC
OPTION HEALTH BENEFIT PLAN, SILVER STATE HEALTH INSURANCE EXCHANGE, PATIENT
PROTECTION COMMISSION, PATIENTS, PHARMACY BENEFIT MANAGERS, PHARMACISTS AND
PHARMACY, PHARMACEUTICAL SALES REPRESENTATIVES, PRESCRIPTIONS and the
PRESCRIPTION DRUG AFFORDABILITY bodies, REBATES — PRESCRIPTION DRUGS,
MEDICAID, MEDICARE, MEDICAL BILLS, MEDICAL DEBT, HOSPITALS, COUNTY
HOSPITALS, TELEHEALTH, PHYSICIANS, PHYSICIAN ASSISTANTS, PHYSICIAN VISA
WAIVER PROGRAM, OSTEOPATHIC PHYSICIANS, NURSES AND NURSING, NURSING POOLS,
MEDICAL EDUCATION COUNCIL, HEALTH SERVICE CORPS, EMERGENCY MEDICAL
SERVICES, and PSYCHOLOGY INTERJURISDICTIONAL COMPACT — with entry-level
keywords harvested from every heading (licensure compact, nurse licensure,
interjurisdictional compact, licensure by endorsement, prior authorization,
utilization review, step therapy, pharmacy benefit, graduate medical
education, residency program, loan repayment, health service corps, network
adequacy, provider network, credentialing, urgent care, emergency room,
freestanding emergency, telehealth, telemedicine, medical debt, surprise
billing, balance billing, out-of-network, health insurance, health benefit
plan, health coverage, reimbursement rate, public option).

All six 2020–2025 special sessions were checked by hand; two
healthcare-relevant special-session bills exist and are documented with
full history and votes in
`sources/nevada/cost-of-living/verification/special-sessions.json`: the
31st (2020) Special Session AB3 (the pandemic budget bill, which reduced
FY2020–2021 appropriations including Department of Health and Human
Services budgets and authorized DHHS budget transfers; enacted 36–6 and
21–0, Chapter 5) and the 36th (2025) Special Session SB5 (the Statewide
Health Care Access and Recruitment Grant Program under the Nevada Health
Authority; enacted 15–6 and 37–0, Chapter 12). SB5's digest names the same
program the regular session's SB434 created before dying on concurrence —
the linkage the front brief reports. Reviewed and set aside as not
healthcare-cost relevant: 32nd (2020) SB4 and SCR1, 36th (2025) SB3 and
SB7 (notes in the same file).

The search yielded 772 bills, hand-curated (every NELIS digest read) into
409 policy bills — 276 core and 133 adjacent, the basis for all headline
numbers — and 363 context bills kept for audit. This is broad,
double-source coverage but not a provably complete universe; the record
shows where each bill stopped, never why (no veto messages or floor
debate). Committee Yea votes are partly inferred (committee membership
minus recorded Nay/Absent) because Nevada minutes usually list only No and
Absent votes; those rows are marked in the source data. Party labels come
from official NELIS legislator rosters (97.7% of roll-call ballot rows
matched; the unmatched rows are minutes-parsing name fragments left
unlabeled). Sponsor party coverage is 100%: three sponsor names missing
from the session rosters (Assemblyman Michael Sprinkle, Senator Kelvin
Atkinson, Assemblyman C.H. Miller) were resolved from their official NELIS
legislator pages and marked `party_source: nelis_legislator_page` in
`processed/bill-sponsors.json`. Two generated provenance strings inside
`evidence-pack.json` (`discovery_note` and one data-limits line) and the
static intro paragraphs of Appendices A, F, H, and README were corrected
after the build to describe this issue's headings and coverage; all counts
are untouched pipeline output. Every factual claim in the reality map and
front brief was checked programmatically against the evidence pack before
writing (`working/nevada/cost-of-living/fact-check-reality-map.py` — all
claims verified).

## Claim-to-source mapping (front brief)

Bill keys are `session:identifier` (80=2019, 81=2021, 82=2023, 83=2025;
`special-31st` / `special-36th` refer to the special-session verification
file). Dispositions, stages, and vote counts come from
`processed/bills-core.json`, `processed/bill-votes.json`, and
`processed/bill-legislative-progress.json`; plain topics from
`working/nevada/cost-of-living/curation-map.json`.

| Front-brief claim | Source |
|---|---|
| 409 healthcare-cost bills; 221 became law; 15 vetoes (all 2023/2025); 95 first-committee deaths | `evidence-pack.json → inventory` + stage counts; veto years verified per bill |
| 187 of 221 laws carried a unanimous floor vote in at least one chamber | `evidence-pack.json → bills[].best_floor_yes_pct` (=100.0, enacted policy bills) |
| First-committee deaths concentrated: Senate HHS 22, Assembly C&L 21, Senate C&L 19, Assembly HHS 16 | `processed/bill-actions.json` first-referral parse, verified in `fact-check-reality-map.py` |
| ER/urgent-care split model never filed | digest scan of all 772 bills for the design; nearest bills listed |
| AB469 (2019) out-of-network emergency billing, 38–3 and 21–0 | 80:AB469 votes |
| SB497 (2023) arbitration; AB317 (2019) distinct identifiers; AB277 (2023) rural emergency hospitals 41–0/21–0 | 82:SB497, 80:AB317, 82:AB277 |
| AB85 (2023) died on origin floor; AB349 (2025) died in first committee | 82:AB85, 83:AB349 progress |
| Telehealth settled law | 81:SB5, 82:SB119 (enacted) |
| No credentialing-deadline or directory-accuracy bill; SB234 (2019) rejection letters 21–0/39–0; SB494 (2023) Medicaid credentialing | 80:SB234, 82:SB494; absence verified by digest scan |
| SB290 (2019) died in first committee; SB90 (2021) died in Assembly after 21–0 | 80:SB290, 81:SB90 |
| PT compact SB186 (2019) + AB248 (2025, 41–1/21–0); EMS AB158 (2023, 42–0/21–0); audiology/SLP AB230 (2025, 41–0/21–0); AB334 endorsement 42–0/21–0 | respective bill keys |
| NLC died in first committee 3×: AB142 (2021), AB108 (2023), SB34 (2025 omnibus) | 81:AB142, 82:AB108, 83:SB34 progress; SB34 digest lists five compacts incl. NLC |
| Physician compact already in statute | 83:SB34 digest ("in the same chapter as the Interstate Medical Licensure Compact") |
| SB124 (2025) foreign medical graduates 41–0/21–0 | 83:SB124 votes |
| PBM: AB141 (2019), SB378 (2019), AB434 (2023), SB389 (2025, 41–0/18–2) enacted; SB352 (2023) Senate 21–0 died in Assembly; SB316 (2025) 18–2/42–0 died on concurrence; licensing died in committee 2021 (SB392) and 2025 (SB149, SB209) | respective bill keys; SB316 final actions in `bill-actions.json` |
| Rate raises enacted: SB96 (2021), SB435 (2023), SB221 (2023), SB185 (2025, 41–1/21–0), SB353 (2025) | respective bill keys |
| Broad rate reform died: AB116 (2019), AB99 (2023), SB255 (2023), SB239 (2025), SB150/SB366 (2025) | respective bill keys, stages |
| 31st (2020) Special Session AB3 cut DHHS appropriations, 36–6 and 21–0 | `verification/special-sessions.json` (AB3 title, digest, votes) |
| SB434 (2025) 18–2 and 42–0, died on concurrence; special-session SB5 enacted the same program 15–6/37–0, Chapter 12 | 83:SB434 actions ("Assembly Amendment No. 972 not concurred in"); verification file; program name in both digests |
| Health Service Corps funded 2019 (SB289) and 2021 (SB233); dental therapy 2019 (SB366); workforce data 2021 (AB278, SB379); SB495 (2025) 13–8 died in Assembly | respective bill keys |
| Residency grants: SB350 (2023, 21–0/40–0), SB262 (2025, unanimous); tax-credit design died on Senate floor twice (SB369, SB269); 2019 appropriation died in committee (AB311) | respective bill keys |
| Loan repayment: AB45 (2023, 41–0/21–0); AB269 (2025, 40–2/21–0); SB266 (2025, 42–0/21–0); failures AB358 (2019), AB372 (2021), AB248 (2023), AB69 (2023) | respective bill keys |
| Prior auth: AB463 (2025) enacted 42–0/20–0; SB128 vetoed after 23–16/15–6; AB290 cleared first committee, re-referred, died; AB295/AB470/SB398 died in first committees; 2019 bills all died in committee; step therapy SB167/SB194 (2023) unanimous | respective bill keys; AB290 actions in `bill-actions.json` |
| Pooling: SB481 (2019) unanimous; SB396 (2021); Public Option SB420 (2021) 12–9/26–15; any-group design never filed | respective bill keys; absence verified by digest scan |
| Political terrain: 270 person-sponsored / 139 committee; Spearman 21, Hardy 19, Scheible 18, Cannizzaro/Lange/Stone/Doñate 16; cross-party 54 bills, 36 enacted | `evidence-pack.json → people_signals` |
| Veto list themes (drug price caps, medical-debt limits, forced-arbitration ban after 42–0, AI denials) | 82:AB250, 83:AB259, 83:AB204, 82:AB439, 83:SB128 + full 15-veto list in reality-map.json |
| New-law-2025 paragraph | 83:AB463, 83:SB389, 83:SB262, 83:AB269, 83:SB266, 83:SB124, 83:AB230, 83:AB248, 83:AB334, 83:SB185, 83:SB497, 83:SB494, special-36th:SB5 |

## Constituent-statement sources

The ten proposals, their consensus notes, and trade-offs come from the
Phase 2 Community Conversation RAG dataset ("NV1 - RAG - Phase 2
Constituent Input", NV1 - Cost of Living sheet, June–July 2026), encoded in
`config/issues/nevada-cost-of-living.yaml → constituent_proposals`.
Participant quotations in the working files ("why get a prior authorization
when the doctor's gonna say I need it anyway?", "a robot") are from that
dataset, not from legislative records. The scope note from the same sheet
(tax incentives for employer coverage, ACA navigator outreach, and
specialty-targeting via health assessments surfaced but with less
consensus) is preserved as comments in the issue config.

## Statute and agency references

NRS chapters most relevant to this issue (URLs in the issue config): 422
(Medicaid), 439A (health planning and costs), 449 (medical facilities), 630
(physicians), 632 (nursing), 683A (insurance administrators and PBMs), 695G
(managed care). Agency starting points: Division of Health Care Financing
and Policy (dhcfp.nv.gov), Division of Insurance (doi.nv.gov), Patient
Protection Commission (ppc.nv.gov).

## Review status

- Programmatic fact-check: `working/nevada/cost-of-living/fact-check-reality-map.py` — ALL CLAIMS VERIFIED (2026-07-26).
- Citizen Reviewer v2.3 checklist: see `review-report.md` / `review-report.json` in the brief folder.
- Reviewers for the PR: Ryan Echols, Jodi Stephens, Ashley Lovell.
