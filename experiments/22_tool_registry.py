from app.tools.registry import get_tool, list_tools


def main():
    print("=" * 70)
    print("TOOL REGISTRY TEST")
    print("=" * 70)

    tools = list_tools()

    print("\nREGISTERED TOOLS")
    print("-" * 70)

    for tool_name in tools:
        print(f"- {tool_name}")

    print("\nTOOL LOOKUP")
    print("-" * 70)

    sql_tool = get_tool("sql_query")

    print(f"sql_query → {sql_tool.__name__}")

    print("\n" + "=" * 70)
    print("TOOL REGISTRY TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
