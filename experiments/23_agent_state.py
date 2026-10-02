from app.agent.state import AgentState


def main():
    print("=" * 70)
    print("AGENT STATE TEST")
    print("=" * 70)

    state = AgentState(
        question="What was the revenue by category in 2025?"
    )

    print("\nINITIAL STATE")
    print("-" * 70)
    print(f"Question: {state.question}")
    print(f"SQL: {state.sql}")
    print(f"Rows: {state.rows}")
    print(f"Answer: {state.answer}")

    state.selected_tools = [
        "sql_query",
        "create_dataframe",
        "calculate_percentage",
    ]

    state.sql = """
    SELECT category, SUM(revenue)
    FROM category_revenue
    GROUP BY category;
    """.strip()

    state.columns = [
        "category",
        "revenue",
    ]

    state.rows = [
        ("Electronics", 41067364.604),
        ("Home", 18083529.0395),
    ]

    state.analysis = {
        "total_revenue": 59150893.6435,
        "top_category": "Electronics",
    }

    state.answer = (
        "Electronics generated the highest revenue."
    )

    print("\nUPDATED STATE")
    print("-" * 70)
    print(f"Question: {state.question}")
    print(f"Tools: {state.selected_tools}")
    print(f"SQL: {state.sql}")
    print(f"Columns: {state.columns}")
    print(f"Rows: {state.rows}")
    print(f"Analysis: {state.analysis}")
    print(f"Answer: {state.answer}")

    print("\n" + "=" * 70)
    print("AGENT STATE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
