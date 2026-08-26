# South Carolina data sources

Data-source map for The Forum's South Carolina citizen legislative reality
briefs. All findings **verified live 2026-08-25** while building
`collectors/sc/` (the spike samples are under `sources/south-carolina/_spike/`).

South Carolina's legislature site (`scstatehouse.gov`) is the analogue of
Nevada's NELIS and New Hampshire's GenCourt — and it is by far the friendliest
of the three: **no WAF, no login, no JavaScript requirement, static HTML for
everything back well past 2020**.

> ## The two facts that shape everything
>
> 1. **scstatehouse.gov is fully scrapable for every target session.** Static
>    bill pages, HTML vote-history tables with verbatim counts, full-text
>    search, and member rosters all work over plain GET/POST — for the 123rd
>    (2019-2020) through the 126th (2025-2026) alike. There is no NH-style
>    "current biennium only" wall and no NELIS-style rate fragility.
> 2. **The omnibus budget is ANNUAL, and its policy lives in Part IB
>    provisos.** Unlike NH's biennial HB1/HB2, South Carolina enacts a
>    General Appropriations Act every year; the policy riders are numbered,
>    captioned provisos in Part IB ("temporary provisions"), served as one
>    static HTML file per version. Seven cycles are in scope (2020→2026), of
>    which six are enacted — **FY 2020-21 was never enacted** (COVID;
>    continuing resolution).

---

## TL;DR — what works, what fails, fallbacks

| Route | What it gives | Coverage | Status |
|-------|---------------|----------|--------|
| **Bill pages** `/sess{N}_{years}/bills/{n}.htm` | Status, sponsors, summary, act number, full action history (with journal page links), veto actions | **All sessions in scope** (and further back) | ✅ Static HTML, one GET per bill |
| **Full-text search** `POST /query.php` (`category=LEGISLATION`) | Keyword discovery over full bill text per session, with bill number + summary + snippet | All sessions in scope | ✅ Works; paginated (`result_pos`); **exact-phrase, no stemming** — see traps |
| **Vote-history table** `votehistory.php?type=BILL&session=&bill_number=` | Every recorded roll call on a bill: date, motion, chamber vote number, yeas/nays/NV/excused/present/abstain, result | All sessions in scope | ✅ HTML table; counts verbatim; H4025 shows 383 roll calls |
| **Ballot PDFs** `votehistory.php?KEY=n` | Per-member ballot for one roll call | All sessions in scope | ✅ PDF, parses with `pypdf`; **names only, no party** |
| **Member rosters** `member.php?chamber=H|S` | Names, districts, **party (D/R)**; historical sessions via `session=` | Current + historical | ✅ The party source (NV-style roster join). Needs a browser UA — see traps |
| **Budget hub** `budget.php` → `gab{bill}.php` → `{ver}p1b.htm` | Part IB proviso full text per cycle and version | FY 2019-20, FY 2021-22 → FY 2026-27 enacted (`tap1b.htm` verified for all) | ✅ Static HTML; 1,354 provisos extracted from FY 2025-26 |
| **SC Code of Laws** `/code/statmast.php`, `/code/title{N}.php` | Statute text for background | Current | ✅ Static HTML |
| **OpenStates bulk CSV** (downloaded once) | Complete bills + sponsors + abstracts + votes per session, incl. committee-killed bills | All four sessions | ✅ **Recommended cross-check/backfill.** Free instant account to download; then keyless, no rate limit (`collectors/sc/openstates_bulk.py`) |
| **OpenStates v3 API** | Same, per-bill | All four sessions | ⚠️ Works but rate-limited (~10/min, 500/day free); needs `OPENSTATES_API_KEY` (not currently set on the VM). Fallback only (`collectors/sc/openstates_api.py`) |

**Bottom line / the working split the collectors use:**

- **Discovery (Pass 1):** scstatehouse full-text search per term per session,
  cross-checked against OpenStates bulk CSVs when on disk (dual-source rule).
- **Detail (Pass 2, known bills only):** one bill page + one vote-history GET
  per bill from scstatehouse; ballot PDFs only for votes a brief will cite.
- **Party:** roster scrape (`member_roster()`), joined to ballot names.
- **Budget provisos:** enacted `tap1b.htm` per cycle, split by
  `collectors/sc/proviso_sections.py`.

## Sessions 2020 → current (resolved and live-checked)

South Carolina runs **two-year sessions** (numbered General Assemblies); bill
numbers persist across both years. "Back to 2020" = the 123rd onward, because
2020 is the second year of the 123rd.

| Session | Years | OpenStates identifier | scstatehouse path segment |
|---------|-------|-----------------------|---------------------------|
| 123rd | 2019–2020 | `2019-2020` | `sess123_2019-2020` |
| 124th | 2021–2022 | `2021-2022` | `sess124_2021-2022` |
| 125th | 2023–2024 | `2023-2024` | `sess125_2023-2024` |
| 126th | 2025–2026 | `2025-2026` | `sess126_2025-2026` |

