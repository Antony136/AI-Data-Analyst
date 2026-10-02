"""
Deterministic plan validation for AI Data Analyst.

Validates the tool plan produced by the LLM planner.
No LLM call is made here.
"""

from app.tools.registry import list_tools


def validate_plan(tools: list[str]) -> list[str]:
    """
    Validate and normalize a planner-generated tool list.

    Returns a cleaned list of tools that is safe for
    the executor to process.
    """

    if not isinstance(tools, list):
        raise ValueError(
            "Tool plan must be a list."
        )

    if not tools:
        raise ValueError(
            "Tool plan cannot be empty."
        )

    available_tools = set(list_tools())

    # --------------------------------------------------
    # 1. Validate tool names
    # --------------------------------------------------

    for tool in tools:
        if not isinstance(tool, str):
            raise ValueError(
                "Every tool in the plan must be a string."
            )

        if tool not in available_tools:
            raise ValueError(
                f"Unknown tool in plan: {tool}"
            )

    # --------------------------------------------------
    # 2. Remove duplicate tools
    # --------------------------------------------------

    cleaned_tools = list(dict.fromkeys(tools))

    # --------------------------------------------------
    # 3. Define DataFrame-dependent tools
    # --------------------------------------------------

    dataframe_tools = {
        "calculate_percentage",
        "calculate_summary",
        "create_bar_chart",
    }

    # --------------------------------------------------
    # 4. DataFrame-dependent tools require create_dataframe
    # --------------------------------------------------

    for tool in dataframe_tools:
        if tool in cleaned_tools:
            if "create_dataframe" not in cleaned_tools:
                raise ValueError(
                    f"'{tool}' requires "
                    "'create_dataframe' to run first."
                )

    # --------------------------------------------------
    # 5. create_dataframe requires sql_query
    # --------------------------------------------------

    if "create_dataframe" in cleaned_tools:
        if "sql_query" not in cleaned_tools:
            raise ValueError(
                "'create_dataframe' requires "
                "'sql_query' to run first."
            )

    # --------------------------------------------------
    # 6. SQL must execute before DataFrame creation
    # --------------------------------------------------

    if "sql_query" in cleaned_tools:
        sql_index = cleaned_tools.index("sql_query")

        if "create_dataframe" in cleaned_tools:
            dataframe_index = cleaned_tools.index(
                "create_dataframe"
            )

            if dataframe_index < sql_index:
                raise ValueError(
                    "'create_dataframe' cannot execute "
                    "before 'sql_query'."
                )

    # --------------------------------------------------
    # 7. DataFrame creation must execute before
    #    DataFrame-dependent tools
    # --------------------------------------------------

    if "create_dataframe" in cleaned_tools:
        dataframe_index = cleaned_tools.index(
            "create_dataframe"
        )

        for tool in dataframe_tools:
            if tool in cleaned_tools:
                tool_index = cleaned_tools.index(tool)

                if tool_index < dataframe_index:
                    raise ValueError(
                        f"'{tool}' cannot execute before "
                        "'create_dataframe'."
                    )

    return cleaned_tools
