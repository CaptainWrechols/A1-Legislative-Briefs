# Review report — Rising Cost of Living in South Carolina (citizen-v2.1)

Citizen Reviewer v2.3 · 2026-08-27 (v2.0) · **re-reviewed 2026-09-04
(v2.1)** after the brief was reworked around the final proposal grid — each
proposal section now opens with the grid's reported frequency, consensus,
and concerns (labeled process input) followed by the record facts addressed
to those points — and a child care assistance section was added for the
reported legislator-discussion topic (17-bill childcare theme, scan at
`working/.../childcare-assistance-scan.md`). The legislative record itself
is unchanged: no bill facts, votes, or outcomes were altered, only
reorganized and extended with the verified childcare set.

**Verdict: READY FOR HUMAN REVIEW**

Reviewers for the PR: Ryan Echols, Jodi Stephens, Ashley Lovell.

## v2.1 provenance flag (for the human reviewers)

The final-grid source document ("SC1 – Rising Cost of Living.docx",
2026-09-04) did not transfer into this workspace. The reported cells used in
the brief, spotlights, config, and Appendix H are the Phase 2 grid's lines
for this issue, which the final grids carry forward verbatim (verified
against the slow-wage-growth final grid processed the same day). Please
confirm the cells — and whether the final grid changed this issue's proposal
set structurally — against the original document. The legislator note on a
"merger of Dominion and Nextera" is quoted only in Appendix H, labeled
unverified.

## A. Purpose fit

| ID | Check | Result | Notes |
|---|---|---|---|
| A1 | Reports the record without telling readers what to pick | PASS | History verbs throughout; no directives |
| A2 | Proposals grouped by record status | PASS (v2.1 restructure) | The rework centers the brief on the grid's points: one section per proposal, each opening with the reported cells (labeled) and closing with the record's status for that proposal; history-basket language is carried inside the sections and in Appendix B. The spotlights keep the viability groups (already law / proven support / stopped early / never filed) |
| A4 | No pursue/adapt/avoid commands | PASS | Advice-word scan of brief + spotlights + appendices: remaining hits are descriptive ("students **must** earn the credit" states the law; "**Urged** lenders" quotes what a resolution did) — logged below |
| A5 | Every constituent proposal covered | PASS | All four [P-…] labels head their own front-brief sections and spotlight sections, with the grid's reported cells verbatim in Appendix H; the childcare topic is covered separately and labeled "not a Phase 2 proposal" everywhere it appears |
| A6 | No worksheet apparatus / meta-commentary / source keys in front brief | PASS | Sources, caveats, and review notes live in Appendices F and I |

## B. Reading level & explainers

| ID | Check | Result | Notes |
|---|---|---|---|
| B1 | Plain professional prose | PASS | Flesch–Kincaid ≈ 11.4 for the v2.1 front brief (a sentence-splitting pass was applied after the rework initially pushed it to 15.1) — the lowest of any shipped Forum brief (SC wage brief 12.2, NH housing 13.1, NV healthcare 13.9–15.5). The ~grade 5–8 aspiration is not met by any brief in this product line; flagged for the human reviewers rather than fixed by cutting facts |
| B2 | Inline explainers in the front brief; glossaries per the combined product | PASS | Inline explainers logged in `working/.../explainer-log.md`; Glossary and Legislative process glossary end-sections follow the combined format |
| B3 | Bill descriptions understandable without legal training | PASS | Plain topics carried from the curation map |

## C. Length & layout

| ID | Check | Result | Notes |
|---|---|---|---|
| C1 | Front brief ≤2 letter pages in HTML **and** Word | PASS | v2.1: front brief occupies pages 1–2 in both renders, with the spotlights starting cleanly on page 3; the combined document totals 5 pages in both (Chrome HTML→PDF and LibreOffice DOCX→PDF; grew from 4 with the childcare spotlight). Standalone spotlights: 4 pages in both |
| C2 | Page 1 carries the essential map | PASS | Landscape, key numbers, proviso callout, and the "often moved" basket on page 1 (render inspected) |
| C3 | Detail in appendices | PASS | 9 appendices; 81-page print HTML (childcare theme in A/B/C/D, provisos in G, addendum in H) |

