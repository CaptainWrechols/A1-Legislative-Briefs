# Citizen Reviewer Report — The Rising Cost of Living in Nevada: Health Care

- **Issue:** `nevada-02-cost-of-living` · **citizen-v1.0** · The Nevada Forum
- **Reviewed by:** citizen-reviewer v2.3 on 2026-07-26
- **Inputs reviewed:** `citizen-brief.md`, `citizen-brief.html`, `citizen-brief.docx`, appendices A–I (+ print HTML + docx), `PACKAGE.md`, working analysis files, rendered pages (headless Chrome for HTML; LibreOffice for the Word file)

## Status: READY FOR HUMAN REVIEW

## Checklist results

| ID | Result | Evidence |
|----|--------|----------|
| A1 no advice | PASS | Word-boundary regex scan clean in md + html; no should/must/recommend/urge/pursue/avoid as commands. |
| A2 grouped by record status | PASS | Three status sections present: no bill on record (2) / reached the Legislature and stalled (3) / precedent exists (5). |
| A4 no command language | PASS | Scan clean. |
| A5 all proposals covered | PASS | All ten Phase 2 healthcare-cost statements have a bold-lead paragraph; probe strings verified programmatically in md and html. |
| A6 no worksheet apparatus | PASS | Programmatic check: no how-to-use, no primer, no discussion questions, no cautions, no source keys, no version/kicker subtitle in the visible document. |
| B1 adult prose | PASS | No inline definitions of session/committee/veto/sponsor; prior authorization, PBM, compact, step therapy, 340B used naturally (see `working/.../explainer-log.md`). |
| B2 no glossary | PASS | None present. |
| B3 readable descriptions | PASS | Bill descriptions in plain professional English. |
| C1 ≤2 pages both renders | PASS | HTML: **2 pages** (headless Chrome, Letter, 0.6in margins). Word: **2 pages** (LibreOffice render of the .docx). |
| C2 page 1 carries the map | PASS | Landscape, stat strip, both never-filed proposals, and all three stalled proposals begin on page 1. |
| C3 detail in appendices | PASS | Appendices A–I; front brief ends with a single pointer line. |
| D1 facts match pack | PASS | Every disposition, stage, vote count, sponsor count, and session statistic verified programmatically against `evidence-pack.json` / processed vote data (`working/nevada/cost-of-living/fact-check-reality-map.py` — all claims verified). Hand spot-checks: SB34 (2025) referred to Senate Commerce and Labor and died under Joint Standing Rule 14.3.1; AB463's digest covers Medicaid, CHIP, and prior authorization; SB366 (2019) creates dental-therapy licensure; SB481 (2019) regulates association plans and multiple-employer arrangements; SB420 (2021) is the Public Option. SB434↔special-session SB5 linkage confirmed textually (both digests name the Statewide Health Care Access and Recruitment Grant Program; SB434's history records "Assembly Amendment No. 972 not concurred in"). |
| D2 no invented votes/parties | PASS | All vote counts from NELIS roll calls; parties from official rosters and NELIS legislator pages; the two special-session bills cite the manual verification file. |
| D3 data limits stated | PASS | Appendix F + Appendix I (kept out of the front brief per v2.3). |
| D4 inferred committee Yeas marked | PASS | Marked in Appendix C intro and source data. |
| E1 no should/must/recommend/urge | PASS | Scan clean. |
| E2 no party blame without cited votes | PASS | Party facts limited to sponsor counts and roster labels; the veto pattern is described by bill outcomes, not party language. |
| E3 people signals descriptive | PASS | Sponsor counts and topics only; no scorecards. |
| E4 recently-passed list neutral | PASS | "New law from the 2025 session" reports outcomes; the reality map (internal) flags saturation as questions. |
| F1 HTML + print CSS exist | PASS | `citizen-brief.html`, `citizen-brief-print.css`. |
| F2 appendices A–F exist | PASS | A–I all present. |
| F3 PACKAGE.md exists | PASS | Present with print + Word instructions. |
| F3b Word exports exist | PASS | `citizen-brief.docx` (2 pages verified, direct-formatting writer) + `appendices/appendices.docx`. |
| F7 reviewer material in appendix | PASS | Claim-to-source map and collection notes in Appendix I only. |
| F4 Phase 2 tokens | PASS | White page, navy `#1A2D4F`, terracotta `#C0392B`, Arial body; no website purple/gold/cream (scan clean). |
| F5 Phase 2 modules | PASS | Masthead, terracotta ALL-CAPS section headers, stat strip; no tables in the front brief (scan clean). |
| F6 no Phase 2 sample text copied | PASS | Module shapes and tokens only; sample headings/kicker absent. |

## Small fixes made in-pass

1. Appendix H status slugs replaced with plain labels ("Tried repeatedly;
   stalled late," etc.) — the appendix builder passes through the reality
   map's machine slugs.
2. Generated appendix intros (A, F path, H, README) corrected from the
   water-template wording to this issue's counts and topic; all table
   numbers are untouched pipeline output. Documented in Appendix I.
3. Front-brief status line updated DRAFT → READY FOR HUMAN REVIEW after all
   checks passed.

## Notes for human reviewers (Ryan Echols, Jodi Stephens, Ashley Lovell)

1. **The SB434 → special-session SB5 story** (shortage grant program passed
   18–2 and 42–0, died on concurrence, enacted three months later 15–6 and
   37–0) rests on the manual special-sessions verification file plus the
   textual match of the program name in both digests. Both sources are in
   the repo; flag if you want the wording hedged further.
2. **The physician-compact sentence** ("in Nevada statute since before this
   record") is sourced to SB34's own digest, which places the PA compact
   "in the same chapter as the Interstate Medical Licensure Compact." The
   IMLC's adoption date itself is outside the 2019–2025 window and is not
   claimed.
3. **AB290's death** is described as "cleared its first committee, was
   re-referred, and died at session's end" — the participants' memory
   ("died in committee") is close but not exact, and the brief follows the
   official history.
4. **The 31st (2020) Special Session AB3 sentence** says the bill cut DHHS
   appropriations (which its title and digest state); it does not repeat
   participants' more specific rate-cut recollections, which the collected
   text does not verify.
5. Quoted participant phrases appear only in working files and the issue
   config, not in the front brief.
