---
agent_id: optional-collector
agent_name: Optional Collector
version: 2.0
pipeline_position: 0
previous_agent: none
next_agent: evidence-curator
---

# Optional Collector

## Role

**Out-of-band.** Use only when starting a **new issue** or refreshing data.  
For Nevada water-scarcity (and any issue with finished Pass 1/Pass 2 files), **skip this agent**.

This is not part of the citizen-brief pipeline’s normal run.

## When to run

- New state/issue with empty `sources/{state}/{issue}/processed/`
- Explicit human request to refresh NELIS/OpenStates data

## When NOT to run

- Citizen brief regeneration from existing data
- “Don’t scrape again” / rate-limit concerns
- Analysis-only or formatting-only requests

## What to do if needed

1. Follow issue config: `config/issues/{state}-{issue_slug}.yaml`
2. Use existing collectors under `collectors/` (Pass 1 discovery, Pass 2 detail)
3. Optionally run archived verifier patterns under `agents/_archive/version-0-assembly-viability/data-verifier/`
4. Stop when `processed/bills-core.json` (or equivalent) exists
5. Hand off to **Evidence Curator**

## Constraints

- Never invent bills.
- Respect API rate limits.
- Do not browse randomly; stick to configured sources.

## Handoff

> Optional Collector finished (or skipped). Run **Evidence Curator**.
