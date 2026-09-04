#!/usr/bin/env python3
"""Independent fact-check of the SC2 Responsive Elected Leaders citizen-v2.1
brief against LIVE official sources (scstatehouse.gov), fetched fresh —
independent of the repository's stored artifacts.

For each measure cited in the brief/spotlights/Appendix H, fetch the live
bill-history page and assert the specific facts the brief states (vote
pairs, act numbers, decisive actions, first-committee referrals). For
design-detail claims, fetch the live bill-text page and assert the language.
"""
import re
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (fact-check; The Forum brief verification)"}
results = []


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def plain(html):
    t = re.sub(r"<[^>]+>", " ", html)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    return re.sub(r"\s+", " ", t)


def hist(session, number):
    return plain(fetch(f"https://www.scstatehouse.gov/billsearch.php?billnumbers={number}&session={session}&summary=B"))


def text_page(spath, number):
    return plain(fetch(f"https://www.scstatehouse.gov/sess{spath}/bills/{number}.htm"))


def check(label, page, needles, forbid=()):
    for n in needles:
        ok = bool(re.search(n, page, re.I))
        results.append((label, n, ok))
        if not ok:
            print(f"  FAIL  {label}: MISSING {n!r}")
    for n in forbid:
        bad = bool(re.search(n, page, re.I))
        results.append((label, f"ABSENT:{n}", not bad))
        if bad:
            print(f"  FAIL  {label}: UNEXPECTEDLY PRESENT {n!r}")


# ------------------------------------------------------------------ headline bills
CHECKS = [
    # (session, number, needles on the live HISTORY page)
    (126, 3570, [r"Disclosure of Economic Interests", r"Yeas-102 Nays-0", r"Ayes-40 Nays-0",
                 r"Yeas-23 Nays-86", r"Conference committee appointed"], [r"Act No\."]),
    (126, 70,   [r"School Board Ethics", r"Ayes-39 Nays-2", r"Yeas-109 Nays-4", r"Act No\. 191",
                 r"Ratified R 221"], []),
    (124, 38,   [r"REACH Act|Constitutional Heritage", r"Ayes-45 Nays-0", r"Yeas-91 Nays-12",
                 r"Act No\. 26"], []),
    (123, 35,   [r"Constitutional Heritage", r"Ayes-29 Nays-7",
                 r"Referred to Committee on Education and Public Works"], [r"Act No\."]),
    (126, 3008, [r"Convention of the States", r"Ayes-29 Nays-14",
                 r"Adopted, returned to House with concurrence"], []),
    (126, 3007, [r"Convention of the States", r"Adopted, returned to House with concurrence"], []),
    (126, 5683, [r"Redistricting", r"Yeas-74 Nays-36", r"Yeas-74 Nays-37",
                 r"Continued", r"Ayes-26 Nays-18"], [r"Act No\."]),
    (126, 4717, [r"Reapportionment", r"Referred to Committee on Judiciary"], [r"Act No\.", r"Committee report"]),
    (124, 4493, [r"REAPPORTIONMENT", r"Yeas-96 Nays-14", r"Yeas-100 Nays-15", r"Ayes-43 Nays-1",
                 r"Yeas-75 Nays-27", r"Act No\. 117"], []),
    (124, 865,  [r"REAPPORTIONMENT", r"Ayes-41 Nays-2", r"Yeas-74 Nays-35", r"Yeas-68 Nays-36",
                 r"Yeas-72 Nays-33", r"Act No\. 118"], []),
    (125, 4561, [r"Dependent Care", r"Yeas-53 Nays-45",
                 r"Referred to Committee on Judiciary"], [r"Act No\."]),
    (124, 133,  [r"Convention of the States", r"Ayes-24 Nays-16", r"Yeas-67 Nays-41",
                 r"Ayes-24 Nays-14", r"Conference committee appointed"], [r"Act No\."]),
    (125, 3676, [r"Convention of the States", r"Yeas-68 Nays-30",
                 r"Committee report: Favorable Judiciary"], []),
    (124, 499,  [r"Election Commission Restructuring", r"Ayes-37 Nays-7",
                 r"Referred to Committee on Judiciary"], [r"Act No\."]),
]

