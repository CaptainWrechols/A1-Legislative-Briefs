# NH collection completeness — housing-affordability

**Verdict: PASS_WITH_WARNINGS**

Bills: 293  |  PASS 17 / WARN 2 / FAIL 0

## Checks

- **PASS** `artifact_pass1` — sources/new-hampshire/housing-affordability/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/new-hampshire/housing-affordability/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/new-hampshire/housing-affordability/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/year={2020: 37, 2021: 24, 2022: 36, 2023: 33, 2024: 49, 2025: 36, 2026: 78}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 293
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — hits={'housing': 122, 'affordable housing': 18, 'workforce housing': 8, 'attainable housing': 0, 'dwelling': 22, 'apartment': 0, 'multi-family': 4, 'multifamily': 2, 'residential development': 3, ' rent': 51, 'rental housing': 3, 'landlord': 15, 'tenant': 28, 'eviction': 10, 'security deposit': 1, 'rent control': 0, 'missing middle': 0, 'zoning': 48, 'land use': 19, 'accessory dwelling': 13, 'ADUs': 1, 'lot size': 0, 'density': 4, 'infill': 0, 'housing production': 0, 'inclusionary': 2, 'impact fee': 2, 'manufactured housing': 17, 'mobile home': 1, 'modular': 0, 'tiny home': 0, 'starter home': 0, 'homebuyer': 0, 'home buyer': 1, 'down payment': 0, 'mortgage': 2, 'housing trust': 0, 'housing appeals': 10, 'homelessness': 4, 'homeless': 7, 'shelter': 7}; empty_search_terms=['attainable housing', 'apartment', 'rent control', 'missing middle', 'lot size', 'infill', 'housing production', 'modular', 'tiny home', 'starter home', 'homebuyer', 'down payment', 'housing trust']
- **PASS** `hb2_2021_sections` — path=working/new-hampshire/housing-affordability/hb2/2021/hb2-sections.json section_count=468 (min 10); source=gencourt:legislation_html
- **PASS** `hb2_2021_votes` — roll_call_count=42
- **PASS** `hb2_2021_relevant_index` — path=working/new-hampshire/housing-affordability/hb2/2021/hb2-relevant.json relevant=25
- **PASS** `hb2_2023_sections` — path=working/new-hampshire/housing-affordability/hb2/2023/hb2-sections.json section_count=612 (min 10); source=gencourt:lba_or_agency_pdf
- **PASS** `hb2_2023_votes` — roll_call_count=17
- **PASS** `hb2_2023_relevant_index` — path=working/new-hampshire/housing-affordability/hb2/2023/hb2-relevant.json relevant=20
- **PASS** `hb2_2025_sections` — path=working/new-hampshire/housing-affordability/hb2/2025/hb2-sections.json section_count=461 (min 10); source=sql:legislationtext
- **PASS** `hb2_2025_votes` — roll_call_count=45
- **PASS** `hb2_2025_relevant_index` — path=working/new-hampshire/housing-affordability/hb2/2025/hb2-relevant.json relevant=21
- **PASS** `rollcall_discovery_not_dropped` — SQL rollcall-title hits missing from pass1: [] (total_missing=0)
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['2026:HR30']

## Empty search terms (no hits)

- `attainable housing`
- `apartment`
- `rent control`
- `missing middle`
- `lot size`
- `infill`
- `housing production`
- `modular`
- `tiny home`
- `starter home`
- `homebuyer`
- `down payment`
- `housing trust`
