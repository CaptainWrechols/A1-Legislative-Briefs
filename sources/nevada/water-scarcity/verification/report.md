# Verification report — nevada-04-water-scarcity

- **Overall status:** PASS_WITH_WARNINGS
- **Verified at:** 2026-07-16T20:19:17.604876+00:00
- **Agent:** data-verifier
- **Note:** Data scraper skipped; existing Pass 1/2 data only.

## Counts

- pass1_bills: 88
- core_bills: 88
- floor_votes: 391
- sponsor_rows: 182
- progress_rows: 88
- action_rows: 861

## Checks

- **bill_identifiers** — `PASS`: 88 bills checked; 0 issues
- **bill_count_consistency** — `PASS`: pass1=88 core=88 expected=88
- **sponsors_coverage** — `PASS`: 88 bills with sponsors; missing=0; classifications={'primary': 131, 'cosponsor': 51}
- **disposition_milestone_consistency** — `PASS`: 0 inconsistencies
- **votes_structure** — `PASS`: 391 floor vote records; 169 missing yes/no counts
- **manifest_coverage** — `PASS_WITH_WARNINGS`: manifest.json not present; Pass 2 uses processed/ + pass1/ caches instead of classic raw/manifest layout
- **links_alive_sample** — `PASS`: Sampled 20 URLs (no full re-scrape); 20 alive
- **official_page_match_sample** — `PASS`: Checked 5 NELIS pages for bill id presence
- **collection_scope** — `PASS_WITH_WARNINGS`: Dataset is keyword-discovered Pass 1/2 set (88 bills), not a proven exhaustive universe of all Nevada water bills. Verifier did not run a new search.

## Failed URLs

- None in sample.