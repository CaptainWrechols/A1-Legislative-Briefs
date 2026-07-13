# How to Run Collectors

This guide walks you through collecting legislative data for the Nevada water scarcity pilot issue.

## Prerequisites

1. Python 3.12 or newer installed
2. OpenStates Application Programming Interface key from https://openstates.org/accounts/profile/
3. This repository cloned to your computer

## One-time setup

```bash
cd a1-legislative-briefs
pip install -r requirements.txt
```

## Run the bill collector locally

**Mac or Linux:**

```bash
export OPENSTATES_API_KEY=your-key-here
python collectors/openstates_bills.py
```

**Windows Command Prompt:**

```cmd
set OPENSTATES_API_KEY=your-key-here
python collectors\openstates_bills.py
```

The collector:

1. Runs **per-term full-text search** (`q=water`, etc.) with pagination retries and partial results on timeouts
2. Applies a **local water-relevance filter** (OpenStates full-text is broader than NELIS title/summary search — see troubleshooting)
3. **Enriches each relevant bill** with `actions`, `votes`, and `sponsorships`
4. Writes derived files: `bill-actions.json`, `bill-votes.json`, `bill-sponsors.json`, `bill-legislative-progress.json`

Note: OpenStates can be flaky (502/504). If results are empty, run `python collectors/diagnose_openstates.py` and re-run later, or use the NELIS collector as a discovery fallback.

## Diagnose OpenStates API (recommended first step)

If collection returns zero bills, run the diagnostic before changing config:

```bash
export OPENSTATES_API_KEY=your-key-here
python collectors/diagnose_openstates.py
```

Output:

```
sources/nevada/water-scarcity/verification/openstates-diagnostic.json
sources/nevada/water-scarcity/verification/openstates-diagnostic.txt
```

### Run diagnostic via GitHub Actions

1. Confirm `OPENSTATES_API_KEY` is set under Settings → Secrets and variables → Actions.
2. Go to the **Actions** tab.
3. Select **Diagnose OpenStates Nevada**.
4. Click **Run workflow**.
5. Download the `openstates-nevada-diagnostic` artifact when the run completes.

The workflow runs the diagnostic, then runs `openstates_bills.py` with the fetch-all strategy, and uploads both reports.

## Expected output files

```
sources/nevada/water-scarcity/
├── manifest.json
├── raw/                          (downloaded PDFs and pages)
└── processed/
    ├── bills-combined.json
    ├── bill-actions.json
    ├── bill-votes.json
    ├── statute-links.json
    └── agency-documents.json
```

## Generate appendix table from collected bills

```bash
python collectors/json_to_appendix.py
```

Output: `briefs/nevada/water-scarcity/version-0/appendix-a-bills.md`

## Run via GitHub Actions (cloud)

**Diagnose OpenStates (start here if bills are empty):**

1. Actions → **Diagnose OpenStates Nevada** → Run workflow.

**Full collection:**

1. Add `OPENSTATES_API_KEY` as a repository secret (Settings → Secrets and variables → Actions).
2. Go to the **Actions** tab.
3. Select **Collect Nevada Water Bills**.
4. Click **Run workflow**.

## After collecting data

Run the agent pipeline in order. See `agents/README.md`.

1. Data Scraper (or use collector scripts above)
2. Data Verifier
3. Synthesizer
4. Analyzer
5. Data Formatter
6. Brief Writer
7. Editor
8. Tone Editor
9. General Formatter
10. Final Reviewer

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Missing OPENSTATES_API_KEY` | Set the environment variable before running |
| `python not found` | Reinstall Python with "Add to PATH" checked |
| Zero bills returned | Run `python collectors/diagnose_openstates.py` first. Nevada uses OpenStates session ids **80, 81, 82, 83** (not 2019–2025). See `config/issues/nevada-water-scarcity.yaml` |
| OpenStates returns far more bills than NELIS | Expected: OpenStates `q=` searches **full bill text**; NELIS matches titles/summaries. The collector writes all hits to `bills-search-candidates.json` and water-relevant bills to `bills-combined.json`. |
| Votes/sponsors empty | Confirm the latest collector ran (detail enrichment). Check `bill-votes.json` / `bill-sponsors.json` and `bills_with_vote_events` in `manifest.json`. |
| HTTP 401 or 403 | Verify your OpenStates key is active |
