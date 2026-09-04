# Appendix F — Data limits

What this packet's data can and cannot say. Everything below applies to the
front brief, the spotlights, and every appendix.

1. **The set is a curated selection, not a proven-complete universe of
   cost-of-living bills.** Discovery ran the official full-text search plus a
   title/summary scan of the certified 123rd–126th universe on the issue
   config's 26 search terms, keeping all 6,814 hits. Hand review then kept
   271 bills (121 core / 136 adjacent / 14 context). Three bills that
   matched no search term (2019-20 H4149 and 2021-22 H3116, personal-finance
   scan; 2023-24 H5205, childcare scan) were found by hand full-text scans
   across the whole universe and added with provenance marked. A relevant
   bill using none of the search terms and not caught by the hand scans
   would be missed.
2. **This is the broadest of the four South Carolina issues** — housing,
   utilities, taxes, and insurance in one set, plus (from 2026-09-04) a
   childcare theme for the legislator-discussion topic. The exclusion rules
   in `curation-map.json` document what was pruned: 'rent' matching
   'pa**rent**al' (family-law bills), 'utility' matching utility-terrain
   vehicles, health/dental/life insurance mandates, industry tax bills,
   water-system ownership disputes, and similar cross-topic noise.
3. **No committee vote counts exist, anywhere.** South Carolina publishes
   committee *outcomes* ("Favorable," "Favorable with amendment") but never
   tallies. Five of every six bills in this set died in committee — so for
   most bills there is no recorded vote of any kind, and none may be implied.
4. **No party labels.** This dataset does not join sponsors or floor votes
   to the member roster, so the packet makes no party claims at all. Ballot
   PDFs are recorded per roll call (`ballot_pdf_key`) and can be fetched on
   demand if human reviewers want party splits on specific cited votes.
5. **Floor counts are verbatim** from the chamber vote-history tables. Only
   passage-type motions (readings, Passage of Bill, ratification) are used
   as support signals; tabling and amendment votes are excluded.
6. **The 126th session is treated as concluded.** Non-enacted 2025-26 bills
   are "did not pass (session ended)" as of the collection date
   (2026-08-27). A special session could revive counts.
7. **FY 2020-21 has no enacted Part IB.** The budget bill died in committee
   during COVID and the state ran on a continuing resolution — so
   budget-proviso coverage runs FY 2021-22 through FY 2026-27, and that gap
   is stated wherever provisos are counted.
8. **One regulatory fact was verified outside the bill record.** The
   personal-finance graduation requirement's status (Regulation 43-234 as
   amended by Document 5130, effective May 26, 2023) was checked against the
   State Register and the State Board of Education's published regulation,
   because a stalled approval resolution does not stop a regulation from
   taking effect under the state's regulation-review law. No other claim
   relies on sources outside the record.
9. **The 2020 market-reform study committee's report is outside this
   record.** The packet documents that Act 187 of 2020 created the study;
   what the committee concluded is not in the bill data.
10. **No fiscal notes.** None of the failed property-tax or utility bills
    carries a cost estimate in this dataset; the packet therefore makes no
    claims about what any proposal would cost or save.
11. **Constituent proposals are process input.** The four [P-…] proposals
    and their frequency/consensus/tradeoff lines come from the final
    proposal grid ("SC1 – Rising Cost of Living", 2026-09-04); the cells are
    carried per the grid convention established in the Phase 2 grid ("Grid
    View for Legislators v2"). They are what participants and the feedback
    grid reported, not verified facts, and the packet labels them
    accordingly. **Provenance caveat:** the final-grid source document did
    not transfer into this workspace; the cells used are the Phase 2 grid
    lines for this issue, which the final grids carry forward verbatim (as
    verified for the slow-wage-growth final grid). Confirmation against the
    original document is an open item for the human reviewers.
12. **Child care assistance is a legislator-discussion topic, not a Phase 2
    proposal.** It entered this packet on a 2026-09-04 request tied to
    reported discussions with sitting legislators; the record scan and its
    method are in `working/south-carolina/rising-cost-of-living/
    childcare-assistance-scan.md`. The reported discussions themselves are
    not part of the legislative record.
