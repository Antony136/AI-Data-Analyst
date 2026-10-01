"""
Database schema inspection for AI Data Analyst.

Reads PostgreSQL metadata and converts it into structured
schema information that can later be supplied to the LLM.
"""

from app.database.connection import get_connection
from app.schemas.database import (
    ColumnInfo,
    ForeignKeyInfo,
    TableInfo,
)


def get_tables():
    """
    Return all user tables in the public schema.
    """

    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            return [
                row[0]
                for row in cursor.fetchall()
            ]

    finally:
        connection.close()


def get_columns():
    """
    Return column information for all public tables.
    """

    query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY
            table_name,
            ordinal_position;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchall()

    finally:
        connection.close()


def get_primary_keys():
    """
    Return primary-key columns.
    """

    query = """
        SELECT
            tc.table_name,
            kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
            AND tc.table_name = kcu.table_name
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'
        ORDER BY
            tc.table_name,
            kcu.ordinal_position;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchall()

    finally:
        connection.close()


def get_foreign_keys():
    """
    Return foreign-key relationships.
    """

    query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = 'public'
        ORDER BY
            tc.table_name,
            kcu.column_name;
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchall()

    finally:
        connection.close()


def get_schema():
    """
    Build a structured representation of the entire database schema.
    """

    tables = get_tables()
    columns = get_columns()
    primary_keys = get_primary_keys()
    foreign_keys = get_foreign_keys()

    primary_key_set = {
        (table, column)
        for table, column in primary_keys
    }

    foreign_key_map = {}

    for (
        table,
        column,
        referenced_table,
        referenced_column,
    ) in foreign_keys:

        foreign_key_map[
            (table, column)
        ] = ForeignKeyInfo(
            column=column,
            referenced_table=referenced_table,
            referenced_column=referenced_column,
        )

    table_columns = {
        table: []
        for table in tables
    }

    for (
        table,
        column,
        data_type,
        nullable,
    ) in columns:

        table_columns[table].append(
            ColumnInfo(
                name=column,
                data_type=data_type,
                nullable=nullable == "YES",
                primary_key=(
                    table,
                    column,
                ) in primary_key_set,
            )
        )

    table_foreign_keys = {
        table: []
        for table in tables
    }

    for (
        table,
        column,
        referenced_table,
        referenced_column,
    ) in foreign_keys:

        table_foreign_keys[table].append(
            ForeignKeyInfo(
                column=column,
                referenced_table=referenced_table,
                referenced_column=referenced_column,
            )
        )

    return [
        TableInfo(
            name=table,
            columns=table_columns[table],
            foreign_keys=table_foreign_keys[table],
        )
        for table in tables
    ]


def format_schema_for_llm(schema):
    """
    Convert the structured schema into a compact text
    representation suitable for an LLM prompt.
    """

    lines = []

    for table in schema:

        lines.append(f"TABLE: {table.name}")

        for column in table.columns:

            column_line = (
                f"  {column.name} "
                f"{column.data_type}"
            )

            if column.primary_key:
                column_line += " PRIMARY KEY"

            lines.append(column_line)

        for foreign_key in table.foreign_keys:

            lines.append(
                f"  FOREIGN KEY "
                f"{foreign_key.column} "
                f"REFERENCES "
                f"{foreign_key.referenced_table}."
                f"{foreign_key.referenced_column}"
            )

        lines.append("")

    return "\n".join(lines)
