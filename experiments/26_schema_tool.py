from app.tools.schema_tool import get_database_schema


def main():
    print("=" * 70)
    print("SCHEMA TOOL TEST")
    print("=" * 70)

    schema_text = get_database_schema()

    print("\nDATABASE SCHEMA")
    print("-" * 70)
    print(schema_text)

    print("\n" + "=" * 70)
    print("SCHEMA TOOL TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
