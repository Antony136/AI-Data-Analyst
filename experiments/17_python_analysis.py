from app.agent.pipeline import answer_question
from app.analysis.dataframe import rows_to_dataframe


def main():
    print("=" * 70)
    print("PYTHON ANALYSIS")
    print("=" * 70)

    question = "What was the revenue by product category in 2025?"

    result = answer_question(question)

    df = rows_to_dataframe(
        result["columns"],
        result["rows"],
    )

    df["total_revenue"] = df["total_revenue"].astype(float)

    total_revenue = df["total_revenue"].sum()

    df["revenue_percentage"] = (
        df["total_revenue"] / total_revenue * 100
    )

    print("\nQUERY RESULT")
    print("-" * 70)
    print(df.to_string(index=False))

    print("\nTOTAL REVENUE")
    print("-" * 70)
    print(f"{total_revenue:,.2f}")

    print("\nREVENUE PERCENTAGE")
    print("-" * 70)

    for _, row in df.iterrows():
        print(
            f"{row['category']}: "
            f"{row['revenue_percentage']:.2f}%"
        )

    print("\n" + "=" * 70)
    print("PYTHON ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
