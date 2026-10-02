"""
Pandas analysis utilities for AI Data Analyst.
"""

import pandas as pd


def rows_to_dataframe(columns: list[str], rows: list) -> pd.DataFrame:
    """
    Convert database query results into a Pandas DataFrame.
    """

    return pd.DataFrame(rows, columns=columns)
