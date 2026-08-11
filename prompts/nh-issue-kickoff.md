# Kickoff prompt — New Hampshire issue lege brief (copy, edit the CAPITALIZED lines, paste)

Upload with this prompt: **the issue's Phase 2 constituent proposal grid**
(the editable "Grid View for Legislators" .docx). Everything else the agent
needs is in the repository — including the OpenStates bulk session CSVs
(2020–2024) already committed under `sources/new-hampshire/_bulk/`.

Prerequisite: the NH housing template PR must be merged to `main` before
starting (it carries `templates/lege-brief/`, `collectors/export_docx_lege_brief.py`,
and the pipeline scripts referenced below).

---

Model: Fable 5. Confirm in your first reply. If you are not Fable 5, stop.
Repo: https://github.com/CaptainWrechols/A1-Legislative-Briefs — start from `main`.

## This chat = ONE New Hampshire issue only

ISSUE_TITLE: PROPERTY TAXES AND REVENUE NEEDS IN NEW HAMPSHIRE   ← edit
ISSUE_SLUG: property-taxes                                        ← edit
ISSUE_ID: new-hampshire-02-property-taxes                         ← edit
PROPOSAL GRID: the attached .docx — use only this issue's grid section and
encode every proposal row (title, frequency, notes, outcome) into the issue
config as `constituent_proposals`.

## Mission

Produce the complete issue packet in the **finalized lege-brief format**,
modeled exactly on the housing packet
(`briefs/new-hampshire/housing-affordability/citizen-v2/` is the exemplar;
its `PACKAGE.md` documents the reuse recipe). The New Hampshire housing brief
is the template: match its architecture, formats, and verification standards
exactly — only content and copy differ.

## Required steps (in order)

1. **Issue config** — copy `config/issues/new-hampshire-housing-affordability.yaml`
   to `config/issues/new-hampshire-{ISSUE_SLUG}.yaml`: same sessions
   (2020→2026) and HB2 omnibus block; `search_terms` / `relevance_terms`
   fitted to this issue (mind SQL substring traps — see the housing config's
   comments); `constituent_proposals` encoded from the attached grid;
   issue-appropriate `affected_rsa_chapters`.
2. **Collect** — `ISSUE_CONFIG=... python3 -m collectors.nh.collect` (keyless;
   the bulk CSVs cover 2020–2024, the state SQL database covers votes and
   2025–2026), then `verify_completeness --strict`. Soft-fail flaky pages;
   document gaps.
3. **Dispositions** — adapt the housing working scripts
   (`working/new-hampshire/housing-affordability/build-bulk-dockets.py`,
   `build-dispositions.py`, `fetch-current-dockets.py`) into
   `working/new-hampshire/{ISSUE_SLUG}/`: official dockets for every bill,
   evidence-backed disposition for every bill, zero unresolved.
4. **Certification** — adapt `certify-universe.py` with a wide-net vocabulary
   for this issue; sweep all 5,467 bills in the 2020–2024 universe; human-review
   every candidate; add real misses as `supplement:universe-certification`;
   record every exclusion with a category. The packet may not claim
   completeness without this artifact.
5. **HB2 analysis** — always include the budget-trailer analysis:
   `working/new-hampshire/{ISSUE_SLUG}/hb2-sections.json` + `.md`
   (hand-curated, section-level, plain language, exclusion audit trail; votes
   are on the whole trailer, never per section). Page 1 of the brief must
   carry an "Also in the budget bill (HB2)" section (or an explicit
   none-found statement).
6. **Curate + analyze** — curation map (plain_topic / theme / relevance tier
   for every bill), evidence pack, reality map with a **passing programmatic
   fact-check** (adapt `fact-check-reality-map.py`). Complete the sponsor
   layer from the bulk sponsorship files (first-listed = prime where the flag
   is absent), as the housing scripts do.
7. **The lege brief** — write
   `briefs/new-hampshire/{ISSUE_SLUG}/citizen-v2/lege-brief.md` in the exact
   housing architecture (WHAT THIS BRIEF COVERS + 4 stat cards → HB2 section →
   CLOSEST TO LAW → PROVEN SUPPORT → ALREADY LAW → LITTLE TRACTION YET →
   MOVEMENT/NONE → FEDERAL OVERLAP → Policy Spotlights on the grid's proposals
   with viability-grouped bullets → topic glossary → legislative process
   glossary). **Copy the LEGISLATIVE PROCESS GLOSSARY verbatim from the
   housing lege-brief.md** — it is intentionally identical across NH briefs.
   Build with:
   `python3 collectors/export_docx_lege_brief.py --source .../lege-brief.md
   --out .../NH1-{Issue}-Lege-Brief.docx --footer "NH1 {Issue} Legislative Brief v1.0"`.
   The format authority is `templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx`;
   never restyle by hand.
8. **Appendices** — adapt `build-appendices-nh.py`: A bills · B themes ·
   C votes with party splits · D sponsors · E paths · F data limits ·
   **G bill-by-bill grid (Year | Bill | Title/subject | Prime sponsor |
   House vote | Senate vote | Governor — honest voice-vote labels, never
   invented tallies)** · H HB2 sections · I claim-to-source map +
   certification. Build `appendices-print.html`, `appendices.docx`, and the
   **Master Appendix** (`NH1-{Issue}-Master-Appendix.docx` + `.pdf`).
9. **Verify** — automated reviewer scans (no advice language; every cited
   bill exists in the pack; every vote pair matches the official record, with
   division-vote exceptions documented); LibreOffice page checks; visual
   comparison against the template.
10. **Ship** — branch `cursor/nh-{ISSUE_SLUG}-lege-brief-...`, commit per
    pipeline stage, push often, draft PR with page screenshots of the brief
    and appendix G embedded.

## Hard rules

- No advice language anywhere in citizen-facing output (should / must /
  recommend / urge as advocacy). Descriptive statements of legal requirements
  are fine.
- No invented votes, parties, sponsors, or bills — every claim traces to the
  collected record; voice/division outcomes are labeled as such.
- HB2 votes are on the whole trailer; never attribute one to a section.
- "Never filed" claims require the universe certification.
- Do not modify the housing packet, the template file, or shared collectors
  except documented per-issue knobs. One issue per chat.

## When done, report

Bill counts (universe / collected / policy set / laws), certification verdict,
the per-proposal spotlight findings, deliverable list with page counts, and
the PR link.
