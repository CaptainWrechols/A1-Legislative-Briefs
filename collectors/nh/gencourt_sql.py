"""Read-only client for the public New Hampshire General Court SQL database.

The General Court publishes its bill-status database for public read access
(documented in ``Downloads`` -> "Public SQL and Data Table Information"). This
is the cleanest source for roll-call votes and, for the current biennium, the
docket / sponsors tables.

    Server:   66.211.150.69  (SQL Server, port 1433)
    Login:    publicuser / PublicAccess
    Database: NHLegislatureDB

Coverage (verified, see ``docs/nh-data-sources.md``):

  * ``rollcallsummary`` / ``rollcallhistory`` -- roll-call votes, **1999 ->
    current** (all target sessions).
  * ``legislation`` -- the master bill table (title, status, chapter,
    committee/floor dates, ``legislationID``). **Current biennium only.**
  * ``legislationtext`` -- full bill text, every version. **Current biennium
    only.**
  * ``sponsors`` -- prime/co-sponsors. Current biennium only.
  * ``docket`` -- action history. Current biennium + <=2016.
  * ``legislators`` -- current membership.

The two big finds -- ``legislation`` and ``legislationtext`` -- are not in the
public schema PDF but are readable by ``publicuser``. They make the current
biennium fully collectable from SQL alone (discovery, status, sponsors, votes,
full text), with **no website scraping and no API key**.

**Older sessions (2020-2024):** GenCourt keeps only roll-call votes for them;
their bill identity/title/status/text are NOT in this database (nor on the live
website, which also serves only the current biennium). Use OpenStates for
older-session bill metadata/text, and still take the votes from here. See
``collectors/nh/openstates_backfill.py``.

Nothing here is Nevada-specific; it does not touch any existing collector.
"""

from __future__ import annotations

import os
from contextlib import contextmanager

SERVER = os.environ.get("NH_SQL_SERVER", "66.211.150.69")
PORT = int(os.environ.get("NH_SQL_PORT", "1433"))
USER = os.environ.get("NH_SQL_USER", "publicuser")
PASSWORD = os.environ.get("NH_SQL_PASSWORD", "PublicAccess")
DATABASE = os.environ.get("NH_SQL_DATABASE", "NHLegislatureDB")


@contextmanager
def connect():
    """Yield a pymssql connection to the public NH database.

    pymssql is imported lazily so the rest of the toolchain does not hard-depend
    on it when the SQL route is not used.
    """
    try:
        import pymssql  # noqa: WPS433 (lazy import by design)
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise SystemExit(
            "pymssql is required for the NH SQL route: pip install pymssql"
        ) from exc

    conn = pymssql.connect(
        server=SERVER,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        port=PORT,
        login_timeout=20,
        timeout=60,
    )
    try:
        yield conn
    finally:
        conn.close()


def query(sql: str, params: tuple = ()) -> list[dict]:
    with connect() as conn:
        cur = conn.cursor(as_dict=True)
        cur.execute(sql, params)
        return list(cur.fetchall())


def rollcall_summaries(bill_no: str, session_year: int) -> list[dict]:
    """Every recorded floor roll call for a bill in a session year.

    ``bill_no`` is the condensed form, e.g. ``HB2`` / ``SB100``.
    """
    return query(
        """
        SELECT sessionYear, legislativeBody, voteSequenceNumber, voteDate,
               condensedBillNo, yeas, nays, present, absent,
               question_Motion, title1, title2
        FROM rollcallsummary
        WHERE condensedBillNo = %s AND sessionYear = %s
        ORDER BY voteDate
        """,
        (bill_no, session_year),
    )


def rollcall_ballots(bill_no: str, session_year: int) -> list[dict]:
    """Individual member votes joined to name + party.

    ``rollcallhistory`` records one row per member per vote; we join to
    ``legislators`` on ``employeeNumber`` so callers get names and party
    without inventing anything.
    """
    return query(
        """
        SELECT h.sessionYear, h.legislativeBody, h.voteSequenceNumber,
               h.condensedBillNo, h.vote,
               l.LastName, l.FirstName, l.Party, l.District, l.CountyCode
        FROM rollcallhistory h
        LEFT JOIN legislators l ON l.EmployeeNo = h.employeeNumber
        WHERE h.condensedBillNo = %s AND h.sessionYear = %s
        ORDER BY h.voteSequenceNumber, l.LastName
        """,
        (bill_no, session_year),
    )


