# NH collection completeness — energy

**Verdict: PASS_WITH_WARNINGS**

Bills: 456  |  PASS 17 / WARN 2 / FAIL 0

## Checks

- **PASS** `artifact_pass1` — sources/new-hampshire/energy/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/new-hampshire/energy/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/new-hampshire/energy/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/year={2020: 79, 2021: 39, 2022: 72, 2023: 61, 2024: 67, 2025: 63, 2026: 75}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 456
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — hits={'energy': 179, 'electric': 142, 'utility': 46, 'utilities': 37, 'renewable': 59, 'net metering': 10, 'net energy metering': 22, 'transmission': 6, 'default service': 6, 'community power': 0, 'aggregation': 9, 'smart meter': 3, 'time-of-use': 1, 'public utilities commission': 18, 'ratepayer': 8, 'weatherization': 3, 'system benefits charge': 8, 'offshore wind': 7, 'hydroelectric': 7, 'geothermal': 0, 'biomass': 5, 'nuclear': 13, 'natural gas': 4, 'propane': 3, 'heating fuel': 1, 'fuel assistance': 1, 'site evaluation committee': 17, 'solar': 22, 'grid': 15, 'thermal': 6, 'pipeline': 1, 'biodiesel': 2, 'decommissioning': 3, 'power line': 1, 'power generation': 6, 'biopower': 2, 'pole attachment': 3, 'greenhouse gas': 8, 'heating oil': 3, 'oil discharge': 2, 'fossil fuel': 1, 'low carbon fuel': 1, 'ethanol': 1, 'carbon': 19, 'emission': 19, 'climate': 22}; empty_search_terms=['community power', 'geothermal']
- **PASS** `hb2_2021_sections` — path=working/new-hampshire/energy/hb2/2021/hb2-sections.json section_count=468 (min 10); source=gencourt:legislation_html
- **PASS** `hb2_2021_votes` — roll_call_count=42
- **PASS** `hb2_2021_relevant_index` — path=working/new-hampshire/energy/hb2/2021/hb2-relevant.json relevant=111
- **PASS** `hb2_2023_sections` — path=working/new-hampshire/energy/hb2/2023/hb2-sections.json section_count=612 (min 10); source=gencourt:lba_or_agency_pdf
- **PASS** `hb2_2023_votes` — roll_call_count=17
- **PASS** `hb2_2023_relevant_index` — path=working/new-hampshire/energy/hb2/2023/hb2-relevant.json relevant=30
- **PASS** `hb2_2025_sections` — path=working/new-hampshire/energy/hb2/2025/hb2-sections.json section_count=461 (min 10); source=sql:legislationtext
- **PASS** `hb2_2025_votes` — roll_call_count=45
- **PASS** `hb2_2025_relevant_index` — path=working/new-hampshire/energy/hb2/2025/hb2-relevant.json relevant=16
- **PASS** `rollcall_discovery_not_dropped` — SQL rollcall-title hits missing from pass1: [] (total_missing=0)
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['2026:HB1723']

## Empty search terms (no hits)

- `community power`
- `geothermal`
