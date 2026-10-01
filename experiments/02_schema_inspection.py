from app.database.schema import (
    get_tables,
    get_columns,
    get_primary_keys,
    get_foreign_keys,
)


def main():

    print("=" * 70)
    print("DATABASE SCHEMA INSPECTION")
    print("=" * 70)

    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    print("\nTABLES")
    print("-" * 70)

    tables = get_tables()

    for table in tables:
        print(f"- {table}")

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    print("\nCOLUMNS")
    print("-" * 70)

    columns = get_columns()

    for (
        table,
        column,
        data_type,
        nullable,
    ) in columns:

        print(
            f"{table}.{column}"
            f" | {data_type}"
            f" | nullable={nullable}"
        )

    # --------------------------------------------------------
    # PRIMARY KEYS
    # --------------------------------------------------------

    print("\nPRIMARY KEYS")
    print("-" * 70)

    primary_keys = get_primary_keys()

    for table, column in primary_keys:
        print(
            f"{table}.{column}"
        )

    # --------------------------------------------------------
    # FOREIGN KEYS
    # --------------------------------------------------------

    print("\nFOREIGN KEYS")
    print("-" * 70)

    foreign_keys = get_foreign_keys()

    for (
        table,
        column,
        foreign_table,
        foreign_column,
    ) in foreign_keys:

        print(
            f"{table}.{column}"
            f" -> "
            f"{foreign_table}.{foreign_column}"
        )

    print("\n" + "=" * 70)
    print("SCHEMA INSPECTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
