# Appendix F — What this data can and cannot say

Plain-language limits of the collected record. Anyone quoting the brief should know these.

- Bill discovery is certified complete for the issue vocabulary: 2020-2024 was collected from the OpenStates bulk CSVs, a full mirror of the official docket (5,467 bills), and every bill in those five sessions was additionally swept with a wide-net housing vocabulary; all matches were either included or individually reviewed and categorized as out of scope (certification-report.json). 2025-2026 comes complete from the official state database. A housing bill could be absent only if its title avoids the entire wide-net vocabulary.
- Bills that span a biennium (e.g. filed 2023, decided 2024) appear once per year in the annual files; first-year records are marked carryover duplicates and counted once.
- Sponsor names now exist for most bills (SQL for 2025-2026, official final texts for 2020-2021, bulk files for 2022-2024); party labels are only on the SQL and final-text layers, so cross-party counts understate the true number.
- NH kills most bills by voice vote or on the consent calendar; a bill with no roll call is not necessarily uncontroversial.
- Committee votes appear only where a committee report recorded them (e.g. 'Vote 10-8; RC' in the docket); there is no complete committee-vote table.
- Roll-call party splits use the legislators table; a few older ballots have no party on record (shown as '?').
- Dispositions for eight older bills rest on archived dockets or cited news/official research rather than the SQL database; each such record carries its citations in dispositions.json.
- HB2 votes are on the whole budget trailer; they are never attributable to a single housing section.

The full machine-readable record — bills, votes, ballots, dockets, HB2 sections, and per-claim evidence — lives in the repository under `sources/new-hampshire/housing-affordability/` and `working/new-hampshire/housing-affordability/`.
