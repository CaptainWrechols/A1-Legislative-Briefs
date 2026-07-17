# Design Package — Growth, Water Scarcity, and Long-Term Supply in Nevada

- **Issue:** `nevada-04-water-scarcity` · citizen-v1.0 · The Nevada Forum · July 2026
- **Packaged by:** design-packager v2.1
- **Token source:** the Phase 2 Issue Brief sample at
  `templates/phase-2-samples/NV1-Issue-Brief-4-Growth-and-Water-Scarcity-v1.5.pdf`,
  as codified in `config/forum-brand.yaml`. Only the sample's colors, fonts,
  spacing, and module shapes were mirrored — no Phase 2 headings, kicker text,
  or body text was reused.

## Files in this package

| File | Purpose |
|---|---|
| `citizen-brief.html` | Printable front brief — fits 2 letter pages (verified with headless Chrome) |
| `citizen-brief-print.css` | Shared print CSS for the front brief and appendices |
| `appendices/appendices-print.html` | All appendices (README + A–G) in one print document with TOC (~48 letter pages) |

## How to export to PDF

1. Open `citizen-brief.html` (or `appendices/appendices-print.html`) in Chrome,
   Edge, or Firefox.
2. Print → destination **Save as PDF**.
3. Paper size **Letter**, margins **Default** (the stylesheet declares
   `@page { size: letter; margin: 0.6in; }` — do not add extra browser margins).
4. Turn **Headers and footers** off; **Background graphics** on (needed for the
   navy table header rows, stat-card bars, and terracotta accents).

Command-line alternative (same result as verified during packaging):

```bash
google-chrome --headless=new --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=citizen-brief.pdf citizen-brief.html
```

## Page budget

- **Page 1** carries all required essentials: eyebrow header + title,
  "How to use this sheet," the five-card stat strip, the bill-path primer,
  the three history baskets (cards + table), and the "One fair caution" note.
- **Page 2** carries the allowed spillover only: people and process signals,
  "Passed recently (2025)," the six-question grid, and the pointer to the
  appendices.
- Verified at 2 pages exactly with headless Chrome (US Letter, 0.6in margins).
  Body copy stayed at ~9pt; explainers at 8.5pt; table/card text at 8pt.
- No facts were trimmed or deleted; no rewrite notes needed. The brief's
  "Source keys (for reviewers)" section was intentionally omitted from the
  printed pages, as the Citizen Brief Writer's note permits; it remains in
  `citizen-brief.md` for the Citizen Reviewer.

## Visual tokens used (from the Phase 2 sample)

| Token | Value |
|---|---|
| Page background | `#FFFFFF` |
| Navy (title, stat numbers, table headers, top rule) | `#1A2D4F` |
| Secondary navy (card headings, bill labels) | `#2E4A78` |
| Terracotta (section headers, kicker lead, accents, question numbers) | `#C0392B` |
| Terracotta soft tint (under quote-card top bars) | `#E8D5D3` |
| Body / muted text | `#444444` / `#666666` |
| Card borders | `#CCCCCC` |
| Table rules / alternating rows | `#C8CDD6` / `#F4F5F7` |
| Fonts | Arial/Helvetica throughout; Georgia serif only inside history example (quote-style) cards |

The retired website palette (purple `#8659B5`, gold, cream `#F2F0ED`,
Bebas Neue, Libre Baskerville) is not used anywhere.

## Module mapping (Phase 2 module → citizen-brief content)

1. **Eyebrow header** → "THE FORUM" bar, navy rule, own kicker
   ("Citizen Brief · citizen-v1.0 · Water in Nevada · The Nevada Forum ·
   July 2026"), navy title. Reused on the appendices cover with an
   "Citizen Brief Appendices" kicker.
2. **Terracotta section headers** → every section: how-to-use, big picture,
   bill primer, baskets, caution, people signals, passed recently, questions,
   where to look next; also appendix sub-headers.
3. **Quote-style cards → history example cards** → four cards, one flagship
   bill per basket (2021 AB356, 2025 SB36, 2023 SB180, 2021 SJR1): serif
   one-liner + navy `YEAR BILL · OUTCOME` label, terracotta top bar with soft
   pink tint.
4. **Navy-bar stat strip** → five cards: 88 bills / 45 became law / 40 did not
   finish / 4 sessions / 26 of 40 first-stop failures.
5. **Navy-header comparison table** → the three history baskets
   (basket | what it means | more example bills · what happened). The theme
   scorecards render as tables in Appendix B instead — the basket table fit
   the front-brief content better, as the agent spec allows.
6. **Numbered question grid** → six deliberation questions, two-column
   bordered cards with terracotta numbers.
7. **Info card pairs** → "Passed recently (2025)": SB36 and SB276 as a two-up
   card pair with the two remaining 2025 bills in an inline explainer below.

Inline explainers (session, sponsor, water banking, groundwater, State
Engineer, water rights) stay in-section at 8.5pt muted gray, with a thin
terracotta left border for the block-style ones — no endnotes, no glossary.

## Appendices document

- One HTML file, README first, then Appendices A–G, each starting on a new
  page; TOC with anchor links at the top.
- All markdown tables render in the navy-header comparison style with
  alternating rows; `thead { display: table-header-group; }` repeats header
  rows across page breaks (verified on the long vote and sponsor tables).
- All `<!-- pdf-page-break -->` markers from the source markdown are honored.
- Rendered length: ~48 letter pages (many pages allowed for appendices).

## Handoff

> Design Packager finished. Run **Citizen Reviewer**.
