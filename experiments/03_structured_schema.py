from app.database.schema import get_schema


def main():

    schema = get_schema()

    print("=" * 70)
    print("STRUCTURED DATABASE SCHEMA")
    print("=" * 70)

    for table in schema:

        print(f"\nTABLE: {table.name}")
        print("-" * 70)

        for column in table.columns:

            flags = []

            if column.primary_key:
                flags.append("PRIMARY KEY")

            if not column.nullable:
                flags.append("NOT NULL")

            flag_text = ""

            if flags:
                flag_text = (
                    " ["
                    + ", ".join(flags)
                    + "]"
                )

            print(
                f"  {column.name}"
                f" : {column.data_type}"
                f"{flag_text}"
            )

        if table.foreign_keys:

            print("\n  FOREIGN KEYS:")

            for foreign_key in table.foreign_keys:

                print(
                    f"    {foreign_key.column}"
                    f" -> "
                    f"{foreign_key.referenced_table}"
                    f"."
                    f"{foreign_key.referenced_column}"
                )

    print("\n" + "=" * 70)
    print("STRUCTURED SCHEMA COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()