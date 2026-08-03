"""Solve the FortiWeb anti-bot JavaScript challenge on gc.nh.gov.

The New Hampshire General Court site (gc.nh.gov / www.gencourt.state.nh.us)
sits behind a FortiWeb WAF. A first request to almost any page returns a tiny
HTML page containing Dean-Edwards-packed JavaScript instead of the real
content. That script:

  1. base64-decodes a token into a hex string,
  2. POSTs it back to the same path as ``?<cookie-name>=<hex>`` with a body of
     ``fwb_dat=<base64 of the original request>``,
  3. the WAF responds with ``Set-Cookie: <cookie-name>=...`` and the real page.

Subsequent requests that carry the cookie are served normally. This module
replicates that handshake with ``requests`` so the rest of the NH collectors
can treat gc.nh.gov like an ordinary site.

This is *not* a CAPTCHA and involves no rate-limit evasion; it only performs
the same benign handshake a browser does. Be polite: reuse one ``Session`` and
sleep between requests during real collection.
"""

from __future__ import annotations

import base64
import re
from urllib.parse import urlsplit

import requests

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

_PACKED_RE = re.compile(
    r"eval\(function\(p,a,c,k,e,d\).*?\}\('(?P<p>.*)',(?P<a>\d+),(?P<c>\d+),"
    r"'(?P<k>.*?)'\.split\('\|'\)",
    re.DOTALL,
)


def _to35(c: int) -> str:
    return "0123456789abcdefghijklmnopqrstuvwxy"[c]


def unpack(source: str) -> str | None:
    """Reverse a Dean Edwards ``p,a,c,k,e,d`` packed script."""
    m = _PACKED_RE.search(source)
    if not m:
        return None
    payload, base, count = m.group("p"), int(m.group("a")), int(m.group("c"))
    words = m.group("k").split("|")

    def token(idx: int) -> str:
        def enc(c: int) -> str:
            head = "" if c < base else enc(c // base)
            c = c % base
            return head + (chr(c + 30) if c > 34 else _to35(c))

        return enc(idx)

    out = payload
    for i in range(count - 1, -1, -1):
        if i < len(words) and words[i]:
            out = re.sub(r"\b" + re.escape(token(i)) + r"\b", words[i], out)
    return out


def is_challenge(text: str) -> bool:
    """True if ``text`` is a FortiWeb challenge page rather than real content."""
    return "eval(function(p,a,c,k,e,d)" in text and len(text) < 20000


def _solve(session: requests.Session, url: str, challenge_html: str) -> None:
    js = unpack(challenge_html)
    if js is None:
        raise RuntimeError("challenge page did not contain packed JS")
    param = re.search(r'var\s+str1\s*=\s*"([^"]+)"', js).group(1)
    which = re.search(r'str1\s*\+\s*"="\s*\+\s*\w+\((\w+)\)', js).group(1)
    token_b64 = re.search(r"var\s+" + which + r'\s*=\s*"([^"]+)"', js).group(1)
    # The site's decode() is a standard base64-decode followed by unescape().
    token = base64.b64decode(token_b64).decode("latin-1")
    send_data_b64 = re.search(r'"fwb_dat="\s*\+\s*"([^"]+)"', js).group(1)
    path = re.search(r'var\s+url\s*=\s*"([^"]+)"', js).group(1)

    parts = urlsplit(url)
    post_url = f"{parts.scheme}://{parts.netloc}{path}?{param}={token}"
    session.post(
        post_url,
        data="fwb_dat=" + send_data_b64,
        headers={"Content-Type": "text/html", "User-Agent": UA},
        timeout=60,
    )


def get(session: requests.Session, url: str, *, max_solves: int = 6, **kw) -> requests.Response:
    """GET ``url`` through the WAF, solving the challenge as needed.

    The WAF rotates several challenge variants; a couple are not parseable, so
    on a parse failure we simply request a fresh challenge and try again.
    """
    kw.setdefault("timeout", 60)
    kw.setdefault("headers", {})
    kw["headers"].setdefault("User-Agent", UA)
    r = session.get(url, **kw)
    attempts = 0
    while is_challenge(r.text) and attempts < max_solves:
        attempts += 1
        try:
            _solve(session, url, r.text)
        except Exception:
            r = session.get(url, **kw)
            continue
        r = session.get(url, **kw)
    if is_challenge(r.text):
        raise RuntimeError(f"still challenged after {attempts} solves: {url}")
    return r


def new_session() -> requests.Session:
    """A pre-warmed session that already holds the WAF cookie."""
    s = requests.Session()
    for _ in range(4):
        try:
            get(s, "https://gc.nh.gov/")
            break
        except Exception:
            continue
    return s


if __name__ == "__main__":
    s = new_session()
    print("cookies:", s.cookies.get_dict())
    r = get(s, "https://gc.nh.gov/downloads/")
    print("downloads page:", r.status_code, len(r.text), "bytes")
