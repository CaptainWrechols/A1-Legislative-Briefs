# HB2 section-by-section extraction workflow

New Hampshire's **HB2** is the omnibus *budget policy trailer* that rides
alongside **HB1** (the operating budget) in every budget biennium (2021, 2023,
2025, …). Where a normal bill has one subject, HB2 bundles dozens or hundreds of
unrelated policy changes into numbered sections. For a citizen issue brief we
therefore cannot treat HB2 as one item — we must pull out **only the sections
that touch the issue** and analyse each on its own.

This document defines how that is done and where the outputs live. It is
designed now (per the NH foundation mission) so full collection can follow once
the four issues are chosen.

## Where HB2 sections come from

`collectors/nh/hb2_fetch.py` pulls the full bill from **government sources**,
trying in order:

| Cycle | Source (verified) |
|-------|-------------------|
| Current biennium (e.g. 2025) | SQL `legislationtext` (Chaptered Final) |
| 2021 | `https://gc.nh.gov/legislation/2021/HB0002.html` (Laws of 2021, Chapter 91) |
| 2023 | LBA chapter-law PDF `gc.nh.gov/LBA/Budget/.../HB 2 Chapter Law.pdf` (Laws of 2023, Chapter 79), with a DHHS mirror as fallback |

`collectors/nh/hb2_sections.py` then splits the text. Introduced HTML uses
`<a name="Chapt{N}">` anchors; chaptered final text (HTML or PDF) uses
`{chapter}:{N}` labels (e.g. `79:26`, `91:9`).

Legacy note — the live `billinfo` postback path
(`collectors/nh/gencourt_web.fetch_version_text()`) still works for the
*current* biennium. In that inline HTML each operative section is marked by an
anchor:

```html
<a name="Chapt9"></a><span>9&nbsp;New Paragraph; Water Management and
Protection; Fill and Dredge In Wetlands; Definitions.&nbsp;Amend RSA 482-A:2 …</span>
```

`collectors/nh/hb2_sections.extract_sections()` splits on `<a name="Chapt{N}">`
and, for each section, records:

- `section` — the section number `N`
- `heading` — the short caption (text up to the first period)
- `affected_rsas` — every `RSA <chapter>:<section>` cited in the section
- `text` — the full operative text (no vote counts, nothing invented)

This anchor pattern was verified stable on HB2 2025 (204 sections). The same
routine should be run against 2021 and 2023 once their `legislationID`s are
resolved.

## The per-issue workflow

For each of the four citizen issues (names TBD from the user):

1. **Fetch HB2 text** for each budget cycle in scope (2021, 2023, 2025).
2. **Extract all sections** with `extract_sections()`.
3. **Select the relevant sections** with
   `hb2_sections.match_sections(sections, issue_terms)`, where `issue_terms`
   come from the issue config's `relevance_terms` plus any RSA chapters the
   issue is known to live in. A human reviews the matches — HB2 headings are
   terse, so err toward recall and prune by hand.
4. **Attach votes** from the SQL roll-call source
   (`gencourt_sql.rollcall_summaries("HB2", year)` /
   `rollcall_ballots(...)`). Votes are recorded on **HB2 as a whole**, not per
   section, so a brief must say the vote was on the whole budget trailer, not on
   the individual section. **Never invent or split vote counts.**
5. **Write outputs** with `hb2_sections.write_outputs()`.

## Output paths

Per issue and cycle, under the standard `working/{state}/{issue}` tree:

```
working/new-hampshire/{issue}/hb2-sections.json     # all sections, machine-readable
working/new-hampshire/{issue}/hb2-sections.md       # all sections, human review
working/new-hampshire/{issue}/hb2-relevant.json     # only issue-matched sections + matched_terms
```

When multiple budget cycles are in scope, namespace by year:

```
working/new-hampshire/{issue}/hb2/2021/hb2-sections.{json,md}
working/new-hampshire/{issue}/hb2/2023/hb2-sections.{json,md}
working/new-hampshire/{issue}/hb2/2025/hb2-sections.{json,md}
```

Raw fetched HTML is cached alongside the spike samples under
`sources/new-hampshire/_spike/raw/` during proving; for real runs it should be
cached under `sources/new-hampshire/{issue}/raw/hb2-{year}-{version}.html` so
extraction is reproducible without re-hitting the WAF.

The JSON `note` field reminds writers that HB2 is an omnibus trailer and that
vote counts are on the whole bill.

## Worked example (spike output)

`python3 -m collectors.nh.spike` produced, for HB2 2025 (`legislationID` 1188,
Introduced version):

- **204 sections** extracted to
  `sources/new-hampshire/_spike/hb2-2025/hb2-sections.{json,md}`.
- Example issue-relevant section: **Section 9 — "New Paragraph; Water Management
  and Protection; Fill and Dredge In Wetlands; Definitions"**, affecting
  `RSA 482-A:2`. A water/environment issue would keep this section; a housing
  issue would drop it.
- HB2 floor roll calls available per cycle: 2021 → 42, 2023 → 17, 2025 → 45
  (`sources/new-hampshire/_spike/hb2-rollcalls-by-cycle.json`).

## Citizen-facing language note

Any example text drawn from HB2 for a brief must stay descriptive: state what a
section *does* to which RSA and how the chamber voted on the overall trailer.
Do **not** use advice language ("should", "must support/oppose") and do **not**
attribute a whole-bill vote to a single section.
