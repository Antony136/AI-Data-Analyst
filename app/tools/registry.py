"""
Tool registry for AI Data Analyst.

Provides a central registry for discovering and
executing available analytics tools.
"""

from app.tools.python_analysis_tool import (
    calculate_percentage,
    calculate_summary,
    create_dataframe,
)
from app.tools.sql_tool import run_sql_query
from app.tools.visualization_tool import create_bar_chart


TOOLS = {
    "sql_query": run_sql_query,
    "create_dataframe": create_dataframe,
    "calculate_percentage": calculate_percentage,
    "calculate_summary": calculate_summary,
    "create_bar_chart": create_bar_chart,
}


def get_tool(name: str):
    """
    Return a registered tool by name.
    """
    if name not in TOOLS:
        raise ValueError(
            f"Unknown tool: {name}. "
            f"Available tools: {list(TOOLS.keys())}"
        )

    return TOOLS[name]


def list_tools() -> list[str]:
    """
    Return the names of all registered tools.
    """
    return list(TOOLS.keys())
