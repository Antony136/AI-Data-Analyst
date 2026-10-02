"""
SQL query tool for AI Data Analyst.

Provides a reusable interface for executing
validated read-only SQL queries.
"""

from app.database.query import execute_query
from app.guardrails.sql_validator import validate_sql


def run_sql_query(sql: str) -> dict:
    """
    Validate and execute a read-only SQL query.
    """

    valid, result = validate_sql(sql)

    if not valid:
        raise ValueError(
            f"SQL query rejected: {result}"
        )

    columns, rows = execute_query(result)

    return {
        "sql": result,
        "columns": columns,
        "rows": rows,
    }
