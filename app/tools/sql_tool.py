"""
SQL query tool for AI Data Analyst.

Provides a reusable interface for executing
validated read-only SQL queries and validating
their database results.
"""

from app.database.query import execute_query
from app.database.schema import get_schema
from app.guardrails.result_guard import validate_result
from app.guardrails.sql_validator import validate_sql


def _get_allowed_tables() -> set[str]:
    """
    Return all tables known to the application schema.
    """

    schema = get_schema()

    return {
        table.name.lower()
        for table in schema
    }


def run_sql_query(sql: str) -> dict:
    """
    Validate and execute a read-only SQL query.

    The execution pipeline is:

    SQL
      ↓
    SQL Validator
      ↓
    Schema Validation
      ↓
    Database Execution
      ↓
    Result Guard
      ↓
    Validated Result
    """

    # --------------------------------------------------
    # 1. Get allowed database tables
    # --------------------------------------------------

    allowed_tables = _get_allowed_tables()

    # --------------------------------------------------
    # 2. Validate SQL
    # --------------------------------------------------

    valid, result = validate_sql(
        sql=sql,
        allowed_tables=allowed_tables,
    )

    if not valid:
        raise ValueError(
            f"SQL query rejected: {result}"
        )

    cleaned_sql = result

    # --------------------------------------------------
    # 3. Execute SQL
    # --------------------------------------------------

    columns, rows = execute_query(
        cleaned_sql
    )

    # --------------------------------------------------
    # 4. Validate database result
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
    # 5. Return validated result
    # --------------------------------------------------

    return {
        "sql": cleaned_sql,
        "columns": columns,
        "rows": rows,
    }
