# Collectors

## Pass 1 — discover bills

```bash
python collectors/pass1_bills.py
```

Output: `sources/nevada/water-scarcity/pass1/bills.json`  
(session, identifier, title, short list summary)

## Pass 1b — full abstracts for those bills only

```bash
python collectors/enrich_abstracts.py
```

Uses each bill’s NELIS Overview page and writes the real **digest** into `abstract`. Cached in `pass1/cache_abstracts.json`.
