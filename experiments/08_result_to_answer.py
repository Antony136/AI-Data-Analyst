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


def main():

    print("=" * 70)
    print("RESULT TO NATURAL LANGUAGE ANSWER")
    print("=" * 70)

    question = "How many customers do we have?"

    # --------------------------------------------------------
    # LOAD SCHEMA
    # --------------------------------------------------------

    schema = get_schema()

    schema_text = format_schema_for_llm(schema)

    # --------------------------------------------------------
    # GENERATE SQL
    # --------------------------------------------------------

    sql_prompt = build_sql_prompt(
        question=question,
        schema_text=schema_text,
    )

    generated_sql = generate_response(sql_prompt)

    # --------------------------------------------------------
    # VALIDATE SQL
    # --------------------------------------------------------

    valid, result = validate_sql(generated_sql)

    if not valid:

        print("\nSQL REJECTED")
        print(result)
        return

    clean_sql = result

    # --------------------------------------------------------
    # EXECUTE SQL
    # --------------------------------------------------------

    columns, rows = execute_query(clean_sql)

    # --------------------------------------------------------
    # GENERATE NATURAL LANGUAGE ANSWER
    # --------------------------------------------------------

    answer_prompt = build_answer_prompt(
        question=question,
        sql=clean_sql,
        columns=columns,
        rows=rows,
    )

    answer = generate_response(answer_prompt)

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\nUSER QUESTION")
    print("-" * 70)
    print(question)

    print("\nGENERATED SQL")
    print("-" * 70)
    print(clean_sql)

    print("\nDATABASE RESULT")
    print("-" * 70)
    print(columns)
    print(rows)

    print("\nFINAL ANSWER")
    print("-" * 70)
    print(answer)

    print("\n" + "=" * 70)
    print("RESULT TO ANSWER COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
