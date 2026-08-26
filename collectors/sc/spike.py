"""Smoke-test the SC data routes and write small sample artifacts.

Run from the repo root:

    python3 -m collectors.sc.spike

Proves each source end to end and drops small, inspectable samples under
``sources/south-carolina/_spike/`` so a human can confirm the foundation works
before any large collection:

  * live session-dropdown check against the registry in collectors/sc/__init__
  * per issue: one full-text search (126th session), one bill page, one
    vote-history table — a few bills each, NOT a full Pass 1
  * one appropriations cycle (FY 2025-26, H4025 enacted): Part IB fetched,
    split into provisos, and matched per issue into
    ``working/south-carolina/{issue}/proviso-sections.json|.md`` and
    ``working/south-carolina/{issue}/proviso-relevant.json``
  * House roster sample (the party source for ballots)

Nothing here writes citizen-facing prose and no vote counts are invented —
counts come verbatim from the official vote-history tables.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from . import BUDGET_CYCLE_BY_YEAR, SESSIONS
from . import proviso_fetch, proviso_sections, scstatehouse

OUT = Path("sources/south-carolina/_spike")
WORKING = Path("working/south-carolina")
CONFIG_DIR = Path("config/issues")
ISSUE_SLUGS = [
    "growth-infrastructure-roads",
    "responsive-elected-leaders",
    "rising-cost-of-living",
    "slow-wage-growth",
]
# A few high-signal terms per issue for the SAMPLE search (full term lists run
# in the issue chats, not here).
SPIKE_TERMS = {
    "growth-infrastructure-roads": ["impact fee", "SCDOT"],
    # exact-phrase search: plural "term limits" hits; singular gets zero
    "responsive-elected-leaders": ["term limits", "ranked choice"],
    "rising-cost-of-living": ["electric rate", "property tax"],
    "slow-wage-growth": ["minimum wage", "apprenticeship"],
}
SPIKE_SESSION = 126          # sample only the current session here
PROVISO_SPIKE_YEAR = 2025    # FY 2025-26 (H4025) — most recent fully enacted


def _save(rel: str, data) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    print(f"  wrote {path}")


def _load_cfg(slug: str) -> dict:
    return yaml.safe_load(
        (CONFIG_DIR / f"south-carolina-{slug}.yaml").read_text(encoding="utf-8"))


def session_mapping_check() -> None:
    """Registry vs the live billsearch.php session dropdown."""
    print("Session mapping: registry vs live dropdown")
    r = scstatehouse.soft_get(f"{scstatehouse.BASE}/billsearch.php")
    live = dict(re.findall(r'<option value="(\d+)">\s*\d+\s*-\s*\((\d{4}-\d{4})\)',
                           r.text)) if r else {}
    rows = []
    for s in SESSIONS:
        got = live.get(str(s["number"]))
        ok = got == s["openstates_identifier"]
        rows.append({**{k: v for k, v in s.items()}, "live_dropdown_years": got,
                     "match": ok})
        print(f"  {s['label']}: live={got} match={ok}")
    _save("session-mapping.json", {
        "note": "scstatehouse session number -> years, checked live against "
                "billsearch.php; openstates_identifier is the year span",
        "sessions": rows,
    })


def issue_samples() -> None:
    """Per issue: one term searched, one bill page, one vote history."""
    for slug in ISSUE_SLUGS:
        print(f"Issue sample: {slug}")
        sample: dict = {"issue_slug": slug, "session": SPIKE_SESSION,
                        "searches": [], "bill_page": None, "vote_history": None}
        first_bill: str | None = None
        for term in SPIKE_TERMS[slug]:
            res = scstatehouse.fulltext_search(term, SPIKE_SESSION,
                                               numrows=50, max_pages=2)
            if res is None:
                sample["searches"].append({"term": term, "soft_fail": True})
                continue
            sample["searches"].append({
                "term": term, "total_matches": res["total_matches"],
                "hits": res["hits"][:10],
            })
            print(f"  '{term}': {res['total_matches']} matches")
            if first_bill is None and res["hits"]:
                first_bill = res["hits"][0]["bill_no"]
        if first_bill:
            num = re.sub(r"[^0-9]", "", first_bill)
            page = scstatehouse.fetch_bill_page(SPIKE_SESSION, num)
            if page:
                page.pop("html", None)  # keep the sample small
                sample["bill_page"] = page
                print(f"  bill page {first_bill}: {page['summary'][:60]!r}")
            votes = scstatehouse.vote_history(SPIKE_SESSION, num)
            if votes is not None:
                sample["vote_history"] = {"bill_no": first_bill,
                                          "roll_call_count": len(votes),
                                          "roll_calls": votes[:5]}
                print(f"  vote history {first_bill}: {len(votes)} roll calls")
        _save(f"issues/{slug}-sample.json", sample)


def proviso_cycle_spike() -> None:
    """One appropriations cycle end to end + per-issue matched outputs."""
    print(f"Part IB provisos: FY cycle year {PROVISO_SPIKE_YEAR}")
    doc = proviso_fetch.fetch_part1b(PROVISO_SPIKE_YEAR, cache_dir=OUT / "raw")
    if doc is None:
        print("  FAILED to fetch any Part IB version")
        return
    provisos = proviso_sections.extract_provisos(doc["html"])
    print(f"  {doc['bill_no']} {doc['version_label']}: "
          f"{len(provisos)} provisos extracted")
    meta_base = {k: doc[k] for k in
                 ("fiscal_year", "year", "bill_no", "version", "version_label",
                  "enacted", "source_url")}
    _save("part1b-summary.json", {
        **meta_base,
        "proviso_count": len(provisos),
        "agency_sections": len({p["section"] for p in provisos}),
        "sample_provisos": provisos[:3],
    })

    # Votes on the appropriations bill (whole bill — never per proviso).
    doc_session = BUDGET_CYCLE_BY_YEAR[PROVISO_SPIKE_YEAR]["session"]
    votes = scstatehouse.vote_history(
        doc_session, re.sub(r"[^0-9]", "", doc["bill_no"]))
    if votes is not None:
        _save("part1b-bill-rollcalls.json", {
            "bill_no": doc["bill_no"], "session": doc_session,
            "note": "roll calls are on the whole appropriations bill, never "
                    "on individual provisos",
            "roll_call_count": len(votes),
            "sample": votes[:5],
        })
        print(f"  {doc['bill_no']} roll calls: {len(votes)}")

    # Per-issue matched outputs -> working/south-carolina/{issue}/
    for slug in ISSUE_SLUGS:
        cfg = _load_cfg(slug)
        terms = [str(t) for t in (cfg.get("relevance_terms") or [])]
        for prop in cfg.get("constituent_proposals") or []:
            terms += [str(t) for t in (prop.get("match_terms") or [])]
        relevant = proviso_sections.match_provisos(provisos, terms)
        out_dir = WORKING / slug
        proviso_sections.write_outputs(provisos, relevant, out_dir, {
            **meta_base, "issue_slug": slug,
            "matched_with": "relevance_terms + constituent_proposals.match_terms",
        })
        print(f"  {slug}: {len(relevant)} relevant provisos -> {out_dir}")


def roster_sample() -> None:
    print("House roster (party source)")
    roster = scstatehouse.member_roster("H")
    if roster is None:
        print("  soft-fail")
        return
    parties: dict[str, int] = {}
    for m in roster:
        parties[m["party"]] = parties.get(m["party"], 0) + 1
    _save("house-roster-sample.json", {
        "note": "party source for ballots — official roll-call PDFs list "
                "names only",
        "member_count": len(roster), "parties": parties,
        "sample": roster[:5],
    })
    print(f"  {len(roster)} members, parties={parties}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    session_mapping_check()
    issue_samples()
    proviso_cycle_spike()
    roster_sample()
    print("Spike complete.")


if __name__ == "__main__":
    main()
