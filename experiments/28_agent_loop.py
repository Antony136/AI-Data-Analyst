from app.agent.loop import run_agent


def main():
    print("=" * 70)
    print("AI DATA ANALYST - COMPLETE AGENT TEST")
    print("=" * 70)

    question = "What was the revenue by product category in 2025?"

    state = run_agent(question)

    print("\nQUESTION")
    print("-" * 70)
    print(state.question)

    print("\nSELECTED TOOLS")
    print("-" * 70)

    for tool in state.selected_tools:
        print(f"- {tool}")

    print("\nITERATIONS")
    print("-" * 70)
    print(state.iteration)

    print("\nGENERATED SQL")
    print("-" * 70)
    print(state.sql)

    print("\nQUERY RESULT")
    print("-" * 70)

    for row in state.rows:
        print(row)

    if "dataframe" in state.analysis:
        print("\nDATAFRAME")
        print("-" * 70)
        print(
            state.analysis["dataframe"].to_string(
                index=False
            )
        )

    print("\nCHART")
    print("-" * 70)

    if state.chart_path:
        print(f"Saved to: {state.chart_path}")
    else:
        print("No chart generated.")

    print("\nFINAL ANSWER")
    print("-" * 70)
    print(state.answer)

    print("\n" + "=" * 70)
    print("COMPLETE AGENT TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
