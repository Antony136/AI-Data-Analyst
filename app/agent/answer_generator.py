"""
Final answer generation component for AI Data Analyst.

Generates a natural-language answer, validates it
against the original database result, normalizes
presentation formatting, and retries when unsupported
numeric values are generated.
"""

from app.guardrails.answer_guard import validate_answer
from app.llm.client import generate_response
from app.llm.prompts import (
    build_answer_correction_prompt,
    build_answer_prompt,
)


MAX_ANSWER_RETRIES = 2


def generate_answer(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
) -> str:
    """
    Generate and validate the final natural-language answer.

    Pipeline:

        Database Result
              ↓
        LLM Answer Generation
              ↓
        Answer Guard
              ↓
        Correction if invalid
              ↓
        Answer Guard
              ↓
        Validated Answer
    """

    prompt = build_answer_prompt(
        question=question,
        sql=sql,
        columns=columns,
        rows=rows,
    )

    answer = generate_response(
        prompt
    )

    for attempt in range(
        MAX_ANSWER_RETRIES + 1
    ):
        valid, result = validate_answer(
            answer=answer,
            rows=rows,
        )

        if valid:
            return result

        if attempt >= MAX_ANSWER_RETRIES:
            raise ValueError(
                "Generated answer failed validation "
                f"after {MAX_ANSWER_RETRIES} retries. "
                f"Last error: {result}"
            )

        correction_prompt = (
            build_answer_correction_prompt(
                question=question,
                sql=sql,
                columns=columns,
                rows=rows,
                failed_answer=answer,
                error_message=result,
            )
        )

        answer = generate_response(
            correction_prompt
        )

    raise RuntimeError(
        "Unexpected answer generation state."
    )
