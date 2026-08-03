# New Hampshire data sources

Data-source map for The Forum's New Hampshire citizen legislative reality
briefs. Findings verified live 2026-08-03; **updated 2026-08-03** after building
the collector, when a decisive fact emerged (see the box below).

The New Hampshire General Court is the analogue of Nevada's NELIS. Its site
(`gc.nh.gov`, also reachable as `www.gencourt.state.nh.us`) behaves very
differently from NELIS, so the Nevada collectors do **not** work against it
unchanged (see the inventory at the bottom).

> ## ⚠️ The one fact that shapes everything
>
> **GenCourt — both the live website *and* its public SQL database — only holds
> the _current biennium_ (2025–2026) for bill identity, title, status,
> sponsors, and full text. The only thing it keeps for older years is
> roll-call votes (1999→current).**
>
> Concretely: `billinfo.aspx?id=N` ignores any `sy=` year and always resolves a
> current-biennium bill; the site search only searches the current biennium;
> and the SQL `legislation` / `legislationtext` tables contain only 2025–2026.
> So **bill data for 2020–2024 cannot come from GenCourt** — it must come from
> OpenStates (or an archive). Votes for 2020–2024 *do* come from GenCourt SQL.

---

## TL;DR — what works, what fails, fallbacks

| Route | What it gives | Coverage | Status |
|-------|---------------|----------|--------|
| **Public SQL `rollcallsummary` / `rollcallhistory`** | Roll-call votes (summary + per-member, joined to name/party) | **1999 → current (all target sessions)** | ✅ Authoritative, keyless, reachable from the VM |
| **Public SQL `legislation` / `legislationtext`** | Bill title, status, chapter, sponsors, **full text (all versions)** | **Current biennium only (2025–2026)** | ✅ Keyless; makes the current biennium fully collectable from SQL alone |
| **gc.nh.gov bill pages + site search** | Title/sponsors/status + full text via postback | **Current biennium only** (`sy=` is ignored) | ✅ Works behind the WAF, but redundant with SQL for the current biennium |
| **LegiScan bulk dataset API** | **Complete** bill list + sponsors + history + votes + text refs for a whole session, incl. committee-killed bills | **All sessions, multiple years back** | ✅ **Recommended for 2020–2024.** One ZIP per session -> no rate limits. Needs free `LEGISCAN_API_KEY` |
| **OpenStates v3 API** | Bills, sponsors, abstracts, versions for older sessions | **2017 → 2026** for NH | ⚠️ Works for 2020–2024 but per-bill and rate-limited. Needs `OPENSTATES_API_KEY`. Secondary fallback |
| **SQL roll-call-title search** (keyless older-year discovery) | Older-session bills **that reached a floor vote** | 1999 → current | ✅ Keyless partial for 2020–2024; misses committee-killed bills |
| **Static document paths / bulk table `.txt` files** | — | — | ❌ WAF-blocked/404. Only `Members.txt` is published. Use SQL. |

**Bottom line / the working split the collector uses:**

- **Votes, every year:** GenCourt SQL (`gencourt_sql.rollcall_*`). Authoritative, keyless.
- **Current biennium bills (2025–2026):** GenCourt SQL `legislation` + `legislationtext`. Complete, keyless.
- **Older bills (2020–2024):** **LegiScan bulk datasets** for the complete bill list + metadata/text (preferred), or OpenStates as a fallback; **votes still from SQL**.

### Getting complete older-year data without rate limits — use LegiScan

No *government* source publishes complete historical NH bill *lists* (with
committee-killed bills) programmatically — GenCourt keeps only the current
biennium (plus votes back to 1999), and every database on its SQL server is
current-biennium-only for bill identity. So older-year completeness needs an
outside mirror of the official data. The two reputable options:

- **LegiScan (recommended).** Its **bulk dataset API** returns one ZIP per
  session containing *every* bill, roll call, and person as JSON — including
  bills that died in committee — plus text references. Mirroring all of
  NH 2020–2026 is about **8 API calls total** (`getDatasetList` +
  `getDataset` per session) against a free **30,000-queries/month** key, so
  rate limits are a non-issue. Full text per bill comes from `getBillText`
  (a handful of extra calls, only for issue-relevant bills). Wrapped in
  `collectors/nh/legiscan.py`.
