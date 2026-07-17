# A1-Legislative-Briefs

Agent and data sets for The Forum's 12 Legislative Briefs.

## What this repository does

This project builds **citizen legislative reality briefs** for The Nevada Forum (and sister state programs). The handout helps everyday people see what lawmakers tried on an issue, what moved, what stalled, and who showed up — **without telling them what to pursue**.

Typical packet:

- A **1–2 page** plain-language front brief (~5th-grade reading level, inline explainers)
- **Print-friendly appendices** (bills, themes, votes, sponsors)
- Phase 2 Issue Brief visual system (tokens in `config/forum-brand.yaml`, extracted from the sample in `templates/phase-2-samples/`)

Collectors still gather public bill data (Pass 1 / Pass 2). The **v2 agent pipeline** starts from that data.

## Pilot issue

**Nevada — Growth, Water Scarcity, and Long-Term Supply** (`nevada-04-water-scarcity`)

## Quick start

```bash
pip install -r requirements.txt
# Only if you need new collection:
export OPENSTATES_API_KEY=your-key-here
python collectors/pass1_bills.py
```

When data already exists under `sources/nevada/water-scarcity/processed/`, skip collection and run the **citizen brief agents** (see `agents/README.md`).

## Repository structure

```
agents/                 Citizen-brief agent instructions (v2) + archived v0
config/                 Issue recipes + Forum brand tokens
collectors/             Python data collection scripts
sources/                Raw and processed public data
working/                Evidence pack + reality map working files
briefs/                 Citizen packets (+ legacy version-0 staff briefs)
templates/              Brief shells + Phase 2 visual sample drop folder
docs/                   Human runbooks and checklists
.github/workflows/      GitHub Actions (manual trigger)
```

## Secrets required

| Secret name | Where to get it |
|-------------|-----------------|
| `OPENSTATES_API_KEY` | https://openstates.org/accounts/profile/ |

Add in GitHub: **Settings → Secrets and variables → Actions**

## Brief types

| Type | Purpose | Location |
|------|---------|----------|
| Citizen legislative reality brief (v2) | Lay handout: what was tried / moved / stalled / who showed up | `briefs/{state}/{issue}/citizen-v1/` |
| Phase 2 Issue Brief | Deliberation conversation guide (external; also our visual-system sample) | `briefs/phase-2/` or `templates/phase-2-samples/` |
| Legacy Version 0 staff brief | Internal assembly-viability memo | `briefs/{state}/{issue}/version-0/` |

## License and attribution

The Forum — nonpartisan citizen deliberation program.
Process note: Briefs use artificial-intelligence-assisted research plus human review.
