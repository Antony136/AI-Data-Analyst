from pathlib import Path

import matplotlib.pyplot as plt

from app.agent.pipeline import answer_question
from app.analysis.dataframe import rows_to_dataframe


def find_revenue_column(df):
    """
    Find the revenue column returned by the LLM-generated SQL.
    """

    candidates = [
        "total_revenue",
        "revenue",
        "category_revenue",
    ]

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        f"Could not find a revenue column. "
        f"Available columns: {list(df.columns)}"
    )


def main():
    print("=" * 70)
    print("REVENUE VISUALIZATION")
    print("=" * 70)

    question = "What was the revenue by product category in 2025?"

    result = answer_question(question)

    df = rows_to_dataframe(
        result["columns"],
        result["rows"],
    )

    revenue_column = find_revenue_column(df)

    df[revenue_column] = df[revenue_column].astype(float)

    df = df.sort_values(
        revenue_column,
        ascending=True,
    )

    output_dir = Path("data") / "visualizations"

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / "revenue_by_category_2025.png"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        df["category"],
        df[revenue_column],
    )

    plt.xlabel("Revenue")
    plt.ylabel("Product Category")
    plt.title("Revenue by Product Category - 2025")

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()

    print("\nGENERATED SQL")
    print("-" * 70)
    print(result["sql"])

    print("\nQUERY RESULT")
    print("-" * 70)
    print(df.to_string(index=False))

    print("\nCHART")
    print("-" * 70)
    print(f"Saved to: {output_path}")

    print("\n" + "=" * 70)
    print("VISUALIZATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
