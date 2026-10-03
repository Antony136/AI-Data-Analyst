"""
Database guardrail experiments.

Tests:
1. Maximum result-row protection.
2. PostgreSQL statement timeout.
"""

from app.database.query import execute_query


def test_result_limit():
    print("\n" + "=" * 70)
    print("TEST 1: RESULT ROW LIMIT")
    print("=" * 70)

    sql = """
        SELECT
            generate_series(1, 1001) AS number;
    """

    try:
        execute_query(sql)

        print("ERROR: Query should have been rejected.")

    except Exception as error:
        print(f"Query rejected as expected:")
        print(error)


def test_statement_timeout():
    print("\n" + "=" * 70)
    print("TEST 2: STATEMENT TIMEOUT")
    print("=" * 70)

    sql = """
        SELECT pg_sleep(11);
    """

    try:
        execute_query(sql)

        print("ERROR: Query should have timed out.")

    except Exception as error:
        print("Query cancelled as expected:")
        print(error)


def main():

    print("=" * 70)
    print("DATABASE GUARDRAIL TEST")
    print("=" * 70)

    test_result_limit()
    test_statement_timeout()

    print("\n" + "=" * 70)
    print("DATABASE GUARDRAIL TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
