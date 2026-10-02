"""
Visualization tool for AI Data Analyst.

Provides reusable chart generation from Pandas DataFrames.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def create_bar_chart(
    df: pd.DataFrame,
    category_column: str,
    value_column: str,
    title: str,
    output_filename: str,
) -> str:
    """
    Create a horizontal bar chart from a DataFrame.
    """
    if category_column not in df.columns:
        raise ValueError(
            f"Column '{category_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    chart_df = df.copy()

    chart_df[value_column] = pd.to_numeric(
        chart_df[value_column],
        errors="raise",
    )

    chart_df = chart_df.sort_values(
        value_column,
        ascending=True,
    )

    output_dir = Path("data") / "visualizations"
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / output_filename

    plt.figure(figsize=(10, 6))

    plt.barh(
        chart_df[category_column],
        chart_df[value_column],
    )

    plt.xlabel(value_column.replace("_", " ").title())
    plt.ylabel(category_column.replace("_", " ").title())
    plt.title(title)

    plt.tight_layout()
    plt.savefig(
        output_path,
        dpi=150,
    )
    plt.close()

    return str(output_path)
