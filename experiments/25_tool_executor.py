from app.agent.executor import execute_tool
from app.agent.state import AgentState


def main():
    print("=" * 70)
    print("TOOL EXECUTOR TEST")
    print("=" * 70)

    state = AgentState(
        question="What was the revenue by category in 2025?"
    )

    state.sql = """
    SELECT
        p.category,
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100)
        ) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE
        o.order_status IN (
            'Completed',
            'Shipped',
            'Processing'
        )
        AND o.order_date >= '2025-01-01'
        AND o.order_date < '2026-01-01'
    GROUP BY p.category
    ORDER BY revenue DESC;
    """.strip()

    tools = [
        "sql_query",
        "create_dataframe",
        "calculate_percentage",
        "create_bar_chart",
    ]

    for tool_name in tools:
        print(f"\nEXECUTING: {tool_name}")
        print("-" * 70)

        state = execute_tool(
            tool_name=tool_name,
            state=state,
        )

        print("Completed.")

    print("\nSQL")
    print("-" * 70)
    print(state.sql)

    print("\nQUERY RESULT")
    print("-" * 70)

    for row in state.rows:
        print(row)

    print("\nANALYSIS")
    print("-" * 70)

    dataframe = state.analysis["dataframe"]

    print(dataframe.to_string(index=False))

    print("\nCHART")
    print("-" * 70)
    print(f"Saved to: {state.chart_path}")

    print("\n" + "=" * 70)
    print("TOOL EXECUTOR TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
