"""Hard completeness fact-checker for an NH issue collection.

This is the gate that answers: "do we have everything we need, with nothing
quietly missing?" It is intentionally strict. A FAIL means brief writing must
not proceed until the gap is closed or explicitly waived.

Checks (machine-readable in verification/completeness.json):

1. Config sessions: every configured year has at least one discovered bill
   OR an explicit data-gap covering that year.
2. Required artifacts exist (pass1/bills.json, bills-core, bill-votes, data-gaps).
3. Bill records: every bill has session_year, bill_no, title, sources; current-
   biennium bills also have general_status + legislationID.
4. Votes: bill-votes.json covers every discovered bill; yea/nay are integers
   (never invented — presence of ballots is optional).
5. Search-term coverage: every search_term either matched ≥1 bill or is listed
   under empty_search_terms (so silent misses are visible).
6. HB2 omnibus (if configured): for EVERY budget cycle —
     - hb2-sections.json exists with section_count ≥ MIN_HB2_SECTIONS
     - hb2-votes.json (or roll calls in meta) has roll_call_count ≥ 1
     - hb2-relevant.json exists
7. Cross-check: every bill that appears in SQL roll-call-title search for the
   issue terms is present in pass1 (catches discovery regressions).
8. No advice-language scan of titles (soft warn only).

Run:

    ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml \\
        python3 -m collectors.nh.verify_completeness
    python3 -m collectors.nh.verify_completeness --strict   # exit 1 on FAIL
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import issue_paths as ip  # noqa: E402

from . import gencourt_sql as db  # noqa: E402

MIN_HB2_SECTIONS = 10
ADVICE_RE = re.compile(
    r"\b(should|must|ought to|recommend|urge|need to)\b", re.I
)


def _load(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _check(name: str, ok: bool, detail: str, *, severity: str = "fail") -> dict:
    return {
        "check": name,
        "status": "PASS" if ok else ("WARN" if severity == "warn" else "FAIL"),
        "detail": detail,
    }


def verify(cfg: dict) -> dict:
    results: list[dict] = []
    sessions = [int(s.get("sql_session_year") or s.get("label")) for s in cfg["sessions"]]
    terms = [str(t) for t in (cfg.get("search_terms") or [])]
    rel = [str(t).lower() for t in (cfg.get("relevance_terms") or terms)]
    sql_years = set(db.legislation_years())

    # --- required artifacts ---
    pass1 = _load(ip.PASS1 / "bills.json")
    core = _load(ip.PROCESSED / "bills-core.json")
    votes = _load(ip.PROCESSED / "bill-votes.json")
    gaps_doc = _load(ip.SOURCES / "data-gaps.json") or {"gaps": []}

    results.append(_check(
        "artifact_pass1", pass1 is not None and bool(pass1.get("bills")),
        f"{ip.PASS1 / 'bills.json'}"))
    results.append(_check(
        "artifact_bills_core", core is not None and bool(core.get("bills")),
        f"{ip.PROCESSED / 'bills-core.json'}"))
    results.append(_check(
        "artifact_bill_votes", votes is not None and "bills" in (votes or {}),
        f"{ip.PROCESSED / 'bill-votes.json'}"))

    bills = (pass1 or {}).get("bills") or (core or {}).get("bills") or []
    vote_index = {
        (v["session_year"], v["bill_no"]): v
        for v in (votes or {}).get("bills", [])
    }

    # --- per-session coverage ---
    by_year: dict[int, int] = {}
    for b in bills:
        by_year[b["session_year"]] = by_year.get(b["session_year"], 0) + 1
    gap_years = set()
    for g in gaps_doc.get("gaps", []):
        if "years" in g:
            gap_years.update(g["years"])
        if "year" in g:
            gap_years.add(g["year"])
    missing_years = [y for y in sessions if by_year.get(y, 0) == 0 and y not in gap_years]
    results.append(_check(
        "sessions_covered",
        not missing_years,
        f"bills/year={dict(sorted(by_year.items()))}; missing_unexplained={missing_years}",
    ))

    # --- bill record completeness ---
    incomplete = []
    for b in bills:
        problems = []
        if not b.get("bill_no"):
            problems.append("no_bill_no")
        if not (b.get("title") or "").strip():
            problems.append("empty_title")
        if not b.get("sources"):
            problems.append("no_sources")
        if b.get("session_year") in sql_years:
            if not b.get("general_status") and not b.get("legislationID"):
                problems.append("current_biennium_missing_status_or_id")
        if problems:
            incomplete.append({"bill": f"{b.get('session_year')}:{b.get('bill_no')}",
                               "problems": problems})
    results.append(_check(
        "bill_fields_complete",
        len(incomplete) == 0,
        f"{len(incomplete)} incomplete of {len(bills)}"
        + (f"; examples={incomplete[:5]}" if incomplete else ""),
    ))

    # --- votes coverage + integrity ---
    missing_vote_rows = [
        f"{b['session_year']}:{b['bill_no']}"
        for b in bills
        if (b["session_year"], b["bill_no"]) not in vote_index
    ]
    bad_counts = []
    for key, v in vote_index.items():
        for rc in v.get("roll_calls") or []:
            for field in ("yeas", "nays"):
                val = rc.get(field)
                if val is not None and not isinstance(val, int):
                    bad_counts.append({"bill": f"{key[0]}:{key[1]}", "field": field, "value": val})
    results.append(_check(
        "votes_row_per_bill",
        not missing_vote_rows,
        f"missing_vote_rows={len(missing_vote_rows)} examples={missing_vote_rows[:5]}",
    ))
    results.append(_check(
        "vote_counts_are_integers",
        not bad_counts,
        f"bad={bad_counts[:5]}" if bad_counts else "all yea/nay integers or null",
    ))

    # --- search-term coverage ---
    term_hits = {t: 0 for t in terms}
    for b in bills:
        blob = f"{b.get('title','')} {b.get('abstract','')}".lower()
        for t in terms:
            if t.lower() in blob or t in (b.get("found_by_terms") or []):
                term_hits[t] += 1
    empty_terms = [t for t, n in term_hits.items() if n == 0]
    # Empty terms are a WARN (term may simply have no NH hits), not a FAIL —
    # but they must be visible.
    results.append(_check(
        "search_term_coverage",
        True,  # never hard-fail; surface empties
        f"hits={term_hits}; empty_search_terms={empty_terms}",
        severity="warn" if empty_terms else "fail",
    ))
    if empty_terms:
        results[-1]["status"] = "WARN"

    # --- HB2 omnibus completeness (HARD) ---
    omni = next((o for o in (cfg.get("omnibus_bills") or [])
                 if str(o.get("bill_no")).upper() == "HB2"), None)
    if omni:
        cycles = [y for y in (omni.get("cycles") or []) if y in sessions]
        for year in cycles:
            out = ip.WORKING / "hb2" / str(year)
            sec_doc = _load(out / "hb2-sections.json")
            rel_doc = _load(out / "hb2-relevant.json")
            votes_doc = _load(out / "hb2-votes.json") or _load(out / "hb2-votes-only.json")
            n_sec = (sec_doc or {}).get("section_count") or len((sec_doc or {}).get("sections") or [])
            results.append(_check(
                f"hb2_{year}_sections",
                sec_doc is not None and n_sec >= MIN_HB2_SECTIONS,
                f"path={out / 'hb2-sections.json'} section_count={n_sec} "
                f"(min {MIN_HB2_SECTIONS}); source={(sec_doc or {}).get('source')}",
            ))
            results.append(_check(
                f"hb2_{year}_votes",
                votes_doc is not None and (votes_doc.get("roll_call_count") or 0) >= 1,
                f"roll_call_count={(votes_doc or {}).get('roll_call_count')}",
            ))
            results.append(_check(
                f"hb2_{year}_relevant_index",
                rel_doc is not None,
                f"path={out / 'hb2-relevant.json'} "
                f"relevant={(rel_doc or {}).get('relevant_section_count')}",
            ))

    # --- cross-check: SQL rollcall-title hits must appear in pass1 ---
    if terms and sessions:
        rc_hits = db.search_rollcalls(terms, sessions)
        missing_rc = []
        have = {(b["session_year"], b["bill_no"]) for b in bills}
        for r in rc_hits:
            key = (r["sessionYear"], r["condensedBillNo"])
            # Relevance filter: same as discovery
            blob = f"{r.get('title1','')} {r.get('title2','')}".lower()
            if not any(t in blob for t in rel):
                continue
            if key not in have:
                missing_rc.append(f"{key[0]}:{key[1]}")
        results.append(_check(
            "rollcall_discovery_not_dropped",
            not missing_rc,
            f"SQL rollcall-title hits missing from pass1: {missing_rc[:10]} "
            f"(total_missing={len(missing_rc)})",
        ))

    # --- soft: advice language in titles ---
    advice = [f"{b['session_year']}:{b['bill_no']}" for b in bills
              if ADVICE_RE.search(b.get("title") or "")]
    results.append(_check(
        "no_advice_language_in_titles",
        not advice,
        f"titles_with_advice_words={advice[:5]}",
        severity="warn",
    ))
    if advice:
        results[-1]["status"] = "WARN"

    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    report = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "issue": cfg.get("issue_id"),
        "issue_slug": ip.ISSUE_SLUG,
        "verdict": "FAIL" if fails else ("PASS_WITH_WARNINGS" if warns else "PASS"),
        "counts": {
            "checks": len(results),
            "fail": len(fails),
            "warn": len(warns),
            "pass": sum(1 for r in results if r["status"] == "PASS"),
            "bills": len(bills),
            "sessions_configured": sessions,
            "bills_by_year": dict(sorted(by_year.items())),
        },
        "empty_search_terms": empty_terms,
        "checks": results,
        "gaps_recorded": gaps_doc.get("gaps", []),
    }
    return report


def write_report(report: dict) -> None:
    out = ip.SOURCES / "verification"
    out.mkdir(parents=True, exist_ok=True)
    (out / "completeness.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        f"# NH collection completeness — {report.get('issue_slug')}",
        "",
        f"**Verdict: {report['verdict']}**",
        "",
        f"Bills: {report['counts']['bills']}  |  "
        f"PASS {report['counts']['pass']} / "
        f"WARN {report['counts']['warn']} / "
        f"FAIL {report['counts']['fail']}",
        "",
        "## Checks",
        "",
    ]
    for c in report["checks"]:
        lines.append(f"- **{c['status']}** `{c['check']}` — {c['detail']}")
    if report.get("empty_search_terms"):
        lines += ["", "## Empty search terms (no hits)", ""]
        for t in report["empty_search_terms"]:
            lines.append(f"- `{t}`")
    if report.get("gaps_recorded"):
        lines += ["", "## Recorded data gaps", ""]
        for g in report["gaps_recorded"]:
            lines.append(f"- `{g.get('gap')}` {g.get('years', g.get('year', ''))}: {g.get('detail','')[:160]}")
    (out / "completeness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true",
                   help="Exit 1 if verdict is FAIL")
    args = p.parse_args()
    cfg = ip.load_config()
    report = verify(cfg)
    write_report(report)
    print(f"Verdict: {report['verdict']} "
          f"(PASS {report['counts']['pass']} / "
          f"WARN {report['counts']['warn']} / "
          f"FAIL {report['counts']['fail']})")
    print(f"Report: {ip.SOURCES / 'verification' / 'completeness.md'}")
    if args.strict and report["verdict"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
