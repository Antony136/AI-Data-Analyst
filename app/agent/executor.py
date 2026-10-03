import pandas as pd

from app.agent.state import AgentState
from app.tools.registry import get_tool


def _find_numeric_column(
    dataframe: pd.DataFrame,
    excluded: set[str] | None = None,
) -> str:
    """
    Find a numeric column.

    PostgreSQL NUMERIC values are returned by psycopg as
    Decimal objects, which Pandas may represent as object
    dtype. Therefore, use pd.to_numeric() rather than relying
    only on Pandas' native numeric dtype detection.
    """

    excluded = excluded or set()

    for column in dataframe.columns:

        if column in excluded:
            continue

        converted = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

        if converted.notna().any():
            return column

    raise ValueError(
        "No numeric column available for analysis."
    )


def _find_category_column(
    dataframe: pd.DataFrame,
) -> str:

    for column in dataframe.columns:

        if not pd.api.types.is_numeric_dtype(
            dataframe[column]
        ):
            return column

    raise ValueError(
        "No categorical column available."
    )


def _sync_dataframe_to_state(
    state: AgentState,
    dataframe: pd.DataFrame,
) -> None:
    """
    Synchronize the latest DataFrame back into agent state.

    This ensures that Python analysis results such as
    calculated percentages are available to the final
    answer generator.
    """

    state.columns = list(
        dataframe.columns
    )

    state.rows = list(
        dataframe.itertuples(
            index=False,
            name=None,
        )
    )


def execute_tool(
    tool_name: str,
    state: AgentState,
) -> AgentState:

    # --------------------------------------------------
    # SQL QUERY
    # --------------------------------------------------

    if tool_name == "sql_query":

        tool = get_tool("sql_query")

        result = tool(state.sql)

        state.sql = result["sql"]
        state.columns = result["columns"]
        state.rows = result["rows"]

    # --------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------

    elif tool_name == "create_dataframe":

        tool = get_tool(
            "create_dataframe"
        )

        dataframe = tool(
            columns=state.columns,
            rows=state.rows,
        )

        state.analysis["dataframe"] = dataframe

    # --------------------------------------------------
    # CALCULATE PERCENTAGE
    # --------------------------------------------------

    elif tool_name == "calculate_percentage":

        if "dataframe" not in state.analysis:

            raise ValueError(
                "DataFrame must be created before "
                "calculating percentages."
            )

        tool = get_tool(
            "calculate_percentage"
        )

        dataframe = state.analysis[
            "dataframe"
        ]

        value_column = _find_numeric_column(
            dataframe,
            excluded={"percentage"},
        )

        dataframe = tool(
            df=dataframe,
            value_column=value_column,
        )

        state.analysis[
            "dataframe"
        ] = dataframe

        _sync_dataframe_to_state(
            state=state,
            dataframe=dataframe,
        )

    # --------------------------------------------------
    # CALCULATE SUMMARY
    # --------------------------------------------------

    elif tool_name == "calculate_summary":

        if "dataframe" not in state.analysis:

            raise ValueError(
                "DataFrame must be created before "
                "calculating summary statistics."
            )

        tool = get_tool(
            "calculate_summary"
        )

        dataframe = state.analysis[
            "dataframe"
        ]

        value_column = _find_numeric_column(
            dataframe
        )

        summary = tool(
            df=dataframe,
            value_column=value_column,
        )

        state.analysis[
            "summary"
        ] = summary

    # --------------------------------------------------
    # CREATE BAR CHART
    # --------------------------------------------------

    elif tool_name == "create_bar_chart":

        if "dataframe" not in state.analysis:

            raise ValueError(
                "DataFrame must be created before "
                "creating a chart."
            )

        tool = get_tool(
            "create_bar_chart"
        )

        dataframe = state.analysis[
            "dataframe"
        ]

        category_column = _find_category_column(
            dataframe
        )

        value_column = _find_numeric_column(
            dataframe
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
