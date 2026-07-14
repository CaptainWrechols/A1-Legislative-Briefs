# A1-Legislative-Briefs

Agent and data sets for The Forum's 12 Legislative Briefs.

## What this repository does

This project generates **Legislative Brief Version 0** documents for The Forum's three state programs (Nevada, New Hampshire, South Carolina). Each brief includes:

- A **1–3 page executive summary** covering legislative history across the last four sessions and enacted policy impact
- **Data appendices** in plain Markdown tables for independent review
- Full **source citation** and version control via GitHub

## Pilot issue

**Nevada — Growth, Water Scarcity, and Long-Term Supply** (`nevada-04-water-scarcity`)

## Quick start

1. Read `docs/how-to-run-collectors.md`
2. Run Pass 1: `python collectors/pass1_bills.py` (needs `OPENSTATES_API_KEY` for OpenStates)
3. Review `sources/nevada/water-scarcity/pass1/bills.json`
4. Pass 2 (votes/actions/sponsors) comes after Pass 1 is solid — not enabled yet
5. See `agents/README.md` for the ten-agent pipeline after data is ready


## Repository structure

```
agents/                 Ten agent instruction files (AGENT.md per folder)
config/issues/          Issue search recipes (YAML)
collectors/             Python data collection scripts
sources/                Raw and processed public data
working/                Synthesis and analysis working files
briefs/                 Executive summaries and appendices
docs/                   Human runbooks and checklists
.github/workflows/      GitHub Actions (manual trigger)
```

## Secrets required

| Secret name | Where to get it |
|-------------|-----------------|
| `OPENSTATES_API_KEY` | https://openstates.org/accounts/profile/ |

Add in GitHub: **Settings → Secrets and variables → Actions**

## Two brief types

| Type | Purpose | Location |
|------|---------|----------|
| Phase 2 Issue Brief | Deliberation conversation guide | `briefs/phase-2/` |
| Legislative Brief Version 0 | Assembly viability / legislative history | `briefs/{state}/{issue}/version-0/` |

## License and attribution

The Forum — nonpartisan citizen deliberation program.
Process note: Briefs use artificial-intelligence-assisted research plus human review.
