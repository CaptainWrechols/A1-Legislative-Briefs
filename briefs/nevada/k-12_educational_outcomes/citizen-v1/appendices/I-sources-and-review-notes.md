# Appendix I — Sources and review notes

This appendix holds the reviewer-facing material that does not belong in the
front brief: the claim-to-source mapping, data-collection notes, and review
status.

## How this record was assembled

Bills were discovered two ways for the 2019, 2021, 2023, and 2025 sessions:
NELIS full-text search (pupil, teacher, public schools, school district,
charter school, per pupil, pupil-centered funding, State Education Fund,
inspector general, recess, physical education, instructional time,
educational technology, kindergarten, prekindergarten, early childhood,
superintendent, class size, teacher salaries, achievement of pupils, college
and career readiness, read by grade, literacy, school counselor, school
social worker, school psychologist, school-based, and safe-to-tell — 438
bills) and a full harvest of the Legislative Counsel Bureau's official
Subject Index of Bills under the K-12 education heading family (EDUCATION,
including the Department of Education, State Board of Education, Inspector
General of Education, and education savings accounts; SCHOOL PUPILS; SCHOOL
PERSONNEL; SCHOOL FINANCES AND FUNDS; SCHOOL ACCOUNTABILITY; SCHOOL FUNDING
COMMISSION; SCHOOL DISTRICTS including the county district headings;
SCHOOLS, PUBLIC / CHARTER / ACHIEVEMENT / EMPOWERMENT / FOR PROFOUNDLY
GIFTED PUPILS; SUPERINTENDENT OF PUBLIC INSTRUCTION; TEACHERS bodies; TEACH
NEVADA; EARLY CHILDHOOD EDUCATION; CAREER AND TECHNICAL EDUCATION; DISTANCE
EDUCATION; ACADEMIC STANDARDS; LOCAL SCHOOL SUPPORT TAX; HOMESCHOOLING;
SCHOOL CHOICE; SCHOOL PRECINCTS — +286 bills), with entry-level keywords
(pupil, public school, school district, charter school, kindergarten,
prekindergarten, early childhood, teacher, classroom, read by grade,
literacy, recess, physical education, school counselor/social
worker/psychologist, class size, per-pupil) harvested from all other
headings. Higher-education-only headings (Nevada System of Higher Education,
postsecondary institutions) were intentionally excluded: the issue is K-12
outcomes.

All six 2020–2025 special sessions were checked by hand and documented with
full history and votes in
`sources/nevada/k-12_educational_outcomes/verification/special-sessions.json`.
Two K-12-relevant items exist, both from the 31st (2020) Special Session:
**AB2** (Clark County school-precinct fund-balance flexibility, placed on
the Chief Clerk's desk and never voted) and **AB3** (the enacted COVID
budget act, Chapter 5). AB3's education provisions were verified from the
enrolled bill text
(leg.state.nv.us/Session/31st2020Special/Bills/AB/AB3_EN.pdf): section 71
struck the Fiscal Year 2020-2021 transfer of $31,429,229 for the Read by
Grade 3 grant program, and section 131.6 made the New Nevada Education
Funding Plan and Read by Grade Three accounts the top two priorities for
restoration if federal offset money arrived. The 31st Session's SB2
(Millennium Scholarship waivers, postsecondary) and the 36th (2025)
Session's AB5 (film-studio workforce act) were reviewed and excluded as
outside the K-12 scope.

The search yielded 724 bills, hand-curated (every NELIS digest read) into
513 policy bills — 359 core plus 154 adjacent, the basis for all headline
numbers — and 211 context bills kept for audit. This is broad,
double-source coverage but not a provably complete universe; the record
shows where each bill stopped, never why (no veto messages or floor
debate). Committee Yea votes are partly inferred (committee membership
minus recorded Nay/Absent) because Nevada minutes usually list only No and
Absent votes; those rows are marked in the source data. Party labels come
from official NELIS legislator rosters (97.9% of roll-call ballot rows
matched; the unmatched rows are minutes-parsing name fragments left
unlabeled; sponsor party coverage is 99.6%).

Generated provenance strings were corrected after the automated builds and
are documented here: the `discovery_note` and `data_limits` fields inside
`evidence-pack.json` (which the assembler stamps with wording from the
first, water-scarcity run) were rewritten to describe the education headings
actually harvested, and the issue-specific introduction sentences of
Appendices A, F, H, and this packet's README were corrected the same way.
All counts are untouched pipeline output. Sponsor tallies merge NELIS name
variants for the same person (Assemblywoman Selena Torres 2019–2023 +
Assemblymember Selena Torres-Fossett 2025; Senator Carrie Buck + Senator
Carrie Ann Buck; title changes from Assemblyman/Assemblywoman to
Assemblymember in 2025); the merges are listed in `reality-map.json`.
Concurrent resolutions carry no final NELIS history action, so two adopted
Financial Literacy Month resolutions read Unknown and 2025 AJR9 reads In
Progress; they are excluded from pass-rate claims. Every factual claim in
the reality map and front brief was checked programmatically against the
evidence pack before writing
(`working/nevada/k-12_educational_outcomes/fact-check-reality-map.py`, all
claims verified).

## Claim-to-source mapping (front brief)

Bill keys are `session:identifier` (80=2019, 81=2021, 82=2023, 83=2025;
special-session bills named in text). Machine sources live in
`working/nevada/k-12_educational_outcomes/evidence-pack.json` and
`reality-map.json`.

