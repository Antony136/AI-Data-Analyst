from app.llm.client import generate_response


def main():

    print("=" * 70)
    print("OLLAMA LLM TEST")
    print("=" * 70)

    prompt = """
You are an AI data analyst.

Explain in one short sentence what SQL is.
"""

    response = generate_response(prompt)

    print("\nMODEL RESPONSE")
    print("-" * 70)
    print(response)

    print("\n" + "=" * 70)
    print("OLLAMA TEST COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()