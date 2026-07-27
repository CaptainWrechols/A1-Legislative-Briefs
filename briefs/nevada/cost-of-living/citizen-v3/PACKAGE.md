# Package — The Rising Cost of Living in Nevada: Health Care (citizen-v3.0)

Design Packager v2.3 · 2026-07-27 · The Nevada Forum

citizen-v3.0 is the formatting-polish pass over citizen-v2.0, produced per
Forum direction (2026-07-27). `citizen-v1/` and `citizen-v2/` are untouched;
compare the folders side by side. Facts, bills, and votes are unchanged
throughout — v2.0 changed presentation, organization, and voice; v3.0
changes formatting, type sizes, and layout only.

## What changed from v2.0 (v3.0 polish + readable type)

v3.0 keeps v2.0's facts, bills, votes, and viability-first organization, with
formatting and readability edits per Forum direction (2026-07-27):

- **Readable type.** No text renders below 10pt: body, explainers, stat
  captions, dek, masthead, and footline are 10pt; section headers are 12.5pt
  ALL-CAPS terracotta, subsection headers 12pt navy, and the title 18pt.
- **Single-line headers.** Every title and section header holds one line in
  both the HTML and Word renders; the nuance lives in the explainer line
  under each header.
- **No widow lines.** No paragraph, dek, or explainer ends with fewer than
  three words (non-breaking-space gluing plus `text-wrap: pretty`); title,
  dek, explainers, and stat captions use balanced wrapping.
- **Tighter structure to hold 2 pages at the larger type.** The stat strip
  now sits directly under the opening section (no separate "Key numbers"
  header), and the former "Sponsors, committees, and who still serves"
  section was folded into the Momentum map as a "Chokepoints and carriers"
  paragraph — keeping every viability-relevant fact (committee chokepoints,
  cross-party success rates, and which sponsors still serve) and dropping
  only viability-neutral tallies (e.g. how many bills were person- vs
  committee-sponsored). Prose was tightened throughout without removing any
  bill, vote, or outcome.
- Both renders re-verified at exactly **2 US Letter pages**.

## What changed from v1.0 (introduced in v2.0, retained here)

- **Sections reordered by viability.** Proposals now appear in order of how
  far their bills traveled: passed both chambers (vetoed or timed out) first,
  then cleared-one-chamber/cleared-committee, then enacted law and the
  openings around it, then never-filed/never-heard/stopped-early routes.
- **Specific section headers with explainers.** Every H2 states what the
  section holds; an italic explainer line under each header says why the
  content is there and what it informs. H3 subheaders split the veto/clock
  and settled/openings material.
- **Positive, opportunity-forward tone.** Bare pass-rate and veto-rate
  statistics were removed or re-anchored to named bills; near-misses are
  framed as the record's most advanced unfinished work without dropping any
  fact about what has failed.
- **Momentum map.** A section states where bills keep appearing and
  advancing, and where the Legislature has shown little or no willingness
  to legislate.
- **Recently passed law analyzed both ways.** New statutes are flagged as
  ground too similar for near-term retreads, and as the lanes where the
  record shows appetite to go further.
- **Federal overlap.** A section notes where current or planned federal
  action already covers a proposal (redundancy risk) and where no federal
  role exists.
- **Current-membership notes.** Every named legislator is marked as still
  serving or departed, per the NELIS 83rd (2025) Session roster in
  `sources/nevada/*/pass2/legislator_roster.json`.
- **Key numbers rebuilt.** Stat cards now carry viability-anchored figures
  tied to named bills instead of bare rate statistics.

## What's in this folder

| File | What it is |
|---|---|
| `citizen-brief.md` | Source markdown of the 2-page front brief (v3.0) |
| `citizen-brief.html` | Print-ready front brief (verified 2 US Letter pages in headless Chrome) |
| `citizen-brief.docx` | Word version of the front brief (verified 2 pages in LibreOffice) |
| `citizen-brief-print.css` | Shared Phase 2 print CSS + v2 `h3.subsec` subsection style (v3 widow/balance rules live in the HTML head) |
| `appendices/` | Appendices A–I (markdown), `appendices-print.html`, `appendices.docx` — unchanged from v1.0 |
| `review-report.md` / `.json` | Citizen Reviewer output for the **v1.0** content (v2.0 revision not yet re-reviewed) |

## Rebuild the outputs

```bash
# HTML (Phase 2 shell; masthead, terracotta H2s, stat strip, subsection H3s)
python collectors/export_brief_html.py --brief-dir briefs/nevada/cost-of-living/citizen-v3

# Word (front brief via python-docx direct formatting; appendices via pandoc)
ISSUE_CONFIG=config/issues/nevada-cost-of-living.yaml \
python collectors/export_docx.py --brief-dir briefs/nevada/cost-of-living/citizen-v3
```

## Print to PDF

1. Open `citizen-brief.html` in Chrome or Edge.
2. Print → Destination: *Save as PDF* → Paper: **Letter** → Margins: **Default** → **Background graphics: on** → no headers/footers.
3. Result should be exactly **2 pages** (verified with headless Chrome at 0.6in margins).
4. Repeat with `appendices/appendices-print.html` for the long appendix PDF.

**If you need Word and cannot run the script:** open `citizen-brief.html` in
Microsoft Word and Save As `.docx`, or upload `citizen-brief.md` to Google
Docs and download as Word.

## Design notes

Visual tokens follow `config/forum-brand.yaml`, extracted from the Phase 2
Issue Brief sample (`templates/phase-2-samples/`): white page, navy `#1A2D4F`
masthead/title/stat numbers, terracotta `#C0392B` ALL-CAPS section headers,
secondary navy `#2E4A78` H3 subheaders, Arial body. v2.0 body sits at 8.5pt
(HTML) / 8.5pt (Word) with compact spacing so the added sections (momentum
map, federal overlap, membership notes) still hold the 2-page budget. The
section explainers reuse the brand's muted-gray inline-explainer style with
a thin terracotta left border. No Phase 2 sample text was copied.
