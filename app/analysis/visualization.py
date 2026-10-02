"""
Visualization utilities for AI Data Analyst.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_category_revenue_chart(
    df: pd.DataFrame,
    output_path: str = "data/category_revenue_2025.png",
) -> str:
    """
    Create a bar chart showing revenue by product category.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    plt.bar(
        df["category"],
        df["total_revenue"],
    )

    plt.title("Revenue by Product Category - 2025")
    plt.xlabel("Product Category")
    plt.ylabel("Revenue")

    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(output_file)
    plt.close()

    return str(output_file)
