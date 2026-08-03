"""Read-only client for the public New Hampshire General Court SQL database.

The General Court publishes its bill-status database for public read access
(documented in ``Downloads`` -> "Public SQL and Data Table Information"). This
is the cleanest source for roll-call votes and, for the current biennium, the
docket / sponsors tables.

    Server:   66.211.150.69  (SQL Server, port 1433)
    Login:    publicuser / PublicAccess
    Database: NHLegislatureDB

Coverage (verified during the NH foundation spike, see
``docs/nh-data-sources.md``):

  * ``rollcallsummary`` / ``rollcallhistory`` -- full, 1999 -> current
  * ``docket`` (status/action history) -- current biennium + <=2016
  * ``sponsors`` -- current biennium only
  * ``legislators`` -- current membership

For older-session bill identity, sponsors, and status, use the website
(``gencourt_web.py``) or OpenStates instead. Nothing here is Nevada-specific;
it does not touch any existing collector.
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


if __name__ == "__main__":
    for yr in (2021, 2023, 2025):
        rows = rollcall_summaries("HB2", yr)
        print(f"HB2 {yr}: {len(rows)} floor roll calls")
