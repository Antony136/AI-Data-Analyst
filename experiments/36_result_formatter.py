from decimal import Decimal

from app.analysis.result_formatter import (
    format_tabular_result,
)


def main():
    print("=" * 70)
    print("RESULT FORMATTER TEST")
    print("=" * 70)

    columns = [
        "category",
        "revenue",
    ]

    rows = [
        (
            "Electronics",
            Decimal("41067364.604"),
        ),
        (
            "Home",
            Decimal("18083529.0395"),
        ),
        (
            "Sports",
            Decimal("7644990.3655"),
        ),
        (
            "Office",
            Decimal("7111185.4035"),
        ),
        (
            "Fashion",
            Decimal("6363825.7335"),
        ),
    ]

    result = format_tabular_result(
        columns=columns,
        rows=rows,
    )

    print("\nFORMATTED RESULT")
    print("-" * 70)
    print(result)

    assert (
        "category: Electronics | "
        "revenue: 41,067,364.60"
        in result
    )

    assert (
        "category: Home | "
        "revenue: 18,083,529.04"
        in result
    )

    assert (
        "category: Sports | "
        "revenue: 7,644,990.37"
        in result
    )

    assert "$" not in result

    print("\n" + "=" * 70)
    print("RESULT FORMATTER TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