- OpenStates jurisdiction: **"South Carolina"** (v3 path segment `sc`); each
  session is a "YYYY-YYYY Regular Session" and the identifier is the year span
  (verified against the OpenStates scraper metadata).
- The registry lives in `collectors/sc/__init__.py` (`SESSIONS`) and was
  checked live against the `billsearch.php` session dropdown
  (`sources/south-carolina/_spike/session-mapping.json` — all four match).
- Bill numbering convention: House bills ≥ 3000, Senate bills < 3000, so a
  bare bill number is unambiguous within a session.

## The General Appropriations Act (annual omnibus) — proven

Registry: `collectors/sc/__init__.py` (`BUDGET_CYCLES`). Full workflow:
[`sc-appropriations-proviso-workflow.md`](sc-appropriations-proviso-workflow.md).

| FY | Bill | Session | Enacted Part IB (`tap1b.htm`) |
|----|------|---------|-------------------------------|
| 2020-21 | H 5201 | 123rd | ❌ **never enacted** — COVID; H 5201 died in committee; the state ran on continuing resolution H 3411 + CARES acts (H 5202, H 3210, H 4014). Latest Part IB version is Senate Finance (`sf20`) |
| 2021-22 | H 4100 | 124th | ✅ verified live |
| 2022-23 | H 5150 | 124th | ✅ verified live |
| 2023-24 | H 4300 | 125th | ✅ verified live |
| 2024-25 | H 5100 | 125th | ✅ verified live (1,406 provisos across 97 agency sections) |
| 2025-26 | H 4025 | 126th | ✅ verified live (1,354 provisos; 383 roll calls on the bill) |
| 2026-27 | H 5126 | 126th | ✅ verified live |

(The FY 2019-20 act, H 4000, also has an enacted `tap1b.htm`, but it predates
the 2020 scope; treat as optional context.)

## The universe sweep (full data layer, collected 2026-08-25)

`collectors/sc/universe.py` swept the complete number space of all four
sessions — **15,817 instruments** — plus every chamber roll call and every
ratification. Certified **PASS** by cross-checking four independent official
surfaces against each other (`sources/south-carolina/_universe/verification/`):

| Session | Bills/resolutions | Floor roll calls | Ratifications | With full text |
|---|---|---|---|---|
| 123rd | 3,897 | 1,683 | 188 | 3,897 (100%) |
| 124th | 3,898 | 2,485 | 272 | 3,898 (100%) |
| 125th | 3,976 | 2,382 | 253 | 3,976 (100%) |
| 126th | 4,046 | 2,329 | 276 | 4,044 (+2 "Reserved" placeholder numbers, never filed) |

Why enumeration is provably complete: SC assigns numbers densely per chamber
desk (Senate from 1, House from 3001); every instrument has a static page; the
sweep stops only after 100 consecutive misses past the last hit and records
interior unused numbers. Cross-checks all pass: every roll call's bill and
every ratified act joins to an enumerated bill; every ratified bill carries
governor-action evidence on its own page.

Data layout under `sources/south-carolina/_universe/{session}/`:
`bills.jsonl.gz` (full records **including latest-version full text**),
`bills-index.json` (browsable, no text), `rollcalls.json` (all floor roll
calls, verbatim counts + ballot-PDF keys), `ratifications.json`,
`unused-numbers.json`.

Per-issue artifacts are then built locally from the universe by
`collectors/sc/collect_issue.py` (Pass 1 discovery via server full-text search
+ local full-text/title scans, bills-core, bill-votes, data-gaps, and Part IB
provisos for every enacted cycle).

### What the state does NOT publish (documented, never invented)

