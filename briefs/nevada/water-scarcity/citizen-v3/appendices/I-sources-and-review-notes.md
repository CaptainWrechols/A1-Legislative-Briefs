# Appendix I — Sources and review notes

This appendix holds the reviewer-facing material that does not belong in the
front brief: the claim-to-source mapping, data-collection notes, and review
status.

## How this record was assembled

Bills were discovered two ways for the 2019, 2021, 2023, and 2025 sessions:
NELIS keyword search (water, groundwater, Colorado River, data center,
partial abatement, and related terms) and a full harvest of the Legislative
Counsel Bureau's official Subject Index of Bills (WATER, WATER RIGHTS AND
APPROPRIATION OF PUBLIC WATERS, STATE ENGINEER, DROUGHT, IRRIGATION, DATA
CENTERS, RIVERS, FLOOD CONTROL, SEWAGE, TAHOE, and related headings). All six
2020–2025 special sessions were checked; none contained water or data-center
bills. The search yielded 189 bills, hand-curated into 108 policy bills (the
basis for all headline numbers) and 81 context bills kept for audit. This is
broad, double-source coverage but not a provably complete universe; the
record shows where each bill stopped, never why. Committee Yea votes are
partly inferred (committee membership minus recorded Nay/Absent) because
Nevada minutes usually list only No and Absent votes; those rows are marked
in the source data. Party labels come from official NELIS legislator
rosters (100% of roll-call rows matched).

## Claim-to-source mapping (front brief)

Bill keys are `session:identifier` (80=2019, 81=2021, 82=2023, 83=2025).
Machine sources live in `working/nevada/water-scarcity/evidence-pack.json`
and `reality-map.json`.

| Front-brief claim | Evidence |
|---|---|
| 108 policy bills; 59 enacted; 27 first-committee deaths (15 in Natural Resources); 3 vetoes; 2025 pass rate 13 of 31 | `evidence-pack.json → inventory`, `people_signals`; `reality-map.json → session_snapshot` |
| 5 of 10 proposals never introduced | `evidence-pack.json → constituent_proposal_crosswalk`; statuses in `reality-map.json → proposal_reality_cards` |
| Data centers: no water/cooling bill; SB547 exemption; AB385 preemption death | `80:SB547`, `83:AB385`; abatement statutes NRS 360.754 et seq.; SNWA moratorium + TMWA dedication practice from LCB memo S25 (2026-03-20) |
| Metering edges | `80:AB95`, `82:SB113`, `82:AB191` |
| Waste fines nearest statute | `80:AB537` |
| Reimbursement design never filed | crosswalk `conditional-tax-incentives` (matched bills are conditioning attempts, not the reimbursement design) |
| Bring your own water / dedication | `80:SB250` (39–0); TMWA 11% drought reserve from LCB memo S25 |
| Expert water body | `80:SB499` (first committee), `83:SB143` (Senate 21–0, died in Assembly) |
| Records/audit | `83:AB485` (first committee); passed pieces `80:AB95`, `82:SB113`, `83:AB577`, `83:SB36` (prior failures `81:AB354`, `82:SB176`) |
| Abatement conditions 0-for-5 | `83:AB77`, `82:SB394` (Senate 14–7), `82:SB429` (vetoed), `81:AB449`, `83:SB364` |
| Statewide standards | `80:AB51`, `82:AB387` (Assembly 26–14); oversight theme 0-for-6 in `reality-map.json → theme_scorecards` |
| Growth restrictions precedent | `81:AB356` (21–0, 42–0), `80:SB250`, `82:SB169` (vetoed), `83:SB143` |
| Groundwater reform | `82:SB113`, `83:SB36`, `82:SB180` (41–0 + unanimous, died), `83:AB363` |
| Political terrain (sponsorship, committees) | `evidence-pack.json → people_signals`; chokepoint counts in `reality-map.json → people_and_process_signals` |
| New 2025 law | `83:SB36`, `83:SB6`, `83:SB442`, `83:SB276`, `83:AB449`, `83:SB326`, `83:AB577` |
| Citizen proposals and quoted phrases | "NV1 - RAG - Phase 2 Constituent Input" (Water sheet), mirrored in `config/issues/nevada-water-scarcity.yaml → constituent_proposals` |

## Review status

See `review-report.md` / `review-report.json` in the packet folder for the
automated checklist (no-advice scan, fact spot-checks, page-count renders)
and the items flagged for human judgment.
