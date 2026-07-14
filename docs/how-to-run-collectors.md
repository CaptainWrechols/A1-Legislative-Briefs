# How to Run Collectors

Two passes. **Only Pass 1 runs now.**

## Pass 1 — bills, titles, abstracts

One script. Disk cache. No PDFs, votes, actions, or sponsors.

```bash
pip install -r requirements.txt
export OPENSTATES_API_KEY=your-key-here   # optional but recommended
python collectors/pass1_bills.py
```

Re-run safely (keeps cache, only fills gaps):

```bash
python collectors/pass1_bills.py
```

Force a full redo:

```bash
python collectors/pass1_bills.py --refresh
```

### Output

```
sources/nevada/water-scarcity/pass1/
  cache_nelis.json         # raw NELIS hits (cached)
  cache_openstates.json    # raw OpenStates hits (cached)
  bills.json               # water-filtered merge for review
```

Each bill in `bills.json` has: `session`, `identifier`, `title`, `abstract`, plus which source(s) found it.

### GitHub Actions

Actions → **Collect Nevada Water Bills** → Run workflow.  
Leave `refresh=false` unless you intentionally want to rebuild the cache.

## Pass 2 — later (not wired yet)

After Pass 1 looks right locally, enrich with:

- sponsors / cosponsors (+ party)
- action history
- votes (who/how)
- enactment / signature

Older scripts under `collectors/` (`nv_nelis_bill_details.py`, `openstates_bills.py`, PDF/verify helpers) are **paused**. Do not run them for day-to-day collection.
