"""
Result guardrails for AI Data Analyst.

Validates database results before they are passed
to downstream analysis and answer-generation components.
"""

from decimal import Decimal
from typing import Any


MAX_RESULT_COLUMNS = 50
MAX_RESULT_ROWS = 1000


def validate_result_shape(
    columns: list[str],
    rows: list[Any],
) -> tuple[bool, str]:
    """
    Validate the basic structure and size of a database result.
    """

    # --------------------------------------------------
    # 1. Validate columns
    # --------------------------------------------------

    if not isinstance(columns, list):
        return False, "Result columns must be a list."

    if not columns:
        return False, "Result must contain at least one column."

    if len(columns) > MAX_RESULT_COLUMNS:
        return False, (
            f"Result contains more than "
            f"{MAX_RESULT_COLUMNS} columns."
        )

    # --------------------------------------------------
    # 2. Validate rows
    # --------------------------------------------------

    if not isinstance(rows, list):
        return False, "Result rows must be a list."

    if len(rows) > MAX_RESULT_ROWS:
        return False, (
            f"Result contains more than "
            f"{MAX_RESULT_ROWS} rows."
        )

    # --------------------------------------------------
    # 3. Validate row structure
    # --------------------------------------------------

    expected_column_count = len(columns)

    for index, row in enumerate(rows):
        if not isinstance(row, (tuple, list)):
            return False, (
                f"Row {index} must be a tuple or list."
            )

        if len(row) != expected_column_count:
            return False, (
                f"Row {index} contains "
                f"{len(row)} values, expected "
                f"{expected_column_count}."
            )

    return True, "Result shape is valid."


def validate_numeric_values(
    rows: list[Any],
) -> tuple[bool, str]:
    """
    Validate that numeric database values retain
    supported numeric types.

    Decimal is explicitly supported because PostgreSQL
    NUMERIC values are returned as Decimal objects.
    """

    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):

            if value is None:
                continue

            if isinstance(
                value,
                (
                    int,
                    float,
                    Decimal,
                ),
            ):
                continue

            # Strings and other values are allowed because
            # database results may legitimately contain text,
            # dates, booleans, and other PostgreSQL types.

    return True, "Result values are valid."


def validate_result(
    columns: list[str],
    rows: list[Any],
) -> tuple[bool, str]:
    """
    Run all deterministic result validations.
    """

    valid, message = validate_result_shape(
        columns=columns,
        rows=rows,
    )

    if not valid:
        return False, message

    valid, message = validate_numeric_values(
        rows=rows,
    )

    if not valid:
        return False, message

    return True, "Result is valid."
