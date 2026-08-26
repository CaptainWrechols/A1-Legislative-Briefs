"""Fetchers for scstatehouse.gov — bill pages, full-text search, votes, roster.

All routes verified live (see docs/sc-data-sources.md): the site serves plain
HTML over GET/POST with no WAF, no login, and no JavaScript requirement.

Guardrails baked in:

* **Soft-fail**: every fetch goes through :func:`soft_get` / :func:`soft_post`,
  which return ``None`` on HTTP errors/timeouts instead of raising, so one
  flaky page never kills a collection run. Callers must record the gap.
* **Politeness**: one shared ``requests.Session``, an identifying User-Agent,
  and a sleep between requests (``SC_FETCH_DELAY`` seconds, default 1.0).
* **Never invent data**: vote counts are parsed verbatim from the vote-history
  table; member ballots come from the official roll-call PDFs; party comes
  from the member roster (vote PDFs list names only).

Run a quick self-check (no collection, ~6 requests):

    python3 -m collectors.sc.scstatehouse
"""

from __future__ import annotations

import io
import os
import re
import time
import html as htmllib

import requests

from . import SESSION_BY_NUMBER

BASE = "https://www.scstatehouse.gov"
# A full browser-style UA is required: scstatehouse.gov sniffs the UA and
# serves a stripped *mobile* page (no roster party markers) to unknown agents.
# The trailing token identifies this research project honestly.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0 "
    "TheForumResearch/1.0"
)
FETCH_DELAY = float(os.environ.get("SC_FETCH_DELAY", "1.0"))
TIMEOUT = int(os.environ.get("SC_FETCH_TIMEOUT", "45"))

_session: requests.Session | None = None
_last_fetch = 0.0


def new_session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def _sess() -> requests.Session:
    global _session
    if _session is None:
        _session = new_session()
    return _session


def _throttle() -> None:
    global _last_fetch
    wait = _last_fetch + FETCH_DELAY - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.time()


def soft_get(url: str, **kw) -> requests.Response | None:
    """GET that returns None instead of raising (soft-fail; caller logs gap)."""
    _throttle()
    try:
        r = _sess().get(url, timeout=TIMEOUT, **kw)
        if r.status_code != 200:
            print(f"  [soft-fail] GET {url} -> {r.status_code}")
            return None
        return r
    except requests.RequestException as exc:
        print(f"  [soft-fail] GET {url} -> {exc}")
        return None


def soft_post(url: str, data: dict, **kw) -> requests.Response | None:
    _throttle()
    try:
        r = _sess().post(url, data=data, timeout=TIMEOUT, **kw)
        if r.status_code != 200:
            print(f"  [soft-fail] POST {url} -> {r.status_code}")
            return None
        return r
    except requests.RequestException as exc:
        print(f"  [soft-fail] POST {url} -> {exc}")
        return None


