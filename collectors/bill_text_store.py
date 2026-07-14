#!/usr/bin/env python3
"""Download and fingerprint official bill text files for integrity checks."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import requests

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore


USER_AGENT = "ForumLegislativeBrief/1.0"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_filename(*parts: str) -> str:
    raw = "_".join(parts)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", raw)


def extract_pdf_text(path: Path, max_pages: int = 3) -> str:
    if PdfReader is None or not path.exists():
        return ""
    try:
        reader = PdfReader(str(path))
        chunks: list[str] = []
        for page in reader.pages[:max_pages]:
            chunks.append(page.extract_text() or "")
        return re.sub(r"\s+", " ", " ".join(chunks)).strip()
    except Exception:  # noqa: BLE001
        return ""


def identifier_in_blob(identifier: str, blob: str) -> bool:
    """True if AB30 / AB 30 style identifier appears in text/filename/url."""
    norm = re.sub(r"\s+", "", identifier or "").upper()
    if not norm:
        return False
    spaced = re.sub(r"([A-Z]+)(\d+)", r"\1 \2", norm)
    blob_u = (blob or "").upper()
    return norm in re.sub(r"\s+", "", blob_u) or spaced in blob_u


def download_bill_file(
    url: str,
    dest: Path,
    *,
    session: requests.Session | None = None,
    timeout: int = 120,
) -> dict:
    """Download one official file; return local path, sha256, bytes, extracted text preview."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT}
    if session is None:
        response = requests.get(url, timeout=timeout, headers=headers)
    else:
        response = session.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    content = response.content
    dest.write_bytes(content)
    text_preview = ""
    if dest.suffix.lower() == ".pdf":
        text_preview = extract_pdf_text(dest)
        preview_path = dest.with_suffix(".txt")
        if text_preview:
            preview_path.write_text(text_preview + "\n", encoding="utf-8")
    return {
        "url": url,
        "local_path": str(dest),
        "sha256": sha256_bytes(content),
        "bytes": len(content),
        "http_status": response.status_code,
        "content_type": response.headers.get("Content-Type", ""),
        "text_preview": text_preview[:2000],
        "text_preview_path": str(dest.with_suffix(".txt")) if text_preview else None,
    }
