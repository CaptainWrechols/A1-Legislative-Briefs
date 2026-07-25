# Evidence Pack — K-12 Educational Outcomes in Nevada

- **Issue:** `nevada-03-k-12-educational-outcomes` · built 2026-07-25 by evidence-curator v2.2
- **Machine pack:** `evidence-pack.json` (assembled by `collectors/build_evidence_pack.py` from `curation-map.json` + processed Pass 2 data)
- **Sessions:** 2019 (80th), 2021 (81st), 2023 (82nd), 2025 (83rd)

## How the set was built

Discovery combined NELIS full-text keyword search (pupil, teacher, public
schools, school district, charter school, per pupil, State Education Fund,
recess, kindergarten/prekindergarten, early childhood, superintendent,
literacy, read by grade, school counselor/social worker/psychologist and
related terms — 438 bills) with a full harvest of the LCB official Subject
Index of Bills under the K-12 education heading family (EDUCATION including
the Department, State Board and Inspector General of Education; SCHOOL
PUPILS; SCHOOL PERSONNEL; SCHOOL FINANCES AND FUNDS; SCHOOL ACCOUNTABILITY;
SCHOOL FUNDING COMMISSION; SCHOOL DISTRICTS including county districts;
SCHOOLS PUBLIC/CHARTER/ACHIEVEMENT/EMPOWERMENT/GIFTED; SUPERINTENDENT OF
PUBLIC INSTRUCTION; TEACHERS bodies; EARLY CHILDHOOD EDUCATION; CAREER AND
TECHNICAL EDUCATION; DISTANCE EDUCATION; ACADEMIC STANDARDS; LOCAL SCHOOL
SUPPORT TAX; HOMESCHOOLING; SCHOOL CHOICE — +286 bills). Higher-education-
only headings were intentionally excluded: the issue is K-12 outcomes.

All six 2020–2025 special sessions were checked by hand
(`sources/nevada/k-12_educational_outcomes/verification/special-sessions.json`).
Two K-12-relevant items exist, both from the 31st (2020) COVID budget
session: **AB2** (Clark County school-precinct fund-balance flexibility,
never voted — died on the Chief Clerk's desk) and **AB3** (the enacted
budget-reduction act, which struck the FY 2020-2021 $31.4 million Read by
Grade 3 transfer and set education accounts as the top federal-relief
restoration priorities — verified from the enrolled bill text).

The search yielded **724 bills**, hand-curated (every NELIS digest read) into:

- **359 core** (K-12 education policy affecting outcomes is the point)
- **154 adjacent** (a real but partial K-12 angle)
- **211 context** (found by broad terms or omnibus indexing; kept for audit,
  excluded from headline numbers)
- **Policy set (core + adjacent): 513 bills** — the basis for all headline
  numbers below.

## Inventory (policy set, 513 bills)

| Disposition | Count |
|---|---|
| Enacted | 228 |
| Failed | 269 |
| Vetoed | 13 |
| Unknown (adopted concurrent resolutions with no final NELIS action) | 2 |
| In Progress (2025 AJR9, resolution) | 1 |

By session: 2019 — 146 bills (77 enacted); 2021 — 110 (50); 2023 — 128
(52, 8 vetoed); 2025 — 129 (49, 5 vetoed). Where the 269 failures stopped:
**193 in their first committee**, 43 on the origin floor or calendar, 30 in
the second house, 3 after passing both houses. Of the 193 first-committee
deaths, 127 died in an Education committee, 40 in the money committees
(Finance / Ways and Means), 12 in Government Affairs.

## Themes (policy bills)

| Theme | Bills | Enacted | Where the rest usually stopped |
|---|---|---|---|
| Pupil health, mental health, discipline, supports | 97 | 51 | first committee (21), origin floor (14) |
| What is taught and time in the school day | 86 | 30 | first committee (34) |
| Teacher pay, hiring, licensing, the shortage | 68 | 33 | first committee (20), origin floor (9) |
| Accountability, boards, superintendents, administrators | 53 | 16 | first committee (26) |
| Charter schools and school choice | 45 | 15 | first committee (27) |
| How schools get money (funding plan, finance) | 44 | 28 | first committee (14) |
| School buildings, safety, transportation, operations | 35 | 21 | first committee (11) |
| Testing, grading, graduation, measuring progress | 35 | 13 | first committee (18) |
| Pre-K, kindergarten, early childhood, reading by 3 | 26 | 14 | first committee (9) |
| Audits and oversight of school spending | 24 | 7 | first committee (13) |

## Constituent-proposal crosswalk (term-matched; verified cards in reality map)

| Phase 2 proposal | Term-matched bills | Reading |
|---|---|---|
| Audit spending / classroom dollars | 12 | Independent-audit bills exist and almost all died early; one legislative-audit bill became law (2023 AB517). |
| Per-pupil funding above average | 27 | The formula itself was rebuilt (2019 SB543); the fights are now about the base amount and revenue. |
| Recess / instructional minutes | 7 | A recess mandate was filed once (2025 AB53) and died in its first committee. |
| Evidence-based ed-tech | 10 | No independent-proof mandate; adjacent law exists (data privacy 2019 SB403, cellphone policies 2025 SB444). |
| Universal pre-K | 23 | Grant-program precedent (2019 SB84); universal pre-K has never been filed. |
| Administrator/superintendent accountability | 33 | Board-reform bills recur and mostly die in committee; principal accountability passed in 2023/2025. |
| Teacher pay / shortage | 36 | The 2023 salary-match money passed; the $45,000 salary floor died in 2019. |
| Growth-based / broader assessment | 33 | Growth already drives star ratings; social-emotional measures keep failing. |
| Read by Grade 3 reform | 24 | Retention was removed by 2019 AB289; assessment fights continue. |
| School mental health | 25 | Ratio-plan and SafeVoice laws exist; the counselor-in-every-school mandate died in 2025. |

## People signals (facts only)

- 340 of 513 policy bills came from named lawmakers; 173 from committees.
- Most frequent primary sponsors: Sen. Marilyn Dondero Loop (D, 37), Sen.
  Scott Hammond (R, 31), Sen. Carrie Buck (R, 23), Asm. Selena Torres (D,
  21), Sen. Heidi Seevers Gansert (R, 19), Sen. Roberta Lange (D, 19), Asm.
  Brittney Miller (D, 18), Sen. Moises Denis (D, 18).
- Cross-party sponsor teams appeared on **55 policy bills; 28 became law**.
- **47 bills drew a floor majority (some unanimous) and still did not become
  law** — mostly second-house deadline deaths.
- Vetoes: 13 policy bills, all in 2023 (8) and 2025 (5).

## Data limits

See `evidence-pack.json → data_limits`: keyword-plus-index discovery is not a
proven complete universe; the record shows where bills stopped, never why;
committee Yeas partly inferred and marked; party labels 97.9% (ballots) /
99.6% (sponsors); resolutions carry no final NELIS action; special-session
facts come from the manual verification file; context bills kept for audit
only.

## Handoff

> Evidence Curator finished. Run **Reality Mapper**.