def _plain(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    fragment = htmllib.unescape(fragment).replace("\xa0", " ")
    return re.sub(r"\s+", " ", fragment).strip()


# ---------------------------------------------------------------------------
# Bill text / status page (static, all sessions back to well before 2020)
# ---------------------------------------------------------------------------

def bill_page_url(session_number: int, bill_number: int | str) -> str:
    path = SESSION_BY_NUMBER[session_number]["scstatehouse_path"]
    n = re.sub(r"[^0-9]", "", str(bill_number))
    return f"{BASE}/{path}/bills/{n}.htm"


def fetch_bill_page(session_number: int, bill_number: int | str) -> dict | None:
    """One static page per bill: status, sponsors, summary, full action history.

    Returns a dict with the raw html plus parsed fields, or None (soft-fail).
    """
    url = bill_page_url(session_number, bill_number)
    r = soft_get(url)
    if r is None:
        return None
    raw = r.text
    txt = _plain(raw)

    def _grab(pattern: str) -> str:
        m = re.search(pattern, txt)
        return m.group(1).strip() if m else ""

    record = {
        "session": session_number,
        "bill_no": f"H{re.sub(r'[^0-9]', '', str(bill_number))}"
        if int(re.sub(r"[^0-9]", "", str(bill_number))) >= 3000
        else f"S{re.sub(r'[^0-9]', '', str(bill_number))}",
        "url": url,
        "summary": _grab(r"Summary:\s*(.+?)(?:\s*HISTORY OF LEGISLATIVE ACTIONS|$)"),
        "sponsors_raw": _grab(r"Sponsors?:\s*(.+?)(?:\s*Document Path|$)"),
        "act_no": _grab(r"\b(A\d+, R\d+, [HS]\d+)\b"),
        "html": raw,
    }
    # Action history lives in a <pre> block: "date  body  action".
    pre = re.search(r"<pre>(.*?)</pre>", raw, re.S)
    actions: list[dict] = []
    if pre:
        body_txt = _plain(pre.group(1))
        for m in re.finditer(
            r"(\d{1,2}/\d{1,2}/\d{4})\s+(House|Senate|Both|--?-?)\s+(.+?)(?=\d{1,2}/\d{1,2}/\d{4}\s+(?:House|Senate|Both|--?-?)|$)",
            body_txt,
        ):
            actions.append({
                "date": m.group(1),
                "body": m.group(2),
                "action": m.group(3).strip(),
            })
    record["actions"] = actions
    return record


# ---------------------------------------------------------------------------
# Full-text discovery search (Pass 1). POST /query.php.
# ---------------------------------------------------------------------------

# Result headers: "Session 123 - (2019-2020) - S 594" for plain bills, but
# "S*401" (asterisk, no space) for ratified/act versions — both must match or
# passed legislation silently vanishes from discovery.
_RESULT_RE = re.compile(
    r"Session\s+(\d{3})\s*-\s*\(\d{4}-\d{4}\)\s*-\s*([HS])[\s*]*(\d+)", re.I
)
# Singular for one hit ("1 match found."), plural otherwise.
_MATCHES_RE = re.compile(r"([\d,]+)\s+match(?:es)? found", re.I)


def fulltext_search(term: str, session_number: int, *, category: str = "LEGISLATION",
                    numrows: int = 100, max_pages: int = 200) -> dict | None:
    """Search full bill text for ``term`` in one session; return every hit.

    Pass 1 rule: keep ALL hits (relevance_terms are a review flag only).

    The result count is per *document* (each bill VERSION is a document), so
    unique bills < total documents. Pagination therefore walks the entire
    document count (``result_pos`` pages until page*numrows >= total) — never
    stopping early just because a page added no new bills.
    """
    hits: list[dict] = []
    total: int | None = None
    seen: set[str] = set()
    for page in range(max_pages):
        r = soft_post(f"{BASE}/query.php", {
            "search": "SEARCH",
            "searchtext": term,
            "category": category,
            "session": str(session_number),
            "conid": "0000",
            "result_pos": str(page * numrows),
            "numrows": str(numrows),
        })
        if r is None:
            return None  # soft-fail: caller records the term/session gap
        raw = r.text
        if total is None:
            m = _MATCHES_RE.search(_plain(raw))
            total = int(m.group(1).replace(",", "")) if m else 0
        # Each result block: "Session 126 - (2025-2026) - H 3226" then
        # "Summary: ..." then a snippet.
        blocks = re.split(r"(?=Session\s+\d{3}\s+-\s+\()", _plain(raw))
        page_docs = 0
        for block in blocks:
            m = _RESULT_RE.match(block.strip())
            if not m:
                continue
            page_docs += 1
            bill_no = f"{m.group(2).upper()}{int(m.group(3))}"
            if bill_no in seen:
                continue
            seen.add(bill_no)
            sm = re.search(r"Summary:\s*(.+?)(?:\.\.\.|$)", block)
            hits.append({
                "session": int(m.group(1)),
                "bill_no": bill_no,
                "summary": sm.group(1).strip()[:300] if sm else "",
                "found_by_term": term,
            })
        if (page + 1) * numrows >= (total or 0) or page_docs == 0:
            break
    return {"term": term, "session": session_number,
            "total_matches": total or 0, "hits": hits}


# ---------------------------------------------------------------------------
# Votes. Bill-level history table is HTML; per-member ballots are PDFs.
# ---------------------------------------------------------------------------

def vote_history(session_number: int, bill_number: int | str) -> list[dict] | None:
    """All recorded roll calls for a bill: motion, chamber vote number, counts.

    Counts are parsed verbatim from the official table — never computed.
    """
    n = re.sub(r"[^0-9]", "", str(bill_number))
    url = f"{BASE}/votehistory.php?type=BILL&session={session_number}&bill_number={n}"
    r = soft_get(url)
    if r is None:
        return None
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", r.text, re.S)
    out: list[dict] = []
    for row in rows:
        cells = [_plain(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if len(cells) < 11 or cells[0] == "Date/Time" or not cells[0]:
            continue
        key_m = re.search(r'KEY=(\d+)', row)
        try:
            counts = [int(c) for c in cells[3:10]]
        except ValueError:
            continue
        out.append({
            "datetime": cells[0],
            "motion": cells[1],
            "vote_no": cells[2],           # e.g. "[H]-679" / "[S]-448"
            "chamber": "House" if cells[2].startswith("[H]") else "Senate",
            "yeas": counts[0],
            "nays": counts[1],
            "not_voting": counts[2],
            "excused_absent": counts[3],
            "present": counts[4],
            "abstain_recused": counts[5],
            "total": counts[6],
            "result": cells[10],
            "ballot_pdf_key": int(key_m.group(1)) if key_m else None,
            "source_url": url,
        })
    return out


_BALLOT_HEADER_RE = re.compile(
    r"(House|Senate) Roll Call Vote Number (\d+).*?"
    r"Yeas:\s*(\d+);\s*Nays:\s*(\d+)", re.S
)
_BALLOT_GROUP_RE = re.compile(
    r"\b(YEAS|NAYS|EXCUSED ABSENCE|NOT VOTING|PRESENT|ABSTAIN(?:/RECUSED)?)\s*-\s*(\d+)\b"
)


def ballot_pdf(key: int) -> dict | None:
    """Per-member ballot from the official roll-call PDF (votehistory.php?KEY=n).

    Names are listed WITHOUT party — attach party from :func:`member_roster`.
    Requires ``pypdf``.
    """
    from pypdf import PdfReader  # lazy: only ballots need it

    r = soft_get(f"{BASE}/votehistory.php?KEY={key}")
    if r is None:
        return None
    try:
        reader = PdfReader(io.BytesIO(r.content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # malformed PDF -> soft-fail, record the gap
        print(f"  [soft-fail] ballot PDF KEY={key}: {exc}")
        return None
    head = _BALLOT_HEADER_RE.search(text)
    groups: dict[str, list[str]] = {}
    marks = list(_BALLOT_GROUP_RE.finditer(text))
    for i, m in enumerate(marks):
        seg = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        # Names are "Last, First M." columns; split on 2+ spaces or newlines.
        names = [n.strip() for n in re.split(r"\n|\s{2,}", seg) if n.strip()]
        groups[m.group(1)] = names
    return {
        "key": key,
        "chamber": head.group(1) if head else None,
        "vote_number": int(head.group(2)) if head else None,
        "yeas": int(head.group(3)) if head else None,
        "nays": int(head.group(4)) if head else None,
        "member_groups": groups,
        "source_url": f"{BASE}/votehistory.php?KEY={key}",
        "note": "names from official PDF; party must be joined from member_roster()",
    }


# ---------------------------------------------------------------------------
# Member roster (party source — vote PDFs have names only)
# ---------------------------------------------------------------------------

def member_roster(chamber: str = "H", session_number: int | None = None) -> list[dict] | None:
    """Current (or historical, via session=) roster with party markers."""
    url = f"{BASE}/member.php?chamber={chamber}"
    if session_number:
        url += f"&session={session_number}"
    r = soft_get(url)
    if r is None:
        return None
    out = []
    for m in re.finditer(
        r'class="membername"\s+href="/member\.php\?code=(\d+)[^"]*"[^>]*>'
        r'\s*(?:Representative|Senator)?\s*([^<]+?)\s*</a>\s*\(([A-Z])\)',
        r.text,
    ):
        out.append({"code": m.group(1), "name": m.group(2).strip(),
                    "party": m.group(3), "chamber": chamber})
    return out


if __name__ == "__main__":
    print("scstatehouse.gov self-check (6 requests)")
    page = fetch_bill_page(126, 4025)
    print(f"  bill page H4025 (126th): summary={page['summary'][:60]!r} "
          f"actions={len(page['actions'])}" if page else "  bill page FAILED")
    res = fulltext_search("minimum wage", 126, numrows=50, max_pages=1)
    print(f"  search 'minimum wage' 126th: total={res['total_matches']} "
          f"first_page_hits={len(res['hits'])}" if res else "  search FAILED")
    votes = vote_history(126, 4025)
    print(f"  vote history H4025: {len(votes)} roll calls; "
          f"latest={votes[0]['motion']!r} {votes[0]['yeas']}-{votes[0]['nays']}"
          if votes else "  votes FAILED")
    roster = member_roster("H")
    parties = {}
    for mm in roster or []:
        parties[mm["party"]] = parties.get(mm["party"], 0) + 1
    print(f"  House roster: {len(roster or [])} members, parties={parties}")
