# NH collection completeness — property-taxes

**Verdict: PASS_WITH_WARNINGS**

Bills: 530  |  PASS 18 / WARN 1 / FAIL 0

## Checks

- **PASS** `artifact_pass1` — sources/new-hampshire/property-taxes/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/new-hampshire/property-taxes/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/new-hampshire/property-taxes/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/year={2020: 78, 2021: 61, 2022: 72, 2023: 65, 2024: 89, 2025: 65, 2026: 100}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 530
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — hits={'property tax': 94, 'statewide education': 13, 'adequate education': 38, 'adequacy': 6, 'education trust fund': 12, 'school funding': 6, 'education funding': 5, 'school building aid': 25, 'interest and dividends': 14, 'business profits': 32, 'business enterprise tax': 14, 'meals and rooms': 24, 'homestead': 18, 'current use': 8, 'land use change tax': 1, 'timber tax': 4, 'excavation tax': 1, 'utility property': 5, 'assessing': 5, 'revaluation': 0, 'equalization': 3, 'abatement': 12, 'tax cap': 17, 'tax rate': 16, 'tax relief': 18, 'tax exemption': 36, 'tax credit': 38, 'tax deferral': 0, 'tax lien': 3, 'tax expenditure': 2, 'income tax': 2, 'sales tax': 9, 'excise': 0, 'taxation': 23, 'tax on': 9, 'revenue': 67, 'local option': 5, 'state aid': 7, 'payment in lieu of taxes': 1, 'communications services tax': 5, 'retirement system contributions': 10, 'cooperative school': 19, 'keno': 8, 'lottery': 8, 'gambling': 4}; empty_search_terms=['revaluation', 'tax deferral', 'excise']
- **PASS** `hb2_2021_sections` — path=working/new-hampshire/property-taxes/hb2/2021/hb2-sections.json section_count=468 (min 10); source=gencourt:legislation_html
- **PASS** `hb2_2021_votes` — roll_call_count=42
- **PASS** `hb2_2021_relevant_index` — path=working/new-hampshire/property-taxes/hb2/2021/hb2-relevant.json relevant=78
- **PASS** `hb2_2023_sections` — path=working/new-hampshire/property-taxes/hb2/2023/hb2-sections.json section_count=612 (min 10); source=gencourt:lba_or_agency_pdf
- **PASS** `hb2_2023_votes` — roll_call_count=17
- **PASS** `hb2_2023_relevant_index` — path=working/new-hampshire/property-taxes/hb2/2023/hb2-relevant.json relevant=53
- **PASS** `hb2_2025_sections` — path=working/new-hampshire/property-taxes/hb2/2025/hb2-sections.json section_count=461 (min 10); source=sql:legislationtext
- **PASS** `hb2_2025_votes` — roll_call_count=45
- **PASS** `hb2_2025_relevant_index` — path=working/new-hampshire/property-taxes/hb2/2025/hb2-relevant.json relevant=71
- **PASS** `rollcall_discovery_not_dropped` — SQL rollcall-title hits missing from pass1: [] (total_missing=0)
- **PASS** `no_advice_language_in_titles` — titles_with_advice_words=[]

## Empty search terms (no hits)

- `revaluation`
- `tax deferral`
- `excise`