- **Committee vote tallies.** Committee pages publish membership and meeting
  videos; bill histories record committee *outcomes* verbatim ("Committee
  report: Favorable with amendment"). No tally tables exist to collect.
- **Roll calls for voice votes.** Zero roll calls on a reading is a real
  answer, not a gap.
- Earlier-draft texts are one recorded GET away (`versions[].url` per bill);
  the latest-version full text is stored for every bill.
- Per-member ballots are PDFs keyed by `ballot_pdf_key` per roll call,
  fetched on demand; party joins from the member roster.

## Traps discovered while proving the routes

1. **Exact-phrase search, no stemming.** `query.php` finds only the literal
   phrase: "term limit" → 0 hits while "term limits" → 9 (126th session).
   Search-term lists must carry singular AND plural forms of multiword
   phrases. (Local relevance/match term matching is substring-based, so the
   singular alone suffices there.)
2. **User-Agent sniffing.** Unknown UAs get a stripped *mobile* page — which,
   among other things, drops the roster's party markers. `scstatehouse.py`
   sends a full browser-style UA with an honest research token appended.
3. **Result-count phrasing.** Search results say "1 match found." (singular)
   vs "14 matches found." — the parser handles both.
4. **Ballot PDFs have no party.** Per-member roll-call PDFs list names only;
   party is joined from the roster scrape — the same pattern as Nevada.
5. **Roll calls are sparse for minor bills.** Many committee-killed bills have
   zero recorded roll calls (SC uses voice votes heavily); an empty
   vote-history table is a real answer, not a parse failure. Never infer or
   invent counts.
6. **robots.txt** disallows only images/dashboard/sys paths — legislation,
   votes, and budget paths are permitted. Keep `SC_FETCH_DELAY` ≥ 1s anyway.
7. **Ratified bills carry an asterisk in search results** (`S*401`, not
   `S 401`). A parser that only accepts the spaced form silently drops
   *passed* legislation from discovery — the worst possible bias. Found when
   a page said "Documents 1 - 100" but only 66 blocks parsed.
8. **Chamber vote lists zero-pad Senate bills** (`S 0001`); bill pages use the
   unpadded form (`S1`). Normalize before joining.
9. **`numrows` above 100 is not honored** by query.php (a 500-row request
   returned ~221 rows while paging by 500 — which would skip documents).
   Paginate at `numrows=100` exactly, and walk the full *document* count:
   result totals are per document (bill **version**), not per bill, so a page
   can add zero new bills without being the end.
10. **Broad-term searches are slow server-side** (~26-60s per page for terms
   like "transportation"). The local full-text scan over the universe JSONL
   covers the same ground instantly on latest-version text; the server search
   is kept for earlier-version coverage and as the independent cross-check.
11. **Two history formats.** Older bill pages use a fixed-width `<pre>` block
   (Body column sometimes blank, wrapped continuation lines); newer pages use
   an HTML table. Parse both; never regex a flattened blob (rows merge).

## Blockers / manual steps

- **`OPENSTATES_API_KEY` is not set** on the VM (checked). Not required for
  the primary routes; needed only for the API fallback. Free + instant at
  open.pluralpolicy.com. Add via Cursor Dashboard → Cloud Agents → Secrets.
- **OpenStates bulk CSVs require an account to download** (free, instant).
  Download the four SC session archives once from
  [open.pluralpolicy.com/data/session-csv](https://open.pluralpolicy.com/data/session-csv/)
  and unzip into `sources/south-carolina/_bulk/openstates/{session-id}/`.
  Until then, scstatehouse.gov alone is sufficient for discovery; record the
  missing cross-check in `data-gaps.json`.
- No LegiScan key either (`LEGISCAN_API_KEY` unset); not needed for SC given
  the above, so it is not part of the SC source order.

---

## Collectors inventory — what applies to SC and what does not

Which existing `collectors/` code can serve South Carolina and which is welded
to another state's systems. SC work is built as **new, isolated adapters under
`collectors/sc/`**; nothing outside it was modified, so Nevada and New
Hampshire are unaffected.

**Does NOT apply to SC (left untouched):**

| Code | Why not |
|------|---------|
| `collectors/nh/gencourt_sql.py`, `fortiweb.py`, `gencourt_web.py`, `hb2_*.py`, `collect.py`, `verify_completeness.py`, `legiscan.py`, `openstates_*.py` (nh) | NH GenCourt SQL database, FortiWeb WAF handshake, and HB2 anchors — none exist for SC. SC has no public SQL server; it doesn't need one (the website covers all years). |
| `pass1_subject_index.py`, `enrich_abstracts.py`, `pass2_nelis.py`, `pass2_committee_votes.py`, `pass2_committee_yeas.py`, `pass2_party_roster.py`, `pass2_sponsors.py`, `pass2_text_diff.py`, `pass2_repair_committee_minutes.py` | Entirely NELIS (`leg.state.nv.us`) tabs/PDFs/rosters. |
| `pass1_bills.py`, `pass2_bills.py`, `pass2_common.py` | NELIS session-path maps, `AB/SB` prefixes, Assembly/Senate labels, NELIS action phrases. SC equivalents live in `collectors/sc/scstatehouse.py`. |

**Reusable for SC (unchanged, pointed at SC configs when issue chats run):**

| Code | Note |
|------|------|
| `issue_paths.py` | Already resolves `sources/{state}/{slug}` from `ISSUE_CONFIG`; works with the SC issue YAMLs as-is (used by `collectors/sc/verify_completeness.py`). |
| `pass2_build_core.py` | Pure JSON merge; works once SC upstream JSON exists. |
| `pass2_attach_party.py` | Roster→ballot JSON join; SC roster has name+party, fits after name-key normalisation. |
| `export_docx.py`, `export_docx_brief.py`, `export_brief_html.py` etc. | Markdown→docx/html assemblers; legislature-agnostic apart from branding/session labels externalised per issue. |
| `pass2_openstates.py` | Generic except a hardcoded jurisdiction URL; the SC package has its own thin API client instead (`openstates_api.py`). |

**Patterns carried over (reimplemented, not imported):** NH's
`openstates_bulk.py` (bulk-CSV ingestion) and `verify_completeness.py` (strict
gate) were adapted into the SC package; NV's roster-party join and
Pass 1/Pass 2 discipline are encoded in `scstatehouse.py`'s API surface.
