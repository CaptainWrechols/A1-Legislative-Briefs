# Agents — Citizen Legislative Reality Brief (v2)

These agents build a **citizen handout**: what was tried, what moved, what stalled, who showed up — so lay people can weigh **political realities** without being told what to do.

Reading target: **about grade 5**.  
Front matter: **1 PDF page of essentials, 2 pages max**.  
Detail: **print-friendly appendices**.

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
| 4 | `design-packager/` | Forum colors/fonts; printable HTML |
| 5 | `citizen-reviewer/` | Reading level, no-advice, ≤2 pages, package gate |

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
5. **Visuals follow Forum brand** (`config/forum-brand.yaml`) or a Phase 2 sample in `templates/phase-2-samples/` when provided.

## Brand / Phase 2 samples

- Tokens: `config/forum-brand.yaml` (from public nvforum.org palette/fonts).
- Drop an official Phase 2 Issue Brief PDF/DOCX into `templates/phase-2-samples/` to force exact visual matching. Design Packager must prefer the sample over YAML when present.

## Outputs (typical)

```
working/{state}/{issue}/
  evidence-pack.json
  reality-map.md
briefs/{state}/{issue}/citizen-v1/
  citizen-brief.md
  citizen-brief.html
  appendices/
  PACKAGE.md
  review-report.md
```
