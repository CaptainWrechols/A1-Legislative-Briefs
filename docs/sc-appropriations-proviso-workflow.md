# SC appropriations proviso-by-proviso workflow

South Carolina's **General Appropriations Act** is the state's annual omnibus
budget (unlike New Hampshire's biennial HB1/HB2 pair). Its policy content
rides in **Part IB — "temporary provisions"**, hundreds of numbered, captioned
**provisos** organised by agency. A single year's enacted Part IB holds well
over a thousand provisos (FY 2025-26: 1,354; FY 2024-25: 1,406 across 97
agency sections).

For a citizen issue brief we therefore cannot treat the appropriations act as
one item — we pull out **only the provisos that touch the issue** and analyse
each on its own. This is the SC analogue of the NH HB2 section workflow
([`nh-hb2-section-workflow.md`](nh-hb2-section-workflow.md)), with one
pleasant upgrade: SC provisos carry stable numbers **and human-readable
captions**, so matching and citation are much cleaner.

## Where proviso text comes from

`collectors/sc/proviso_fetch.py` pulls Part IB from the official budget pages
(hub: [`scstatehouse.gov/budget.php`](https://www.scstatehouse.gov/budget.php)).
Each fiscal year has an index page per **version**, and every version's Part IB
is one static HTML file:

    https://www.scstatehouse.gov/{session_path}/appropriations{year}/{ver}p1b.htm

Version prefixes, in enactment order (the fetcher prefers `ta`, falling back
down the list, soft-fail all the way):

| Prefix | Version |
|--------|---------|
| `wm` | Ways & Means Committee |
| `hp` | Passed by the House |
| `sf` | Senate Finance Committee |
| `sp` | Passed by the Senate |
| `hr` | Returned to the House |
| `cr` | Conference Report |
| `ta` | **Ratified / enacted** |

The Ways & Means index (`wm{yy}ndx.php`) and its proviso-summary PDFs remain
available per cycle for cross-checking committee-stage changes.

Cycles in scope are canonical in `collectors/sc/__init__.py::BUDGET_CYCLES`
(FY 2020-21 → FY 2026-27, with bill numbers H 5201 / H 4100 / H 5150 /
H 4300 / H 5100 / H 4025 / H 5126).

> **FY 2020-21 caveat (COVID):** H 5201 was never enacted — it died in
> committee and the state ran on continuing resolution H 3411 plus CARES acts.
> The latest available Part IB for that cycle is the Senate Finance version
> (`sf20`), which was never law. A brief must either skip the cycle or state
> explicitly that no budget was enacted that year.

## Parsing (proven live)

`collectors/sc/proviso_sections.py::extract_provisos()` splits the file on the
verified markup:

```html
<a name="s1"><b>SECTION</a> 1 - H630 - DEPARTMENT OF EDUCATION</b>
<b> … 1.1. … </b>(SDE: Appropriation Transfer Prohibition) The amounts appropriated…<br>
```

- **Agency sections** are anchored `<a name="s{N}">` with header
  `SECTION {N} - {agency code} - {AGENCY NAME}`. Section 117 is "General
  Provisions" (203 provisos in FY 2024-25) — many cross-cutting policy riders
  live there.
- **Provisos** are bold-numbered `{section}.{n}.` followed by a parenthesised
  caption `(AGY: Short Title)` and the verbatim text.

Each record captures: `proviso` (e.g. `1.1`, `117.32`), `section`,
`agency_code`, `agency_name`, `caption`, `text` (verbatim), and
`sc_code_cites` (every `Section XX-XX-XXXX` SC-Code citation in the text).

## The per-issue workflow

For each of the four SC citizen issues:

1. **Fetch Part IB** for each cycle in scope
   (`proviso_fetch.fetch_part1b(year, cache_dir=…)`; raw HTML is cached so
   extraction is reproducible without re-hitting the site).
2. **Extract all provisos** with `extract_provisos()`.
3. **Select relevant provisos** with `match_provisos(provisos, terms)`, where
   `terms` = the issue config's `relevance_terms` plus every
   `constituent_proposals[].match_terms`. Err toward recall — a human prunes
   the matches (generic terms like "pay" or "housing" pull in hundreds; that
   is intentional at this stage).
4. **Attach votes at the bill level only**
   (`scstatehouse.vote_history(session, bill_number)`). Roll calls are
   recorded on the **whole appropriations bill** (H 4025 2025: 383 of them,
   including per-amendment floor votes), never on one proviso. A brief must
   say a vote was on the whole budget (or a specific amendment), not on the
   proviso. **Never invent or split vote counts.**
5. **Write outputs** with `proviso_sections.write_outputs()`.

## Output paths

Per issue, under the standard `working/{state}/{issue}` tree:

```
working/south-carolina/{issue}/proviso-sections.json   # all provisos, machine-readable
working/south-carolina/{issue}/proviso-sections.md     # all provisos, human review
working/south-carolina/{issue}/proviso-relevant.json   # issue-matched + matched_terms
```

When multiple cycles are collected in an issue chat, namespace by year and
keep the flat files pointing at the most recent enacted cycle:

```
working/south-carolina/{issue}/provisos/2021/proviso-sections.{json,md}
working/south-carolina/{issue}/provisos/2022/…
…
```

Raw fetched HTML is cached under `sources/south-carolina/_spike/raw/` during
proving; real runs should cache under
`sources/south-carolina/{issue}/raw/part1b-{year}-{version}.htm`.

## Worked proof (spike output, 2026-08-25)

`python3 -m collectors.sc.spike` produced, for FY 2025-26 (H 4025, ratified
`ta` version):

- **1,354 provisos** extracted; summary in
  `sources/south-carolina/_spike/part1b-summary.json`; raw HTML cached in
  `sources/south-carolina/_spike/raw/part1b-2025-ta.htm`.
- **383 roll calls** on the bill itself
  (`sources/south-carolina/_spike/part1b-bill-rollcalls.json`) — including
  the House conference-report adoption 88–25 and per-amendment votes.
- Per-issue matched sets written to `working/south-carolina/{issue}/`:
  growth-infrastructure-roads 291, responsive-elected-leaders 231,
  rising-cost-of-living 544, slow-wage-growth 649 (high recall by design;
  issue chats prune by hand).

## Citizen-facing language note

Any brief text drawn from a proviso must stay descriptive: state what the
proviso *does*, for which agency, in which fiscal year, and how the chamber
voted on the overall bill (or a named amendment). Do **not** use advice
language ("should", "must support/oppose") and do **not** attribute a
whole-bill vote to a single proviso. Proviso numbers are stable within a year
but renumber across years — cite as "FY 2025-26 proviso 117.32", never a bare
number.
