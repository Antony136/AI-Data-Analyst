from app.agent.pipeline import answer_question


def main():

    print("=" * 70)
    print("ANALYTICAL QUESTION")
    print("=" * 70)

    question = "What was the revenue in 2025?"

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
    print("ANALYTICAL QUESTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
