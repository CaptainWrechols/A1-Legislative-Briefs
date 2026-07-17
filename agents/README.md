# Agents — Citizen Legislative Reality Brief (v2)

These agents build a **citizen handout**: what was tried, what moved, what stalled, who showed up — so lay people can weigh **political realities** without being told what to do.

The primary readers are **citizen working groups sharpening specific
proposals** (the `constituent_proposals` block in the issue config). Page 1
of the front brief checks each proposal against the legislative record.

Reading target: **about grade 8**.  
Front matter: **1 PDF page of essentials, 2 pages max**.  
Detail: **print-friendly appendices** + **Word (.docx) exports**.

## Pipeline (normal run — data already collected)

```
Evidence Curator
  → Reality Mapper
  → Citizen Brief Writer  ┐
  → Appendix Builder      ┘ (can run in parallel after Reality Mapper)
  → Design Packager
  → Citizen Reviewer
  → Human PR review
```

**Skip Optional Collector** when `sources/{state}/{issue}/processed/` already has core files.

## Agent map

| Order | Folder | Purpose |
|------:|--------|---------|
| 0 (rare) | `optional-collector/` | New issue / refresh scrapes only |
| 1 | `evidence-curator/` | Pack existing bills, votes, sponsors into themes |
| 2 | `reality-mapper/` | History baskets: often moved / unfinished / rarely moved |
| 3 | `citizen-brief-writer/` | 1–2 page plain-language front brief + inline explainers |
| 3b | `appendix-builder/` | Long PDF/Word-friendly appendices |
| 4 | `design-packager/` | Phase 2 visual system (navy/terracotta/white, Arial); printable HTML |
| 5 | `citizen-reviewer/` | Reading level, no-advice, ≤2 pages, Phase 2 modules, package gate |

Archived staff-only Version 0 agents live in `_archive/version-0-assembly-viability/`.

## How to run in Cursor

Paste (edit paths as needed):

```
Read and follow agents/evidence-curator/AGENT.md exactly.

Parameters:
- STATE=nevada
- ISSUE_SLUG=water-scarcity
- ISSUE_ID=nevada-04-water-scarcity
- ISSUE_TITLE=Growth, Water Scarcity, and Long-Term Supply in Nevada
- SOURCES_DIR=sources/nevada/water-scarcity
- WORKING_DIR=working/nevada/water-scarcity
- BRIEF_DIR=briefs/nevada/water-scarcity/citizen-v1
- SESSIONS=2019, 2021, 2023, 2025
- BRAND_CONFIG=config/forum-brand.yaml
- REVIEWERS=Ryan Echols, Jodi Stephens, Ashley Lovell

Use only existing files in this repository. Do not scrape or search for new bills.
```

Then continue in order: Reality Mapper → (Citizen Brief Writer + Appendix Builder) → Design Packager → Citizen Reviewer.

## Product rules (all agents)

1. **No advice:** never tell citizens or lawmakers what they should pass.
2. **History baskets, not commands:** “Often moved before” / “Got support but didn’t finish” / “Rarely moved before.”
3. **Inline explainers** for hard words — in the section, not a glossary appendix.
4. **Front brief stays short;** appendices hold depth.
5. **Visuals follow the Phase 2 Issue Brief system**: white page, navy `#1A2D4F`, terracotta `#C0392B` section headers, Arial body, modular cards/tables. Tokens live in `config/forum-brand.yaml`; the authoritative sample is `templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`. Mirror its colors/fonts/spacing/modules — never its headings or text.

## Brand / Phase 2 sample

- Tokens: `config/forum-brand.yaml` — extracted from the Phase 2 sample PDF (this replaced the old website purple/cream palette).
- Sample: `templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`. Design Packager mirrors its module types (eyebrow header, terracotta H2s, quote-style history cards, navy-bar stat strip, navy-header tables, numbered question grid).

## Outputs (typical)

```
working/{state}/{issue}/
  evidence-pack.json
  reality-map.md
briefs/{state}/{issue}/citizen-v1/
  citizen-brief.md
  citizen-brief.html
  citizen-brief.docx
  appendices/           (incl. appendices.docx)
  PACKAGE.md
  review-report.md
```

Word export: `python collectors/export_docx.py --brief-dir briefs/{state}/{issue}/citizen-v1`
(requires pandoc; manual fallback steps are written into each PACKAGE.md).
