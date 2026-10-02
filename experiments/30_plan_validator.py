from app.guardrails.plan_validator import validate_plan


def test_valid_plan():
    plan = [
        "sql_query",
        "create_dataframe",
        "calculate_percentage",
    ]

    result = validate_plan(plan)

    assert result == plan

    print("PASS: Valid plan accepted")


def test_duplicate_tools():
    plan = [
        "sql_query",
        "create_dataframe",
        "create_dataframe",
    ]

    result = validate_plan(plan)

    expected = [
        "sql_query",
        "create_dataframe",
    ]

    assert result == expected

    print("PASS: Duplicate tools removed")


def test_missing_dataframe():
    plan = [
        "sql_query",
        "calculate_percentage",
    ]

    try:
        validate_plan(plan)
        raise AssertionError(
            "Invalid plan was accepted"
        )
    except ValueError:
        print(
            "PASS: Missing DataFrame dependency rejected"
        )


def test_missing_sql():
    plan = [
        "create_dataframe",
    ]

    try:
        validate_plan(plan)
        raise AssertionError(
            "Invalid plan was accepted"
        )
    except ValueError:
        print(
            "PASS: Missing SQL dependency rejected"
        )


def test_wrong_order():
    plan = [
        "create_dataframe",
        "sql_query",
    ]

    try:
        validate_plan(plan)
        raise AssertionError(
            "Invalid order was accepted"
        )
    except ValueError:
        print(
            "PASS: Incorrect tool order rejected"
        )


def test_unknown_tool():
    plan = [
        "sql_query",
        "some_fake_tool",
    ]

    try:
        validate_plan(plan)
        raise AssertionError(
            "Unknown tool was accepted"
        )
    except ValueError:
        print(
            "PASS: Unknown tool rejected"
        )


def main():
    print("=" * 70)
    print("PLAN VALIDATOR TEST")
    print("=" * 70)

    test_valid_plan()
    test_duplicate_tools()
    test_missing_dataframe()
    test_missing_sql()
    test_wrong_order()
    test_unknown_tool()

    print("\n" + "=" * 70)
    print("PLAN VALIDATOR TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
