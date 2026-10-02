"""
Tool execution component for AI Data Analyst.

Executes registered tools using the current agent state.
"""

import pandas as pd

from app.agent.state import AgentState
from app.tools.registry import get_tool


def execute_tool(
    tool_name: str,
    state: AgentState,
) -> AgentState:
    """
    Execute one tool and update the agent state.
    """

    if tool_name == "sql_query":
        tool = get_tool("sql_query")

        result = tool(state.sql)

        state.sql = result["sql"]
        state.columns = result["columns"]
        state.rows = result["rows"]

    elif tool_name == "create_dataframe":
        tool = get_tool("create_dataframe")

        dataframe = tool(
            columns=state.columns,
            rows=state.rows,
        )

        state.analysis["dataframe"] = dataframe

    elif tool_name == "calculate_percentage":
        if "dataframe" not in state.analysis:
            raise ValueError(
                "DataFrame must be created before "
                "calculating percentages."
            )

        tool = get_tool("calculate_percentage")

        dataframe = state.analysis["dataframe"]

        value_column = _find_numeric_column(
            dataframe,
            excluded={"percentage"},
        )

        dataframe = tool(
            df=dataframe,
            value_column=value_column,
        )

        state.analysis["dataframe"] = dataframe

    elif tool_name == "calculate_summary":
        if "dataframe" not in state.analysis:
            raise ValueError(
                "DataFrame must be created before "
                "calculating summary statistics."
            )

        tool = get_tool("calculate_summary")

        dataframe = state.analysis["dataframe"]

        value_column = _find_numeric_column(
            dataframe,
        )

        summary = tool(
            df=dataframe,
            value_column=value_column,
        )

        state.analysis["summary"] = summary

    elif tool_name == "create_bar_chart":
        if "dataframe" not in state.analysis:
            raise ValueError(
                "DataFrame must be created before "
                "creating a chart."
            )

        tool = get_tool("create_bar_chart")

        dataframe = state.analysis["dataframe"]

        category_column = _find_category_column(
            dataframe,
        )

        value_column = _find_numeric_column(
            dataframe,
        )

        state.chart_path = tool(
            df=dataframe,
            category_column=category_column,
            value_column=value_column,
            title=state.question,
            output_filename="agent_chart.png",
        )

    else:
        raise ValueError(
            f"Unsupported tool: {tool_name}"
        )

    return state


def _find_numeric_column(
    dataframe: pd.DataFrame,
    excluded: set[str] | None = None,
) -> str:
    """
    Find a numeric column, including columns containing
    Decimal or numeric values represented as object dtype.
    """
    excluded = excluded or set()

    for column in dataframe.columns:
        if column in excluded:
            continue

        converted = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        if converted.notna().all():
            dataframe[column] = converted
            return column

    raise ValueError(
        "No suitable numeric column found."
    )


def _find_category_column(
    dataframe: pd.DataFrame,
) -> str:
    """
    Find the first non-numeric column in a DataFrame.
    """
    for column in dataframe.columns:
        converted = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        if not converted.notna().all():
            return column

    raise ValueError(
        "No suitable category column found."
    )
