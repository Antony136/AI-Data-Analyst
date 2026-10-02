"""
SQL generation component for AI Data Analyst.

Generates SQL from a user's natural-language question,
validates it, and provides SQL correction support when
database execution fails.
"""

from app.guardrails.sql_validator import validate_sql
from app.llm.client import generate_response
from app.llm.prompts import (
    build_sql_correction_prompt,
    build_sql_prompt,
)


MAX_SQL_RETRIES = 2


def generate_sql(
    question: str,
    schema_text: str,
) -> str:
    """
    Generate and validate SQL for the user's question.
    """

    prompt = build_sql_prompt(
        question=question,
        schema_text=schema_text,
    )

    response = generate_response(prompt)

    valid, result = validate_sql(response)

    if not valid:
        raise ValueError(
            f"Generated SQL was rejected: {result}"
        )

    return result


def correct_sql(
    question: str,
    schema_text: str,
    failed_sql: str,
    error_message: str,
) -> str:
    """
    Ask the LLM to correct SQL that failed during
    database execution.

    The corrected SQL is validated before being returned.
    """

    prompt = build_sql_correction_prompt(
        question=question,
        schema_text=schema_text,
        failed_sql=failed_sql,
        error_message=error_message,
    )

    response = generate_response(prompt)

    valid, result = validate_sql(response)

    if not valid:
        raise ValueError(
            f"Corrected SQL was rejected: {result}"
        )

    return result
