# Appendix F — What this data can and cannot say

Plain-language limits of the collected record. Anyone quoting the brief should know these.

- 2020-2024 discovery is roll-call-based: GenCourt keeps only the current biennium's bill list, and no API key or bulk file was available for the OpenStates/LegiScan backfill in this run. Bills from 2020-2024 that died without any floor roll call are therefore missing from the set. The set under-counts failures in those years, so cross-year failure comparisons are not safe; 2025-2026 coverage is complete from the official database.
- Sponsor names are complete for 2025-2026 (SQL) and for 2020-2021 (official final-text pages); they are absent for most 2022-2024 bills.
- NH kills most bills by voice vote or on the consent calendar; a bill with no roll call is not necessarily uncontroversial.
- Committee votes appear only where a committee report recorded them (e.g. 'Vote 10-8; RC' in the docket); there is no complete committee-vote table.
- Roll-call party splits use the legislators table; a few older ballots have no party on record (shown as '?').
- Dispositions for eight older bills rest on archived dockets or cited news/official research rather than the SQL database; each such record carries its citations in dispositions.json.
- HB2 votes are on the whole budget trailer; they are never attributable to a single housing section.

The full machine-readable record — bills, votes, ballots, dockets, HB2 sections, and per-claim evidence — lives in the repository under `sources/new-hampshire/housing-affordability/` and `working/new-hampshire/housing-affordability/`.
