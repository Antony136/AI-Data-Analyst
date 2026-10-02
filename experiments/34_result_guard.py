from decimal import Decimal

from app.guardrails.result_guard import (
    validate_result,
    validate_result_shape,
)


def test_valid_result():
    columns = [
        "category",
        "revenue",
    ]

    rows = [
        (
            "Electronics",
            Decimal("41067364.60"),
        ),
        (
            "Home",
            Decimal("18083529.04"),
        ),
    ]

    valid, message = validate_result(
        columns=columns,
        rows=rows,
    )

    assert valid
    assert message == "Result is valid."

    print("PASS: Valid database result accepted")


def test_empty_columns():
    columns = []
    rows = [(100,)]

    valid, message = validate_result_shape(
        columns=columns,
        rows=rows,
    )

    assert not valid

    print("PASS: Empty column list rejected")


def test_too_many_columns():
    columns = [
        f"column_{index}"
        for index in range(51)
    ]

    rows = [
        tuple(range(51))
    ]

    valid, message = validate_result_shape(
        columns=columns,
        rows=rows,
    )

    assert not valid

    print("PASS: Excessive column count rejected")


def test_mismatched_row():
    columns = [
        "category",
        "revenue",
    ]

    rows = [
        ("Electronics",)
    ]

    valid, message = validate_result_shape(
        columns=columns,
        rows=rows,
    )

    assert not valid

    print("PASS: Mismatched row rejected")


def test_too_many_rows():
    columns = [
        "customer_id",
    ]

    rows = [
        (index,)
        for index in range(1001)
    ]

    valid, message = validate_result_shape(
        columns=columns,
        rows=rows,
    )

    assert not valid

    print("PASS: Excessive row count rejected")


def main():
    print("=" * 70)
    print("RESULT GUARD TEST")
    print("=" * 70)

    test_valid_result()
    test_empty_columns()
    test_too_many_columns()
    test_mismatched_row()
    test_too_many_rows()

    print("\n" + "=" * 70)
    print("RESULT GUARD TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
