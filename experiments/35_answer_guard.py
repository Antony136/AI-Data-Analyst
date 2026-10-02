from decimal import Decimal

from app.guardrails.answer_guard import (
    extract_numeric_values,
    validate_answer,
)


def test_valid_answer():
    rows = [
        (
            "Electronics",
            Decimal("41067364.604"),
        ),
        (
            "Home",
            Decimal("18083529.0395"),
        ),
    ]

    answer = """
    Electronics: 41,067,364.60
    Home: 18,083,529.04
    """

    valid, result = validate_answer(
        answer=answer,
        rows=rows,
    )

    assert valid

    print(
        "PASS: Supported numeric answer accepted"
    )


def test_currency_normalized():
    rows = [
        (
            "Electronics",
            Decimal("41067364.604"),
        ),
    ]

    answer = (
        "Electronics: $41,067,364.60"
    )

    valid, result = validate_answer(
        answer=answer,
        rows=rows,
    )

    assert valid
    assert "$" not in result
    assert "41,067,364.60" in result

    print(
        "PASS: Unsupported currency symbol normalized"
    )


def test_wrong_number_rejected():
    rows = [
        (
            "Electronics",
            Decimal("41067364.604"),
        ),
    ]

    answer = (
        "Electronics: 999999"
    )

    valid, message = validate_answer(
        answer=answer,
        rows=rows,
    )

    assert not valid

    print(
        "PASS: Unsupported numeric value rejected"
    )


def test_number_extraction():
    answer = (
        "Electronics: 41,067,364.60"
    )

    values = extract_numeric_values(
        answer
    )

    assert values == [
        Decimal("41067364.60")
    ]

    print(
        "PASS: Numeric values extracted correctly"
    )


def main():
    print("=" * 70)
    print("ANSWER GUARD TEST")
    print("=" * 70)

    test_valid_answer()
    test_currency_normalized()
    test_wrong_number_rejected()
    test_number_extraction()

    print("\n" + "=" * 70)
    print("ANSWER GUARD TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
