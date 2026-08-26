# SC collection completeness — rising-cost-of-living (full mode)

**Verdict: PASS_WITH_WARNINGS**

PASS 21 / WARN 1 / FAIL 0

## Checks

- **PASS** `config_sessions` — 4 sessions; need the 123rd-126th with OpenStates ids and scstatehouse paths
- **PASS** `config_search_terms` — 26 search terms
- **PASS** `config_relevance_terms` — 11 relevance terms
- **PASS** `config_constituent_proposals` — 4 proposals; incomplete=[]
- **PASS** `config_omnibus_cycles` — method=proviso-by-proviso; 7 appropriations cycles
- **PASS** `proviso_sections_present` — working/south-carolina/rising-cost-of-living/proviso-sections.json: proviso_count=1394 (min 100); cycle=2026-2027 version=ta
- **PASS** `proviso_relevant_present` — working/south-carolina/rising-cost-of-living/proviso-relevant.json: relevant=564
- **PASS** `proviso_cycle_2021` — FY 2021-2022 (H4100): covered
- **PASS** `proviso_cycle_2022` — FY 2022-2023 (H5150): covered
- **PASS** `proviso_cycle_2023` — FY 2023-2024 (H4300): covered
- **PASS** `proviso_cycle_2024` — FY 2024-2025 (H5100): covered
- **PASS** `proviso_cycle_2025` — FY 2025-2026 (H4025): covered
- **PASS** `proviso_cycle_2026` — FY 2026-2027 (H5126): covered
- **PASS** `artifact_pass1` — sources/south-carolina/rising-cost-of-living/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/south-carolina/rising-cost-of-living/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/south-carolina/rising-cost-of-living/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/session={123: 1572, 124: 1713, 125: 1740, 126: 1789}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 6814
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **PASS** `search_term_coverage` — empty_search_terms=[]
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['123:H3012', '123:H3019', '123:H3554', '123:H3575', '123:H3619']
