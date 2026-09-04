# Review report — Slow Wage Growth in South Carolina (citizen-v2.0)

Citizen Reviewer v2.3 · 2026-08-26 · re-reviewed 2026-08-27 after the
package was completed to the combined format (NV citizen-v4 pattern):
proposal spotlights, glossary, and legislative process glossary added to
the brief, plus the standalone `proposal-spotlights` companion.

**Verdict: READY FOR HUMAN REVIEW**

Reviewers for the PR: Ryan Echols, Jodi Stephens, Ashley Lovell.

## A. Purpose fit

| ID | Check | Result | Notes |
|---|---|---|---|
| A1 | Reports the record without telling readers what to pick | PASS | History verbs throughout; no directives |
| A2 | Proposals grouped by record status | PASS | "Often moved before" / "Got support but didn't finish" / "Rarely moved before" (incl. never-filed) |
| A4 | No pursue/adapt/avoid commands | PASS | Advice-word scan of brief + appendices: zero hits |
| A5 | Every constituent proposal covered | PASS | All four [P-…] labels appear in the front brief and again in the spotlight sections; bill-by-bill viability groups in the standalone spotlights; deep dive in Appendix H |
| A6 | No worksheet apparatus / meta-commentary / source keys in front brief | PASS | Sources, caveats, and review notes live in Appendices F and I |

## B. Reading level & explainers

| ID | Check | Result | Notes |
|---|---|---|---|
| B1 | Plain professional prose | PASS | Flesch–Kincaid ≈ 12.2 after the reviewer's sentence-splitting pass — the lowest of any shipped Forum brief (NH housing 13.1, NV healthcare 13.9–15.5). The ~grade 5–8 aspiration is not met by any brief in this product line; flagged for the human reviewers rather than fixed by cutting facts |
| B2 | Inline explainers in the front brief; glossaries per the combined product | PASS | Inline explainers retained on pages 1–2 and logged in `working/.../explainer-log.md`; the Glossary and Legislative process glossary end-sections follow the NV citizen-v4 combined format (they supplement, not replace, the inline explainers) |
| B3 | Bill descriptions understandable without legal training | PASS | Plain topics carried from the curation map |

## C. Length & layout

| ID | Check | Result | Notes |
|---|---|---|---|
| C1 | Front brief ≤2 letter pages in HTML **and** Word | PASS | The front brief occupies pages 1–2 in both renders; the combined document (front brief + spotlights + glossaries, per the NV citizen-v4 format) totals 4 pages in both (Chrome HTML→PDF and LibreOffice DOCX→PDF). Standalone spotlights: 2 pages in both |
| C2 | Page 1 carries the essential map | PASS | Landscape, key numbers, proviso callout, and the two strongest baskets on page 1 (render inspected after the additions) |
| C3 | Detail in appendices | PASS | 9 appendices; 44-page print HTML |

## D. Evidence integrity

| ID | Check | Result | Notes |
|---|---|---|---|
| D1 | Every example bill exists in Appendix A / evidence pack | PASS | Programmatic check: all 21 cited bill numbers resolve in the pack (budget bill numbers resolve in Appendix G) |
| D2 | No invented vote counts or parties | PASS | Every yes–no pair in the brief matched verbatim against `bill-votes.json` passage votes; zero party claims anywhere (roster join deliberately not fetched) |
| D3 | Data limits stated | PASS | Appendix F (8 items), including the FY 2020-21 proviso gap |
| D4 | Inferred committee Yeas marked | PASS (n/a) | No committee tallies exist in SC and none appear or are implied; stated in F, G, and the appendices-print note |

## E. Forum fairness

| ID | Check | Result | Notes |
|---|---|---|---|
| E1 | No should/must/recommend/urge | PASS | One "should" in Appendix F rephrased during review (see fixes) |
| E2 | No party blame | PASS | No party labels at all |
| E3 | People signals descriptive | PASS | Sponsor names with bill counts only |
| E4 | Recently-passed list flags saturation as a question, not shame | PASS | "Recently done — groups may ask whether a gap remains" framing in reality map; brief states the new law neutrally |

## F. Package completeness

