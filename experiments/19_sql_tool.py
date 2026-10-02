from app.tools.sql_tool import run_sql_query


def main():
    print("=" * 70)
    print("SQL TOOL TEST")
    print("=" * 70)

    sql = """
    SELECT
        COUNT(*) AS total_orders
    FROM orders;
    """

    result = run_sql_query(sql)

    print("\nEXECUTED SQL")
    print("-" * 70)
    print(result["sql"])

    print("\nCOLUMNS")
    print("-" * 70)
    print(result["columns"])

    print("\nROWS")
    print("-" * 70)
    print(result["rows"])

    print("\n" + "=" * 70)
    print("SQL TOOL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()