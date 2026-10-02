import time

from app.agent.trace import AgentTrace


def main():
    print("=" * 70)
    print("AGENT TRACE TEST")
    print("=" * 70)

    trace = AgentTrace(
        question=(
            "What was the revenue by product "
            "category in 2025?"
        )
    )

    trace.start()

    trace.selected_tools = [
        "sql_query",
        "create_dataframe",
        "create_bar_chart",
    ]

    trace.sql = (
        "SELECT category, SUM(revenue) "
        "FROM products GROUP BY category"
    )

    time.sleep(0.01)

    trace.add_tool_trace(
        tool_name="sql_query",
        success=True,
        duration_ms=12.5,
    )

    trace.set_result(
        columns=[
            "category",
            "total_revenue",
        ],
        rows=[
            ("Electronics", 41067364.60),
            ("Home", 18083529.04),
        ],
    )

    trace.final_answer = (
        "Electronics generated the highest revenue."
    )

    trace.finish()

    result = trace.to_dict()

    print("\nTRACE")
    print("-" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")

    assert result["question"].startswith(
        "What was the revenue"
    )

    assert result["selected_tools"] == [
        "sql_query",
        "create_dataframe",
        "create_bar_chart",
    ]

    assert result["result_rows"] == 2
    assert result["result_columns"] == 2

    assert len(result["tool_traces"]) == 1

    assert result["tool_traces"][0][
        "tool_name"
    ] == "sql_query"

    assert result["total_duration_ms"] > 0

    print("\n" + "=" * 70)
    print("AGENT TRACE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
