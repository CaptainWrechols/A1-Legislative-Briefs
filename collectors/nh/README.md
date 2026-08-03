# New Hampshire collectors

**Isolated** adapters for the New Hampshire General Court — they do not touch the
Nevada / NELIS collectors. Full details and coverage are in
[`docs/nh-data-sources.md`](../../docs/nh-data-sources.md).

> **The fact that shapes everything:** GenCourt (website *and* SQL) only holds
> the **current biennium (2025–2026)** for bill identity/title/status/text; only
> **roll-call votes** go back to 1999. So 2020–2024 bill metadata/text comes from
> OpenStates, while votes for every year come from GenCourt SQL.

## Modules

| Module | Purpose |
|--------|---------|
| `collect.py` | **Main entry point.** Config-driven collector: discovers bills + pulls all vote data for one issue across all sessions, picking the right source per year. |
| `gencourt_sql.py` | Read-only client for the public NH SQL database: votes (all years) + `legislation`/`legislationtext`/sponsors (current biennium) + keyword search. |
| `openstates_bulk.py` | **Recommended older-year backfill.** Reads OpenStates *bulk CSV* files you download once (free instant account) and drop in a folder — no API calls, no rate limits, no review queue. Votes still come from SQL. |
| `legiscan.py` | Older-year backfill via LegiScan bulk datasets (one ZIP/session, no rate limits). Needs `LEGISCAN_API_KEY` — note key issuance involves a manual review that can take a while. |
| `openstates_backfill.py` | Older-year backfill via the OpenStates *API* (per-bill, rate-limited). Votes still come from SQL. Needs `OPENSTATES_API_KEY` (issued instantly). |
| `hb2_sections.py` | Split the HB2 omnibus budget trailer into numbered sections and select the issue-relevant ones. |
| `fortiweb.py` | Solve the `gc.nh.gov` FortiWeb anti-bot challenge (used by the web fallback). |
| `gencourt_web.py` | Bill detail + full text via ASP.NET postback (current biennium; fallback/cross-check — SQL is primary). |
| `spike.py` | Original source-proving smoke test (writes samples under `sources/new-hampshire/_spike/`). |

## Quick start

```bash
pip install -r requirements.txt            # brings in pymssql

# Collect one issue end to end (all years):
ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml python3 -m collectors.nh.collect
ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml python3 -m collectors.nh.collect --skip-ballots

# Lower-level checks:
python3 -m collectors.nh.gencourt_sql   # legislation years + HB2 vote counts
python3 -m collectors.nh.fortiweb       # WAF handshake
```

Start from the example config `config/issues/new-hampshire-water-example.yaml`
(a filled-in copy of the template) to see the expected output shape.

## Sources per year (what the collector does)

- **Votes, every year:** `gencourt_sql.rollcall_summaries()` / `rollcall_ballots()`
  — authoritative, keyless, 1999→current.
- **Current biennium bills:** `gencourt_sql.search_legislation()` +
  `legislation_record()` + `full_bill_version()` — title/status/sponsors/text.
- **Older bills (2020–2024):** `gencourt_sql.search_rollcalls()` (keyless, voted
  bills) plus a full backfill for committee-killed bills. Backfill priority:
  local OpenStates bulk CSVs (`openstates_bulk.py`, keyless, no rate limit) →
  LegiScan bulk API (`legiscan.py`) → OpenStates API (`openstates_backfill.py`).
- **HB2 sections:** `hb2_sections.extract_sections()` +
  `match_sections(sections, issue_terms)`. See
  [`docs/nh-hb2-section-workflow.md`](../../docs/nh-hb2-section-workflow.md).

## Env vars

| Var | Default | Purpose |
|-----|---------|---------|
| `NH_SQL_SERVER` | `66.211.150.69` | Public SQL Server host |
| `NH_SQL_PORT` | `1433` | Port |
| `NH_SQL_USER` / `NH_SQL_PASSWORD` | `publicuser` / `PublicAccess` | Public credentials |
| `NH_SQL_DATABASE` | `NHLegislatureDB` | Database |
| `OPENSTATES_API_KEY` | — | Only needed for the OpenStates fallback |

## Guardrails

- Do not invent or split vote counts; HB2 votes are on the whole trailer.
- No advice language in any citizen-facing text.
- Reuse one `requests.Session` and sleep between requests when collecting.
