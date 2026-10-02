from app.tools.python_analysis_tool import create_dataframe
from app.tools.visualization_tool import create_bar_chart


def main():
    print("=" * 70)
    print("VISUALIZATION TOOL TEST")
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

    output_path = create_bar_chart(
        df=df,
        category_column="category",
        value_column="revenue",
        title="Revenue by Product Category - 2025",
        output_filename="revenue_by_category_tool_test.png",
    )

    print("\nDATA")
    print("-" * 70)
    print(df.to_string(index=False))

    print("\nCHART")
    print("-" * 70)
    print(f"Saved to: {output_path}")

    print("\n" + "=" * 70)
    print("VISUALIZATION TOOL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
