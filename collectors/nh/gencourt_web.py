"""Fetch NH bill detail pages and full bill text from gc.nh.gov.

The bill-status app is ASP.NET WebForms behind the FortiWeb WAF. Two things
this module proves out and wraps:

  * ``billinfo.aspx?id=<legislationID>&inflect=2`` renders the bill's title,
    sponsors, committee/status, and the list of *versions* (Introduced ...
    Chaptered) and amendments.
  * The full text of a version is not a static URL; it is loaded by an ASP.NET
    ``__doPostBack`` on the version link (``rVersions$ctlNN$linkv``). Posting
    that back with the page's ``__VIEWSTATE`` returns the bill text inline,
    where each section is anchored by ``<a name="Chapt{N}"></a>``.

``legislationID`` for the current biennium comes from ``gencourt_sql`` (docket
-> sponsors). For older sessions it must come from the site search or
OpenStates -- see ``docs/nh-data-sources.md``.
"""

from __future__ import annotations

import html
import re

import requests

from . import fortiweb

BILLINFO = "https://gc.nh.gov/bill_status/billinfo.aspx"


def _hidden(page: str, name: str) -> str:
    m = re.search(r'id="' + re.escape(name) + r'"[^>]*value="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else ""


def _clean(fragment: str) -> str:
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(fragment)).strip()


def fetch_billinfo(session: requests.Session, legislation_id: int) -> str:
    url = f"{BILLINFO}?id={legislation_id}&inflect=2"
    return fortiweb.get(session, url).text


def parse_billinfo(page: str) -> dict:
    """Pull title/sponsors/status and the version list out of a billinfo page."""
    def field(label: str) -> str:
        m = re.search(label + r"\s*</span>\s*(?:<[^>]+>\s*)*([^<]+)", page)
        return html.unescape(m.group(1)).strip() if m else ""

    # The version dropdown is an ASP.NET repeater; grab the <select> whose
    # placeholder option is "Select a Bill Version".
    versions = []
    m = re.search(
        r'<select[^>]*>\s*<option[^>]*>[^<]*Select a Bill Version.*?</select>',
        page,
        re.S | re.I,
    )
    if m:
        for vid, label in re.findall(
            r'<option[^>]*value="(\d+)"[^>]*>([^<]+)</option>', m.group(0)
        ):
            versions.append({"version_id": vid, "label": html.unescape(label).strip()})

    text = re.sub(r"<[^>]+>", " ", page)
    text = re.sub(r"[ \t]+", " ", html.unescape(text))

    def near(label: str) -> str:
        m = re.search(re.escape(label) + r"\s*([^\n]{0,120})", text)
        return m.group(1).strip() if m else ""

    return {
        "title": near("Title:").split("Sponsors")[0].strip(" :"),
        "sponsors": near("Sponsors:").split("LSR Number")[0].strip(" :"),
        "lsr_number": near("LSR Number:").split("General Status")[0].strip(" :"),
        "general_status": near("General Status:").split("Chapter")[0].strip(" :"),
        "chapter_number": near("Chapter Number:").split("House")[0].strip(" :"),
        "versions": versions,
    }


def fetch_version_text(
    session: requests.Session, legislation_id: int, version_index: int = 0
) -> str:
    """Return the full inline HTML for a bill version via the linkv postback.

    ``version_index`` selects the entry in the versions dropdown
    (0 = Introduced). The returned HTML contains the operative text with
    ``<a name="Chapt{N}">`` section anchors.
    """
    url = f"{BILLINFO}?id={legislation_id}&inflect=2"
    page = fortiweb.get(session, url).text
    target = f"ctl00$pageBody$rVersions$ctl{version_index:02d}$linkv"
    data = {
        "__EVENTTARGET": target,
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": _hidden(page, "__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": _hidden(page, "__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": _hidden(page, "__EVENTVALIDATION"),
        "__LASTFOCUS": "",
    }
    resp = session.post(
        url,
        data=data,
        headers={"User-Agent": fortiweb.UA, "Referer": url},
        timeout=90,
    )
    resp.raise_for_status()
    return resp.text


if __name__ == "__main__":
    s = fortiweb.new_session()
    # HB2 2025 legislationID resolved via SQL during the spike.
    info = parse_billinfo(fetch_billinfo(s, 1188))
    print("title:", info["title"][:80])
    print("versions:", [v["label"] for v in info["versions"]])
