from app.database.query import execute_query
from app.guardrails.sql_validator import validate_sql


def main():

    print("=" * 70)
    print("SQL EXECUTION")
    print("=" * 70)

    # FIXED: Changed the closing markdown blocks to exactly 3 backticks
    generated_sql = """
    ```sql
    SELECT COUNT(*) AS total_customers
    FROM customers;
    ```
    """

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    valid, result = validate_sql(generated_sql)

    if not valid:

        print("\nSQL REJECTED")
        print(result)
        return

    clean_sql = result

    print("\nVALIDATED SQL")
    print("-" * 70)
    print(clean_sql)

    # --------------------------------------------------------
    # EXECUTE
    # --------------------------------------------------------

    columns, rows = execute_query(clean_sql)

    print("\nCOLUMNS")
    print("-" * 70)

    print(columns)

    print("\nRESULT")
    print("-" * 70)

    for row in rows:
        print(row)

    print("\n" + "=" * 70)
    print("SQL EXECUTION COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    main()
