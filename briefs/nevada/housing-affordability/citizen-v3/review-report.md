# Citizen Reviewer Report — Housing Affordability in Nevada

- **Issue:** `nevada-01-housing-affordability` · **citizen-v1.0** · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.3 on 2026-07-24
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief.docx`, appendices A–I (+ print HTML + docx), `PACKAGE.md`, working analysis files, rendered pages (headless Chrome for HTML; LibreOffice for the Word file)

## Status: READY FOR HUMAN REVIEW

## Checklist results

| ID | Result | Evidence |
|----|--------|----------|
| A1 no advice | PASS | Word-boundary regex scan clean in md + html; no should/must/recommend/urge/pursue/avoid as commands. |
| A2 grouped by record status | PASS | Three status sections present: no bill on record (2) / reached the Legislature and stalled (5) / precedent exists (3). |
| A4 no command language | PASS | Scan clean. |
| A5 all proposals covered | PASS | All ten Phase 2 housing statements have a bold-lead paragraph; probe strings verified programmatically. |
| A6 no worksheet apparatus | PASS | Programmatic check: no how-to-use, no primer, no discussion questions, no cautions, no source keys, no version/kicker subtitle in the visible document. |
| B1 adult prose | PASS | No inline definitions of session/committee/veto/sponsor; inclusionary, linkage fee, by right, ADU used naturally (see `working/.../explainer-log.md`). |
| B2 no glossary | PASS | None present. |
| B3 readable descriptions | PASS | Bill descriptions in plain professional English. |
| C1 ≤2 pages both renders | PASS | HTML: **2 pages** (headless Chrome, Letter, 0.6in margins). Word: **2 pages** (LibreOffice render of the .docx). |
| C2 page 1 carries the map | PASS | Landscape, stat strip, both never-filed proposals, and three of five stalled proposals on page 1. |
| C3 detail in appendices | PASS | Appendices A–I; front brief ends with a single pointer line. |
| D1 facts match pack | PASS | Every disposition, stage, vote count, sponsor count, and session statistic in the prose verified programmatically against `evidence-pack.json` / processed vote data (`working/nevada/housing-affordability/fact-check-reality-map.py` — all claims verified). Spot-checks by hand: SB151 (2019) §7.2 is the 5% late-fee cap; SB99 (2025) history ends at delivery to the Governor with no signature; special-session SB10 "REQUIRES TWO-THIRDS MAJORITY VOTE" is printed on the bill face. |
| D2 no invented votes/parties | PASS | All vote counts from NELIS roll calls; parties from official rosters; the two special-session bills cite the manual verification file. |
| D3 data limits stated | PASS | Appendix F + Appendix I (moved out of the front brief per v2.3). |
| D4 inferred committee Yeas marked | PASS | Marked in Appendix C intro and source data. |
| E1 no should/must/recommend/urge | PASS | Scan clean. |
| E2 no party blame without cited votes | PASS | Party facts limited to sponsor counts and roster labels; veto pattern described by bill outcomes, not party language. |
| E3 people signals descriptive | PASS | Sponsor counts and topics only; no scorecards. |
| E4 recently-passed list neutral | PASS | "New law from the 2025 session" reports outcomes; the reality map (internal) flags saturation as questions. |
| F1 HTML + print CSS exist | PASS | `citizen-brief.html`, `citizen-brief-print.css`. |
| F2 appendices A–F exist | PASS | A–I all present. |
| F3 PACKAGE.md exists | PASS | Present with print + Word instructions. |
| F3b Word exports exist | PASS | `citizen-brief.docx` (2 pages verified) + `appendices/appendices.docx`. |
| F7 reviewer material in appendix | PASS | Claim-to-source map and collection notes in Appendix I only. |
| F4 Phase 2 tokens | PASS | White page, navy `#1A2D4F`, terracotta `#C0392B`, Arial body; no website purple/gold/cream. |
| F5 Phase 2 modules | PASS | Masthead, terracotta ALL-CAPS section headers, stat strip; no tables in the front brief. |
| F6 no Phase 2 sample text copied | PASS | Module shapes and tokens only; sample headings/kicker absent. |

## Small fixes made in-pass

1. Appendix H status slugs replaced with plain labels ("Tried; stopped at the
   finish line," etc.) — the appendix builder's label map predates this
   issue's statuses.
2. Generated appendix intros (A, H, README, F path) corrected from the water
   template wording to this issue's counts and topic; all table numbers are
   untouched pipeline output.
3. Front-brief status line updated DRAFT → READY FOR HUMAN REVIEW after all
   checks passed.

## Notes for human reviewers (Ryan Echols, Jodi Stephens, Ashley Lovell)

1. **SB99's ending is stated in record language** ("delivered to the
   governor … the official history ends there — no signature, no chapter,
   not law"). NELIS shows no veto action; we did not infer a veto or a
   pocket outcome. Flag if you want the wording tightened further.
2. **The special-session SB10 facts** (18–0 Senate; 27–10 recorded Lost;
   two-thirds requirement) come from a hand-collected verification file
   (`sources/nevada/housing-affordability/verification/special-sessions.json`)
   because the shared pipeline covers only regular sessions. The two-thirds
   requirement is printed on the bill's face.
3. The one remaining non-prose module is the **Key numbers** stat strip
   (five cards), matching the Phase 2 sample's module.
4. Quoted participant phrases ("will get shut down quickly," "nobody has
   done anything legislatively") appear once each, attributed to
   participants — flag if any paraphrase reads as endorsement.
