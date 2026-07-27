# Citizen Reviewer report — K-12 Educational Outcomes in Nevada (citizen-v1.0)

- **Reviewer:** citizen-reviewer v2.3 · 2026-07-25
- **Status:** **READY FOR HUMAN REVIEW**
- **Scope:** `citizen-brief.md` / `.html` / `.docx`, appendices A–I, reality map

## Checklist result

| Area | Result |
|---|---|
| A. Purpose fit (A1, A2, A4, A5, A6) | **Pass.** The brief reports the record without telling readers what to pick; proposals are grouped by record status (no bill on record / reached and stalled / precedent exists); all ten config proposals carry a bold-lead paragraph; automated advice-language and banned-section scans returned zero hits (no how-to-use, discussion questions, primers, cautions, meta-commentary, or source keys). |
| B. Reading level & explainers | **Pass.** Adult professional prose, no glossary, no definitions of common civic terms; see `working/nevada/k-12_educational_outcomes/explainer-log.md`. |
| C. Length & layout | **Pass.** Headless Chrome renders `citizen-brief.html` at exactly 2 US Letter pages; LibreOffice renders `citizen-brief.docx` at exactly 2 pages (page images in `render-check/`). Page 1 carries the landscape, stat strip, the never-filed proposal, and the stalled proposals. |
| D. Evidence integrity | **Pass.** Every bill key in the brief and reality map exists in the evidence pack; 100+ disposition/stage/vote claims were verified programmatically (`fact-check-reality-map.py`, all claims verified); data limits stated in Appendix F; inferred committee Yeas marked `*` and explained in Appendix C. |
| E. Forum fairness | **Pass.** No should/must/recommend directed at readers or the Legislature; party mentions are sponsor facts or roll-call counts; people signals descriptive; the 2025 enactment list is neutral record. |
| F. Package completeness | **Pass.** HTML + print CSS, appendices A–I, `PACKAGE.md`, Word exports (front brief direct-formatted, 2 pages), reviewer material confined to Appendix I, Phase 2 tokens and modules used, no Phase 2 sample text copied. |

## Fact spot-checks (sample)

1. AB517 (2023) legislative audits — enacted 42–0 and 21–0. Verified.
2. AB53 (2025) recess mandate — died in Assembly Education without a vote. Verified.
3. AB386 (2025) — passed 40–0 and 21–0; history ends "No further action taken"; not signed, not vetoed. Verified.
4. AB265 (2023) — passed 42–0 and 20–0, vetoed. Verified.
5. 13 policy vetoes: 8 in 2023, 5 in 2025. Verified.
6. 31st (2020) Special Session AB3 — struck the $31,429,229 FY 2021 Read by Grade 3 transfer; verified from the enrolled bill text recorded in the verification file.
7. 193 first-committee deaths (127 Education, 40 money committees, 12 Government Affairs). Verified.
8. 55 cross-party policy bills, 28 enacted. Verified.

## Small fixes made in-pass (logged)

- Reworded two descriptive phrasings that pattern-matched the advice scan ("districts must adopt" → "districts are required to adopt"; the funding commission "recommends the gap" → "charged with calculating what full funding would take").
- Removed an uncollected characterization ("52-year-old" Nevada Plan) in favor of neutral wording.
- Normalized plain-topic tense to disposition across the curation map (178 topics) so failed bills never read as enacted fact.
- Corrected issue-title strings stamped by the shared assemblers from the water run (evidence-pack `discovery_note`/`data_limits`; intros of Appendices A, F, H and the appendices README; `appendices-print.html` title/kicker/footline). Documented in Appendix I; all counts are untouched pipeline output.

## Items flagged for human judgment

- Sponsor counts merge NELIS name variants for the same person (Torres/Torres-Fossett; Buck/Carrie Ann Buck; 2025 "Assemblymember" titles). Merges listed in `reality-map.json` and Appendix I.
- Two adopted concurrent resolutions read Unknown and 2025 AJR9 reads In Progress (NELIS records no final action for resolutions); excluded from pass-rate claims.
- The growth-assessment card rests on three failed bills (SB351, SB313, SB314) — certainty medium.
- The first AB517 performance audits are due August 2026; worth revisiting when published.

> Citizen Reviewer finished. Open a Pull Request for human review: Ryan Echols, Jodi Stephens, Ashley Lovell.
