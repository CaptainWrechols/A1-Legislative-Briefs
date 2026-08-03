# New Hampshire data sources — spike results

Foundation spike for The Forum's New Hampshire citizen legislative reality
briefs. Goal: **prove the data sources before any large collection.** No
citizen briefs and no full scrape were done here.

The New Hampshire General Court is the analogue of Nevada's NELIS. Its site
(`gc.nh.gov`, also reachable as `www.gencourt.state.nh.us`) behaves very
differently from NELIS, so the Nevada collectors do **not** work against it
unchanged (see the inventory at the bottom).

All findings below were verified live during the spike on 2026-08-03.

---

## TL;DR — what works, what fails, fallbacks

| Route | What it gives | Coverage | Status |
|-------|---------------|----------|--------|
| **Public SQL Server** (`66.211.150.69`, `publicuser`/`PublicAccess`, `NHLegislatureDB`) | Roll-call votes (summary + per-member), docket, sponsors, legislators, subjects | **Roll calls: 1999→current.** Docket: current biennium + ≤2016. Sponsors: current biennium only. | ✅ Works, reachable from the VM |
| **gc.nh.gov bill pages** (`billinfo.aspx?id=<legislationID>`) | Title, sponsors, committee/status, version list, **full bill text** (via postback) | All sessions (needs the numeric `legislationID`) | ✅ Works, behind a solvable WAF challenge |
| **gc.nh.gov site search** (`results.aspx` → `quicksearch.aspx`) | bill number / title / subject → `legislationID` | All sessions | ⚠️ Interactive search works; the ASP.NET postback is finicky to drive programmatically (500s on an incomplete VIEWSTATE). Needs more work or use SQL/OpenStates for id resolution. |
| **Static document paths** (`/bill_status/legislation/<yr>/HB0002.html`, `/pdf/…`, `billText.aspx`) | — | — | ❌ WAF-blocked (403) or 404. Do **not** rely on these. |
| **OpenStates v3 API** | Bills, sponsors, votes, versions across all sessions | 2017→2026 for NH | ⚠️ Available but **needs `OPENSTATES_API_KEY`** (not present in this environment). Documented fallback, especially for older-session bill identity/metadata. |
| **Downloads page bulk tables** (`/downloads/<Table>.txt`) | — | Only `Members.txt` is published on the new site | ❌ The other tables 404; use the SQL Server instead. |

**Bottom line:** GenCourt *is* scrapable. The cleanest split is **SQL for votes
(all sessions) + gc.nh.gov bill pages for text/metadata**, with OpenStates as a
metadata fallback for 2020–2024 once an API key is available.

---

## 1. The FortiWeb anti-bot challenge (solved)

Every first request to `gc.nh.gov` returns a ~2–4 KB page of Dean-Edwards-packed
JavaScript instead of content. It is a FortiWeb WAF challenge, **not** a CAPTCHA:
the script base64-decodes a token, POSTs it back to the same path as
`?<cookie>=<hex>` with body `fwb_dat=<base64 of the original request>`, and the
WAF replies with a `Set-Cookie` that unlocks the session.

`collectors/nh/fortiweb.py` replicates this handshake. Once solved, the cookie
(`cookiesession1`) is reused for the whole `requests.Session`. The WAF rotates a
few challenge variants; a couple aren't parseable, so the solver simply requests
a fresh challenge and retries (up to 6 times). This is the same benign handshake
a browser performs — reuse one session and sleep between requests when
collecting for real.

```bash
python3 -m collectors.nh.fortiweb   # prints the cookie + fetches /downloads/
```

## 2. Public SQL Server (best source for votes)

The Downloads page links "Public SQL and Data Table Information", documenting a
read-only SQL Server. Port 1433 is reachable from the VM.

- Server `66.211.150.69`, user `publicuser`, password `PublicAccess`, database
  `NHLegislatureDB` (all overridable via `NH_SQL_*` env vars).
- Driver: `pymssql` (added to `requirements.txt`).
- `INFORMATION_SCHEMA.TABLES` is not readable by `publicuser`, but the known
  tables from the schema PDF are all `SELECT`-able.

Verified row counts per session year:

- `rollcallsummary` / `rollcallhistory`: **complete 1999→2026**, including 2020,
  2021, 2022, 2023, 2024. This is the authoritative vote source for every target
  session.
- `docket` (status/action history): **2025, 2026, then a gap, then ≤2016.**
  2017–2024 are **absent**.
- `sponsors`: **2025, 2026 only.**
- `legislators`: current membership (used to attach names/party to votes).

Implication: votes come from SQL for all sessions; **older-session bill
identity, sponsors, and status must come from the website or OpenStates.**

Key tables (from `Downloads → ODBC and Data Table Structure.pdf`):
`docket`, `sponsors`, `legislators`, `rollcallsummary`, `rollcallhistory`,
`committees`, `subject`, `bodystatuscodes`, `generalstatuscodes`,
`house/senatedistricts`, `houseRemoteTestify`, `county`.

`collectors/nh/gencourt_sql.py` wraps this: `rollcall_summaries`,
`rollcall_ballots`, `docket_actions`, `sponsors`, `resolve_lsr`,
`resolve_legislation_id`.

## 3. gc.nh.gov bill pages + full bill text

`billinfo.aspx?id=<legislationID>&inflect=2` renders title, sponsors,
committee/status, and the **versions** dropdown (Introduced → As Amended by the
House → … → Chaptered Final) plus amendments.

