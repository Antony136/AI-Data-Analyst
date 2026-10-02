from app.agent.planner import plan_tools


QUESTIONS = [
    "What was the total number of orders in 2025?",
    "What percentage of revenue came from each product category in 2025?",
    "Show revenue by product category in 2025 as a chart.",
    "Give me the average and maximum revenue by category in 2025.",
]


def main():
    print("=" * 70)
    print("ANALYTICS PLANNER TEST")
    print("=" * 70)

    for index, question in enumerate(QUESTIONS, start=1):
        print(f"\nQUESTION {index}")
        print("-" * 70)
        print(question)

        tools = plan_tools(question)

        print("\nSELECTED TOOLS")
        print("-" * 70)

        for tool in tools:
            print(f"- {tool}")

    print("\n" + "=" * 70)
    print("PLANNER TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
