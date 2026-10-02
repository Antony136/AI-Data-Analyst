from app.agent.sql_generator import generate_sql
from app.tools.schema_tool import get_database_schema


def main():
    print("=" * 70)
    print("SQL GENERATOR TEST")
    print("=" * 70)

    question = "What was the revenue by product category in 2025?"

    schema_text = get_database_schema()

    sql = generate_sql(
        question=question,
        schema_text=schema_text,
    )

    print("\nQUESTION")
    print("-" * 70)
    print(question)

    print("\nGENERATED SQL")
    print("-" * 70)
    print(sql)

    print("\n" + "=" * 70)
    print("SQL GENERATOR TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
