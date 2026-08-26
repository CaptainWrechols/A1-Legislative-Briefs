# SC universe audit — independent endpoint reconciliation

**Verdict: PASS**  
Audited: 2026-08-26T13:46:06.457670+00:00 (sample seed 20260826)

Audit endpoints (per-bill vote history, yearly Act Lists) were NOT used to build the universe; agreement is an independent confirmation.

## Checks

- **PASS** `123_per_bill_vote_endpoint_sample` — sampled 20 bills (12 with roll calls, 8 without); mismatches=[] (n=0)
- **PASS** `124_per_bill_vote_endpoint_sample` — sampled 20 bills (12 with roll calls, 8 without); mismatches=[] (n=0)
- **PASS** `125_per_bill_vote_endpoint_sample` — sampled 20 bills (12 with roll calls, 8 without); mismatches=[] (n=0)
- **PASS** `126_per_bill_vote_endpoint_sample` — sampled 20 bills (12 with roll calls, 8 without); mismatches=[] (n=0)
- **PASS** `acts_2019_join_universe` — 112 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2020_join_universe` — 75 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2021_join_universe` — 117 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2022_join_universe` — 151 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2023_join_universe` — 102 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2024_join_universe` — 148 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2025_join_universe` — 94 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
- **PASS** `acts_2026_join_universe` — 176 act rows; not in enumeration: [] (n=0); no page evidence: [] (n=0)