# 21 redistricting commission/criteria bills + civics bills: existence,
# right title, Judiciary/EPW referral, and NO act number / NO floor passage.
DIED_IN_COMMITTEE = [
    (123, 3044, r"Independent Reapportionment Commission", r"Judiciary"),
    (123, 6,    r"Independent Reapportionment Commission", r"Judiciary"),
    (123, 135,  r"Independent Reapportionment Commission", r"Judiciary"),
    (123, 3167, r"Citizens Redistricting Commission", r"Judiciary"),
    (123, 3390, r"Citizens Redistricting Commission", r"Judiciary"),
    (123, 249,  r"Citizens Redistricting Commission", r"Judiciary"),
    (123, 3432, r"Citizens Redistricting Commission", r"Judiciary"),
    (123, 254,  r"Citizens Redistricting Commission", r"Judiciary"),
    (123, 3054, r"Redistricting Commission", r"Judiciary"),
    (123, 230,  r"Redistricting Commission", r"Judiciary"),
    (124, 3279, r"Independent Reapportionment Commission", r"Judiciary"),
    (124, 561,  r"Independent Reapportionment Commission", r"Judiciary"),
    (124, 4201, r"Citizens Redistricting Commission", r"Judiciary"),
    (124, 4202, r"Redistricting", r"Judiciary"),
    (124, 4229, r"Fairness, Accountability, and Integrity in Redistricting", r"Judiciary"),
    (124, 750,  r"Fairness, Accountability, and Integrity in Redistricting", r"Judiciary"),
    (125, 3173, r"Independent Reapportionment Commission", r"Judiciary"),
    (125, 3243, r"Citizens Redistricting Commission", r"Judiciary"),
    (125, 3245, r"Redistricting", r"Judiciary"),
    (125, 3069, r"Fairness, Accountability, and Integrity in Redistricting", r"Judiciary"),
    (125, 4222, r"Anti-Gerrymandering", r"Judiciary"),
    (126, 3547, r"Civics", r"Education and Public Works"),
    (124, 4392, r"Civics", r"Education and Public Works"),
    (123, 4296, r"Constitutional Heritage", r"Education and Public Works"),
    (124, 3338, r"Constitutional Heritage", r"Education and Public Works"),
]

# design-detail claims verified on the live bill-TEXT pages
TEXT_CHECKS = [
    ("123_2019-2020", 6,    [r"nine members", r"Applicant Review Panel", r"Inspector General", r"referendum"]),
    ("123_2019-2020", 3044, [r"nine members", r"Applicant Review Panel", r"Inspector General", r"referendum"]),
    ("125_2023-2024", 4222, [r"twelve members", r"State Ethics Commission", r"five must be majority party",
                             r"largest minority political party", r"two must be members of other political parties",
                             r"ten maps"]),
    ("125_2023-2024", 3243, [r"no mechanism for executive or legislative alteration", r"veto",
                             r"adjourn sine die"]),
    ("123_2019-2020", 230,  [r"may not adjourn sine die", r"decennial"]),
    ("123_2019-2020", 3432, [r"State Ethics Commission shall oversee the appointment"]),
    ("126_2025-2026", 3547, [r"middle school students must complete one unit of civics",
                             r"Palmetto Middle School Civics Challenge",
                             r"State Board of Education to adopt related curriculum",
                             r"2027-2028"]),
    ("124_2021-2022", 4392, [r"Keep Partisanship Out of Civics", r"private funding", r"lobbying"]),
]

for sess, num, needles, forbid in CHECKS:
    label = f"{sess}:{'H' if num >= 3000 else 'S'}{num}"
    try:
        page = hist(sess, num)
        check(label, page, needles, forbid)
    except Exception as e:
        results.append((label, "FETCH", False)); print("  FETCH FAIL", label, e)
    time.sleep(0.4)

for sess, num, title_re, cmte in DIED_IN_COMMITTEE:
    label = f"{sess}:{'H' if num >= 3000 else 'S'}{num}"
    try:
        page = hist(sess, num)
        check(label, page, [title_re, rf"Referred to Committee on [^.]*{cmte}"],
              [r"Act No\.", r"Yeas-\d+ Nays-\d+", r"Ayes-\d+ Nays-\d+"])
    except Exception as e:
        results.append((label, "FETCH", False)); print("  FETCH FAIL", label, e)
    time.sleep(0.4)

for spath, num, needles in TEXT_CHECKS:
    label = f"text {spath}:{num}"
    try:
        page = text_page(spath, num)
        check(label, page, needles)
    except Exception as e:
        results.append((label, "FETCH", False)); print("  FETCH FAIL", label, e)
    time.sleep(0.4)

# ------------------------------------------------------------------ provisos (live enacted Part IB)
PROVISO_CHECKS = [
    ("https://www.scstatehouse.gov/sess126_2025-2026/appropriations2026/tap1b.htm", "FY2026-27", [
        r"117\.219", r"shall report the specific State or political subdivision body",
        r"117\.145", r"unconditional right to intervene",
        r"110\.2", r"meet at least one time each month",
        r"118\.6", r"prohibited from using general fund appropriations to compensate employees who engage in lobbying",
        r"117\.92", r"Local Government Fund to compensate employees for lobbying",
        r"Center for American Civic Leadership and Public Discourse",
    ]),
    ("https://www.scstatehouse.gov/sess125_2023-2024/appropriations2024/tap1b.htm", "FY2024-25", [
        r"45\.11", r"Center for Civic Engagement",
        r"110\.1", r"Public Disclosure and Accountability Reporting System",
    ]),
]
for url, label, needles in PROVISO_CHECKS:
    try:
        page = plain(fetch(url))
        check(label, page, needles)
    except Exception as e:
        results.append((label, "FETCH", False)); print("  FETCH FAIL", label, e)
    time.sleep(0.4)

ok = sum(1 for _, _, r in results if r)
bad = [(l, n) for l, n, r in results if not r]
print(f"\n==== {ok}/{len(results)} checks passed; {len(bad)} failed ====")
for l, n in bad:
    print("FAILED:", l, n)
