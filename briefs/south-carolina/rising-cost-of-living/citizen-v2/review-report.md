# Review report — Rising Cost of Living in South Carolina (citizen-v2.0)

Citizen Reviewer v2.3 · 2026-08-27 · reviewed against the combined format
(NV citizen-v4 pattern, as shipped for SC slow-wage-growth): two-page front
brief + proposal spotlights + glossary + legislative process glossary in one
document, plus the standalone `proposal-spotlights` companion and
appendices A–I.

**Verdict: READY FOR HUMAN REVIEW**

Reviewers for the PR: Ryan Echols, Jodi Stephens, Ashley Lovell.

## A. Purpose fit

| ID | Check | Result | Notes |
|---|---|---|---|
| A1 | Reports the record without telling readers what to pick | PASS | History verbs throughout; no directives |
| A2 | Proposals grouped by record status | PASS | "Often moved before" / "Got support but didn't finish" / "Rarely moved before" / "Already policy — through the budget" (this issue's financial-education proposal is enacted policy, so a fourth status group was used rather than forcing it into a basket) |
| A4 | No pursue/adapt/avoid commands | PASS | Advice-word scan of brief + spotlights + appendices: remaining hits are descriptive ("students **must** earn the credit" states the law; "**Urged** lenders" quotes what a resolution did) — logged below |
| A5 | Every constituent proposal covered | PASS | All four [P-…] labels appear in the front brief (each in a bold-lead paragraph inside a status group) and again in the spotlight sections; deep dive in Appendix H |
| A6 | No worksheet apparatus / meta-commentary / source keys in front brief | PASS | Sources, caveats, and review notes live in Appendices F and I |

## B. Reading level & explainers

| ID | Check | Result | Notes |
|---|---|---|---|
| B1 | Plain professional prose | PASS | Flesch–Kincaid ≈ 11.6 for the front brief (12.5 with spotlights) — the lowest of any shipped Forum brief (SC wage brief 12.2, NH housing 13.1, NV healthcare 13.9–15.5). The ~grade 5–8 aspiration is not met by any brief in this product line; flagged for the human reviewers rather than fixed by cutting facts |
| B2 | Inline explainers in the front brief; glossaries per the combined product | PASS | Inline explainers logged in `working/.../explainer-log.md`; Glossary and Legislative process glossary end-sections follow the combined format |
| B3 | Bill descriptions understandable without legal training | PASS | Plain topics carried from the curation map |

## C. Length & layout

| ID | Check | Result | Notes |
|---|---|---|---|
| C1 | Front brief ≤2 letter pages in HTML **and** Word | PASS | Front brief occupies pages 1–2 in both renders; the combined document totals 4 pages in both (Chrome HTML→PDF and LibreOffice DOCX→PDF). Standalone spotlights: 3 pages in both (this issue's tax lane alone has 80 bills; the sibling issue fit in 2) |
| C2 | Page 1 carries the essential map | PASS | Landscape, key numbers, proviso callout, and the "often moved" basket on page 1 (render inspected) |
| C3 | Detail in appendices | PASS | 9 appendices; 77-page print HTML |

## D. Evidence integrity

| ID | Check | Result | Notes |
|---|---|---|---|
| D1 | Every example bill exists in Appendix A / evidence pack | PASS | Programmatic check: all 89 cited bill numbers resolve in the pack (budget bill numbers resolve in Appendix G) |
| D2 | No invented vote counts or parties | PASS | Every en-dash vote pair in the brief and spotlights matched verbatim against `bill-votes.json` passage votes, per-bill for the 24 headline claims; zero party claims anywhere (roster join deliberately not fetched). The one derived figure — "438–1, four times" — is the sum of four verified House votes (105–1, 101–0, 118–0, 114–0) and is labeled as combined |
| D3 | Data limits stated | PASS | Appendix F (11 items), including the FY 2020-21 proviso gap and the one out-of-record verification (the graduation regulation's status) |
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

1. Spotlights: "Treasurers must accept your car-tax payment…" rephrased to
   "Two bills (H3385, H3085) would have barred treasurers from refusing…" —
   the original read as current law; the bills died in committee.
2. Curation plain topic for H4940: "…study of whether South Carolina should
   adopt electricity-market reforms" → "…study of electricity-market reforms
   and their potential public benefits" (advice-verb removal at the source;
   propagated to evidence pack and Appendices A and E).
3. Combined-document length: glossary entries tightened (one low-value entry
   in each glossary removed, several shortened) to hold the 4-page total in
   both renders after the Word render initially spilled a few lines to
   page 5. No facts were cut; page counts re-verified at 4/4 with the front
   brief on pages 1–2.
4. Reality-map correction during writing (pre-review, logged for
   transparency): an early draft grouped the housing bill H4158 (98–10) into
   the "utility-accountability" combined vote; the brief's combined figure
   was corrected to the four utility bills only (438–1) and H4158 is cited
   separately as a housing-lane example.

## Items for the human reviewers

- Reading level is 11.6 (front brief) against a ~5–8 aspiration; best in the
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
