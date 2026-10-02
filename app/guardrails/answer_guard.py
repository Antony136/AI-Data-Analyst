"""
Answer guardrails for AI Data Analyst.

Validates and normalizes LLM-generated answers against
the original database result before the answer is returned.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Any


UNSUPPORTED_CURRENCY_SYMBOLS = {
    "$",
    "€",
    "£",
    "₹",
    "¥",
    "₽",
    "₩",
}


def normalize_answer(answer: str) -> str:
    """
    Remove unsupported currency symbols from the generated answer.

    Currency is not stored in the current database schema,
    so these symbols cannot be treated as authoritative data.
    """

    normalized = answer

    for symbol in UNSUPPORTED_CURRENCY_SYMBOLS:
        normalized = normalized.replace(
            symbol,
            "",
        )

    return normalized


def extract_numeric_values(
    text: str,
) -> list[Decimal]:
    """
    Extract numeric values from generated text.

    Supports:
    - integers
    - decimals
    - thousands separators
    - negative numbers
    """

    matches = re.findall(
        r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?",
        text,
    )

    values = []

    for match in matches:
        cleaned = match.replace(",", "")

        try:
            values.append(
                Decimal(cleaned)
            )
        except InvalidOperation:
            continue

    return values


def extract_result_numeric_values(
    rows: list[Any],
) -> list[Decimal]:
    """
    Extract numeric values from database result rows.
    """

    values = []

    for row in rows:
        for value in row:

            if isinstance(
                value,
                (
                    int,
                    float,
                    Decimal,
                ),
            ):
                values.append(
                    Decimal(str(value))
                )

    return values


def numeric_value_is_supported(
    value: Decimal,
    result_values: list[Decimal],
) -> bool:
    """
    Check whether a generated numeric value corresponds
    to a numeric value present in the database result.

    Exact values are accepted.

    Rounded values are also accepted when they are a
    mathematically rounded representation of a result value.
    """

    for result_value in result_values:

        if value == result_value:
            return True

        for decimal_places in range(0, 5):

            rounded_result = result_value.quantize(
                Decimal(
                    "1."
                    + ("0" * decimal_places)
                )
            )

            if value == rounded_result:
                return True

    return False


def validate_answer(
    answer: str,
    rows: list[Any],
) -> tuple[bool, str]:
    """
    Validate an LLM-generated answer against database results.
    """

    if not answer or not answer.strip():
        return False, "Answer is empty."

    # Normalize unsupported presentation-only symbols.
    normalized_answer = normalize_answer(
        answer
    )

    # Extract numeric values.
    answer_values = extract_numeric_values(
        normalized_answer
    )

    result_values = extract_result_numeric_values(
        rows
    )

    # Validate every generated numeric value.
    for value in answer_values:

        if not numeric_value_is_supported(
            value=value,
            result_values=result_values,
        ):
            return False, (
                f"Answer contains unsupported numeric "
                f"value: {value}"
            )

    return True, normalized_answer
