# SC collection completeness — responsive-elected-leaders (full mode)

**Verdict: PASS_WITH_WARNINGS**

PASS 21 / WARN 1 / FAIL 0

## Checks

- **PASS** `config_sessions` — 4 sessions; need the 123rd-126th with OpenStates ids and scstatehouse paths
- **PASS** `config_search_terms` — 28 search terms
- **PASS** `config_relevance_terms` — 12 relevance terms
- **PASS** `config_constituent_proposals` — 2 proposals; incomplete=[]
- **PASS** `config_omnibus_cycles` — method=proviso-by-proviso; 7 appropriations cycles
- **PASS** `proviso_sections_present` — working/south-carolina/responsive-elected-leaders/proviso-sections.json: proviso_count=1394 (min 100); cycle=2026-2027 version=ta
- **PASS** `proviso_relevant_present` — working/south-carolina/responsive-elected-leaders/proviso-relevant.json: relevant=234
- **PASS** `proviso_cycle_2021` — FY 2021-2022 (H4100): covered
- **PASS** `proviso_cycle_2022` — FY 2022-2023 (H5150): covered
- **PASS** `proviso_cycle_2023` — FY 2023-2024 (H4300): covered
- **PASS** `proviso_cycle_2024` — FY 2024-2025 (H5100): covered
- **PASS** `proviso_cycle_2025` — FY 2025-2026 (H4025): covered
- **PASS** `proviso_cycle_2026` — FY 2026-2027 (H5126): covered
- **PASS** `artifact_pass1` — sources/south-carolina/responsive-elected-leaders/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/south-carolina/responsive-elected-leaders/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/south-carolina/responsive-elected-leaders/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/session={123: 1252, 124: 1364, 125: 1414, 126: 1518}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 5548
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **PASS** `search_term_coverage` — empty_search_terms=[]
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['123:H3012', '123:H3575', '123:H3619', '123:H4099', '123:H4259']
