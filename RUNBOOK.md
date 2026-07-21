# Runbook — producing a citizen brief for a new issue

This is the end-to-end recipe that produced the Nevada water brief
(citizen-v4.0). It assumes a fresh agent chat starting from `main` — no
knowledge from previous conversations is required; everything the process
needs lives in this repository.

## The one-line version

Create an issue config → run the collectors with `ISSUE_CONFIG` set → curate
→ run the builders → write the brief per `agents/citizen-brief-writer/AGENT.md`
(v2.3 rules: adult prose, no tables, no worksheet apparatus) → verify 2-page
renders in HTML **and** Word → PR.

## 0. Prerequisites (per machine)

```bash
pip install -r requirements.txt
sudo apt-get install -y pandoc poppler-utils            # docx export + page counting
# optional, for verifying the .docx page count exactly:
sudo apt-get install -y --no-install-recommends libreoffice-writer
# Chrome (usually preinstalled) is used to verify the HTML page count.
```

## 1. Issue config

Copy `config/issues/nevada-water-scarcity.yaml` to
`config/issues/{state}-{slug}.yaml` and edit:

- `state`, `issue_id`, `issue_title`, `issue_slug` (these drive all paths:
  `sources/{state}/{slug}`, `working/{state}/{slug}`, `briefs/{state}/{slug}/citizen-v1`)
- `sessions` (for Nevada: NELIS session ids and paths)
- `search_terms` — seed from the issue's vocabulary **and** from the
  constituent statements
- `relevance_terms` — the on-topic flag vocabulary
- `constituent_proposals` — the top citizen statements from the Phase 2 RAG
  dataset for this issue, with `match_terms` per statement. **The brief is
  organized around these.**

Every collector reads the active issue from the environment:

```bash
export ISSUE_CONFIG=config/issues/nevada-housing.yaml
```

## 2. Collection (Nevada issues)

```bash
python collectors/pass1_bills.py            # NELIS + OpenStates keyword search
python collectors/pass1_subject_index.py    # LCB official Subject Index harvest
python collectors/enrich_abstracts.py       # full digests for every found bill
python collectors/pass2_bills.py --skip-openstates   # history, floor votes, progress
python collectors/pass2_sponsors.py
python collectors/pass2_committee_votes.py  # committee votes from minutes PDFs
python collectors/pass2_committee_yeas.py   # infer Yeas from membership
python collectors/pass2_party_roster.py     # once per state; cached
python collectors/pass2_attach_party.py
python collectors/pass2_text_diff.py        # introduced vs enrolled (governor-bound)
python collectors/pass2_build_core.py
python collectors/export_pass2_readable.py
```

Notes:
- **Edit `HEAD_PATTERNS` / `ENTRY_KEYWORDS` in `pass1_subject_index.py`** for
  the new issue's subject headings (they are issue-specific; the water list is
  the template). Check what headings exist in the cached index HTML first.
- Check special sessions if the topic could plausibly appear there
  (the water run checked all six 2020–2025 special sessions).
- `OPENSTATES_API_KEY` is optional; NELIS + official rosters carried the
  water run at 100% party coverage.

## 3. Curation (the judgment step)

Write `working/{state}/{slug}/curation-map.json`: for every collected bill, a
`plain_topic` (one plain sentence), a `theme` (6–10 citizen-facing themes),
and a `relevance` tier (`core` / `adjacent` / `context`). Read the digests —
titles lie. Context bills stay in the set for audit but are excluded from
headline numbers. This is agent/human work, not scripted.

## 4. Analysis builders (deterministic)

```bash
python collectors/build_evidence_pack.py    # inventory, themes, crosswalk, people signals
```

Then write the reality map (`working/{state}/{slug}/reality-map.json` + `.md`)
per `agents/reality-mapper/AGENT.md`: one **reality card per constituent
statement** (tried? where did it die? which venue owns it? who carried it?),
theme baskets, high-support non-enactments, chokepoints, veto watch.
**Fact-check every card programmatically against the evidence pack before
writing the brief.**

## 5. The front brief (v2.3 rules — read the agent spec)

`agents/citizen-brief-writer/AGENT.md`. The hard rules learned on water:

- Adult prose only; no civics primers, no explainers of common terms
- No tables; bold-lead paragraphs grouped by record status
  (*no bill on record / reached the Legislature and stalled / precedent exists*)
- No worksheet apparatus (how-to-use, questions), no cautions/meta-commentary,
  no version/kicker subtitle, no source keys (those go to Appendix I)
- ≤ 2 pages in **both** HTML and Word renders
- Phase 2 visual system (`config/forum-brand.yaml`; sample PDF in
  `templates/phase-2-samples/`)

## 6. Packaging

```bash
python collectors/build_appendices.py                       # A–H from data
# write appendices/I-sources-and-review-notes.md by hand (claim→source map)
python collectors/build_appendices_print.py --brief-dir briefs/{state}/{slug}/citizen-v1
python collectors/export_docx.py --brief-dir briefs/{state}/{slug}/citizen-v1
```

The front-brief .docx is written by `export_docx_brief.py` with **direct
formatting** (literal Arial/RGB/uppercase per run) so it renders identically
in Word, Google Docs, and LibreOffice. Do not switch it back to style-based
export.

Verify page counts:

```bash
google-chrome --headless=new --no-sandbox --user-data-dir=/tmp/c \
  --print-to-pdf=/tmp/b.pdf --no-pdf-header-footer citizen-brief.html   # expect 2 pages
soffice --headless --convert-to pdf citizen-brief.docx                  # expect 2 pages
```

## 7. Review gate

Run the `agents/citizen-reviewer/AGENT.md` v2.3 checklist: advice-language
scan, banned-section scan, fact spot-checks against the pack, both page
counts, Phase 2 tokens, Appendix I present. Write `review-report.md`/`.json`.

## 8. Ship

Branch `cursor/<issue>-...`, commit per pipeline stage, open a draft PR with
page screenshots embedded. Never push data and analysis in one opaque commit.

---

## New states (New Hampshire, South Carolina)

The **agents, builders, curation format, brief rules, and Word/print
packaging are state-agnostic** and reusable as-is. What is Nevada-specific is
Pass 1/Pass 2 collection (`pass1_bills.py`, `pass1_subject_index.py`,
`pass2_*.py` all speak NELIS). For each new state, before any brief work:

1. **Source survey first** (one scoped agent task per state): where do bill
   text, history, roll-call votes, committee votes, sponsors, and party
   rosters live? Is there an official subject index? What are the session
   identifiers? (NH: gencourt.state.nh.us; SC: scstatehouse.gov; OpenStates
   covers both as a cross-check.)
2. Write `collectors/nh/…` / `collectors/sc/…` equivalents that emit the
   **same output schema** (`pass1/bills.json`, `processed/bills-core.json`,
   `bill-votes.json`, `bill-legislative-progress.json`, …). Everything
   downstream then works unchanged.
3. NH and SC legislatures meet **annually** — session structure, deadlines,
   and "died at session end" semantics differ from Nevada's biennium; encode
   that in the state's session config.

## Practical notes for running this in Cursor

- **One fresh agent chat per issue run**, started from `main`. The repo docs
  are the memory; do not rely on any prior conversation.
- **Same repository for everything** (all states, all issues). The pipeline
  is shared infrastructure; per-issue artifacts are namespaced by path.
- Run one issue at a time per branch to keep PRs reviewable.
- Environment: this VM needs `pip install -r requirements.txt`, pandoc, and
  (for docx verification) LibreOffice on each fresh start — consider an env
  setup run at cursor.com/onboard so agents start with these preinstalled.
