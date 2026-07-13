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

**Primary — Nevada NELIS (recommended):**

```bash
python collectors/nv_nelis_bills.py
```

This scrapes the Nevada Legislature Information System and typically returns 100+ water-related bills across the last four sessions.

**Supplemental — OpenStates API (optional):**

```bash
export OPENSTATES_API_KEY=your-key-here
python collectors/openstates_bills.py
```

Note: OpenStates full-text search has returned zero Nevada bills in testing; NELIS is the authoritative source.

## Run the brief pipeline after collection

```bash
python collectors/build_brief_pipeline.py
```

This generates synthesis, analysis, executive summary draft, and appendices B–F in `briefs/nevada/water-scarcity/version-0/`.

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
| Zero bills returned | Nevada uses OpenStates session ids **80, 81, 82, 83** (not 2019–2025). See `config/issues/nevada-water-scarcity.yaml` |
| HTTP 401 or 403 | Verify your OpenStates key is active |