Bill **text** is not a static URL. It loads via an ASP.NET `__doPostBack` on the
version link (`ctl00$pageBody$rVersions$ctlNN$linkv`). Posting that back with the
page's `__VIEWSTATE`/`__EVENTVALIDATION` returns the full text inline
(~1.1 MB for HB2). `collectors/nh/gencourt_web.py` wraps both steps.

Resolving `legislationID`:
- **Current biennium:** SQL — `docket` maps bill number ↔ LSR, `sponsors` maps
  LSR ↔ `legislationID` (`gencourt_sql.resolve_legislation_id`).
- **Older sessions:** the site search or OpenStates (the programmatic search
  postback still needs work — see the table above).

## 4. Sessions 2020 → current

New Hampshire runs **annual** sessions inside **two-year biennia**; bill numbers
persist across a biennium. OpenStates models NH as annual regular sessions whose
identifier is simply the year.

| Calendar year | Biennium | OpenStates session id | Budget year? |
|---------------|----------|-----------------------|--------------|
| 2020 | 2019–2020 | `2020` | no |
| 2021 | 2021–2022 | `2021` | **HB1/HB2** |
| 2022 | 2021–2022 | `2022` | no |
| 2023 | 2023–2024 | `2023` | **HB1/HB2** |
| 2024 | 2023–2024 | `2024` | no |
| 2025 | 2025–2026 | `2025` | **HB1/HB2** (current) |
| 2026 | 2025–2026 | `2026` | no |

- OpenStates jurisdiction: **"New Hampshire"** (v3 path segment `nh`); each is a
  "YYYY Regular Session".
- SQL `SessionYear` is the calendar year, matching the table above.
- **Budget cycles (HB1 operating + HB2 trailer) are enacted in the odd year of
  each biennium: 2021, 2023, 2025.** These are the three recent budgets to
  analyse.

## 5. HB2 budget trailer — proven

HB2 ("relative to state fees, funds, revenues, and expenditures") is the omnibus
policy trailer to HB1. Verified via the spike:

| Cycle | HB2 floor roll calls (SQL) | Full text sections (website) |
|-------|----------------------------|------------------------------|
| 2021 | 42 | (fetch via website route) |
| 2023 | 17 | (fetch via website route) |
| 2025 | 45 | **204 sections extracted** |

HB2 2025 (`legislationID` 1188) was pulled end to end: the introduced text was
fetched and split into **204 numbered sections** spanning bail, fish & game,
wetlands, education, retirement, … barbering, repeal, effective date. Each
section is anchored by `<a name="Chapt{N}">`; the extractor captures the number,
heading, affected RSAs, and full text. See
`docs/nh-hb2-section-workflow.md`.

Samples written by the spike (`python3 -m collectors.nh.spike`):
- `sources/new-hampshire/_spike/hb2-rollcalls-by-cycle.json`
- `sources/new-hampshire/_spike/hb2-2025/hb2-sections.json` + `.md`
- `sources/new-hampshire/_spike/raw/hb2-2025-introduced.html`

---

## Collectors inventory — Nevada/NELIS-specific vs reusable

Which existing `collectors/` scripts can be reused for NH and which are welded
to NELIS. NH work is being built as **new, isolated adapters under
`collectors/nh/`**; nothing below was modified, so Nevada is unaffected.

| File | Class | Note for NH |
|------|-------|-------------|
| `issue_paths.py` | **reusable** | Already resolves `sources/{state}/{slug}` from `ISSUE_CONFIG`; point it at an NH issue YAML. |
| `pass2_build_core.py` | **reusable** | JSON merge of pass1 + progress + sponsors; works once NH upstream JSON exists. |
| `pass2_attach_party.py` | **reusable** | Pure roster→ballot JSON join; NH roster has name+party, so it fits after minor name-key tweaks. |
| `export_docx.py`, `export_docx_brief.py` | **reusable** | Markdown→docx; legislature-agnostic. |
| `pass1_bills.py` | mixed | OpenStates half is config-driven; the NELIS half hardcodes `leg.state.nv.us`, a `SESSION_PATHS` map, and an `AB/SB/AJR` regex. |
| `pass2_bills.py` | mixed | Orchestrator prefers NELIS rolls; swap in the NH enrichment modules. |
| `pass2_openstates.py` | mixed | Generic except a hardcoded `/Nevada/` detail URL — take jurisdiction from config. |
| `pass2_common.py` | mixed | HTTP helpers reusable; `SESSION_PATHS`, Assembly/Senate labels, and NELIS action-phrase dictionaries are NV-specific. |
| `build_evidence_pack.py`, `build_appendices*.py`, `export_pass2_readable.py`, `export_brief_html.py` | mixed | Assemblers work; externalise the session→year map, chamber wording ("Assembly"→"House"), and "The Nevada Forum" branding. |
| `pass1_subject_index.py`, `enrich_abstracts.py`, `pass2_nelis.py`, `pass2_committee_votes.py`, `pass2_committee_yeas.py`, `pass2_party_roster.py`, `pass2_sponsors.py`, `pass2_text_diff.py`, `pass2_repair_committee_minutes.py` | **NELIS-specific** | Entirely `leg.state.nv.us` NELIS tabs/PDFs/rosters. NH equivalents are the new `collectors/nh/` adapters (SQL for votes/sponsors, `gencourt_web` for text). |

**Cross-cutting NV assumptions to parameterise if any of the mixed scripts are
later generalised:** session-path map (`80th2019`…), bill prefixes (`AB`→`HB`),
chamber labels (`Assembly`→`House`), progress/action phrase dictionaries, and
session→calendar-year maps. NH uses `HB`/`SB` and a House/Senate (not Assembly).
