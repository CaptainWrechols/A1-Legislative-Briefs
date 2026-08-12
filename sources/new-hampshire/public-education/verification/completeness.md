# NH collection completeness — public-education

**Verdict: PASS_WITH_WARNINGS**

Bills: 1049  |  PASS 17 / WARN 2 / FAIL 0

## Checks

- **PASS** `artifact_pass1` — sources/new-hampshire/public-education/pass1/bills.json
- **PASS** `artifact_bills_core` — sources/new-hampshire/public-education/processed/bills-core.json
- **PASS** `artifact_bill_votes` — sources/new-hampshire/public-education/processed/bill-votes.json
- **PASS** `sessions_covered` — bills/year={2020: 120, 2021: 73, 2022: 169, 2023: 134, 2024: 203, 2025: 134, 2026: 216}; missing_unexplained=[]
- **PASS** `bill_fields_complete` — 0 incomplete of 1049
- **PASS** `votes_row_per_bill` — missing_vote_rows=0 examples=[]
- **PASS** `vote_counts_are_integers` — all yea/nay integers or null
- **WARN** `search_term_coverage` — hits={'school district': 120, 'public school': 122, 'chartered public school': 39, 'charter school': 9, 'education freedom': 73, 'freedom account': 72, 'education savings': 2, 'scholarship organization': 10, 'education tax credit': 5, 'special education': 56, 'adequate education': 38, 'adequacy': 6, 'statewide education': 13, 'education trust fund': 12, 'school funding': 6, 'education funding': 5, 'school building aid': 25, 'cooperative school': 19, 'school administrative unit': 17, 'per pupil': 5, 'state aid': 7, 'teacher': 23, 'educator': 21, 'pupil': 31, 'student': 146, 'kindergarten': 12, 'curriculum': 13, 'school board': 33, 'school building': 29, 'tuition': 13, 'school meal': 11, 'school lunch': 6, 'school breakfast': 1, 'IEP': 0, 'career and technical': 13, 'school attendance': 4, 'open enrollment': 2, 'home education': 5, 'nonpublic school': 5, 'superintendent': 11, 'school nurse': 4, 'paraprofessional': 2, 'school year': 4, 'school employee': 4, 'school personnel': 1, 'school property': 2, 'school safety': 2, 'school bus': 15, 'school calendar': 1, 'school health': 1, 'literacy': 6, 'graduation': 11, 'competency': 9, 'proficiency': 3, 'civics': 12, 'dyslexia': 2, 'statewide assessment': 1, 'education program': 14, 'educational institution': 11, 'department of education': 68, 'state board of education': 19, 'classroom': 6, 'instruction': 20, 'teaching': 15, 'learning': 15, 'academic': 12, 'minimum standards': 5, 'school approval': 2, 'divisive concepts': 1, 'parental bill of rights': 8, "parents' bill of rights": 2, 'bullying': 9, 'early childhood': 8, 'vocational': 4, 'apprenticeship': 4, 'workforce development': 5}; empty_search_terms=['IEP']
- **PASS** `hb2_2021_sections` — path=working/new-hampshire/public-education/hb2/2021/hb2-sections.json section_count=468 (min 10); source=gencourt:legislation_html
- **PASS** `hb2_2021_votes` — roll_call_count=42
- **PASS** `hb2_2021_relevant_index` — path=working/new-hampshire/public-education/hb2/2021/hb2-relevant.json relevant=53
- **PASS** `hb2_2023_sections` — path=working/new-hampshire/public-education/hb2/2023/hb2-sections.json section_count=612 (min 10); source=gencourt:lba_or_agency_pdf
- **PASS** `hb2_2023_votes` — roll_call_count=17
- **PASS** `hb2_2023_relevant_index` — path=working/new-hampshire/public-education/hb2/2023/hb2-relevant.json relevant=62
- **PASS** `hb2_2025_sections` — path=working/new-hampshire/public-education/hb2/2025/hb2-sections.json section_count=461 (min 10); source=sql:legislationtext
- **PASS** `hb2_2025_votes` — roll_call_count=45
- **PASS** `hb2_2025_relevant_index` — path=working/new-hampshire/public-education/hb2/2025/hb2-relevant.json relevant=56
- **PASS** `rollcall_discovery_not_dropped` — SQL rollcall-title hits missing from pass1: [] (total_missing=0)
- **WARN** `no_advice_language_in_titles` — titles_with_advice_words=['2023:HB371']

## Empty search terms (no hits)

- `IEP`
