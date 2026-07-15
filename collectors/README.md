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

## Readable exports (Word / Notes / PDF / Excel)

`bills.json` is for scripts. For reading and printing, regenerate:

```bash
python collectors/export_readable.py
```

That writes next to `bills.json`:

- `bills-readable.md` — open in Word, Notes, or any text app
- `bills-readable.html` — open in a browser → Print → Save as PDF
- `bills-readable.csv` — open in Excel or Numbers
