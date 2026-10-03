"""
SQL query execution for AI Data Analyst.

Provides a controlled database execution layer with
query validation, timeout protection, and result-size
protection.
"""

from app.database.connection import get_connection
from app.guardrails.query_guard import (
    get_query_limits,
    validate_query_shape,
)


def execute_query(sql: str):
    """
    Execute a validated read-only SQL query.

    Applies deterministic execution protections:

    1. Query-shape validation
    2. Statement timeout
    3. Maximum result-row limit
    4. Safe connection cleanup
    """

    # ------------------------------------------------------
    # 1. Validate query shape before touching the database
    # ------------------------------------------------------

    valid, result = validate_query_shape(sql)

    if not valid:
        raise ValueError(
            f"Query rejected: {result}"
        )

    cleaned_sql = result

    # ------------------------------------------------------
    # 2. Load execution limits
    # ------------------------------------------------------

    limits = get_query_limits()

    max_result_rows = limits["max_result_rows"]
    timeout_ms = limits["timeout_ms"]

    # ------------------------------------------------------
    # 3. Open database connection
    # ------------------------------------------------------

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # --------------------------------------------------
            # 4. Set PostgreSQL statement timeout
            # --------------------------------------------------

            cursor.execute(
                f"SET statement_timeout = {timeout_ms}"
            )

            # --------------------------------------------------
            # 5. Execute the validated query
            # --------------------------------------------------

            cursor.execute(cleaned_sql)

            # --------------------------------------------------
            # 6. Read only the allowed number of rows
            # --------------------------------------------------

            rows = cursor.fetchmany(
                max_result_rows
            )

            # --------------------------------------------------
            # 7. Detect whether additional rows exist
            # --------------------------------------------------

            extra_row = cursor.fetchone()

            if extra_row is not None:
                raise ValueError(
                    f"Query returned more than "
                    f"{max_result_rows} rows."
                )

            # --------------------------------------------------
            # 8. Get column names
            # --------------------------------------------------

            columns = [
                description.name
                for description in cursor.description
            ]

            return columns, rows

    finally:

        # ------------------------------------------------------
        # 9. Always close the database connection
        # ------------------------------------------------------

        connection.close()
