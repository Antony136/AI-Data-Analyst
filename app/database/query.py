"""
SQL query execution for AI Data Analyst.
"""

from app.database.connection import get_connection


def execute_query(sql: str):
    """
    Execute a validated read-only SQL query
    and return column names and rows.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(sql)

            columns = [
                description.name
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            return columns, rows

    finally:
        connection.close()