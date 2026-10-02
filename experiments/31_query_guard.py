from app.guardrails.query_guard import (
    get_query_limits,
    validate_query_shape,
)


def test_valid_select():
    sql = "SELECT COUNT(*) FROM orders"

    valid, result = validate_query_shape(sql)

    assert valid
    assert result == sql

    print("PASS: Valid SELECT accepted")


def test_empty_query():
    valid, result = validate_query_shape("")

    assert not valid

    print("PASS: Empty query rejected")


def test_non_select():
    sql = "DELETE FROM orders"

    valid, result = validate_query_shape(sql)

    assert not valid

    print("PASS: Non-SELECT query rejected")


def test_sql_comment():
    sql = "SELECT * FROM orders -- comment"

    valid, result = validate_query_shape(sql)

    assert not valid

    print("PASS: SQL comment rejected")


def test_multiple_statements():
    sql = "SELECT * FROM orders; SELECT * FROM customers"

    valid, result = validate_query_shape(sql)

    assert not valid

    print("PASS: Multiple statements rejected")


def test_limits():
    limits = get_query_limits()

    assert limits["max_result_rows"] == 1000
    assert limits["timeout_ms"] == 10_000

    print("PASS: Query limits configured")


def main():
    print("=" * 70)
    print("QUERY GUARD TEST")
    print("=" * 70)

    test_valid_select()
    test_empty_query()
    test_non_select()
    test_sql_comment()
    test_multiple_statements()
    test_limits()

    print("\n" + "=" * 70)
    print("QUERY GUARD TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
