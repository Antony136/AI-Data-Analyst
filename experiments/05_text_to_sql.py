from app.database.schema import (
    get_schema,
    format_schema_for_llm,
)
from app.llm.client import generate_response
from app.llm.prompts import build_sql_prompt


def main():

    print("=" * 70)
    print("TEXT TO SQL")
    print("=" * 70)

    question = "How many customers do we have?"

    # --------------------------------------------------------
    # LOAD DATABASE SCHEMA
    # --------------------------------------------------------

    schema = get_schema()

    schema_text = format_schema_for_llm(schema)

    # --------------------------------------------------------
    # BUILD LLM PROMPT
    # --------------------------------------------------------

    prompt = build_sql_prompt(
        question=question,
        schema_text=schema_text,
    )

    # --------------------------------------------------------
    # GENERATE SQL
    # --------------------------------------------------------

    sql = generate_response(prompt)

    print("\nUSER QUESTION")
    print("-" * 70)
    print(question)

    print("\nGENERATED SQL")
    print("-" * 70)
    print(sql)

    print("\n" + "=" * 70)
    print("TEXT TO SQL COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