| ID | Check | Result | Notes |
|---|---|---|---|
| F1 | HTML + print CSS exist | PASS | `citizen-brief.html`, `citizen-brief-print.css` |
| F2 | Appendices A–F exist | PASS | A–I present |
| F3 | PACKAGE.md exists | PASS | With rebuild commands and manual fallbacks |
| F3b | Word exports exist, brief ≤2 pages | PASS | `citizen-brief.docx` (2 pp), `appendices/appendices.docx` (41 pp) |
| F7 | Reviewer material in appendix only | PASS | Appendix I claim-to-source map |
| F4 | Phase 2 tokens only | PASS | White/navy `#1A2D4F`/terracotta `#C0392B`/Arial; no purple/gold/cream |
| F5 | Phase 2 modules present; no tables in front brief | PASS | Masthead, terracotta H2s, stat strip, bold-lead prose; zero front-brief tables |
| F6 | No Phase 2 sample text copied | PASS | Module shapes/tokens only; all headings and text original |

## SC-specific gates (workflow doc)

| Check | Result | Notes |
|---|---|---|
| Page-1 "Also in the state budget (provisos)" callout | PASS | Names FY 2026-27 provisos 117.155, 25.4, 3.8 (WINS $), 117.138; states the one-year nature and the whole-bill vote rule |
| Explicit none-found where applicable | PASS | FY 2020-21 no-enacted-Part-IB gap stated in Appendices F and G |
| No implied committee vote tallies | PASS | Committee stops always described as outcomes ("died in," "reported out"), never with numbers |
| Constituent proposals labeled [P-…] as process input | PASS | Labels in brief; process-input framing in Appendix H and F |
| Completeness gate before curation | PASS | `verify_completeness --strict`: PASS_WITH_WARNINGS (20/2/0); both warnings benign and disclosed in Appendix I |

## Fixes made during review (logged)

1. Appendix F: "readers should treat any such number elsewhere with
   suspicion" → "any such number found elsewhere has no official source"
   (advice-verb removal).
2. Front brief: five sentences over ~35 words split in place (WINS history,
   career-pathways overhaul, minimum-wage inventory, group wage floors,
   second-chamber chokepoint; proviso callout sentence split). No facts
   changed; grade improved 13.1 → 12.2; page counts re-verified at 2/2.
3. Earlier factual corrections during writing (pre-review, logged for
   transparency): H4603 lead sponsor corrected to Rep. Jones and year to
   2026 (prefiled December 2025); "96% or better" floor-vote claim replaced
   with the exact worst margin (84–12); proviso citations moved from
   FY 2025-26 to FY 2026-27 numbering.
4. 2026-08-27 completion pass: local-preemption correction. The fixed-floor
   minimum-wage bills (H3114, H3467, H3341, H3480, H5187) amend §6-1-130 so
   that local governments *may not exceed* the new state floor — the
   curation-map plain topics had said the opposite ("let local governments
   go higher"). Verified against full bill text; corrected in the curation
   map, evidence pack, Appendix A, and both spotlight texts. All vote pairs
   in the new spotlight/glossary sections re-verified programmatically
   against `bill-votes.json` (zero unmatched); advice-language and
   party-label scans re-run clean on all citizen-facing files.
5. 2026-09-04 final-grid rework (lege brief v1.1). The deliverable was
   reworked around the FINAL proposal grid ("SC1 – Slow Wage Growth"): three
   proposals, with the standalone raise-minimum-wage item folded into the
   age-bracketed proposal per the grid's consensus line. The config's
   `constituent_proposals` block and Appendix H were updated to match. New
   record facts added and verified against source data: no age-based rate
   language exists in any of the 24 minimum-wage bills (full-text scan);
   both advisory ballot questions (S633, S28) asked about a $15 minimum
   (bill text); S557's apprentice credit is open to any taxpayer with a
   registered apprentice (bill text); the awareness provisos (25.8, 1.94)
   and the never-filed direct-bonus finding address the grid's stated
   concerns descriptively. The legislative record itself is unchanged. All
   scans re-run clean; every cited bill and vote pair re-verified (zero
   unmatched). 8 pages, LibreOffice-verified.

## Items for the human reviewers

- Reading level is 12.2 against a ~5–8 aspiration; consistent with (and
  slightly better than) every shipped NV/NH brief. A simplified variant
  would require cutting vote numbers and bill counts from the front brief.
- The 126th session is treated as concluded ("did not pass (session
  ended)") per the August 2026 collection date; if a special session
  revives any 2025-26 bill, the brief's counts would need a refresh.
- Party-blind presentation is deliberate (no roster join); if reviewers
  want party splits on the handful of cited floor votes, the ballot PDFs
  are recorded per roll call (`ballot_pdf_key`) and can be fetched
  on demand.