def docket_actions(bill_no: str, session_year: int) -> list[dict]:
    """Status/action history for a bill (current biennium + <=2016 only)."""
    return query(
        """
        SELECT SessionYear, LSR, CondensedBillNo, ExpandedBillNo,
               LegislativeBody, StatusDate, Description
        FROM docket
        WHERE CondensedBillNo = %s AND SessionYear = %s
        ORDER BY StatusDate
        """,
        (bill_no, session_year),
    )


def resolve_lsr(bill_no: str, session_year: int) -> int | None:
    rows = query(
        "SELECT DISTINCT LSR FROM docket WHERE CondensedBillNo = %s AND SessionYear = %s",
        (bill_no, session_year),
    )
    return rows[0]["LSR"] if rows else None


def resolve_legislation_id(bill_no: str, session_year: int) -> int | None:
    """legislationID for a current-biennium bill via docket LSR -> sponsors.

    Returns ``None`` for sessions the ``sponsors`` table does not cover; use
    the website search (``gencourt_web.py``) for those.
    """
    lsr = resolve_lsr(bill_no, session_year)
    if lsr is None:
        return None
    rows = query(
        "SELECT DISTINCT legislationID FROM sponsors WHERE SessionYear = %s AND Lsr = %s",
        (session_year, lsr),
    )
    return rows[0]["legislationID"] if rows else None


def sponsors(bill_no: str, session_year: int) -> list[dict]:
    lsr = resolve_lsr(bill_no, session_year)
    if lsr is None:
        return []
    return query(
        """
        SELECT s.SessionYear, s.Lsr, s.primeSponsor, s.signedOff,
               l.LastName, l.FirstName, l.Party, l.LegislativeBody, l.District
        FROM sponsors s
        LEFT JOIN legislators l ON l.PersonID = s.PersonID
        WHERE s.SessionYear = %s AND s.Lsr = %s
        ORDER BY s.primeSponsor DESC, l.LastName
        """,
        (session_year, lsr),
    )


# --------------------------------------------------------------------------
# legislation / legislationtext (current biennium) -- code maps and search
# --------------------------------------------------------------------------

_STATUS_CODES: dict[str, str] | None = None
_COMMITTEES: dict[str, str] | None = None
_SUBJECTS: dict[str, str] | None = None


def general_status_codes() -> dict[str, str]:
    global _STATUS_CODES
    if _STATUS_CODES is None:
        _STATUS_CODES = {
            r["GeneralCode"]: r["GeneralDescription"]
            for r in query("SELECT GeneralCode, GeneralDescription FROM generalstatuscodes")
        }
    return _STATUS_CODES


def committees_map() -> dict[str, str]:
    global _COMMITTEES
    if _COMMITTEES is None:
        _COMMITTEES = {
            r["CommitteeCode"]: r["CommitteeName"]
            for r in query("SELECT CommitteeCode, CommitteeName FROM committees")
        }
    return _COMMITTEES


def subjects_map() -> dict[str, str]:
    global _SUBJECTS
    if _SUBJECTS is None:
        _SUBJECTS = {
            str(r["subjectID"]): r["subject"]
            for r in query("SELECT subjectID, subject FROM subject")
        }
    return _SUBJECTS


def legislation_years() -> list[int]:
    """Session years present in the ``legislation`` table (current biennium)."""
    rows = query("SELECT DISTINCT sessionyear y FROM legislation ORDER BY sessionyear DESC")
    return [r["y"] for r in rows]


def search_legislation(terms: list[str], session_years: list[int]) -> list[dict]:
    """Bills whose LSRTitle matches any term, in the given (current-biennium)
    session years. Keyless, one query per term. Returns merged unique rows with
    the matching terms recorded in ``found_by_terms``.
    """
    have = set(legislation_years())
    years = [y for y in session_years if y in have]
    if not years:
        return []
    year_ph = ",".join(["%s"] * len(years))
    merged: dict[tuple, dict] = {}
    for term in terms:
        rows = query(
            f"""
            SELECT sessionyear, CondensedBillNo, ExpandedBillNo, LSRTitle,
                   GeneralStatusCode, ChapterNo, BillType, SubjectCode,
                   HouseStatusCode, SenateStatusCode, legislationID, lsr
            FROM legislation
            WHERE LSRTitle LIKE %s AND sessionyear IN ({year_ph})
            """,
            (f"%{term}%", *years),
        )
        for r in rows:
            key = (r["sessionyear"], r["CondensedBillNo"])
            rec = merged.setdefault(key, {**r, "found_by_terms": []})
            if term not in rec["found_by_terms"]:
                rec["found_by_terms"].append(term)
    out = sorted(merged.values(), key=lambda r: (r["sessionyear"], r["CondensedBillNo"]))
    statuses = general_status_codes()
    for r in out:
        r["general_status"] = statuses.get(str(r["GeneralStatusCode"]).zfill(2), r["GeneralStatusCode"])
    return out


