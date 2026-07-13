# Agents — Legislative Brief Version 0 Pipeline

This folder contains ten agent instruction files for The Forum's Legislative Brief system.
Each agent lives in its own subfolder with a single file: `AGENT.md`.

## Pipeline order (run in this sequence)

```
Data Scraper
  → Data Verifier
  → Synthesizer
  → Analyzer
  → Data Formatter
  → Brief Writer
  → Editor
  → Tone Editor
  → General Formatter
  → Final Reviewer
  → Human Pull Request review
```

## Agent folders

| Order | Folder | Purpose |
|-------|--------|---------|
| 1 | `data-scraper/` | Collect public legislative and policy data |
| 2 | `data-verifier/` | Verify links and fact-check collected data |
| 3 | `synthesizer/` | Merge verified sources into one fact base |
| 4 | `analyzer/` | Identify legislative patterns and viability indicators |
| 5 | `data-formatter/` | Build appendix tables in Markdown |
| 6 | `brief-writer/` | Write the 1–3 page executive summary |
| 7 | `editor/` | Edit for accuracy, citations, and clarity |
| 8 | `tone-editor/` | Apply The Forum nonpartisan voice |
| 9 | `general-formatter/` | Consistent Markdown packaging |
| 10 | `final-reviewer/` | Automated checklist before human review |

## How to run an agent in Cursor

1. Open the repository in Cursor.
2. Start a new agent chat (or use this Cloud Agent).
3. Paste a message like this (replace parameters):

```
Read and follow agents/brief-writer/AGENT.md exactly.

Parameters:
- STATE=nevada
- ISSUE_SLUG=water-scarcity
- ISSUE_ID=nevada-04-water-scarcity
- ISSUE_TITLE=Growth, Water Scarcity, and Long-Term Supply in Nevada
- CONFIG_PATH=config/issues/nevada-water-scarcity.yaml
- SOURCES_DIR=sources/nevada/water-scarcity
- WORKING_DIR=working/nevada/water-scarcity
- BRIEF_DIR=briefs/nevada/water-scarcity/version-0
- SESSIONS=2019, 2021, 2023, 2025
- JURISDICTION=nevada
- BRIEF_VERSION=version-0
- IMPACT_LOOKBACK_YEARS=20
- REVIEWERS=Ryan Echols, Jodi Stephens, Ashley Lovell

Use only files that exist in this repository. Do not browse the web unless the agent file explicitly allows it.
```

4. Run agents in pipeline order. Do not skip Data Verifier.

## Parameters reference

| Parameter | Example | Used by |
|-----------|---------|---------|
| `STATE` | `nevada` | All agents |
| `ISSUE_SLUG` | `water-scarcity` | All agents |
| `ISSUE_ID` | `nevada-04-water-scarcity` | All agents |
| `ISSUE_TITLE` | Full issue title string | Writer, Formatter, Reviewer |
| `CONFIG_PATH` | `config/issues/nevada-water-scarcity.yaml` | Scraper, Analyzer |
| `SOURCES_DIR` | `sources/nevada/water-scarcity` | Most agents |
| `WORKING_DIR` | `working/nevada/water-scarcity` | Synthesizer through Reviewer |
| `BRIEF_DIR` | `briefs/nevada/water-scarcity/version-0` | Formatter through Reviewer |
| `SESSIONS` | `2019, 2021, 2023, 2025` | Scraper, Analyzer |
| `JURISDICTION` | `nevada` | Scraper |
| `OPENSTATES_API_KEY` | Environment variable only | Scraper (never commit) |

## Repository layout

```
config/issues/          Issue search recipes (YAML)
collectors/             Python scripts that download data
sources/{state}/{issue}/ Raw and processed data files
working/{state}/{issue}/ Synthesis and analysis working files
briefs/{state}/{issue}/version-0/  Executive summary and appendices
agents/                 This folder — agent instructions
docs/                   Human runbooks and checklists
.github/workflows/      GitHub Actions (manual trigger)
```

## Pilot issue

**Nevada — Water Scarcity and Long-Term Supply** (`nevada-04-water-scarcity`)

## Secrets (you must add manually)

In GitHub: **Settings → Secrets and variables → Actions → New repository secret**

- Name: `OPENSTATES_API_KEY`
- Value: your key from https://openstates.org/accounts/profile/

The Cloud Agent cannot add secrets for you.
