# NH collection completeness — water-example

**Verdict: PASS_WITH_WARNINGS**

Bills: 148  |  PASS 18 / WARN 1 / FAIL 0

## Checks

- **PASS** `artifact_pass1` — sources/new-hampshire/water-example/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/new-hampshire/water-example/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/new-hampshire/water-example/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/year={2020: 25, 2021: 16, 2022: 25, 2023: 15, 2024: 29, 2025: 18, 2026: 20}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 148
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — hits={'water': 118, 'groundwater': 23, 'wetland': 13, 'shoreland': 9, 'aquifer': 0, 'drinking water': 32, 'PFAS': 31, 'stormwater': 3}; empty_search_terms=['aquifer']
- **PASS** `hb2_2021_sections` — path=working/new-hampshire/water-example/hb2/2021/hb2-sections.json section_count=468 (min 10); source=gencourt:legislation_html
- **PASS** `hb2_2021_votes` — roll_call_count=42
- **PASS** `hb2_2021_relevant_index` — path=working/new-hampshire/water-example/hb2/2021/hb2-relevant.json relevant=12
- **PASS** `hb2_2023_sections` — path=working/new-hampshire/water-example/hb2/2023/hb2-sections.json section_count=612 (min 10); source=gencourt:lba_or_agency_pdf
- **PASS** `hb2_2023_votes` — roll_call_count=17
- **PASS** `hb2_2023_relevant_index` — path=working/new-hampshire/water-example/hb2/2023/hb2-relevant.json relevant=30
- **PASS** `hb2_2025_sections` — path=working/new-hampshire/water-example/hb2/2025/hb2-sections.json section_count=461 (min 10); source=sql:legislationtext
- **PASS** `hb2_2025_votes` — roll_call_count=45
- **PASS** `hb2_2025_relevant_index` — path=working/new-hampshire/water-example/hb2/2025/hb2-relevant.json relevant=25
- **PASS** `rollcall_discovery_not_dropped` — SQL rollcall-title hits missing from pass1: [] (total_missing=0)
- **PASS** `no_advice_language_in_titles` — titles_with_advice_words=[]

## Empty search terms (no hits)

- `aquifer`
