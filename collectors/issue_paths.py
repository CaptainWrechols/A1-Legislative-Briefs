"""Resolve per-issue paths from an issue config (multi-issue support).

Every collector imports its paths from here instead of hardcoding one issue.
The active issue is selected with the ISSUE_CONFIG environment variable:

  ISSUE_CONFIG=config/issues/nevada-water-scarcity.yaml  python collectors/pass1_bills.py
  ISSUE_CONFIG=config/issues/nevada-housing.yaml         python collectors/pass1_bills.py

Default: config/issues/nevada-water-scarcity.yaml (the first issue).

Derived layout (created on demand):

  sources/{state}/{issue_slug}/pass1|pass2|processed|raw|verification
  working/{state}/{issue_slug}/
  briefs/{state}/{issue_slug}/citizen-v1/
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

ISSUE_CONFIG = Path(
    os.environ.get("ISSUE_CONFIG", "config/issues/nevada-water-scarcity.yaml")
)

if not ISSUE_CONFIG.exists():
    raise SystemExit(
        f"Issue config not found: {ISSUE_CONFIG} "
        "(set ISSUE_CONFIG=config/issues/<state>-<issue>.yaml)"
    )

_cfg = yaml.safe_load(ISSUE_CONFIG.read_text(encoding="utf-8"))

STATE: str = _cfg["state"]
ISSUE_SLUG: str = _cfg["issue_slug"]
ISSUE_ID: str = _cfg["issue_id"]
ISSUE_TITLE: str = _cfg["issue_title"]

SOURCES = Path("sources") / STATE / ISSUE_SLUG
WORKING = Path("working") / STATE / ISSUE_SLUG
BRIEF_DIR = Path("briefs") / STATE / ISSUE_SLUG / "citizen-v1"

PASS1 = SOURCES / "pass1"
PASS2 = SOURCES / "pass2"
PROCESSED = SOURCES / "processed"
RAW = SOURCES / "raw"


def load_config() -> dict:
    return dict(_cfg)
