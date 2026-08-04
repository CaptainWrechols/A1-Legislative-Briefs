"""Fetch HB2 full text for every budget cycle from government sources.

GenCourt only keeps the *current* biennium in SQL/`billinfo`, but older HB2
texts are still published as static HTML or LBA/agency chapter PDFs:

  2021  https://gc.nh.gov/legislation/2021/HB0002.html          (Chapter 91)
  2023  LBA chapter-law PDF (Chapter 79) — see KNOWN_PDF_SOURCES
  2025  SQL ``legislationtext`` (current biennium)

This module tries sources in order, caches the raw bytes under
``sources/new-hampshire/_spike/raw/`` (or a caller-supplied dir), and returns
HTML or plain text suitable for ``hb2_sections.extract_sections`` /
``extract_sections_from_plain``.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

from . import fortiweb, gencourt_sql as db

# Static GenCourt HTML for older biennia (verified live).
KNOWN_HTML_SOURCES = {
    2021: "https://gc.nh.gov/legislation/2021/HB0002.html",
}

# Chaptered final PDFs hosted by NH agencies (verified live).
KNOWN_PDF_SOURCES = {
    2023: [
        "https://gc.nh.gov/LBA/Budget/operating_budgets/2024-2025/House_Finance/HB%202%20Chapter%20Law.pdf",
        "https://www.dhhs.nh.gov/sites/g/files/ehbemt476/files/documents2/hb2-chapter-79-laws-of-2023.pdf",
    ],
}

# Chapter number of the chaptered final law (for section labels like "79:12").
CHAPTER_NUMBERS = {
    2021: 91,   # Laws of 2021, Chapter 91
    2023: 79,   # Laws of 2023, Chapter 79
}


def _is_html_404(text: str) -> bool:
    title = re.search(r"<title>([^<]+)", text, re.I)
    return bool(title and "404" in title.group(1))


def fetch_hb2_text(session_year: int, *, cache_dir: Path | None = None) -> dict:
    """Return ``{source, format, text/html, url, chapter}`` for one HB2 cycle.

    Raises ``RuntimeError`` if no government source yields usable text.
    """
    cache_dir = Path(cache_dir or "sources/new-hampshire/_spike/raw")
    cache_dir.mkdir(parents=True, exist_ok=True)

    # 1) Current-biennium SQL (full HTML of Introduced; prefer Chaptered if present).
    if session_year in set(db.legislation_years()):
        lid = db.legislation_id("HB2", session_year)
        if lid:
            for label in ("CHAPTERED FINAL VERSION", "Version adopted by both bodies",
                          "Introduced"):
                ver = db.full_bill_version(lid, label)
                if ver and ver.get("html_text") and len(ver["html_text"]) > 10000:
                    path = cache_dir / f"hb2-{session_year}-sql-{label.replace(' ', '_').lower()}.html"
                    path.write_text(ver["html_text"], encoding="utf-8")
                    return {
                        "session_year": session_year,
                        "source": "sql:legislationtext",
                        "format": "html",
                        "url": f"sql://legislationtext/{lid}/{label}",
                        "version_label": label,
                        "chapter": CHAPTER_NUMBERS.get(session_year),
                        "text": ver["html_text"],
                        "cache_path": str(path),
                    }

    session = fortiweb.new_session()

    # 2) Known static HTML.
    html_url = KNOWN_HTML_SOURCES.get(session_year)
    if html_url:
        r = fortiweb.get(session, html_url)
        if not _is_html_404(r.text) and len(r.text) > 10000:
            path = cache_dir / f"hb2-{session_year}-gencourt.html"
            path.write_text(r.text, encoding="utf-8")
            return {
                "session_year": session_year,
                "source": "gencourt:legislation_html",
                "format": "html",
                "url": html_url,
                "version_label": "CHAPTERED FINAL VERSION",
                "chapter": CHAPTER_NUMBERS.get(session_year),
                "text": r.text,
                "cache_path": str(path),
            }

    # 3) Known chapter PDFs (LBA / agency mirrors).
    for pdf_url in KNOWN_PDF_SOURCES.get(session_year, []):
        try:
            if "gc.nh.gov" in pdf_url or "gencourt" in pdf_url:
                r = fortiweb.get(session, pdf_url)
                content = r.content
            else:
                import requests
                content = requests.get(
                    pdf_url, timeout=90,
                    headers={"User-Agent": fortiweb.UA},
                ).content
        except Exception:
            continue
        if not content.startswith(b"%PDF"):
            continue
        from pypdf import PdfReader
        plain = "\n".join(
            (p.extract_text() or "") for p in PdfReader(io.BytesIO(content)).pages
        )
        if len(plain) < 5000:
            continue
        path = cache_dir / f"hb2-{session_year}-chapter.pdf"
        path.write_bytes(content)
        text_path = cache_dir / f"hb2-{session_year}-chapter.txt"
        text_path.write_text(plain, encoding="utf-8")
        return {
            "session_year": session_year,
            "source": "gencourt:lba_or_agency_pdf",
            "format": "plain",
            "url": pdf_url,
            "version_label": "CHAPTERED FINAL VERSION",
            "chapter": CHAPTER_NUMBERS.get(session_year),
            "text": plain,
            "cache_path": str(path),
            "text_cache_path": str(text_path),
        }

    # 4) Generic static HTML probe (may work for future biennia once archived).
    probe = f"https://gc.nh.gov/legislation/{session_year}/HB0002.html"
    try:
        r = fortiweb.get(session, probe)
        if not _is_html_404(r.text) and len(r.text) > 10000:
            path = cache_dir / f"hb2-{session_year}-gencourt.html"
            path.write_text(r.text, encoding="utf-8")
            return {
                "session_year": session_year,
                "source": "gencourt:legislation_html",
                "format": "html",
                "url": probe,
                "version_label": "CHAPTERED FINAL VERSION",
                "chapter": CHAPTER_NUMBERS.get(session_year),
                "text": r.text,
                "cache_path": str(path),
            }
    except Exception:
        pass

    raise RuntimeError(
        f"No government source yielded HB2 full text for {session_year}. "
        f"Tried SQL, known HTML, known PDFs, and {probe}."
    )


if __name__ == "__main__":
    for yr in (2021, 2023, 2025):
        try:
            rec = fetch_hb2_text(yr)
            print(f"{yr}: OK source={rec['source']} format={rec['format']} "
                  f"chars={len(rec['text'])} url={rec['url'][:80]}")
        except Exception as exc:
            print(f"{yr}: FAIL {exc}")