- **OpenStates (fallback).** Complete for 2017→2026 too, but its per-bill API
  is rate-limited. The collector minimises calls (votes come from SQL, not
  OpenStates; discovery is one cached `/bills?q=<term>` per term/session with
  long 429 backoff) and is resumable, but LegiScan's bulk route is simpler and
  faster. Wrapped in `collectors/nh/openstates_backfill.py`.

Either way, **votes always come from GenCourt SQL** — the authoritative
government source — and only bill *identity/metadata/text* for older years comes
from the mirror.

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

## 2. Public SQL Server (votes for all years + the whole current biennium)

The Downloads page links "Public SQL and Data Table Information", documenting a
read-only SQL Server. Port 1433 is reachable from the VM.

- Server `66.211.150.69`, user `publicuser`, password `PublicAccess`, database
  `NHLegislatureDB` (all overridable via `NH_SQL_*` env vars).
- Driver: `pymssql` (in `requirements.txt`).
- `INFORMATION_SCHEMA.TABLES` is not readable by `publicuser`, but named tables
  are `SELECT`-able — including two that are **not** in the public schema PDF.

Coverage by table (verified):

- `rollcallsummary` / `rollcallhistory`: **complete 1999→2026** (all target
  sessions). Authoritative vote source. `rollcallhistory` is one row per member
  per vote; join to `legislators` on `EmployeeNo` for name/party.
- **`legislation`** *(undocumented; the master bill table)*: `LSRTitle`,
  `GeneralStatusCode`, `ChapterNo`, `BillType`, `SubjectCode`, House/Senate
  status codes + dates, `EffectiveDate`, `legislationID`. **Current biennium
  only (2025–2026).**
- **`legislationtext`** *(undocumented)*: full bill text (`HTMLText`, `Text`) for
  every version (Introduced … Chaptered Final). **Current biennium only.**
- `sponsors`: prime/co-sponsors. Current biennium only.
- `docket` (action history): current biennium + ≤2016.
- `legislators`, `committees`, `subject`, `generalstatuscodes`,
  `bodystatuscodes`, `house/senatedistricts`, `county`.

Implication: for **2025–2026**, SQL alone gives discovery (keyword search over
`legislation.LSRTitle`), status, chapter, sponsors, votes, and full text — no
website scraping, no API key. For **2020–2024**, SQL gives votes only.

`collectors/nh/gencourt_sql.py` wraps all of this:
`rollcall_summaries`, `rollcall_ballots`, `search_legislation`,
`search_rollcalls` (keyless older-year voted-bill discovery),
`legislation_record`, `legislation_id`, `bill_text_versions`,
`full_bill_version`, `sponsors_by_legislation_id`, and the code maps.

## 3. gc.nh.gov bill pages (current biennium only; redundant with SQL)

`billinfo.aspx?id=<legislationID>&inflect=2` renders title, sponsors,
committee/status, the **versions** dropdown, and (via an ASP.NET `linkv`
postback) the full text inline. `collectors/nh/gencourt_web.py` wraps this.

**Two hard limits discovered while building the collector:**

- The `sy=<year>` query param is **ignored** — `billinfo.aspx?id=N` always
  resolves a bill in the *current* biennium (its LSR always starts `25-`).
- The site search (`quicksearch.aspx`) only searches the current biennium; the
  year param does not switch sessions.

So the website cannot reach 2020–2024 bills, and for the current biennium it is
redundant with the SQL `legislation`/`legislationtext` tables (which are faster
and need no WAF handshake). The web module is kept for text cross-checks and as
a fallback, but the collector reads current-biennium text from SQL.

**For 2020–2024 bill identity/metadata/text, the source is OpenStates**
(`collectors/nh/openstates_backfill.py`), with votes still taken from SQL.

## 3a. The collector

`collectors/nh/collect.py` ties the sources together, driven by an issue config
(`ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml`):

```bash
ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml python3 -m collectors.nh.collect
```

Per session it discovers bills (SQL `legislation` for the current biennium; SQL
roll-call titles for older voted bills; OpenStates for older committee-killed
bills when a key is present), enriches them (status/chapter/sponsors for the
current biennium; **votes from SQL for every year**), splits HB2 into sections
for each budget cycle, and writes `pass1/bills.json`,
`processed/bills-core.json`, `processed/bill-votes.json`, the HB2 section files,
and a `data-gaps.json` recording anything that needs the OpenStates key.

Verified end to end on an example water issue: 51 bills across 2020–2026, real
votes attached (e.g. HB1264 2020 passed 23–1), and HB2 2025 split into 204
sections with 22 flagged water-relevant.

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
