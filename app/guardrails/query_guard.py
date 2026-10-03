"""
Database query guardrails for AI Data Analyst.

Provides deterministic checks for SQL queries before
they reach the database execution layer.
"""

import re


MAX_RESULT_ROWS = 1000
QUERY_TIMEOUT_MS = 10_000


def validate_query_shape(
    sql: str,
) -> tuple[bool, str]:
    """
    Validate the structural shape of a SQL query.

    Allowed:
    - SELECT queries
    - WITH ... SELECT queries (CTEs)

    Rejected:
    - empty queries
    - multiple statements
    - SQL comments
    - non-SELECT statements
    """

    sql = sql.strip()

    # --------------------------------------------------------
    # EMPTY QUERY
    # --------------------------------------------------------

    if not sql:
        return False, "Query is empty."

    # --------------------------------------------------------
    # COMMENTS
    # --------------------------------------------------------

    if "--" in sql:
        return False, "SQL comments are not allowed."

    if "/*" in sql or "*/" in sql:
        return False, "SQL block comments are not allowed."

    # --------------------------------------------------------
    # STATEMENT COUNT
    # --------------------------------------------------------

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) != 1:
        return (
            False,
            "Multiple SQL statements are not allowed.",
        )

    # --------------------------------------------------------
    # QUERY TYPE
    # --------------------------------------------------------

    if not re.match(
        r"^\s*(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return False, "Only SELECT queries are allowed."

    return True, sql


def get_query_limits() -> dict[str, int]:
    """
    Return deterministic database query limits.
    """

    return {
        "max_result_rows": MAX_RESULT_ROWS,
        "timeout_ms": QUERY_TIMEOUT_MS,
    }
