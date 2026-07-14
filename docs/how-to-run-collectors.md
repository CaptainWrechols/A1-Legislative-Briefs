# How to Run Collectors

This guide covers **dual-source** collection for the Nevada water scarcity pilot: **NELIS** (official state site) and **OpenStates** (structured API), plus a **cross-reference** step so reviewers can check consistency.

## Prerequisites

1. Python 3.12 or newer
2. OpenStates API key from https://openstates.org/accounts/profile/ (needed only for the OpenStates collector)
3. This repository cloned locally

## One-time setup

```bash
cd a1-legislative-briefs
pip install -r requirements.txt
```

## Recommended local sequence

Both collectors read the **same** `search_terms` from `config/issues/nevada-water-scarcity.yaml` and apply the **same** water-relevance title/summary filter (`collectors/water_relevance.py`).

```bash
# 1) NELIS search stubs (no API key) — shared terms + shared filter
python collectors/nv_nelis_bills.py

# 2) NELIS details: history, hearings, floor votes + member names, sponsors + party, bill PDF links
#    Optional smoke test: NELIS_DETAIL_LIMIT=5
python collectors/nv_nelis_bill_details.py

# 3) OpenStates search + detail enrichment (same terms + same filter)
export OPENSTATES_API_KEY=your-key-here
# Optional: OPENSTATES_DETAIL_LIMIT=10 OPENSTATES_RESUME=1 OPENSTATES_DETAIL_DELAY=2.5
python collectors/openstates_bills.py

# 4) Cross-reference both packages (normalizes AB 30 ↔ AB30)
python collectors/reconcile_bill_sources.py
```

### What each source gives you

| Field | NELIS | OpenStates |
|-------|-------|------------|
| Discovery terms | Same `config` `search_terms` | Same `config` `search_terms` |
| Water relevance filter | Same `water_relevance.py` on title/summary | Same filter on title/abstract |
| Bill history / actions | Overview history table | `include=actions` detail |
| Committee signal | Past Hearings recommendations (e.g. Do pass) | Action classifications + committee vote events when present |
| Floor votes + member names | `GetBillVotes` / `GetBillVoteMembers` | `include=votes` (voter lists when API returns them) |
| Sponsors + party | Overview sponsors + legislator pages | `include=sponsorships` (`person.party` when present) |
| Bill text | PDF/HTML links on Text tab (`bill-texts.json`) | Usually not full text via this collector |

`vote_event_count = 0` in OpenStates means **no vote records were returned by the API**, not that no vote happened. Many enrolled/signed bills still have Final Passage tallies on NELIS; some chambers may also use unrecorded voice votes. Prefer NELIS vote files when OpenStates votes are empty.

## Output layout

```
sources/nevada/water-scarcity/
├── nelis/
│   ├── bills-search-stubs.json
│   ├── bills.json
│   ├── bill-actions.json
│   ├── bill-votes.json
│   ├── bill-sponsors.json
│   ├── bill-hearings.json
│   ├── bill-texts.json
│   └── collection-summary.json
├── openstates/
│   ├── bills-search-candidates.json
│   ├── bills.json
│   ├── bill-actions.json
│   ├── bill-votes.json
│   ├── bill-sponsors.json
│   ├── bill-legislative-progress.json
│   └── collection-summary.json
├── crossref/
│   ├── bill-match-report.json
│   └── summary.md
├── manifest.json
└── raw/
```

## GitHub Actions

1. Add `OPENSTATES_API_KEY` under Settings → Secrets and variables → Actions.
2. Actions → **Collect Nevada Water Bills** → Run workflow.
3. Optional inputs:
   - `nelis_detail_limit` / `openstates_detail_limit` for capped smoke runs
   - `skip_openstates=true` for NELIS-only collection
   - `nelis_download_text=true` to store bill PDFs under `raw/nelis-text/`
4. Download the `nevada-water-collected-data` artifact and open `crossref/summary.md`.

GitHub does **not** host NELIS/OpenStates data itself. Actions only runs these collectors in the cloud and uploads the JSON artifacts into the workflow run (and into the repo if you commit them).

## Diagnose OpenStates first (if enrichment fails)

```bash
export OPENSTATES_API_KEY=your-key-here
python collectors/diagnose_openstates.py
```

Or run Actions → **Diagnose OpenStates Nevada**.

OpenStates detail calls often hit **429 / 502 / 504**. The collector now backs off on those statuses, supports `OPENSTATES_RESUME=1`, and slows detail requests via `OPENSTATES_DETAIL_DELAY`.

## Generate appendix A

```bash
cp sources/nevada/water-scarcity/nelis/bills.json \
   sources/nevada/water-scarcity/processed/bills-combined.json
python collectors/json_to_appendix.py
```

## After collecting data

Run the agent pipeline in order. See `agents/README.md`.

1. Data Scraper (collectors above)
2. Data Verifier (include `crossref/summary.md`)
3. Synthesizer → Final Reviewer

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Missing OPENSTATES_API_KEY` | Set the env var or skip OpenStates |
| NELIS details empty | Confirm stubs exist; check `nelis/detail-failures.json` |
| OpenStates votes/sponsors empty | Re-run with `OPENSTATES_RESUME=1` and higher `OPENSTATES_DETAIL_DELAY`; check `enrich_failures` in `openstates/collection-summary.json` |
| Far more OpenStates bills than NELIS | Expected: OpenStates searches full text. Compare filtered `openstates/bills.json` to NELIS, not `bills-search-candidates.json` |
| Cross-ref conflicts | Open `crossref/bill-match-report.json`; prefer NELIS for citation wording and investigate mismatched vote/sponsor/enactment fields before publishing |
| Session ids | Nevada OpenStates ids are **80–83**; NELIS paths are `80th2019` … `83rd2025` |
