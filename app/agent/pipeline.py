"""
Core AI Data Analyst pipeline.

Flow:
Natural language
    ↓
Schema
    ↓
LLM generates SQL
    ↓
SQL validation
    ↓
PostgreSQL execution
    ↓
LLM generates final answer
"""

from app.database.query import execute_query
from app.database.schema import (
    get_schema,
    format_schema_for_llm,
)
from app.guardrails.sql_validator import validate_sql
from app.llm.client import generate_response
from app.llm.prompts import (
    build_sql_prompt,
    build_answer_prompt,
)


def answer_question(question: str) -> dict:
    """
    Process a natural-language analytical question.

    Returns:
        A dictionary containing the generated SQL,
        query result, and final answer.
    """

    # --------------------------------------------------------
    # STEP 1: LOAD DATABASE SCHEMA
    # --------------------------------------------------------

    schema = get_schema()

    schema_text = format_schema_for_llm(schema)

    # --------------------------------------------------------
    # STEP 2: GENERATE SQL
    # --------------------------------------------------------

    sql_prompt = build_sql_prompt(
        question=question,
        schema_text=schema_text,
    )

    generated_sql = generate_response(sql_prompt)

    # --------------------------------------------------------
    # STEP 3: VALIDATE SQL
    # --------------------------------------------------------

    valid, result = validate_sql(generated_sql)

    if not valid:
        raise ValueError(
            f"Generated SQL was rejected: {result}"
        )

    clean_sql = result

    # --------------------------------------------------------
    # STEP 4: EXECUTE SQL
    # --------------------------------------------------------

    columns, rows = execute_query(clean_sql)

    # --------------------------------------------------------
    # STEP 5: GENERATE FINAL ANSWER
    # --------------------------------------------------------

    answer_prompt = build_answer_prompt(
        question=question,
        sql=clean_sql,
        columns=columns,
        rows=rows,
    )

    answer = generate_response(answer_prompt)

    return {
        "question": question,
        "sql": clean_sql,
        "columns": columns,
        "rows": rows,
        "answer": answer,
    }
