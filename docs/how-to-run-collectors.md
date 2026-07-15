# Collect Nevada water bills

## Pass 1 — list bills

```bash
pip install -r requirements.txt
export OPENSTATES_API_KEY=your-key-here
python collectors/pass1_bills.py
```

Output: `sources/nevada/water-scarcity/pass1/bills.json`

All NELIS search hits are kept (high recall for human review).  
`passes_water_title_filter` marks bills whose title looks strongly water-related; bills with `false` stay in the list so nothing is silently dropped.

## Pass 1b — full abstracts (those bills only)

After Pass 1 looks right:

```bash
python collectors/enrich_abstracts.py
```

This visits each bill’s NELIS Overview page and replaces `abstract` with the full digest (not the short search-list title). Re-runs are cached.

## GitHub Actions

Actions → **Collect Nevada Water Bills** runs Pass 1, then abstract enrichment.
