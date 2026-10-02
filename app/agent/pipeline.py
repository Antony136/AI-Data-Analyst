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
If execution fails → LLM corrects SQL → retry
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
    build_answer_prompt,
    build_sql_correction_prompt,
    build_sql_prompt,
)


MAX_SQL_RETRIES = 2


def answer_question(question: str) -> dict:
    schema = get_schema()
    schema_text = format_schema_for_llm(schema)

    sql_prompt = build_sql_prompt(
        question=question,
        schema_text=schema_text,
    )

    generated_sql = generate_response(sql_prompt)

    valid, result = validate_sql(generated_sql)

    if not valid:
        raise ValueError(
            f"Generated SQL was rejected: {result}"
        )

    clean_sql = result

    last_error = None

    for attempt in range(MAX_SQL_RETRIES + 1):
        try:
            columns, rows = execute_query(clean_sql)
            last_error = None
            break

        except Exception as error:
            last_error = str(error)

            if attempt >= MAX_SQL_RETRIES:
                raise RuntimeError(
                    "SQL execution failed after "
                    f"{MAX_SQL_RETRIES} retries: "
                    f"{last_error}"
                ) from error

            correction_prompt = build_sql_correction_prompt(
                question=question,
                schema_text=schema_text,
                failed_sql=clean_sql,
                error_message=last_error,
            )

            corrected_sql = generate_response(
                correction_prompt
            )

            valid, result = validate_sql(corrected_sql)

            if not valid:
                raise ValueError(
                    f"Corrected SQL was rejected: {result}"
                )

            clean_sql = result

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
