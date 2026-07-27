# Appendix F — What this data can and cannot say

Plain-language limits of the record behind this packet.

1. The set was found by keyword search plus the official subject index; it is broad but not guaranteed complete.
2. The record shows where each bill stopped - never why (no veto messages or floor debate in the dataset).
3. Committee Yea votes are inferred (membership minus recorded Nay/Absent) because Nevada minutes usually list only No and Absent votes; these rows are marked in the source data.
4. No OpenStates data in this collection; party labels come from official NELIS legislator directories (97.9% of roll-call ballot rows matched; the unmatched rows are minutes-parsing name fragments left unlabeled; sponsor party coverage is 99.6%).
5. Concurrent resolutions carry no final NELIS history action, so their disposition reads Unknown (two adopted Financial Literacy Month resolutions) or In Progress (2025 AJR9); they are excluded from pass-rate claims.
6. Special-session facts come from a manual verification file (verification/special-sessions.json), not the regular pipeline.
7. Context bills (found by broad terms or omnibus indexing) are kept for audit but excluded from headline counts.

Known collection gaps recorded during the collection: 725 items (see `sources/nevada/k-12_educational_outcomes/processed/data-gaps.json`). OpenStates was unavailable for this refresh; all history, votes, and party labels come from the official NELIS system and legislator rosters, with committee votes read from official minutes PDFs.
