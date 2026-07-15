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
