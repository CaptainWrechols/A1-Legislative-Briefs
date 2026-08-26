"""Completeness fact-checker for a South Carolina issue collection (stub).

Mirrors the strict NH gate (collectors/nh/verify_completeness.py): a FAIL means
brief writing must not proceed until the gap is closed or explicitly waived.
Wired to the four SC issue configs now, ahead of full collection, so the issue
chats inherit a working gate.

Two modes:

* ``--foundation`` — what can be checked BEFORE full Pass 1/Pass 2 collection:
  config shape (sessions, terms, constituent_proposals with match_terms,
  omnibus proviso cycles) and the spike's proviso outputs under
  ``working/south-carolina/{issue}/``. This is the mode that should PASS on
  the foundation branch.
* default (full) — additionally requires the collection artifacts
  (pass1/bills.json, processed/bills-core.json, processed/bill-votes.json),
  per-session coverage, votes-per-bill, per-cycle proviso outputs, and
  search-term coverage. Expected to FAIL until an issue chat runs collection.

Run against every SC config:

    for f in config/issues/south-carolina-0*.yaml config/issues/south-carolina-[a-z]*.yaml; do
        ISSUE_CONFIG=$f python3 -m collectors.sc.verify_completeness --foundation
    done

    ISSUE_CONFIG=config/issues/south-carolina-<slug>.yaml \\
        python3 -m collectors.sc.verify_completeness --strict   # full gate
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

MIN_PROVISOS = 100         # an enacted SC Part IB holds well over 1,000
ADVICE_RE = re.compile(r"\b(should|must|ought to|recommend|urge|need to)\b", re.I)


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


def _config_checks(cfg: dict) -> list[dict]:
    """Foundation-level checks: the config itself is complete and consistent."""
    results: list[dict] = []
    sessions = cfg.get("sessions") or []
    results.append(_check(
        "config_sessions",
        len(sessions) == 4 and all(
            s.get("number") and s.get("openstates_identifier")
            and s.get("scstatehouse_path") for s in sessions),
        f"{len(sessions)} sessions; need the 123rd-126th with OpenStates ids "
        f"and scstatehouse paths",
    ))
    results.append(_check(
        "config_search_terms", bool(cfg.get("search_terms")),
        f"{len(cfg.get('search_terms') or [])} search terms"))
    results.append(_check(
        "config_relevance_terms", bool(cfg.get("relevance_terms")),
        f"{len(cfg.get('relevance_terms') or [])} relevance terms"))

    props = cfg.get("constituent_proposals") or []
    bad_props = [p.get("id", "?") for p in props
                 if not all(p.get(k) for k in
                            ("id", "title", "detail", "consensus", "tradeoffs",
                             "match_terms"))]
    results.append(_check(
        "config_constituent_proposals",
        bool(props) and not bad_props,
        f"{len(props)} proposals; incomplete={bad_props}",
    ))

    omni = (cfg.get("omnibus_bills") or [{}])[0]
    cycles = omni.get("cycles") or []
    results.append(_check(
        "config_omnibus_cycles",
        omni.get("method") == "proviso-by-proviso" and len(cycles) >= 6,
        f"method={omni.get('method')}; {len(cycles)} appropriations cycles",
    ))
    return results


def _proviso_checks(cfg: dict, *, foundation: bool) -> list[dict]:
    """Proviso outputs under working/{state}/{issue}."""
    results: list[dict] = []
    sec_doc = _load(ip.WORKING / "proviso-sections.json")
    rel_doc = _load(ip.WORKING / "proviso-relevant.json")
    n = (sec_doc or {}).get("proviso_count") or len((sec_doc or {}).get("provisos") or [])
    results.append(_check(
        "proviso_sections_present",
        sec_doc is not None and n >= MIN_PROVISOS
        and (ip.WORKING / "proviso-sections.md").exists(),
        f"{ip.WORKING / 'proviso-sections.json'}: proviso_count={n} "
        f"(min {MIN_PROVISOS}); cycle={(sec_doc or {}).get('fiscal_year')} "
        f"version={(sec_doc or {}).get('version')}",
    ))
    results.append(_check(
        "proviso_relevant_present",
        rel_doc is not None,
        f"{ip.WORKING / 'proviso-relevant.json'}: "
        f"relevant={(rel_doc or {}).get('relevant_proviso_count')}",
    ))
    if not foundation:
        # Full mode: every enacted cycle in scope must have per-cycle outputs
        # (working/{issue}/provisos/{year}/...), except the cycle already
        # covered by the flat spike files.
        omni = (cfg.get("omnibus_bills") or [{}])[0]
        flat_year = (sec_doc or {}).get("year")
        for cyc in omni.get("cycles") or []:
            if not cyc.get("enacted"):
                continue
            year = cyc["year"]
            per = _load(ip.WORKING / "provisos" / str(year) / "proviso-sections.json")
            ok = per is not None or year == flat_year
            results.append(_check(
                f"proviso_cycle_{year}",
                ok,
                f"FY {cyc['fiscal_year']} ({cyc['bill_no']}): "
                + ("covered" if ok else
                   f"missing {ip.WORKING / 'provisos' / str(year) / 'proviso-sections.json'}"),
            ))
    return results


def _collection_checks(cfg: dict) -> list[dict]:
    """Full-mode checks over the Pass 1/Pass 2 artifacts (NH pattern)."""
    results: list[dict] = []
    pass1 = _load(ip.PASS1 / "bills.json")
    core = _load(ip.PROCESSED / "bills-core.json")
    votes = _load(ip.PROCESSED / "bill-votes.json")
    gaps_doc = _load(ip.SOURCES / "data-gaps.json") or {"gaps": []}

    results.append(_check("artifact_pass1",
                          pass1 is not None and bool(pass1.get("bills")),
                          str(ip.PASS1 / "bills.json")))
    results.append(_check("artifact_bills_core",
                          core is not None and bool(core.get("bills")),
                          str(ip.PROCESSED / "bills-core.json")))
    results.append(_check("artifact_bill_votes",
                          votes is not None and "bills" in (votes or {}),
                          str(ip.PROCESSED / "bill-votes.json")))

    bills = (pass1 or {}).get("bills") or (core or {}).get("bills") or []
    sessions = [int(s["number"]) for s in cfg.get("sessions") or []]

    # Per-session coverage (a session with zero bills needs an explicit gap).
    by_session: dict[int, int] = {}
    for b in bills:
        by_session[b.get("session")] = by_session.get(b.get("session"), 0) + 1
    gap_sessions = set()
    for g in gaps_doc.get("gaps", []):
        gap_sessions.update(g.get("sessions", []))
        if "session" in g:
            gap_sessions.add(g["session"])
    missing = [s for s in sessions
               if by_session.get(s, 0) == 0 and s not in gap_sessions]
    results.append(_check(
        "sessions_covered", not missing,
        f"bills/session={dict(sorted(by_session.items()))}; "
        f"missing_unexplained={missing}"))

    # Bill fields.
    incomplete = [f"{b.get('session')}:{b.get('bill_no')}" for b in bills
                  if not b.get("bill_no") or not (b.get("title")
                  or b.get("summary") or "").strip() or not b.get("sources")]
    results.append(_check(
        "bill_fields_complete", not incomplete,
        f"{len(incomplete)} incomplete of {len(bills)}"
        + (f"; examples={incomplete[:5]}" if incomplete else "")))

    # Votes: one row per bill; counts are integers (never invented).
    vote_index = {(v.get("session"), v.get("bill_no")): v
                  for v in (votes or {}).get("bills", [])}
    missing_votes = [f"{b.get('session')}:{b.get('bill_no')}" for b in bills
                     if (b.get("session"), b.get("bill_no")) not in vote_index]
    bad_counts = []
    for key, v in vote_index.items():
        for rc in v.get("roll_calls") or []:
            for field in ("yeas", "nays"):
                val = rc.get(field)
                if val is not None and not isinstance(val, int):
                    bad_counts.append({"bill": f"{key[0]}:{key[1]}",
                                       "field": field, "value": val})
    results.append(_check(
        "votes_row_per_bill", not missing_votes,
        f"missing_vote_rows={len(missing_votes)} examples={missing_votes[:5]}"))
    results.append(_check(
        "vote_counts_are_integers", not bad_counts,
        f"bad={bad_counts[:5]}" if bad_counts else "all yea/nay integers or null"))

    # Search-term coverage: empty terms are a visible WARN, never silent.
    terms = [str(t) for t in (cfg.get("search_terms") or [])]
    term_hits = {t: 0 for t in terms}
    for b in bills:
        blob = f"{b.get('title', '')} {b.get('summary', '')}".lower()
        for t in terms:
            if t.lower() in blob or t in (b.get("found_by_terms") or []):
                term_hits[t] += 1
    empty_terms = [t for t, nn in term_hits.items() if nn == 0]
    results.append(_check(
        "search_term_coverage", not empty_terms,
        f"empty_search_terms={empty_terms}", severity="warn"))

    # Soft: advice language in titles.
    advice = [f"{b.get('session')}:{b.get('bill_no')}" for b in bills
              if ADVICE_RE.search(b.get("title") or b.get("summary") or "")]
    results.append(_check(
        "no_advice_language_in_titles", not advice,
        f"titles_with_advice_words={advice[:5]}", severity="warn"))
    return results


def verify(cfg: dict, *, foundation: bool) -> dict:
    results = _config_checks(cfg)
    results += _proviso_checks(cfg, foundation=foundation)
    if not foundation:
        results += _collection_checks(cfg)

    fails = [r for r in results if r["status"] == "FAIL"]
    warns = [r for r in results if r["status"] == "WARN"]
    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "issue": cfg.get("issue_id"),
        "issue_slug": ip.ISSUE_SLUG,
        "mode": "foundation" if foundation else "full",
        "verdict": "FAIL" if fails else ("PASS_WITH_WARNINGS" if warns else "PASS"),
        "counts": {"checks": len(results), "fail": len(fails),
                   "warn": len(warns),
                   "pass": sum(1 for r in results if r["status"] == "PASS")},
        "checks": results,
    }


def write_report(report: dict) -> None:
    out = ip.SOURCES / "verification"
    out.mkdir(parents=True, exist_ok=True)
    suffix = "-foundation" if report["mode"] == "foundation" else ""
    (out / f"completeness{suffix}.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        f"# SC collection completeness — {report.get('issue_slug')} "
        f"({report['mode']} mode)",
        "",
        f"**Verdict: {report['verdict']}**",
        "",
        f"PASS {report['counts']['pass']} / WARN {report['counts']['warn']} / "
        f"FAIL {report['counts']['fail']}",
        "",
        "## Checks",
        "",
    ]
    for c in report["checks"]:
        lines.append(f"- **{c['status']}** `{c['check']}` — {c['detail']}")
    (out / f"completeness{suffix}.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true", help="Exit 1 if verdict is FAIL")
    p.add_argument("--foundation", action="store_true",
                   help="Check only what exists before full collection")
    args = p.parse_args()
    cfg = ip.load_config()
    report = verify(cfg, foundation=args.foundation)
    write_report(report)
    print(f"[{ip.ISSUE_SLUG}] {report['mode']} verdict: {report['verdict']} "
          f"(PASS {report['counts']['pass']} / WARN {report['counts']['warn']} / "
          f"FAIL {report['counts']['fail']})")
    if args.strict and report["verdict"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
