"""
Visualization tool for AI Data Analyst.

Provides controlled chart generation from Pandas DataFrames.

This module does not execute arbitrary code or accept
arbitrary filesystem paths.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


MAX_DATAFRAME_ROWS = 1000
MAX_DATAFRAME_COLUMNS = 50

OUTPUT_DIRECTORY = (
    Path("data") / "visualizations"
)


def _validate_dataframe(
    df: pd.DataFrame,
) -> None:
    """
    Validate the DataFrame before visualization.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "Visualization input must be a Pandas DataFrame."
        )

    if len(df) == 0:
        raise ValueError(
            "Cannot create a chart from an empty DataFrame."
        )

    if len(df) > MAX_DATAFRAME_ROWS:
        raise ValueError(
            f"DataFrame contains {len(df)} rows. "
            f"Maximum allowed is {MAX_DATAFRAME_ROWS}."
        )

    if len(df.columns) > MAX_DATAFRAME_COLUMNS:
        raise ValueError(
            f"DataFrame contains {len(df.columns)} columns. "
            f"Maximum allowed is {MAX_DATAFRAME_COLUMNS}."
        )


def _validate_output_filename(
    output_filename: str,
) -> str:
    """
    Validate that the output filename is a simple
    filename and cannot escape the visualization directory.
    """

    if not output_filename:
        raise ValueError(
            "Output filename cannot be empty."
        )

    filename = Path(output_filename)

    if filename.name != output_filename:
        raise ValueError(
            "Output filename must be a filename only. "
            "Directory paths are not allowed."
        )

    if filename.suffix.lower() != ".png":
        raise ValueError(
            "Only PNG chart output is allowed."
        )

    if filename.name in {".", ".."}:
        raise ValueError(
            "Invalid output filename."
        )

    return filename.name


def create_bar_chart(
    df: pd.DataFrame,
    category_column: str,
    value_column: str,
    title: str,
    output_filename: str,
) -> str:
    """
    Create a horizontal bar chart from a DataFrame.

    Only predefined PNG output inside
    data/visualizations is permitted.
    """

    _validate_dataframe(df)

    output_filename = _validate_output_filename(
        output_filename
    )

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

    chart_df = df[
        [category_column, value_column]
    ].copy()

    chart_df[value_column] = pd.to_numeric(
        chart_df[value_column],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=[value_column]
    )

    if chart_df.empty:
        raise ValueError(
            f"Column '{value_column}' contains no "
            f"usable numeric values."
        )

    chart_df = chart_df.sort_values(
        value_column,
        ascending=True,
    )

    output_dir = OUTPUT_DIRECTORY

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir / output_filename
    ).resolve()

    output_dir_resolved = (
        output_dir.resolve()
    )

    if output_dir_resolved not in output_path.parents:
        raise ValueError(
            "Chart output path is outside the "
            "allowed visualization directory."
        )

    plt.figure(figsize=(10, 6))

    plt.barh(
        chart_df[category_column].astype(str),
        chart_df[value_column],
    )

    plt.xlabel(
        value_column.replace(
            "_",
            " ",
        ).title()
    )

    plt.ylabel(
        category_column.replace(
            "_",
            " ",
        ).title()
    )

    plt.title(title)

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=150,
    )

    plt.close()

    return str(output_path)
