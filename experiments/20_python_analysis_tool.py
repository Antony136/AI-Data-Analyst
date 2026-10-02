from app.tools.python_analysis_tool import (
    calculate_percentage,
    calculate_summary,
    create_dataframe,
)


def main():
    print("=" * 70)
    print("PYTHON ANALYSIS TOOL TEST")
    print("=" * 70)

    columns = [
        "category",
        "revenue",
    ]

    rows = [
        ("Electronics", 41067364.604),
        ("Home", 18083529.0395),
        ("Sports", 7644990.3655),
        ("Office", 7111185.4035),
        ("Fashion", 6363825.7335),
    ]

    df = create_dataframe(
        columns=columns,
        rows=rows,
    )

    df["revenue"] = df["revenue"].astype(float)

    df = calculate_percentage(
        df=df,
        value_column="revenue",
    )

    summary = calculate_summary(
        df=df,
        value_column="revenue",
    )

    print("\nDATAFRAME")
    print("-" * 70)
    print(df.to_string(index=False))

    print("\nSUMMARY")
    print("-" * 70)

    for key, value in summary.items():
        print(f"{key}: {value:.2f}")

    print("\n" + "=" * 70)
    print("PYTHON ANALYSIS TOOL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
