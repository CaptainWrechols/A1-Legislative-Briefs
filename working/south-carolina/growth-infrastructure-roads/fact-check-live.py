#!/usr/bin/env python3
"""Independent live fact-check for the growth-infrastructure-roads citizen brief.

Re-verifies the front brief's load-bearing claims against scstatehouse.gov
LIVE (independent of the 2026-08-25 snapshot the brief was built from):

  1. Bill statuses and act numbers for every enacted measure the brief cites.
  2. Every floor vote pair the brief and spotlights cite, verbatim, from the
     live vote-history tables.
  3. Key non-enactment paths (S227 amended-then-died, H5071 recommitted,
     shortline credit's two House passages, RIA 112-0, the 2020 regulation
     resolutions stranded on the calendar).
  4. Proviso numbers, captions, and verbatim dollar figures from the live
     enacted Part IB pages (FY 2021-22, 2024-25, 2025-26, 2026-27).
  5. Background-law claims from the live SC Code of Laws (impact fee act,
     penny-tax chapters, gas user fee phase-in).

Writes working/south-carolina/growth-infrastructure-roads/fact-check-live.json
Respects the >=1s fetch delay via collectors.sc.scstatehouse throttling.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
from collectors.sc import scstatehouse as sc  # noqa: E402
from collectors.sc.proviso_fetch import part1b_url  # noqa: E402
from collectors.sc.proviso_sections import extract_provisos  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def check(name, ok, detail):
    results.append({"check": name, "ok": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " — " + detail)


# ---------------------------------------------------------------- 1+3: bills
# (session, bill_no, expected_act_or_None, [history substrings expected])
BILLS = [
    (126, "S831", "177", ["Act No. 177", "POTHOLE MITIGATION PROGRAM", "CHOICE LANE FACILITIES",
                          "PHASED DESIGN-BUILD", "PUBLIC-PRIVATE PARTNERSHIPS",
                          "INDEPENDENT AUDIT OF THE DEPARTMENT EVERY FOUR YEARS",
                          "fifteen million dollars", "within seven days",
                          "thirty-three percent", "not exceed sixty years"]),
    (124, "S152", "166", ["Act No. 166"]),
    (123, "S259", "163", ["Act No. 163"]),
    (123, "S401", "36", ["Act No. 36"]),
    (124, "H3505", "70", ["Act No. 70"]),
    (126, "H3768", "244", ["Act No. 244"]),
    (126, "H4589", "203", ["Act No. 203"]),
    (126, "S399", "222", ["Act No. 222"]),
    (123, "H4262", "179", ["Act No. 179"]),
    (123, "S217", "146", ["Act No. 146"]),
    (124, "S40", "89", ["Act No. 89"]),
    (124, "S304", "46", ["Act No. 46"]),
    (125, "H4115", "69", ["Act No. 69"]),
    (126, "S227", None, ["Committee report: Favorable with amendment", "Amended"]),
    (126, "H5071", None, ["Recommitted to Committee on Ways and Means"]),
    (124, "H4817", None, ["Read third time and sent to Senate", "Referred to Committee on Finance"]),
    (125, "H3737", None, ["Read third time and sent to Senate", "Referred to Committee on Finance"]),
    (125, "H3075", None, ["Read third time and sent to Senate", "Referred to Committee on Finance"]),
    (123, "S1069", None, ["placed on calendar without reference"]),
    (123, "S1070", None, ["placed on calendar without reference"]),
    (126, "H5363", None, ["Referred to Committee on Ways and Means"]),
    (126, "H5742", None, ["Referred to Committee on Judiciary"]),
]

def strip_tags(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))


for sess, bn, act, needles in BILLS:
    page = sc.fetch_bill_page(sess, bn)
    if page is None:
        check("bill %d:%s live fetch" % (sess, bn), False, "fetch failed")
        continue
    # Search tag-stripped page text: some live pages parse to zero action rows
    # (older <pre> format variant), but the full history is in the raw HTML.
    blob = json.dumps(page, ensure_ascii=False) + " " + strip_tags(page.get("html", ""))
    if act is not None:
        ok = ("Act No. %s" % act) in blob or (page.get("act_no") or "").lstrip("A") == act
        check("bill %d:%s Act %s" % (sess, bn, act), ok,
              "live act_no=%r" % page.get("act_no"))
    for nd in needles:
        if nd.startswith("Act No."):
            continue
        check("bill %d:%s page has %r" % (sess, bn, nd), nd in blob,
              "searched live page text (history/long title)")
    # negative check for non-enacted: no act number
    if act is None:
        check("bill %d:%s NOT enacted" % (sess, bn), not page.get("act_no"),
              "live act_no=%r" % page.get("act_no"))

# ---------------------------------------------------------------- 2: votes
# (session, bill_no, [(yeas, nays, motion_substr)])
VOTES = [
    (126, "S831", [(37, 1, "3rd Reading"), (114, 0, "Passage"), (112, 2, "Conference"), (43, 0, "conference")]),
    (124, "S152", [(43, 1, "2nd"), (41, 3, "3rd"), (67, 28, "Passage")]),
    (123, "S259", [(44, 1, "2nd"), (65, 35, "Passage")]),
    (123, "S401", [(38, 0, "2nd"), (108, 0, "Passage")]),
    (124, "H3505", [(106, 4, ""), (42, 2, "")]),
    (126, "H3768", [(103, 0, "Passage"), (44, 0, "2nd")]),
    (126, "H4589", [(81, 18, ""), (40, 2, ""), (91, 14, "")]),
    (126, "S399", [(44, 0, ""), (107, 0, "Passage")]),
    (123, "H4262", [(108, 2, ""), (32, 6, ""), (104, 1, "")]),
    (123, "S217", [(34, 2, ""), (87, 15, "")]),
    (124, "S40", [(44, 0, ""), (102, 10, "")]),
    (124, "H4817", [(106, 3, "Passage")]),
    (125, "H3737", [(65, 46, "")]),
    (125, "H3075", [(112, 0, "Passage")]),
    (125, "H4115", [(90, 15, ""), (42, 0, ""), (107, 0, "")]),
    (124, "S304", [(43, 1, ""), (110, 2, "")]),
    (123, "H4369", [(107, 0, "")]),
]

for sess, bn, pairs in VOTES:
    rcs = sc.vote_history(sess, bn)
    if rcs is None:
        check("votes %d:%s live fetch" % (sess, bn), False, "fetch failed")
        continue
    live = [(r["yeas"], r["nays"], r["motion"]) for r in rcs]
    for y, n, msub in pairs:
        hit = [m for (ly, ln, m) in live if ly == y and ln == n and (msub.lower() in m.lower() if msub else True)]
        check("vote %d:%s %d-%d %s" % (sess, bn, y, n, msub or "(any motion)"),
              bool(hit), (hit[0][:60] if hit else "no matching live roll call; live=" + str(live[:8])))

# ---------------------------------------------------------------- 4: provisos
PROV = [
    (2021, [("117.96", "School Construction Development Impact Fee Assessment Prohibition", None),
            ("86.1", "Increased Funding", "repairs, maintenance, and improvements"),
            ("84.12", "Preventative Maintenance Credit", None),
            ("118.18", "Nonrecurring Revenue", "$ 200,000,000")]),
    (2022, [("118.19", "Nonrecurring Revenue", "133,636,230")]),
    (2024, [("118.22", "Homestead Exemption Fund", "CTC Acceleration Fund $200,000,000"),
            ("84.18", "Programmed Project Viewer Dashboard", None)]),
    (2025, [("118.22", "Nonrecurring Revenue", "Bridge Modernization $ 200,000,000")]),
    (2026, [("84.18", "Road Buyback Program", "Section 57-5-80"),
            ("118.21", "Nonrecurring Revenue", "CTC Acceleration $ 175,000,000"),
            ("86.1", "Increased Funding", None)]),
]
NORM = lambda s: re.sub(r"\s+", " ", s)

for year, picks in PROV:
    url = part1b_url(year, "ta")
    resp = sc.soft_get(url)
    if resp is None or resp.status_code != 200:
        check("part1b %d live fetch" % year, False, url)
        continue
    provisos = {p["proviso"]: p for p in extract_provisos(resp.text)}
    for pid, cap_sub, txt_sub in picks:
        p = provisos.get(pid)
        if p is None:
            check("FY%d proviso %s exists" % (year, pid), False, "not found live")
            continue
        ok_cap = cap_sub in p["caption"]
        check("FY%d proviso %s caption ~ %r" % (year, pid, cap_sub), ok_cap,
              "live caption=%r" % p["caption"])
        if txt_sub:
            ok_txt = NORM(txt_sub) in NORM(p["text"])
            check("FY%d proviso %s text has %r" % (year, pid, txt_sub), ok_txt,
                  "verbatim figure check against live enacted text")
    # negative: preventative maintenance credit absent from FY2025-26 onward
    if year in (2025, 2026):
        gone = not any("Preventative Maintenance Credit" in p["caption"] for p in provisos.values())
        check("FY%d Preventative Maintenance Credit absent" % year, gone,
              "confirms the proviso stopped appearing")

# ---------------------------------------------------------------- 5: SC Code
CODE = [
    ("https://www.scstatehouse.gov/code/t06c001.php", [
        ("6-1-910 impact fee article exists", "Development Impact Fee"),
        ("impact fees exclude maintenance/operation", "repair, operation"),
    ]),
    ("https://www.scstatehouse.gov/code/t04c010.php", [
        ("4-10-310 capital project sales tax", "Capital Project"),
        ("green space sales tax article", "green space"),
    ]),
    ("https://www.scstatehouse.gov/code/t04c037.php", [
        ("4-37-30 transportation sales tax / tolls", "sales and use tax"),
    ]),
    ("https://www.scstatehouse.gov/code/t12c028.php", [
        ("12-28-310 gas user fee phase-in", "user fee"),
        ("Act 40 two-cents-a-year language", "two cents"),
    ]),
]
for url, needles in CODE:
    resp = sc.soft_get(url)
    if resp is None or resp.status_code != 200:
        check("code fetch %s" % url, False, "fetch failed")
        continue
    txt = NORM(resp.text)
    for name, nd in needles:
        check("SC Code: %s" % name, nd.lower() in txt.lower(), "searched %s" % url.rsplit('/', 1)[-1])

out = {
    "generated_by": "fact-check-live.py (independent live verification, scstatehouse.gov)",
    "checks": results,
    "totals": {"pass": sum(1 for r in results if r["ok"]),
               "fail": sum(1 for r in results if not r["ok"]),
               "total": len(results)},
}
json.dump(out, open(os.path.join(HERE, "fact-check-live.json"), "w"), indent=1)
print("\nTOTAL: %d pass / %d fail of %d" % (out["totals"]["pass"], out["totals"]["fail"], out["totals"]["total"]))
