#!/usr/bin/env python3
"""Shared water-relevance search terms helpers for NELIS and OpenStates.

Both collectors MUST read discovery terms from
config/issues/nevada-water-scarcity.yaml (`search_terms`) and apply the same
local title/summary filter (`is_water_relevant_text`) so corpora stay aligned.
"""

from __future__ import annotations

import re

# Used only for the local post-search filter (title / abstract / NELIS summary).
# Keep in sync with the intent of config search_terms: water-policy focus, not
# generic "conservation" agency/org hits.
WATER_TITLE_TERMS = [
    "water",
    "groundwater",
    "colorado river",
    "consumptive use",
    "water rights",
    "irrigation",
    "drought",
    "aquifer",
    "wastewater",
    "reclaimed water",
    "snwa",
    "water conservation",
]


def normalize_bill_identifier(identifier: str | None) -> str:
    """Normalize 'AB 30' / 'AB30' / 'ab30' → 'AB30' for cross-source joins."""
    return re.sub(r"\s+", "", (identifier or "")).upper()


def is_water_relevant_text(title: str | None, *extra_blobs: str | None) -> bool:
    """True when title/summary text is about water (or explicit data-center nexus)."""
    parts = [title or "", *[blob or "" for blob in extra_blobs]]
    blob = " ".join(parts).lower()
    title_l = (title or "").lower()

    if any(term in blob for term in WATER_TITLE_TERMS):
        return True
    # Forum pilot also tracks data-center legislation as a water-demand nexus.
    if "data center" in title_l or "data centers" in title_l:
        return True
    return False
