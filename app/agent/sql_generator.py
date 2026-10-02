"""
SQL generation component for AI Data Analyst.

Generates SQL from a user's natural-language question
using the current database schema.
"""

from app.guardrails.sql_validator import validate_sql
from app.llm.client import generate_response
from app.llm.prompts import build_sql_prompt


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
