"""
SQL query tool for AI Data Analyst.

Provides a reusable interface for executing
validated read-only SQL queries and validating
their database results.
"""

from app.database.query import execute_query
from app.guardrails.result_guard import validate_result
from app.guardrails.sql_validator import validate_sql


def run_sql_query(sql: str) -> dict:
    """
    Validate and execute a read-only SQL query.

    The execution pipeline is:

    SQL
      ↓
    SQL Validator
      ↓
    Database Execution
      ↓
    Result Guard
      ↓
    Validated Result
    """

    # --------------------------------------------------
    # 1. Validate SQL
    # --------------------------------------------------

    valid, result = validate_sql(sql)

    if not valid:
        raise ValueError(
            f"SQL query rejected: {result}"
        )

    cleaned_sql = result

    # --------------------------------------------------
    # 2. Execute SQL
    # --------------------------------------------------

    columns, rows = execute_query(
        cleaned_sql
    )

    # --------------------------------------------------
    # 3. Validate database result
    # --------------------------------------------------

    valid, message = validate_result(
        columns=columns,
        rows=rows,
    )

    if not valid:
        raise ValueError(
            f"Database result rejected: {message}"
        )

    # --------------------------------------------------
    # 4. Return validated result
    # --------------------------------------------------

    return {
        "sql": cleaned_sql,
        "columns": columns,
        "rows": rows,
    }
