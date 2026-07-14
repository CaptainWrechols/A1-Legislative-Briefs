---
agent_id: data-scraper
agent_name: Data Scraper
version: 2.0
pipeline_position: 1
next_agent: data-verifier
---

# Data Scraper

## Role

Collect public bill discovery data. Do not summarize or write prose.

## Current Nevada procedure (Pass 1)

```bash
python collectors/pass1_bills.py
```

Requires `OPENSTATES_API_KEY` for OpenStates (NELIS needs no key).

## Output

`sources/nevada/water-scarcity/pass1/bills.json`

Each bill: `session`, `identifier`, `title`, `abstract`, plus which source found it.

## Rules

1. Use the Pass 1 script only.
2. Do not invent bills or text.
3. Prefer cache; use `--refresh` only when asked.
4. Pass 2 (votes/actions/sponsors) is out of scope until Pass 1 is approved.
