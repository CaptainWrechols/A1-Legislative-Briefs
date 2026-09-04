# Independent fact-check — Responsive Elected Leaders citizen-v2.1

Date: 2026-09-04 · Method: verification against **live external sources
fetched fresh on the check date**, independent of this repository's stored
artifacts. Two layers: (1) the live official record at scstatehouse.gov,
re-fetched page by page and checked programmatically; (2) third-party
outlets and organizations for the brief's headline claims.

## Layer 1 — Live official record (automated)

Script: `working/south-carolina/responsive-elected-leaders/fact-check-verify.py`
(rerunnable). It fetches the live bill-history page for every measure the
brief cites, the live bill-text pages for every design-detail claim, and the
live enacted Part IB proviso pages, then asserts each specific fact the
brief states.

**Result: 230 of 230 checks passed, 0 failed.** Coverage:

- **Vote pairs, verbatim** — every roll call cited in the brief confirmed on
  the live history pages, including H3570 (102–0, 40–0, 23–86), S70 (39–2,
  109–4), S38 (45–0, 91–12), S35 (29–7), H3008 (29–14), H5683 (74–36,
  74–37, 26–18), H4493 (96–14, 100–15, 43–1, 75–27), S865 (41–2, 74–35,
  68–36, 72–33), H4561 (53–45), S133 (24–16, 67–41, 24–14), H3676 (68–30),
  S499 (37–7).
- **Act and ratification numbers** — Act 191 of 2026 (S70, R221), Act 26 of
  2021 (S38), Act 117 (H4493), Act 118 (S865); and the absence of any act
  number on every measure the brief says did not pass.
- **Decisive actions** — H3570's conference committee appointment; H3008's
  and H3007's "Adopted, returned to House with concurrence"; H5683's Senate
  "Continued" action paired with the 26–18 roll call; H4717's Judiciary
  referral with no committee report; S133's conference appointment.
- **The 21 commission/criteria bills and 4 civics bills** — each checked for
  correct title, the Judiciary (or House Education and Public Works)
  referral the brief states, and the absence of any act number or floor
  roll call.
- **Design-detail claims, against live bill text** — S6/H3044 (nine members,
  Applicant Review Panel appointed by the Inspector General, referendum
  approval); H4222 (twelve members appointed by the State Ethics Commission,
  five majority party / five largest minority party / two other, ten maps);
  H3243 (no legislative or executive alteration or veto; no sine die
  adjournment until adoption); S230 (sine die lock, decennial cycle); H3432
  (State Ethics Commission oversees appointments); H3547 (required
  middle-school civics unit, Palmetto Middle School Civics Challenge, State
  Board of Education adopts curriculum, 2027-2028); H4392 (private-funding
  and lobbying-credit restrictions).
- **Provisos, against the live enacted Part IB pages** — FY 2026-27:
  117.219 (ethics filers must name the paying government body), 117.145
  (unconditional right to intervene in election-law suits), 110.2 (monthly
  Ethics Commission meetings), 118.6 (no general funds for agency
  lobbying), 117.92 (Local Government Fund lobbying ban), and the USC
  Center for American Civic Leadership and Public Discourse line;
  FY 2024-25: 45.11 (Clemson Center for Civic Engagement study) and 110.1
  (ethics committees' approval power over the Public Disclosure and
  Accountability Reporting System).

## Layer 2 — Third-party sources (headline claims)

- **H5683 (mid-decade congressional redraw):** The State, WACH, South
  Carolina Public Radio, and the Post & Courier all confirm the House
  passed it 74–37 in overnight voting during the May 2026 special session
  and that the Senate's 26–18 vote to "continue" the bill on May 26, 2026
  effectively killed the redistricting effort without a vote on the bill
  itself — matching the brief's account, including its labeling of the
  26–18 vote as a procedural shelving motion rather than a passage vote.
- **REACH Act:** the SC Commission on Higher Education's compliance policy
  and USC's Provost office independently confirm Act 26 of 2021 requires
  undergraduates at public institutions to complete a three-credit course
  reading the founding documents — matching the brief's description.
- **H3008 (congressional term-limits application):** U.S. Term Limits'
  announcement and two independent vote trackers confirm the Senate's
  29–14 adoption in May 2025, completing the application after earlier
  House adoption — matching the brief.
- **S70 (School Board Ethics Act):** the SC Policy Council's 2026 session
  recap, a State Board of Education committee briefing, and the official
  ratification log confirm Act 191 of 2026 (signed May 18, 2026): a
  required model code of ethics adopted by the State Board with mandatory
  local adoption, plus mandatory training — matching the brief.
- Availability note: LegiScan blocks automated access (bot protection) and
  the OpenStates/Plural bulk CSV links are behind a scripted page, so the
  third-party layer used news outlets, agency documents, and advocacy/
  tracker pages reachable at check time.

## Corrections made as a result of the fact-check

Two precision fixes (no substantive claim was wrong; both tightened wording
that could over-read the record):

1. **H3008 adoption timing.** The House adopted it in March 2025 and the
   Senate in May 2025; two appendix rows generated from the working files
   said "adopted by both chambers in May 2025." Fixed at the source
   (curation and stage-override scripts) and regenerated; citizen-facing
   text already used the accurate "adopted May 2025, Senate 29–14"
   (adoption completed May 2025).
2. **H5683 amendment count.** The brief said "roughly fifty amendments were
   tabled"; the precise record is 28 amendments tabled on roll-call votes,
   with 55 tabling votes in all (including motions to reconsider) among 62
   House roll calls. Reworded everywhere to "dozens of amendments were
   tabled (28 on roll-call votes, 55 tabling votes in all)" or equivalent.

## Addendum (2026-09-04, state-vs-local venue review)

A follow-up review checked the packet for places where "nothing has been
tried" language could hide county- or district-level activity or authority.
Four clarifications were added (no record claims changed), each grounded
before use:

- **S.C. Code Section 4-9-90** (fetched from the official code site):
  county councils must reapportion their own council districts after each
  federal decennial census — supporting the new "county and city lines are
  drawn locally" language.
- **Local school-board reapportionment acts** (from the certified
  universe): roughly a dozen enacted after the 2020 census (Abbeville,
  Hampton, Cherokee, Union, Greenwood 50, Aiken, Spartanburg 5 and 7,
  Florence 3, Kershaw, Saluda, Anderson) — supporting the "school-board
  lines usually move through separate local acts" language; these were
  always excluded from the 21-bill commission count as local housekeeping.
- **S.C. Code Section 7-13-35** (official code site): election authorities
  must publish official election notices (registration deadlines,
  precincts, polling places) — supporting the tightened voter-information
  claim ("election offices already publish the official basics; what no
  bill proposes is a neutral guide to candidates and issues").
- **District curriculum authority:** state law sets required minimums and
  the State Board adopts standards; districts control offerings beyond
  them — supporting the new "district lever" note in the civics spotlight.

## Scope notes

- The two constituent proposals' frequency, consensus, and concern lines
  are quoted from the final proposal grid document itself (Forum process
  input); they are provenance-checked against that document, not
  externally verifiable facts, and the brief labels them as process input.
- "Did not pass" statements for the 126th session reflect the record as of
  the original collection date (2026-08-26) and were re-confirmed against
  the live pages on 2026-09-04 (no cited measure has moved since).

**Verdict: all legislative-record claims in the citizen-v2.1 package are
confirmed against the live official record, with the two wording
tightenings above applied.**
