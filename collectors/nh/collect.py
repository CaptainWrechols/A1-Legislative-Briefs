"""Config-driven New Hampshire bill + vote collector.

Pulls all bill and vote data for one issue across all configured sessions,
choosing the right source per year (see ``docs/nh-data-sources.md``):

  * **Votes (every session):** GenCourt public SQL -- authoritative, keyless.
  * **Current biennium bills:** GenCourt SQL ``legislation`` / ``legislationtext``
    (title, status, chapter, sponsors, full text) -- keyless.
  * **Older-session bills (2020-2024):**
      - keyless partial: SQL roll-call-title search (bills that reached a vote);
      - full: OpenStates backfill (needs ``OPENSTATES_API_KEY``) for bills that
        died in committee too. Votes still come from SQL.

Run:

    ISSUE_CONFIG=config/issues/new-hampshire-<slug>.yaml \
        python3 -m collectors.nh.collect
    python3 -m collectors.nh.collect --skip-ballots   # summaries only (faster)

Outputs (config-derived paths):

    sources/new-hampshire/{slug}/pass1/bills.json         # discovery
    sources/new-hampshire/{slug}/processed/bills-core.json
    sources/new-hampshire/{slug}/processed/bill-votes.json
    sources/new-hampshire/{slug}/data-gaps.json
    working/new-hampshire/{slug}/hb2/{year}/hb2-sections.json (+ relevant)

Nothing here writes citizen-facing prose or invents any vote counts.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import issue_paths as ip  # noqa: E402

from . import gencourt_sql as db  # noqa: E402
from . import hb2_sections, legiscan, openstates_backfill, openstates_bulk  # noqa: E402


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _sessions(cfg: dict) -> list[dict]:
    out = []
    for s in cfg["sessions"]:
        year = int(s.get("sql_session_year") or s.get("label"))
        out.append(
            {
                "year": year,
                "label": str(s.get("label", year)),
                "openstates_identifier": str(s.get("openstates_identifier", year)),
                "budget": bool(s.get("budget")),
            }
        )
    return out


def discover(cfg: dict, sessions: list[dict], gaps: list[dict]) -> dict[tuple, dict]:
    """Return {(year, bill_no): record} merged across all sources."""
    terms = [str(t) for t in (cfg.get("search_terms") or [])]
    rel = [str(t).lower() for t in (cfg.get("relevance_terms") or terms)]
    sql_years = set(db.legislation_years())
    all_years = [s["year"] for s in sessions]
    bills: dict[tuple, dict] = {}

    def add(year, bill_no, source, title, found_terms, extra=None):
        key = (year, bill_no)
        rec = bills.get(key)
        if rec is None:
            rec = {
                "session_year": year,
                "bill_no": bill_no,
                "title": title or "",
                "sources": [],
                "found_by_terms": [],
            }
            bills[key] = rec
        if source not in rec["sources"]:
            rec["sources"].append(source)
        if title and not rec["title"]:
            rec["title"] = title
        for t in found_terms:
            if t not in rec["found_by_terms"]:
                rec["found_by_terms"].append(t)
        if extra:
            rec.update({k: v for k, v in extra.items() if k not in rec})

    # 1) Current-biennium: complete discovery from the legislation table.
    current_years = [y for y in all_years if y in sql_years]
    if current_years:
        for r in db.search_legislation(terms, current_years):
            add(r["sessionyear"], r["CondensedBillNo"], "sql:legislation",
                r["LSRTitle"], r["found_by_terms"],
                {"legislationID": r["legislationID"],
                 "general_status": r.get("general_status")})

    # 2) All years (esp. older): keyless voted-bill discovery from roll calls.
    for r in db.search_rollcalls(terms, all_years):
        add(r["sessionYear"], r["condensedBillNo"], "sql:rollcall",
            r.get("title1") or r.get("title2"), r["found_by_terms"])

    # 3) Older years: full backfill for committee-killed bills too.
    #    Prefer LegiScan (bulk datasets -> no rate limits, complete); fall back
    #    to OpenStates; otherwise record a gap (SQL roll-call titles above still
    #    captured the voted bills).
    older_years = [s for s in sessions if s["year"] not in sql_years]
    if older_years:
        # Priority: local OpenStates bulk files (keyless, no rate limit) >
        # LegiScan bulk API > OpenStates API > keyless-partial only.
        bulk_years = [s for s in older_years if openstates_bulk.available(s["label"])]
        remaining = [s for s in older_years if s not in bulk_years]
        for s in bulk_years:
            for b in openstates_bulk.discover_session(s["label"], terms, rel):
                add(s["year"], b["bill_no"], "openstates_bulk", b["title"],
                    b["found_by_terms"],
                    {"abstract": b["abstract"], "openstates_url": b["openstates_url"],
                     "os_sponsors": b["sponsors"], "subject": b.get("subject")})
        if remaining:
            if legiscan.available():
                _legiscan_discover(remaining, terms, rel, add, gaps)
            elif openstates_backfill.available():
                try:
                    _openstates_discover(remaining, terms, rel, add)
                except openstates_backfill.RateLimitExhausted as exc:
                    gaps.append({
                        "gap": "openstates_rate_limit_exhausted",
                        "years": [s["year"] for s in remaining],
                        "detail": (
                            f"{exc} Voted bills for these years were still "
                            "captured via SQL roll-call titles. For complete "
                            "older-year data without limits, use the OpenStates "
                            "bulk-CSV route (sources/new-hampshire/_bulk/openstates/"
                            "<year>/)."
                        ),
                    })
            else:
                gaps.append({
                    "gap": "older_session_discovery_incomplete",
                    "years": [s["year"] for s in remaining],
                    "detail": (
                        "No local OpenStates bulk files, LEGISCAN_API_KEY, or "
                        "OPENSTATES_API_KEY for these years. Bills that reached a "
                        "floor vote were still found via SQL roll-call titles, but "
                        "committee-killed bills are not captured. Drop OpenStates "
                        "bulk CSVs in sources/new-hampshire/_bulk/openstates/<year>/ "
                        "(no rate limit) or set a key to complete them."
                    ),
                })
    return bills


def _legiscan_discover(older_years, terms, rel, add, gaps) -> None:
    """Fill older years from LegiScan bulk datasets (cached, ~1 call/session)."""
    want = {s["year"] for s in older_years}
    cache_dir = ip.RAW / "legiscan"
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        datasets = legiscan.dataset_list(year_min=min(want))
    except legiscan.NoApiKey:
        return
    for ds in datasets:
        y0, y1 = int(ds.get("year_start", 0)), int(ds.get("year_end", 0))
        years_covered = {y for y in want if y0 <= y <= y1}
        if not years_covered:
            continue
        sid = ds["session_id"]
        cache = cache_dir / f"{sid}.json"
        if cache.exists():
            parsed = json.loads(cache.read_text(encoding="utf-8"))
        else:
            parsed = legiscan.fetch_dataset(sid, ds["access_key"])
            cache.write_text(json.dumps(parsed), encoding="utf-8")
        for b in legiscan.discover_session(parsed, terms, rel):
            year = _legiscan_bill_year(b, years_covered, y0)
            add(year, b["bill_no"], "legiscan", b["title"], b["found_by_terms"],
                {"description": b["description"], "legiscan_status": b["status"],
                 "legiscan_url": b["legiscan_url"], "ls_sponsors": b["sponsors"],
                 "ls_texts": b["texts"], "ls_history": b["history"]})


def _legiscan_bill_year(bill: dict, years_covered: set, default_year: int) -> int:
    """Best-effort session year for a LegiScan bill from its first history date."""
    for h in bill.get("history") or []:
        d = str(h.get("date", ""))
        if len(d) >= 4 and d[:4].isdigit() and int(d[:4]) in years_covered:
            return int(d[:4])
    return min(years_covered) if years_covered else default_year


def _openstates_discover(older_years, terms, rel, add) -> None:
    for s in older_years:
        try:
            found = openstates_backfill.discover(terms, s["openstates_identifier"])
        except openstates_backfill.NoApiKey:
            return
        for b in found:
            blob = (b["title"] + " " + b["abstract"]).lower()
            if not any(t in blob for t in rel):
                continue
            add(s["year"], b["identifier"], "openstates",
                b["title"], b["found_by_terms"],
                {"abstract": b["abstract"], "openstates_url": b["openstates_url"],
                 "os_sponsors": b["sponsors"], "os_versions": b["versions"]})


def enrich(bills: dict[tuple, dict], sessions: list[dict], *, ballots: bool) -> tuple[list, list]:
    sql_years = set(db.legislation_years())
    core: list[dict] = []
    votes: list[dict] = []
    for (year, bill_no), rec in sorted(bills.items()):
        entry = {
            "session_year": year,
            "bill_no": bill_no,
            "title": rec["title"],
            "found_by_terms": rec["found_by_terms"],
            "sources": rec["sources"],
        }
        if year in sql_years:
            lr = db.legislation_record(bill_no, year)
            if lr:
                entry.update({
                    "expanded_bill_no": lr.get("ExpandedBillNo"),
                    "general_status": lr.get("general_status"),
                    "chapter_no": lr.get("ChapterNo"),
                    "bill_type": lr.get("BillType"),
                    "legislationID": lr.get("legislationID"),
                    "effective_date": lr.get("EffectiveDate"),
                })
                sp = db.sponsors_by_legislation_id(lr["legislationID"])
                entry["sponsors"] = [
                    {"name": f"{s['FirstName']} {s['LastName']}".strip(),
                     "party": s.get("Party"), "body": s.get("LegislativeBody"),
                     "prime": bool(s.get("primeSponsor"))}
                    for s in sp
                ]
                entry["text_available_in_sql"] = True
        else:
            entry["abstract"] = rec.get("abstract", "")
            entry["openstates_url"] = rec.get("openstates_url")
            if rec.get("os_sponsors"):
                entry["sponsors"] = rec["os_sponsors"]
        core.append(entry)

        # Votes: authoritative from SQL for every year.
        summaries = db.rollcall_summaries(bill_no, year)
        vrec = {"session_year": year, "bill_no": bill_no,
                "roll_calls": summaries, "roll_call_count": len(summaries)}
        if ballots and summaries:
            vrec["ballots"] = db.rollcall_ballots(bill_no, year)
        votes.append(vrec)
    return core, votes


def collect_hb2(cfg: dict, sessions: list[dict], gaps: list[dict]) -> None:
    omni = cfg.get("omnibus_bills") or []
    hb2 = next((o for o in omni if str(o.get("bill_no")).upper() == "HB2"), None)
    if not hb2:
        return
    rel = [str(t).lower() for t in (cfg.get("relevance_terms") or cfg.get("search_terms") or [])]
    sql_years = set(db.legislation_years())
    cycles = [y for y in (hb2.get("cycles") or []) if any(s["year"] == y for s in sessions)]
    for year in cycles:
        out_dir = ip.WORKING / "hb2" / str(year)
        meta = {"bill_no": "HB2", "session_year": year,
                "source": "gc.nh.gov legislationtext (SQL)"}
        if year in sql_years:
            lid = db.legislation_id("HB2", year)
            version = db.full_bill_version(lid, "Introduced") if lid else None
            if version and version.get("html_text"):
                secs = hb2_sections.extract_sections(version["html_text"])
                hb2_sections.write_outputs(secs, out_dir, meta)
                relevant = hb2_sections.match_sections(secs, rel)
                save(out_dir / "hb2-relevant.json",
                     {"session_year": year, "matched_terms_source": "relevance_terms",
                      "relevant_section_count": len(relevant), "sections": relevant})
                continue
        # Older cycle: SQL has votes but not text.
        summaries = db.rollcall_summaries("HB2", year)
        save(out_dir / "hb2-votes-only.json",
             {"session_year": year, "note": (
                 "HB2 full text for this cycle is not in GenCourt (current "
                 "biennium only). Section extraction needs the OpenStates "
                 "version link or an archived PDF. Votes below are authoritative."),
              "roll_call_count": len(summaries), "roll_calls": summaries})
        gaps.append({"gap": "hb2_text_unavailable_older_cycle", "year": year,
                     "detail": "HB2 full text not in SQL/live site for this cycle."})


def main() -> None:
    p = argparse.ArgumentParser(description="Collect NH bill + vote data for an issue")
    p.add_argument("--skip-ballots", action="store_true",
                   help="Roll-call summaries only (skip per-member ballots)")
    args = p.parse_args()

    cfg = ip.load_config()
    sessions = _sessions(cfg)
    gaps: list[dict] = []

    print(f"Issue: {cfg.get('issue_title')} ({ip.STATE}/{ip.ISSUE_SLUG})")
    print(f"Sessions: {[s['year'] for s in sessions]}")
    print(f"SQL legislation years: {db.legislation_years()}")

    bills = discover(cfg, sessions, gaps)
    print(f"Discovered {len(bills)} bills")
    core, votes = enrich(bills, sessions, ballots=not args.skip_ballots)

    save(ip.PASS1 / "bills.json", {
        "collected_at": now(), "issue": cfg.get("issue_id"),
        "note": "NH discovery: SQL legislation (current biennium) + SQL roll-call "
                "titles (all years) + OpenStates backfill (older years, if key).",
        "count": len(core), "bills": core,
    })
    save(ip.PROCESSED / "bills-core.json", {"collected_at": now(), "bills": core})
    save(ip.PROCESSED / "bill-votes.json", {
        "collected_at": now(),
        "note": "Roll-call votes from the NH public SQL database (authoritative, "
                "1999->current). Nothing inferred or invented.",
        "bills": votes,
    })

    collect_hb2(cfg, sessions, gaps)
    save(ip.SOURCES / "data-gaps.json", {"collected_at": now(), "gaps": gaps})

    voted = sum(1 for v in votes if v["roll_call_count"])
    print(f"Enriched {len(core)} bills; {voted} have recorded votes; "
          f"{len(gaps)} data gaps.")
    print(f"Outputs under sources/{ip.STATE}/{ip.ISSUE_SLUG}/ and working/.")


if __name__ == "__main__":
    main()
