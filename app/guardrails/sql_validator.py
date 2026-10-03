"""
SQL validation and safety checks for AI Data Analyst.

Validates SQL safety and verifies that referenced database
tables exist in the known application schema.
"""

import re


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
}


def clean_sql(sql: str) -> str:
    """
    Clean common formatting added by an LLM.

    Removes:
    - Markdown SQL fences
    - Leading 'SQL:' labels
    - Backticks

    Preserves valid PostgreSQL WITH queries.
    """

    sql = sql.strip()

    sql = re.sub(
        r"```(?:sql)?",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"^(?:here\s+is\s+the\s+)?sql\s*:\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = sql.replace("```", "")
    sql = sql.replace("`", "")

    return sql.strip()


def extract_cte_names(sql: str) -> set[str]:
    """
    Extract Common Table Expression names.

    Handles nested SELECT statements inside CTEs.

    Example:

        WITH
            revenue AS (
                SELECT ...
            ),
            totals AS (
                SELECT ...
            )
        SELECT *
        FROM totals

    Returns:

        {"revenue", "totals"}
    """

    cte_names: set[str] = set()

    match = re.match(
        r"\s*WITH\s+",
        sql,
        flags=re.IGNORECASE,
    )

    if not match:
        return cte_names

    position = match.end()
    length = len(sql)

    while position < length:

        # --------------------------------------------------
        # Skip whitespace before the next CTE
        # --------------------------------------------------

        while position < length and sql[position].isspace():
            position += 1

        # --------------------------------------------------
        # Read CTE name
        # --------------------------------------------------

        name_match = re.match(
            r"([a-zA-Z_][a-zA-Z0-9_]*)",
            sql[position:],
        )

        if not name_match:
            break

        cte_name = name_match.group(1).lower()

        position += name_match.end()

        # --------------------------------------------------
        # Optional column list
        #
        # Example:
        #
        # revenue(category, amount) AS (...)
        # --------------------------------------------------

        while position < length and sql[position].isspace():
            position += 1

        if position < length and sql[position] == "(":

            depth = 0

            while position < length:

                character = sql[position]

                if character == "(":
                    depth += 1

                elif character == ")":
                    depth -= 1

                    if depth == 0:
                        position += 1
                        break

                position += 1

        # --------------------------------------------------
        # Expect AS
        # --------------------------------------------------

        as_match = re.match(
            r"\s*AS\s*",
            sql[position:],
            flags=re.IGNORECASE,
        )

        if not as_match:
            break

        position += as_match.end()

        # --------------------------------------------------
        # Expect opening parenthesis of CTE body
        # --------------------------------------------------

        while position < length and sql[position].isspace():
            position += 1

        if position >= length or sql[position] != "(":
            break

        cte_names.add(cte_name)

        # --------------------------------------------------
        # Skip complete CTE body.
        #
        # Parenthesis depth allows nested SELECTs.
        # --------------------------------------------------

        depth = 0

        while position < length:

            character = sql[position]

            if character == "(":
                depth += 1

            elif character == ")":
                depth -= 1

                if depth == 0:
                    position += 1
                    break

            position += 1

        # --------------------------------------------------
        # Check whether another CTE follows.
        # --------------------------------------------------

        while position < length and sql[position].isspace():
            position += 1

        if position >= length or sql[position] != ",":
            break

        position += 1

    return cte_names


def extract_table_names(sql: str) -> list[str]:
    """
    Extract table-like names appearing after FROM or JOIN.

    CTE names are excluded from the returned list.
    """

    matches = re.findall(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE,
    )

    cte_names = extract_cte_names(sql)

    return list(
        dict.fromkeys(
            table.lower()
            for table in matches
            if table.lower() not in cte_names
        )
    )


def validate_tables(
    sql: str,
    allowed_tables: set[str],
) -> tuple[bool, str]:

    referenced_tables = extract_table_names(sql)

    for table in referenced_tables:

        if table not in allowed_tables:

            return False, (
                f"Unknown table referenced in SQL: {table}. "
                f"Valid tables are: "
                f"{', '.join(sorted(allowed_tables))}"
            )

    return True, sql


def validate_sql(
    sql: str,
    allowed_tables: set[str] | None = None,
) -> tuple[bool, str]:

    # ------------------------------------------------------
    # 1. Clean LLM output
    # ------------------------------------------------------

    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        return False, "SQL query is empty."

    # ------------------------------------------------------
    # 2. Reject Markdown fences that survived cleaning
    # ------------------------------------------------------

    if "```" in cleaned_sql:
        return False, (
            "Markdown code fences are not allowed in SQL."
        )

    # ------------------------------------------------------
    # 3. Only SELECT / WITH queries are allowed
    # ------------------------------------------------------

    normalized_sql = cleaned_sql.upper()

    is_select = normalized_sql.startswith("SELECT")
    is_with = normalized_sql.startswith("WITH")

    if not is_select and not is_with:
        return False, (
            "Only SELECT statements are allowed."
        )

    # ------------------------------------------------------
    # 4. Reject dangerous SQL keywords
    # ------------------------------------------------------

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            normalized_sql,
        ):
            return False, (
                f"Forbidden SQL keyword detected: {keyword}"
            )

    # ------------------------------------------------------
    # 5. Validate referenced tables
    # ------------------------------------------------------

    if allowed_tables is not None:

        valid, result = validate_tables(
            sql=cleaned_sql,
            allowed_tables=allowed_tables,
        )

        if not valid:
            return False, result

    return True, cleaned_sql
