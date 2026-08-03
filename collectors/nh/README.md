# New Hampshire collectors (foundation)

Thin, **isolated** adapters for the New Hampshire General Court. They stand up
NH data access without touching the Nevada / NELIS collectors. Full details and
coverage are in [`docs/nh-data-sources.md`](../../docs/nh-data-sources.md).

> Status: **foundation only.** Sources are proven and sample artifacts are
> generated. No citizen briefs and no full collection yet.

## Modules

| Module | Purpose |
|--------|---------|
| `fortiweb.py` | Solve the `gc.nh.gov` FortiWeb anti-bot challenge and hold the WAF cookie. |
| `gencourt_sql.py` | Read-only client for the public NH SQL database (roll-call votes for all sessions; docket/sponsors for the current biennium). |
| `gencourt_web.py` | Fetch bill detail pages and full bill text (ASP.NET version postback). |
| `hb2_sections.py` | Split the HB2 omnibus budget trailer into numbered sections. |
| `spike.py` | Smoke-test all routes and write sample artifacts. |

## Quick start

```bash
pip install -r requirements.txt            # brings in pymssql

# Prove the WAF handshake
python3 -m collectors.nh.fortiweb

# Prove SQL votes for each budget cycle
python3 -m collectors.nh.gencourt_sql

# Run the full spike (writes samples under sources/new-hampshire/_spike/)
python3 -m collectors.nh.spike
```

## What the routes give you

- **Votes (all sessions 1999→current):** `gencourt_sql.rollcall_summaries()` and
  `rollcall_ballots()`. This is the authoritative, non-invented vote source.
- **Bill text (all sessions):** `gencourt_web.fetch_version_text()`. Needs the
  numeric `legislationID` — from SQL for the current biennium
  (`gencourt_sql.resolve_legislation_id()`), or the site search / OpenStates for
  older sessions.
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
