from app.guardrails.sql_validator import validate_sql


def test_query(sql: str):

    print("\nSQL")
    print("-" * 70)
    print(sql)

    valid, result = validate_sql(sql)

    print("\nVALIDATION RESULT")
    print("-" * 70)

    if valid:
        print("ACCEPTED")
        print(f"Clean SQL: {result}")
    else:
        print("REJECTED")
        print(f"Reason: {result}")


def main():

    print("=" * 70)
    print("SQL VALIDATION")
    print("=" * 70)

    # LLM-style output
    test_query(
        """```sql
SELECT COUNT(*) AS total_customers
FROM customers;
```"""
    )

    # Dangerous query
    test_query(
        "DELETE FROM customers;"
    )

    # Another dangerous query
    test_query(
        "DROP TABLE customers;"
    )

    print("\n" + "=" * 70)
    print("SQL VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
