from app.database.query import execute_query


def test_result_row_limit():
    """
    Verify that queries returning more than the configured
    maximum number of rows are rejected.
    """

    sql = """
    SELECT
        customer_id,
        first_name,
        last_name
    FROM customers
    """

    try:
        execute_query(sql)

        raise AssertionError(
            "Query returning more than 1000 rows was accepted"
        )

    except ValueError as error:
        assert "1000 rows" in str(error)

        print(
            "PASS: Query exceeding 1000 rows was rejected"
        )


def test_small_result():
    """
    Verify that queries returning fewer than the limit
    still work normally.
    """

    sql = """
    SELECT
        customer_id,
        first_name
    FROM customers
    LIMIT 10
    """

    columns, rows = execute_query(sql)

    assert len(columns) == 2
    assert len(rows) == 10

    print(
        "PASS: Query within row limit executed successfully"
    )


def main():
    print("=" * 70)
    print("QUERY LIMIT TEST")
    print("=" * 70)

    test_result_row_limit()
    test_small_result()

    print("\n" + "=" * 70)
    print("QUERY LIMIT TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