| Front-brief claim | Evidence |
|---|---|
| 513 policy bills; 228 enacted; 193 first-committee deaths (127 Education, 40 money committees); 13 vetoes all in 2023 (8) and 2025 (5) | `evidence-pack.json → inventory`; stage and committee counts in `reality-map.json → session_snapshot`; verified in `fact-check-reality-map.py` |
| 7 independent-audit bills filed, none voted | `80:AB146`, `80:AB296`, `81:AB108`, `82:AB149`, `82:AB353`, `83:AB33`, `83:AB154` (all Failed at first committee or origin floor); oversight committee `82:AB395` (first committee); enacted legislative audits `82:AB517` (42–0, 21–0); consultant-review repeal `83:SB411` (first committee) |
| Funding formula rebuilt; guarantee keeps dying | `80:SB543` (18–3, 34–7), `81:SB439` (20–1, 36–5), `81:AB495` (28–14, 16–5), `82:SB503`, `83:SB500` (42–0, 13–8), `82:SB231` (21–0, 41–1); failed floors `82:AB459`, `83:SB471`; revenue designs `80:SB305`, `83:AB307`, `83:AB508` |
| Recess/minutes stalled | `83:AB53` (first committee), `81:SB182` (first committee), `82:AB228` (origin floor); contrast `82:AB274` (40–0, 20–0), `83:SB444` (42–0, 21–0) |
| Growth/broader assessment stalled | `83:SB351` (first committee), `82:SB313` and `83:SB314` (origin floor), `83:SB403` (21–0, second house), `83:AB24` (first committee); enacted trims `81:SB353` (42–0, 21–0), `82:SB9`; `83:AB401` (first committee) |
| Read by Grade 3 | `80:AB289` (28–11, 17–4, enacted), `83:AB386` (40–0, 21–0, died awaiting concurrence — history in `processed/bill-actions.json`), `83:SB278` (42–0, 21–0, enacted), `82:AB187` (first committee), `81:SB273` (first committee), `82:AB400` (41–0, 20–1, enacted); $31.4M special-session cut from the verification file |
| Ed-tech never filed; edge laws exist | crosswalk `evidence-based-edtech`; `80:SB403` (40–0, 21–0), `81:SB66`, `83:SB444`, `83:AB406` (42–0, 20–1), `82:SB214`, `83:SB248` (first committee) |
| Pre-K precedent, no entitlement bill | `80:SB84` (41–0, 20–0), `82:AB400`, `82:AB348`, `83:AB212` (38–4, 21–0); failed structure `82:AB113` (origin floor), `83:SB82`, `83:SB58`, `83:AB292` (first committees) |
| Administrator accountability | `82:SB292` (21–0, 39–3), `83:SB460` (21–0, 38–4), `82:AB175` (29–11, 16–4), `83:AB156` (24–18, died in Senate); committee deaths `80:AB57`, `80:SB105`, `80:AB491`, `81:AB255`, `81:SB111`, `82:SB64`, `82:SB65`; no superintendent-pay bill: crosswalk + card `administrator-accountability` |
| Teacher pay and pipeline | `82:SB231` (21–0, 41–1), `83:AB398` (20–0, 41–1), `82:SB442` (42–0), `82:AB515`/`82:AB428` (42–0), `83:AB49` (42–0, 21–0), `83:AB472`; failed `80:SB445`, `82:AB335`; vetoed `82:AB282` (31–11, 16–4), `83:AB155`, `82:AB172` |
| School mental health | `80:SB319` (41–0, 21–0), `81:SB151` (33–8, 18–3), `83:SB277` (38–1, 15–5), `80:SB80`, `80:SB204`, `81:SB249`; failed mandates `83:AB298`, `83:AB374`, `83:SB254`; vetoed `82:AB265` (42–0, 20–0), `82:AB201` |
| Political terrain (340 person-sponsored; Dondero Loop 37; Hammond 31; Buck 31; Miller 24 with merged name forms; 55 cross-party, 28 enacted; committee chokepoints) | `evidence-pack.json → people_signals`; merged variants and chokepoints in `reality-map.json → people_and_process_signals`; verified in `fact-check-reality-map.py` |
| New 2025 law | `83:AB398`, `83:AB49`, `83:SB460`, `83:SB278`, `83:SB444`, `83:AB406`, `83:SB277`, `83:AB224` (41–1, 21–0), `83:AB533` (38–1, 21–0), `83:SB500` |
| Citizen proposals and quoted phrases | "NV1 - RAG - Phase 2 Constituent Input" (NV1 - Education sheet), mirrored in `config/issues/nevada-k-12_educational_outcomes.yaml → constituent_proposals` |

## Statute and agency references

K-12 administration and accountability: NRS 385 and 385A
([leg.state.nv.us/NRS/NRS-385.html](https://www.leg.state.nv.us/NRS/NRS-385.html),
[NRS-385A.html](https://www.leg.state.nv.us/NRS/NRS-385A.html)); school
finance and the State Education Fund: NRS 387; the system of public
instruction (courses, charter schools in 388A): NRS 388 and 388A;
examinations and diplomas: NRS 389–390; educational personnel: NRS 391;
pupils, attendance, discipline, and Read by Grade 3: NRS 392 (392.750–.760).
Nevada Department of Education: [doe.nv.gov](https://doe.nv.gov/); the
Commission on School Funding publishes its recommendations through the
Department; accountability data: [nevadareportcard.nv.gov](https://nevadareportcard.nv.gov/).
Special-session bill text for the 31st (2020) Session AB3:
leg.state.nv.us/Session/31st2020Special/Bills/AB/AB3_EN.pdf.

## Review status

See `review-report.md` / `review-report.json` in the packet folder for the
automated checklist (no-advice scan, banned-section scan, fact spot-checks,
page-count renders) and the items flagged for human judgment.
