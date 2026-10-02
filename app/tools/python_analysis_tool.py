"""
Python analysis tool for AI Data Analyst.

Provides reusable Pandas-based analysis
over SQL query results.
"""

import pandas as pd

from app.analysis.dataframe import rows_to_dataframe


def create_dataframe(
    columns: list[str],
    rows: list,
) -> pd.DataFrame:
    """
    Convert SQL query results into a Pandas DataFrame.
    """
    return rows_to_dataframe(
        columns=columns,
        rows=rows,
    )


def calculate_percentage(
    df: pd.DataFrame,
    value_column: str,
) -> pd.DataFrame:
    """
    Calculate each row's percentage contribution
    to the total of a numeric column.
    """
    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    total = df[value_column].sum()

    if total == 0:
        df["percentage"] = 0.0
    else:
        df["percentage"] = (
            df[value_column] / total * 100
        )

    return df


def calculate_summary(
    df: pd.DataFrame,
    value_column: str,
) -> dict:
    """
    Calculate basic statistical summary
    for a numeric column.
    """
    if value_column not in df.columns:
        raise ValueError(
            f"Column '{value_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    series = pd.to_numeric(
        df[value_column],
        errors="coerce",
    )

    return {
        "count": int(series.count()),
        "sum": float(series.sum()),
        "mean": float(series.mean()),
        "min": float(series.min()),
        "max": float(series.max()),
    }
