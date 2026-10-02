"""
Database query guardrails for AI Data Analyst.

Provides deterministic checks for SQL queries before
they reach the database execution layer.
"""

import re


MAX_RESULT_ROWS = 1000
QUERY_TIMEOUT_MS = 10_000


def validate_query_shape(sql: str) -> tuple[bool, str]:
    """
    Validate the structural shape of a query before execution.

    This guard ensures that the query:
    - is not empty
    - contains only one SQL statement
    - starts with SELECT
    - does not contain SQL comments
    """

    sql = sql.strip()

    # --------------------------------------------------
    # 1. Query must not be empty
    # --------------------------------------------------

    if not sql:
        return False, "Query is empty."

    # --------------------------------------------------
    # 2. Reject SQL comments
    # --------------------------------------------------

    if "--" in sql:
        return False, "SQL comments are not allowed."

    if "/*" in sql or "*/" in sql:
        return False, "SQL block comments are not allowed."

    # --------------------------------------------------
    # 3. Only SELECT queries are allowed
    # --------------------------------------------------

    if not re.match(
        r"^\s*SELECT\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return False, "Only SELECT queries are allowed."

    # --------------------------------------------------
    # 4. Reject multiple statements
    # --------------------------------------------------

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed."

    return True, sql


def get_query_limits() -> dict[str, int]:
    """
    Return deterministic database execution limits.
    """

    return {
        "max_result_rows": MAX_RESULT_ROWS,
        "timeout_ms": QUERY_TIMEOUT_MS,
    }
