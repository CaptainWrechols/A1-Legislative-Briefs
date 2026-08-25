# SC collection completeness — slow-wage-growth (full mode)

**Verdict: FAIL**

PASS 12 / WARN 1 / FAIL 9

## Checks

- **PASS** `config_sessions` — 4 sessions; need the 123rd-126th with OpenStates ids and scstatehouse paths
- **PASS** `config_search_terms` — 26 search terms
- **PASS** `config_relevance_terms` — 10 relevance terms
- **PASS** `config_constituent_proposals` — 4 proposals; incomplete=[]
- **PASS** `config_omnibus_cycles` — method=proviso-by-proviso; 7 appropriations cycles
- **PASS** `proviso_sections_present` — working/south-carolina/slow-wage-growth/proviso-sections.json: proviso_count=1354 (min 100); cycle=2025-2026 version=ta
- **PASS** `proviso_relevant_present` — working/south-carolina/slow-wage-growth/proviso-relevant.json: relevant=649
- **FAIL** `proviso_cycle_2021` — FY 2021-2022 (H4100): missing working/south-carolina/slow-wage-growth/provisos/2021/proviso-sections.json
- **FAIL** `proviso_cycle_2022` — FY 2022-2023 (H5150): missing working/south-carolina/slow-wage-growth/provisos/2022/proviso-sections.json
- **FAIL** `proviso_cycle_2023` — FY 2023-2024 (H4300): missing working/south-carolina/slow-wage-growth/provisos/2023/proviso-sections.json
- **FAIL** `proviso_cycle_2024` — FY 2024-2025 (H5100): missing working/south-carolina/slow-wage-growth/provisos/2024/proviso-sections.json
- **PASS** `proviso_cycle_2025` — FY 2025-2026 (H4025): covered
- **FAIL** `proviso_cycle_2026` — FY 2026-2027 (H5126): missing working/south-carolina/slow-wage-growth/provisos/2026/proviso-sections.json
- **FAIL** `artifact_pass1` — sources/south-carolina/slow-wage-growth/pass1/bills.json
- **FAIL** `artifact_bills_core` — sources/south-carolina/slow-wage-growth/processed/bills-core.json
- **FAIL** `artifact_bill_votes` — sources/south-carolina/slow-wage-growth/processed/bill-votes.json
- **FAIL** `sessions_covered` — bills/session={}; missing_unexplained=[123, 124, 125, 126]
- **PASS** `bill_fields_complete` — 0 incomplete of 0
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — empty_search_terms=['wage', 'wages', 'salary', 'pay', 'minimum wage', 'living wage', 'youth wage', 'training wage', 'income', 'worker', 'labor', 'workforce', 'apprenticeship', 'career pathway', 'technical college', 'workforce development', 'ready to work', 'tip credit', 'overtime', 'wage theft', 'employer', 'tax credit', 'incentive', 'unemployment', 'right to work', 'collective bargaining']
- **PASS** `no_advice_language_in_titles` — titles_with_advice_words=[]
