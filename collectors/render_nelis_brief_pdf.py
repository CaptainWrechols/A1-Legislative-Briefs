#!/usr/bin/env python3
"""Render nelis-preliminary executive-summary.html to a letter-size printable PDF."""

from __future__ import annotations

from pathlib import Path

from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "briefs/nevada/water-scarcity/nelis-preliminary/executive-summary.html"
PDF_PATH = ROOT / "briefs/nevada/water-scarcity/nelis-preliminary/executive-summary.pdf"


def main() -> None:
    if not HTML_PATH.exists():
        raise SystemExit(f"Missing HTML brief: {HTML_PATH}")
    HTML(filename=str(HTML_PATH)).write_pdf(str(PDF_PATH))
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