## D. Evidence integrity

| ID | Check | Result | Notes |
|---|---|---|---|
| D1 | Every example bill exists in Appendix A / evidence pack | PASS | Programmatic re-check (v2.1): all 261 cited bill ids across the brief, spotlights, appendices, and childcare scan resolve in the pack (budget bill numbers resolve in Appendix G) |
| D2 | No invented vote counts or parties | PASS | Re-verified for v2.1: every en-dash vote pair across all citizen-facing files matched against `bill-votes.json` passage votes (zero unmatched), per-bill for the headline claims incl. the childcare set (S595 39–0/100–1, H4023 41–0/107–0, S862 44–0/108–0, S946 45–0/105–0); zero party claims. Derived/actions figures labeled: "438–1, four times" is the sum of four verified House votes; H5118's 23–76 is the recorded non-concurrence roll call from the official history |
| D3 | Data limits stated | PASS | Appendix F (12 items), including the FY 2020-21 proviso gap, the graduation-regulation verification, the final-grid provenance caveat, and the childcare topic's non-record origin |
| D4 | Inferred committee Yeas (if shown) marked | PASS (n/a) | No committee tallies exist in SC and none appear or are implied; stated in F, G, and the appendices-print note |

## E. Forum fairness

| ID | Check | Result | Notes |
|---|---|---|---|
| E1 | No should/must/recommend/urge directed at citizens or legislature | PASS | Remaining "must" instances state what laws require of others (graduation credit; the enacted service-fee rule); "urged" describes a resolution's own content. One real fix made during review (below) |
| E2 | No party blame | PASS | No party labels at all |
| E3 | People signals descriptive | PASS | Sponsor names with bill counts and outcomes only; chamber leaders identified by role, not judged |
| E4 | Recently passed list flags saturation as a question, not shame | PASS | "Recently done — groups may ask whether a repeat is needed or whether a gap remains" framing in the reality map; brief states new law neutrally |

## F. Package completeness

| ID | Check | Result | Notes |
|---|---|---|---|
| F1 | HTML + print CSS exist | PASS | `citizen-brief.html`, `citizen-brief-print.css` |
| F2 | Appendices A–F exist | PASS | A–I present |
| F3 | PACKAGE.md exists | PASS | With rebuild commands and manual fallbacks |
| F3b | Word exports exist, front brief ≤2 pages | PASS | `citizen-brief.docx` (front brief pp. 1–2 of 4), `appendices/appendices.docx` (76 pp) |
| F7 | Reviewer material in appendix only | PASS | Appendix I claim-to-source map |
| F4 | Phase 2 tokens only | PASS | White/navy `#1A2D4F`/terracotta `#C0392B`/Arial; no purple/gold/cream |
| F5 | Phase 2 modules present; no tables in front brief | PASS | Masthead, terracotta H2s, stat strip, bold-lead prose; zero front-brief tables |
| F6 | No Phase 2 sample text copied | PASS | Module shapes/tokens only; all headings and text original |

## SC-specific gates (workflow doc)

| Check | Result | Notes |
|---|---|---|
| Page-1 "Also in the state budget (provisos)" callout | PASS | Names FY 2026-27 provisos 117.220 (extra $25,000 homestead exemption), 117.191/117.208 (tax-rate acceleration), FY 2022-23 proviso 1.101 (personal-finance order), and 72.3 (Santee Cooper oversight funding); states the one-year nature and the whole-bill vote rule |
| Explicit none-found where applicable | PASS | FY 2020-21 no-enacted-Part-IB gap stated in Appendices F and G; Appendix G also states the explicit none-found for financial-education provisos in every cycle except FY 2022-23 |
| No implied committee vote tallies | PASS | Committee stops always described as outcomes ("died in," "recommitted to," "reported out"), never with numbers |
| Constituent proposals labeled [P-…] as process input | PASS | Labels in brief and spotlights; process-input framing in Appendix H and F |
| Completeness gate before curation | PASS | `verify_completeness --strict`: PASS_WITH_WARNINGS (21/1/0); the warning (optional OpenStates mirror absent) is benign and disclosed in Appendix I |
| Do not re-scrape the full state | PASS | All legislative data from prebuilt artifacts and the certified universe; the single outside check (State Register status of Regulation 43-234/Doc. 5130) is disclosed in Appendix F item 8 and Appendix I |

