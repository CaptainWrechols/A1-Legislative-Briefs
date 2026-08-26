# SC collection completeness — slow-wage-growth (full mode)

**Verdict: PASS_WITH_WARNINGS**

PASS 20 / WARN 2 / FAIL 0

## Checks

- **PASS** `config_sessions` — 4 sessions; need the 123rd-126th with OpenStates ids and scstatehouse paths
- **PASS** `config_search_terms` — 26 search terms
- **PASS** `config_relevance_terms` — 10 relevance terms
- **PASS** `config_constituent_proposals` — 4 proposals; incomplete=[]
- **PASS** `config_omnibus_cycles` — method=proviso-by-proviso; 7 appropriations cycles
- **PASS** `proviso_sections_present` — working/south-carolina/slow-wage-growth/proviso-sections.json: proviso_count=1394 (min 100); cycle=2026-2027 version=ta
- **PASS** `proviso_relevant_present` — working/south-carolina/slow-wage-growth/proviso-relevant.json: relevant=674
- **PASS** `proviso_cycle_2021` — FY 2021-2022 (H4100): covered
- **PASS** `proviso_cycle_2022` — FY 2022-2023 (H5150): covered
- **PASS** `proviso_cycle_2023` — FY 2023-2024 (H4300): covered
- **PASS** `proviso_cycle_2024` — FY 2024-2025 (H5100): covered
- **PASS** `proviso_cycle_2025` — FY 2025-2026 (H4025): covered
- **PASS** `proviso_cycle_2026` — FY 2026-2027 (H5126): covered
- **PASS** `artifact_pass1` — sources/south-carolina/slow-wage-growth/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/south-carolina/slow-wage-growth/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/south-carolina/slow-wage-growth/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/session={123: 1373, 124: 1420, 125: 1426, 126: 1525}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 5744
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — empty_search_terms=['youth wage', 'training wage', 'tip credit', 'wage theft']
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['123:H3019', '123:H3554', '123:H3575', '123:H3619', '123:S70']
