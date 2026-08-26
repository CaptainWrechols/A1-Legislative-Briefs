# South Carolina collectors

**Isolated** adapters for the South Carolina General Assembly — they do not
touch the Nevada/NELIS collectors or `collectors/nh/`. Full route details and
live verification are in [`docs/sc-data-sources.md`](../../docs/sc-data-sources.md);
the budget-proviso workflow is in
[`docs/sc-appropriations-proviso-workflow.md`](../../docs/sc-appropriations-proviso-workflow.md).

> **The facts that shape everything:** scstatehouse.gov is fully scrapable —
> static bill pages, HTML vote-history tables, and full-text search work for
> **every session back to 2020** (no WAF, no key, no JavaScript). And South
> Carolina's omnibus budget is **annual** (unlike NH's biennial HB1/HB2): the
> General Appropriations Act carries its policy in **Part IB provisos**, which
> are numbered and captioned — handle them proviso-by-proviso.

## Modules

| Module | Purpose |
|--------|---------|
| `__init__.py` | Canonical registries: the 123rd–126th sessions (numbers, OpenStates ids, site paths) and every General Appropriations cycle 2020→2026 (bill numbers, enacted flags). |
| `universe.py` | **Full-universe sweep** (run once, resumable): every instrument in every session by dense number enumeration — identity, sponsors, complete action history incl. governor action, latest-version full text — plus all chamber roll calls and ratifications, with a four-surface cross-check certification. |
| `collect_issue.py` | Build one issue's complete artifact set (pass1/bills-core/bill-votes/data-gaps + Part IB provisos for every enacted cycle) from the universe + server-side full-text search (cached). |
| `scstatehouse.py` | Fetchers for scstatehouse.gov: static bill pages, full-text discovery search (`query.php`), vote-history tables (counts verbatim), roll-call ballot PDFs (per-member), member roster (the party source). Soft-fail + throttled. |
| `proviso_fetch.py` | Fetch Part IB full text for a budget cycle (enacted `ta` version first, earlier versions as fallback), with on-disk caching. |
| `proviso_sections.py` | Split Part IB into individual provisos (number, agency, caption, text, SC-Code cites), match them to issue terms, write the working outputs. |
| `openstates_bulk.py` | **Recommended OpenStates route**: read locally downloaded bulk CSVs (free instant account, no API calls, no rate limits). Dual-source cross-check for discovery. |
| `openstates_api.py` | OpenStates v3 API fallback (needs `OPENSTATES_API_KEY`; heavily throttled + cached; soft-fails without a key). |
| `verify_completeness.py` | Completeness gate wired to the four SC configs. `--foundation` mode checks config + proviso outputs (passes now); full mode gates issue-chat collection. |
| `spike.py` | Source-proving smoke test (writes samples under `sources/south-carolina/_spike/` and per-issue proviso outputs under `working/south-carolina/`). |

## Quick start

```bash
pip install -r requirements.txt

python3 -m collectors.sc.scstatehouse       # 6-request self-check
python3 -m collectors.sc.spike              # full smoke test (~25 requests)

# The data layer (already collected on this branch; resumable if re-run):
python3 -m collectors.sc.universe           # full sweep, hours
python3 -m collectors.sc.universe --certify-only

# Per-issue artifacts from the universe (search results are disk-cached):
ISSUE_CONFIG=config/issues/south-carolina-<slug>.yaml \
    python3 -m collectors.sc.collect_issue

# Completeness gates:
ISSUE_CONFIG=config/issues/south-carolina-<slug>.yaml \
    python3 -m collectors.sc.verify_completeness --strict          # full gate
```

Issue configs: `config/issues/south-carolina-{growth-infrastructure-roads,
responsive-elected-leaders,rising-cost-of-living,slow-wage-growth}.yaml`
(template: `south-carolina-TEMPLATE.yaml`).

## Sources and their order (the dual-source rule)

1. **OpenStates** (bulk CSV preferred, API fallback) — discovery cross-check
   and structured metadata. Session identifiers: `2019-2020`, `2021-2022`,
   `2023-2024`, `2025-2026`.
2. **scstatehouse.gov** — the official source: bill pages
   (`/sess{N}_{years}/bills/{n}.htm`), full-text search, vote-history tables,
   ballot PDFs, member rosters.
3. **budget.php + appropriations indexes** — Part IB proviso text per cycle
   (`…/appropriations{year}/tap1b.htm` for enacted budgets).
4. **SC Code of Laws** (`/code/statmast.php`) — background statute text.

## Pass 1 / Pass 2 rules (carried over from NV + NH)

- **Pass 1** = keyword discovery. Keep **all** hits; `relevance_terms` only
  set a review flag. The scstatehouse search is **exact-phrase, no stemming**
  ("term limit" → 0 hits, "term limits" → 9) — configs carry both forms.
- **Pass 2** = detail on known bills only (bill page + vote history per bill).
- Dual-source where possible: official site + OpenStates.
- Soft-fail flaky pages; record every gap in `data-gaps.json`.
- **Never invent vote counts** — they are parsed verbatim from the official
  vote-history table. Ballot PDFs list names only; **party comes from the
  member roster scrape** (`member_roster()`), exactly like the NV roster join.
- Appropriations roll calls attach to the **whole bill, never one proviso**.

## Env vars

| Var | Default | Purpose |
|-----|---------|---------|
| `SC_FETCH_DELAY` | `1.0` | Seconds between scstatehouse.gov requests |
| `SC_FETCH_TIMEOUT` | `45` | Per-request timeout (seconds) |
| `SC_OPENSTATES_BULK_DIR` | `sources/south-carolina/_bulk/openstates` | Where the downloaded bulk CSVs live |
| `OPENSTATES_API_KEY` | — | Only for the API fallback |
| `OPENSTATES_MIN_INTERVAL` | `7` | Seconds between OpenStates API calls |

## Guardrails

- No advice language in any citizen-facing text.
- `constituent_proposals` in the configs are Forum **process input** — label
  `[P-xxx]` in briefs, never present as verified fact.
- Do not re-scrape Nevada or New Hampshire; keep those collectors unchanged.
- The desktop User-Agent in `scstatehouse.py` matters: unknown agents get a
  stripped mobile page with no roster party markers.
