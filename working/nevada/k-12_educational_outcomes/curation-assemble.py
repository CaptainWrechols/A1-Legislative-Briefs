#!/usr/bin/env python3
"""Assemble curation-map.json from the per-session curation entry files.

The judgment (plain_topic / theme / relevance per bill) lives in
curation-entries-80.py ... curation-entries-83.py, written by reading every
NELIS Overview digest. This script only merges and validates.

  python3 working/nevada/k-12_educational_outcomes/curation-assemble.py
"""
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BILLS = Path("sources/nevada/k-12_educational_outcomes/pass1/bills.json")

THEMES = {
    "school-funding": "How schools get money: the per-pupil funding plan, formulas, and school finance",
    "spending-oversight": "Audits, transparency, and oversight of how school money is spent",
    "teacher-workforce": "Teacher pay, hiring, licensing, and the educator shortage",
    "accountability-governance": "School and district accountability, school boards, superintendents, and administrators",
    "testing-graduation": "Testing, grading, graduation, and how pupil progress is measured",
    "early-learning-reading": "Pre-K, kindergarten, early childhood, and reading by grade three",
    "classroom-time-content": "What is taught and time in the school day: courses, recess, PE, and class size",
    "student-supports": "Pupil health, mental health, meals, discipline, and student and family supports",
    "charters-choice": "Charter schools, school choice, and non-district schooling",
    "facilities-operations": "School buildings, safety, transportation, and operations",
    "context": "Context bills (not K-12 education policy)",
}

entries = {}
for sess in ("80", "81", "82", "83"):
    mod = runpy.run_path(str(HERE / f"curation-entries-{sess}.py"))
    for k, v in mod["E"].items():
        if k in entries:
            sys.exit(f"duplicate entry {k}")
        entries[k] = v

bills = json.loads(BILLS.read_text())["bills"]
keys = {f"{b['session']}:{b['identifier']}" for b in bills}

missing = sorted(keys - set(entries))
extra = sorted(set(entries) - keys)
if missing:
    sys.exit(f"missing curation for {len(missing)} bills: {missing[:20]}")
if extra:
    sys.exit(f"curation entries not in bills.json: {extra}")
bad_theme = [k for k, v in entries.items() if v["theme"] not in THEMES]
if bad_theme:
    sys.exit(f"unknown themes: {bad_theme[:10]}")
bad_rel = [k for k, v in entries.items() if v["relevance"] not in ("core", "adjacent", "context")]
if bad_rel:
    sys.exit(f"bad relevance: {bad_rel[:10]}")
mismatch = [k for k, v in entries.items() if (v["relevance"] == "context") != (v["theme"] == "context")]
if mismatch:
    sys.exit(f"theme/relevance mismatch (context theme must pair with context relevance): {mismatch}")

out = {
    "note": (
        "Evidence Curator v2.2 curation map for nevada-03-k-12-educational-outcomes. "
        "One entry per bill: plain_topic (citizen wording), theme_id, relevance "
        "(core = K-12 education policy affecting educational outcomes is the point "
        "of the bill; adjacent = a real but partial K-12 angle, such as facilities "
        "money, school-adjacent health services, or bargaining mechanics; context = "
        "found by broad search or omnibus indexing but not K-12 education policy, "
        "including higher-education-only bills). Themes are citizen-facing labels. "
        "Written by reading every NELIS Overview digest."
    ),
    "themes": THEMES,
    "bills": {k: entries[k] for k in sorted(entries)},
}
target = HERE / "curation-map.json"
target.write_text(json.dumps(out, indent=1), encoding="utf-8")

from collections import Counter
rel = Counter(v["relevance"] for v in entries.values())
th = Counter(v["theme"] for v in entries.values() if v["relevance"] != "context")
print(f"wrote {target}: {len(entries)} bills")
print("relevance:", dict(rel))
print("policy themes:", dict(th.most_common()))
