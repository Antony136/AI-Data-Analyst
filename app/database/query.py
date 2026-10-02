"""
SQL query execution for AI Data Analyst.

Provides a controlled database execution layer with
query timeout and result-size protection.
"""

from app.database.connection import get_connection
from app.guardrails.query_guard import (
    get_query_limits,
)


def execute_query(sql: str):
    """
    Execute a validated read-only SQL query.

    Applies deterministic execution limits:
    - statement timeout
    - maximum returned rows
    """

    limits = get_query_limits()

    max_result_rows = limits["max_result_rows"]
    timeout_ms = limits["timeout_ms"]

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # --------------------------------------------------
            # 1. Set PostgreSQL statement timeout
            # --------------------------------------------------

            cursor.execute(
                f"SET statement_timeout = {timeout_ms}"
            )

            # --------------------------------------------------
            # 2. Execute the query
            # --------------------------------------------------

            cursor.execute(sql)

            # --------------------------------------------------
            # 3. Read only the allowed number of rows
            # --------------------------------------------------

            rows = cursor.fetchmany(max_result_rows)

            # --------------------------------------------------
            # 4. Detect whether more rows exist
            # --------------------------------------------------

            extra_row = cursor.fetchone()

            if extra_row is not None:
                raise ValueError(
                    f"Query returned more than "
                    f"{max_result_rows} rows."
                )

            # --------------------------------------------------
            # 5. Get column names
            # --------------------------------------------------

            columns = [
                description.name
                for description in cursor.description
            ]

            return columns, rows

    finally:
        connection.close()
