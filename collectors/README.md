# Collectors

## Pass 1 — discover bills

```bash
python collectors/pass1_bills.py
```

Output: `sources/nevada/water-scarcity/pass1/bills.json`  
(session, identifier, title, abstract). Keeps **all** NELIS search hits; `passes_water_title_filter` is only a review flag.

## Pass 1b — full abstracts for those bills only

```bash
python collectors/enrich_abstracts.py
```

Uses each bill’s NELIS Overview page and writes the real **digest** into `abstract`. Cached in `pass1/cache_abstracts.json`.

## Pass 2 — votes, actions, progress (known bills only)

Only enriches bills already listed in `pass1/bills.json` (no new discovery).

```bash
python collectors/pass2_bills.py
python collectors/pass2_bills.py --limit 5          # smoke test
python collectors/pass2_bills.py --skip-openstates  # NELIS only
```

Outputs under `sources/nevada/water-scarcity/processed/`:

- `bill-legislative-progress.json` — committee/floor/crossover/enactment yes/no milestones
- `bill-votes.json` — each vote with yea/nay voters; party when OpenStates matches
- `bill-actions.json`, `bill-sponsors.json`, `data-gaps.json`

Caches: `pass2/cache_nelis_pass2.json`, `pass2/cache_openstates_pass2.json`

Set `OPENSTATES_API_KEY` for voter party enrichment (recommended).
