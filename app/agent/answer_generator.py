"""
Final answer generation component for AI Data Analyst.

Converts database and analysis results into a concise
natural-language answer for the user.
"""

from app.llm.client import generate_response
from app.llm.prompts import build_answer_prompt


def generate_answer(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
) -> str:
    """
    Generate the final natural-language answer
    from the executed query result.
    """

    prompt = build_answer_prompt(
        question=question,
        sql=sql,
        columns=columns,
        rows=rows,
    )

    return generate_response(prompt)