## Fixes made during review (logged)

### v2.1 (2026-09-04)

1. Front brief trimmed (New law section shortened, vote details deduplicated
   against the sections that already carry them) to hold the front brief on
   pages 1–2 in both renders after the rework and the childcare section
   initially pushed it onto page 3. No facts were cut — every removed
   detail remains in the spotlights or appendices.
2. Sentence-splitting pass on the reworked proposal sections after the
   "reported vs. record" compound sentences pushed the front brief's
   Flesch–Kincaid to 15.1; final 11.4. No facts changed.
3. Appendix F reviewer note "Human reviewers should confirm…" rephrased to
   "Confirmation … is an open item for the human reviewers" (advice-verb
   removal).
4. Landscape/terrain counts recomputed for the enlarged set (257 policy
   bills, 31 enacted, 201 first-committee deaths — "four of every five,"
   replacing v2.0's "five of every six" of the smaller set) and re-verified
   programmatically.

### v2.0 (2026-08-27)

1. Spotlights: "Treasurers must accept your car-tax payment…" rephrased to
   "Two bills (H3385, H3085) would have barred treasurers from refusing…" —
   the original read as current law; the bills died in committee.
2. Curation plain topic for H4940: "…study of whether South Carolina should
   adopt electricity-market reforms" → "…study of electricity-market reforms
   and their potential public benefits" (advice-verb removal at the source;
   propagated to evidence pack and Appendices A and E).
3. Combined-document length: glossary entries tightened to hold the (then)
   4-page total in both renders. No facts were cut.
4. Reality-map correction during writing: an early draft grouped the housing
   bill H4158 (98–10) into the "utility-accountability" combined vote; the
   combined figure was corrected to the four utility bills only (438–1) and
   H4158 is cited separately as a housing-lane example.

## Independent fact-check (2026-09-04)

On request, every headline claim was re-verified against sources independent
of the repository mirror: live scstatehouse.gov bill histories and ratified
texts (31 headline bills — all act numbers and all cited roll calls
matched, House "Yeas" and Senate "Ayes" lines both checked), 17
committee-stop/conference claims, the live enacted Part IB pages (9 proviso
citations and quoted effects), and the current SC Code (9 statute
references), plus the State Register for Regulation 43-234. **No
discrepancies found.** Report:
`working/south-carolina/rising-cost-of-living/independent-fact-check-2026-09-04.md`.

## Items for the human reviewers

- **Final-grid provenance (v2.1):** see the flag at the top — the source
  docx did not transfer; the reported cells need confirmation against the
  original, including whether the final grid restructured this issue's
  proposal set. (The reported cells are process input and are not
  fact-checkable against the legislative record; everything checkable was
  checked — see the independent fact-check section.)
- **Child care assistance framing (v2.1):** the topic is presented strictly
  as a record scan tied to reported legislator discussions, labeled "not a
  Phase 2 proposal" everywhere. The "what the record indicates" passages are
  descriptive pattern statements (venue, acceleration, floor viability,
  never-filed designs), not recommendations — please confirm the framing
  reads that way.
- Reading level is 11.4 (front brief) against a ~5–8 aspiration; best in the
  product line so far, but a simplified variant would require cutting vote
  numbers and bill counts.
- The 126th session is treated as concluded ("did not pass (session
  ended)") per the August 2026 collection date; a special session could
  change counts.
- The claim that the personal-finance graduation requirement is in force
  rests on the State Register / State Board regulation (disclosed in
  Appendix F item 8), because the approval joint resolution itself never
  passed. Please confirm the framing is comfortable.
- Party-blind presentation is deliberate (no roster join); ballot PDFs are
  recorded per roll call (`ballot_pdf_key`) and can be fetched on demand if
  reviewers want party splits on the handful of cited floor votes.
- The 2020 Electricity Market Reform Measures Study Committee's report is
  outside the bill record; the brief says only that the study was created.
  If reviewers want its findings summarized, that is a new collection task.
