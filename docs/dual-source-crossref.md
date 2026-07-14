# Dual-source collection and cross-reference

Goal: pull the **same bill facts** from **NELIS** and **OpenStates**, then diff them so brief writers only cite figures both sources support—or explicitly flag conflicts for human review.

## Pipeline

```text
NELIS search  →  NELIS details  ┐
                               ├─→ reconcile_bill_sources.py → crossref/
OpenStates search → details   ┘
```

| Step | Command | Needs |
|------|---------|-------|
| 1 | `python collectors/nv_nelis_bills.py` | network |
| 2 | `python collectors/nv_nelis_bill_details.py` | network |
| 3 | `python collectors/openstates_bills.py` | `OPENSTATES_API_KEY` |
| 4 | `python collectors/reconcile_bill_sources.py` | local JSON from 1–3 |

Or run Actions → **Collect Nevada Water Bills** (same order; OpenStates can `continue-on-error` if the API is limited).

## Match key

Bills are joined as `{openstates_session}:{identifier}` (example: `82:AB19`).

Identifiers are normalized so OpenStates `AB 19` matches NELIS `AB19`.

NELIS session paths (`82nd2023`) map to OpenStates ids (`82`) via `openstates_session` on stubs / the reconciler map.

## Shared search terms

Both collectors use `config/issues/nevada-water-scarcity.yaml` → `search_terms`, then `collectors/water_relevance.py` so title/summary noise (e.g. generic “conservation” agency bills) is dropped consistently.

## Full bill language

NELIS Session PDFs and OpenStates `versions`/`documents` are downloaded with SHA-256 fingerprints. Run `python collectors/verify_bill_texts.py` and require `verification/bill-text-integrity.md` → Analysis ready before synthesis/analysis agents start.

## What gets compared

- Title token overlap
- Sponsor name sets
- Floor vote yea/nay fingerprints when both sources have vote events
- Signed-into-law inference (NELIS history wording vs OpenStates progress/latest action)
- Presence gaps (only-in-NELIS / only-in-OpenStates, missing actions or votes)

## Authority rule for briefs

1. **Cite NELIS** for official history wording, hearing recommendations, and bill PDF text.
2. **Use OpenStates** to corroborate structured vote/sponsor/action fields and for party when NELIS party lookup is thin.
3. **Do not publish** a contested vote count, sponsor list, or enactment claim until `crossref/summary.md` conflicts for that bill are resolved.

## Smoke tests

```bash
NELIS_DETAIL_LIMIT=3 python collectors/nv_nelis_bill_details.py
OPENSTATES_DETAIL_LIMIT=3 OPENSTATES_RESUME=1 python collectors/openstates_bills.py
python collectors/reconcile_bill_sources.py
```
