# Kickoff prompt — new issue brief (copy, edit the three CAPITALIZED lines, paste)

Upload with this prompt: **the Phase 2 RAG constituent-input spreadsheet**
(`NV1 - RAG - Phase 2 Constituent Input.xlsx`). Everything else the agent
needs is in the repository.

---

Repo: https://github.com/CaptainWrechols/A1-Legislative-Briefs — start from `main`.

ISSUE: NEVADA HOUSING AFFORDABILITY            ← edit
ISSUE_SLUG: housing-affordability              ← edit
RAG SHEET: "NV1 - Housing"                     ← edit (tab name in the attached xlsx)

Read RUNBOOK.md and follow it end to end to produce the citizen brief for this issue. The agent specs in agents/*/AGENT.md are binding, especially citizen-brief-writer v2.3 and citizen-reviewer v2.3.

Steps, per the runbook:

1. Create config/issues/nevada-{ISSUE_SLUG}.yaml modeled on the water config: same sessions (2019/2021/2023/2025), search_terms and relevance_terms fitted to this issue, and constituent_proposals encoded from the attached spreadsheet's RAG sheet (every proposal row: title, detail, consensus, tradeoffs, match_terms). The constituent proposals are the organizing spine of the brief.
2. export ISSUE_CONFIG=config/issues/nevada-{ISSUE_SLUG}.yaml, then run the full collection sequence (RUNBOOK step 2). For pass1_subject_index.py, first inspect the cached LCB subject indexes and choose the heading patterns appropriate to this issue; check special sessions if plausibly relevant.
3. Curate every collected bill in working/nevada/{ISSUE_SLUG}/curation-map.json (plain_topic, theme, relevance core/adjacent/context) by reading the digests.
4. Build the evidence pack, then write the reality map with one reality card per constituent statement (tried? where did it die, with votes? which venue owns the decision? who carried adjacent bills?). Programmatically fact-check every card against the evidence pack before writing the brief.
5. Write the front brief per citizen-brief-writer v2.3: adult prose only, no tables, no how-to-use, no civics primers, no discussion questions, no cautions or process commentary, no source keys, no version/kicker subtitle. Structure: title + one-line scope subtitle; The legislative landscape; Key numbers stat strip; proposal paragraphs grouped by record status (no bill on record / reached the Legislature and stalled / precedent exists); The political terrain; New law from the latest session; one closing pointer line to the appendices. Phase 2 visual system (config/forum-brand.yaml; sample in templates/phase-2-samples/).
6. Build appendices A–H with the builders, write Appendix I (sources and review notes: claim-to-source map, collection notes) by hand, build appendices-print.html, and export Word files with collectors/export_docx.py (the front brief must come from the direct-formatting writer, export_docx_brief.py).
7. Verify: citizen-brief.html renders exactly ≤2 US Letter pages in headless Chrome AND citizen-brief.docx renders ≤2 pages in LibreOffice. Run the citizen-reviewer v2.3 checklist (advice-language scan, banned-section scan, fact spot-checks) and write review-report.md/.json.
8. Commit and push per pipeline stage on a branch named cursor/{ISSUE_SLUG}-brief-... and open a draft PR with page screenshots of both the HTML and the Word renders embedded.

Hard rules: no advice language anywhere in citizen outputs; no invented votes, parties, or bills; facts only from collected data; do not modify the water-scarcity packet, its data, or the shared agents/collectors except for the documented per-issue knobs (subject-index heading patterns). Keep headline numbers to the curated policy set, with context bills kept for audit.

When done, report: bill counts (collected/policy/context), the per-proposal findings table, both page counts, and the PR link.

---

## Notes

- One issue per chat. Do not batch issues.
- For the other Nevada issues, the sheet tabs in the same xlsx are:
  `NV1 - Housing`, `NV1 - Cost of Living`, `NV1 - Water`, `NV1 - Education`.
- New Hampshire / South Carolina issues need the per-state source survey and
  collectors first — see RUNBOOK.md ("New states") before using this prompt.
