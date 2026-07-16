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
- `bill-votes.json` — each vote with yea/nay voters and party
- `bill-actions.json`, `bill-sponsors.json`, `data-gaps.json`

### Party affiliation (no OpenStates)

```bash
python collectors/pass2_party_roster.py   # scrape NELIS legislator directories (+ Ballotpedia fallback)
python collectors/pass2_attach_party.py   # write party onto each ballot in bill-votes.json
```

### Introduced vs enrolled text (Governor-bound only)

```bash
python collectors/pass2_text_diff.py
python collectors/pass2_build_core.py
```

Compares **As Introduced** vs **As Enrolled** PDFs for bills that went to the Governor.
Writes `processed/bill-text-changes.json` and merges abstracts + progress into
`processed/bills-core.json`.

### Sponsors / co-sponsors

```bash
python collectors/pass2_sponsors.py
```

Writes `processed/bill-sponsors.json` (primary vs cosponsor, with party when matched).

### Committee votes (from minutes PDFs)

NELIS Votes tab only has floor Final Passage. Committee work-session votes are in minutes:

```bash
python collectors/pass2_committee_votes.py
python collectors/pass2_committee_yeas.py   # infer Yeas = membership − Nay/Absent
```

Nevada minutes usually list only NO/ABSENT. `pass2_committee_yeas.py` pulls each
committee’s session roster from NELIS and marks remaining members as Yea.

### Readable review files (Word / Notes / PDF / Excel)

**Look on branch `cursor/pass2-bill-progress-a39c` (PR #14), not `main`.**

```bash
python collectors/export_pass2_readable.py
```

Creates `sources/nevada/water-scarcity/processed/readable/`:

- `README.md` — index of files
- `bills-core-readable.md` / `.html` / `.csv` — **best starting point**
- `progress-readable.md` / `.csv` — milestones **plus full abstracts**
- `votes-readable.md` / `.csv` — floor rolls **and** committee votes
- `text-changes-readable.md` — introduced vs enrolled
