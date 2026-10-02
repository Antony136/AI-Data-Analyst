"""
Final answer generation component for AI Data Analyst.

The LLM provides natural-language explanation only.

Authoritative numeric values are formatted deterministically
by Python and appended directly to the final answer.
"""

from app.analysis.result_formatter import (
    format_tabular_result,
)
from app.llm.client import generate_response


def build_explanation_prompt(
    question: str,
    formatted_result: str,
) -> str:
    """
    Build a prompt that prevents the LLM from generating
    authoritative numeric values.
    """

    return f"""
You are the explanation component of an AI data analyst.

USER QUESTION
-------------
{question}

AUTHORITATIVE DATABASE RESULT
-----------------------------
{formatted_result}

Your task is to provide a short natural-language
explanation of the result.

STRICT RULES
------------
1. Do NOT write any numbers.
2. Do NOT write percentages.
3. Do NOT write currency symbols.
4. Do NOT calculate any values.
5. Do NOT repeat numeric values from the result.
6. Do NOT invent facts.
7. You may describe qualitative observations.
8. Keep the explanation concise.
9. Do not mention SQL, prompts, models, or internal systems.
10. If the result is already self-explanatory, a single
    short sentence is sufficient.

EXPLANATION:
""".strip()


def generate_answer(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
) -> str:
    """
    Generate a grounded final answer.

    Architecture:

        Database Result
              ↓
        Deterministic Formatter
              ↓
        Exact Numeric Result
              ↓
        LLM Explanation
              ↓
        Final Answer
    """

    formatted_result = format_tabular_result(
        columns=columns,
        rows=rows,
    )

    prompt = build_explanation_prompt(
        question=question,
        formatted_result=formatted_result,
    )

    explanation = generate_response(
        prompt
    ).strip()

    return (
        f"{explanation}\n\n"
        f"{formatted_result}"
    )
