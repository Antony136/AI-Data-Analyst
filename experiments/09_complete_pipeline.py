from app.agent.pipeline import answer_question


def main():

    print("=" * 70)
    print("AI DATA ANALYST")
    print("=" * 70)

    question = "How many customers do we have?"

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
    print(result["rows"])

    print("\nFINAL ANSWER")
    print("-" * 70)
    print(result["answer"])

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()