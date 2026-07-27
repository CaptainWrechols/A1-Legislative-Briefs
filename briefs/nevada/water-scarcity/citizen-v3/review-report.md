# Citizen Reviewer Report — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · **citizen-v4.0** · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.3 on 2026-07-20
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief.docx`, appendices A–I (+ print HTML + docx), `PACKAGE.md`, working analysis files, rendered pages (headless Chrome for HTML; LibreOffice for the Word file)

## Status: READY FOR HUMAN REVIEW

## What changed from v3.0 (per Forum direction, 2026-07-20)

The front brief was rebuilt as an **adult, prose-only working-group
document**:

- Removed: kicker/version subtitle, "How to use this sheet," the
  how-a-bill-moves primer, all tables, "Questions for your group," data
  cautions and process commentary, and the source-keys section.
- The ten constituent proposals are covered in bold-lead prose paragraphs,
  grouped by record status: **no bill on record** (5), **reached the
  Legislature and stalled** (4 groupings), **precedent exists** (2).
- Reviewer-facing material moved to a new **Appendix I — Sources and review
  notes** (claim-to-source mapping, collection notes, review status).
- The Word exporter was rebuilt: Arial 9pt body with compact spacing,
  navy title/H1, terracotta ALL-CAPS H2s, 0.6-inch margins — the docx now
  matches the Phase 2 look and holds 2 pages.

## Checklist results

| ID | Result | Evidence |
|----|--------|----------|
| A1 no advice | PASS | Regex scan clean in md + html; no should/must/recommend/urge. |
| A2 grouped by record status | PASS | Three status sections present. |
| A4 no command language | PASS | Scan clean. |
| A5 all proposals covered | PASS | All ten statements have a bold-lead paragraph (statements 3/6 pieces are covered inside the audit/records and incentive paragraphs). |
| A6 no worksheet apparatus | PASS | Programmatic check: no how-to-use, no primer, no questions, no cautions, no source keys, no version subtitle in the visible document. |
| B1 adult prose | PASS | No inline definitions of session/committee/veto/sponsor; abatement/moratorium/closed-loop used naturally. |
| B3 readable descriptions | PASS | Bill descriptions in plain professional English. |
| C1 ≤2 pages both renders | PASS | HTML: 2 pages (headless Chrome, Letter, 0.6in). **Word: 2 pages** (LibreOffice render of the .docx). |
| C3 detail in appendices | PASS | Appendices A–I; front brief ends with a single pointer line. |
| D1 facts match pack | PASS | All bill dispositions, stages, and vote counts in the prose re-checked against `evidence-pack.json` (34/34 from v3 still hold; no new factual claims added). |
| D2 no invented votes/parties | PASS | Party/vote data from NELIS rosters and roll calls. |
| D3/D4 data limits + inferred yeas | PASS | Stated in Appendix I and Appendix C/F (moved out of the front brief per direction). |
| E1–E4 fairness | PASS | No party blame; people signals descriptive; recent laws reported as fact. |
| F1–F3b package | PASS | HTML + CSS + PACKAGE.md + Word exports present; brief docx verified 2 pages. |
| F4 Phase 2 tokens | PASS | Navy #1A2D4F, terracotta #C0392B, Arial; docx reference doc now carries the same tokens. |
| F5 modules | PASS | Masthead, terracotta H2s, stat strip; no tables in the front brief. |
| F6 no Phase 2 text copied | PASS | Module shapes and tokens only. |
| F7 reviewer material in appendix | PASS | Appendix I. |

## Notes for human reviewers (Ryan Echols, Jodi Stephens, Ashley Lovell)

1. The one remaining non-prose module is the **Key numbers** stat strip
   (five stat cards). The Phase 2 sample uses the same module; flag if you
   want pure prose instead.
2. The closing line ("Full bill-by-bill detail … Appendices A–I") is the
   only pointer retained; it can be dropped if it reads as commentary.
3. Quoted phrases from participants ("keep getting shut down in committee")
   appear twice, attributed to participants — flag if any paraphrase reads
   as endorsement.