def search_rollcalls(terms: list[str], session_years: list[int]) -> list[dict]:
    """Discover bills by roll-call title across ANY years (keyless).

    ``rollcallsummary`` covers 1999->current, so this finds issue bills that
    reached a floor vote even in sessions the ``legislation`` table no longer
    holds. It cannot see bills killed in committee without a recorded vote --
    for full older-session coverage, supplement with OpenStates.
    """
    if not session_years:
        return []
    year_ph = ",".join(["%s"] * len(session_years))
    merged: dict[tuple, dict] = {}
    for term in terms:
        rows = query(
            f"""
            SELECT sessionYear, condensedBillNo,
                   MIN(title1) AS title1, MIN(title2) AS title2,
                   COUNT(*) AS roll_call_count
            FROM rollcallsummary
            WHERE (title1 LIKE %s OR title2 LIKE %s)
              AND sessionYear IN ({year_ph})
            GROUP BY sessionYear, condensedBillNo
            """,
            (f"%{term}%", f"%{term}%", *session_years),
        )
        for r in rows:
            key = (r["sessionYear"], r["condensedBillNo"])
            rec = merged.setdefault(key, {**r, "found_by_terms": []})
            if term not in rec["found_by_terms"]:
                rec["found_by_terms"].append(term)
    return sorted(merged.values(), key=lambda r: (r["sessionYear"], r["condensedBillNo"]))


def legislation_record(bill_no: str, session_year: int) -> dict | None:
    rows = query(
        """
        SELECT sessionyear, CondensedBillNo, ExpandedBillNo, LSRTitle,
               GeneralStatusCode, GeneralStatusDate, ChapterNo, BillType,
               SubjectCode, HouseStatusCode, HouseStatusDate,
               SenateStatusCode, SenateStatusDate, EffectiveDate,
               legislationID, lsr
        FROM legislation
        WHERE CondensedBillNo = %s AND sessionyear = %s
        """,
        (bill_no, session_year),
    )
    if not rows:
        return None
    rec = rows[0]
    rec["general_status"] = general_status_codes().get(
        str(rec["GeneralStatusCode"]).zfill(2), rec["GeneralStatusCode"]
    )
    return rec


def legislation_id(bill_no: str, session_year: int) -> int | None:
    """legislationID straight from the ``legislation`` table (current biennium)."""
    rec = legislation_record(bill_no, session_year)
    return rec["legislationID"] if rec else None


def bill_text_versions(legislation_id_val: int) -> list[dict]:
    """Full-text versions for a bill (Introduced ... Chaptered), newest schema
    order. ``text`` columns are CAST so pymssql returns them as strings.
    """
    return query(
        """
        SELECT DocumentVersion, TextDescription, LegislationTextID,
               CAST(HTMLText AS VARCHAR(MAX)) AS html_text,
               CAST(Text AS VARCHAR(MAX)) AS plain_text
        FROM legislationtext
        WHERE LegislationID = %s
        ORDER BY LegislationTextID
        """,
        (legislation_id_val,),
    )


def full_bill_version(legislation_id_val: int, version_label: str) -> dict | None:
    """One named full-bill version (e.g. 'Introduced', 'CHAPTERED FINAL
    VERSION'), skipping the per-amendment 'OLS Release' fragments.
    """
    for v in bill_text_versions(legislation_id_val):
        if (v.get("DocumentVersion") or "").strip() == version_label:
            return v
    return None


def sponsors_by_legislation_id(legislation_id_val: int) -> list[dict]:
    """Sponsors joined to names/party via the ``legislation``-derived LSR.

    Works for the current biennium (sponsors table coverage).
    """
    return query(
        """
        SELECT s.SessionYear, s.primeSponsor, s.signedOff,
               l.LastName, l.FirstName, l.Party, l.LegislativeBody, l.District
        FROM sponsors s
        LEFT JOIN legislators l ON l.PersonID = s.PersonID
        WHERE s.legislationID = %s
        ORDER BY s.primeSponsor DESC, l.LastName
        """,
        (legislation_id_val,),
    )


if __name__ == "__main__":
    print("legislation years:", legislation_years())
    hits = search_legislation(["water"], legislation_years())
    print(f"water bills (current biennium): {len(hits)}")
    for yr in (2021, 2023, 2025):
        print(f"HB2 {yr}: {len(rollcall_summaries('HB2', yr))} floor roll calls")
