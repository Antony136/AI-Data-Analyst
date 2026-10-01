from app.agent.pipeline import answer_question


def main():
    print("=" * 70)
    print("TIME-SERIES ANALYSIS")
    print("=" * 70)

    question = "What was the monthly revenue in 2025?"

    result = answer_question(question)

    print("\nQUESTION")
    print("-" * 70)
    print(result["question"])

    print("\nGENERATED SQL")
    print("-" * 70)
    print(result["sql"])

    print("\nDATABASE RESULT")
    print("-" * 70)
    print(result["columns"])

    for row in result["rows"]:
        print(row)

    print("\nFINAL ANSWER")
    print("-" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("TIME-SERIES ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
