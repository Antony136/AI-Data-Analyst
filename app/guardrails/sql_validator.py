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
    Clean common LLM formatting around SQL.
    """

    sql = sql.strip()

    # Remove Markdown SQL code fences.
    sql = re.sub(
        r"```(?:sql)?",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # Remove common prefixes such as:
    # "SQL:"
    # "Here is the SQL:"
    sql = re.sub(
        r"^(?:here\s+is\s+the\s+)?sql\s*:\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # If the model added explanatory text before SELECT,
    # keep only the SQL statement.
    select_match = re.search(
        r"\bSELECT\b",
        sql,
        flags=re.IGNORECASE,
    )

    if select_match:
        sql = sql[select_match.start():]

    # Remove any remaining Markdown backticks.
    sql = sql.replace("```", "")
    sql = sql.replace("`", "")

    return sql.strip()


def extract_table_names(sql: str) -> list[str]:
    """
    Extract table names used after FROM and JOIN clauses.

    This intentionally focuses on ordinary table references.
    CTE/subquery parsing can be added later if needed.
    """

    matches = re.findall(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        flags=re.IGNORECASE,
    )

    return list(dict.fromkeys(
        table.lower()
        for table in matches
    ))


def validate_tables(
    sql: str,
    allowed_tables: set[str],
) -> tuple[bool, str]:
    """
    Verify that all referenced tables exist in the schema.
    """

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
    """
    Validate that the generated query is a safe SELECT statement.

    If allowed_tables is provided, all tables referenced by
    FROM and JOIN clauses are also checked against the schema.
    """

    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        return False, "SQL query is empty."

    if "```" in cleaned_sql:
        return False, (
            "Markdown code fences are not allowed in SQL."
        )

    normalized_sql = cleaned_sql.upper()

    if not normalized_sql.startswith("SELECT"):
        return False, "Only SELECT statements are allowed."

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized_sql):
            return False, (
                f"Forbidden SQL keyword detected: {keyword}"
            )

    if allowed_tables is not None:
        valid, result = validate_tables(
            sql=cleaned_sql,
            allowed_tables=allowed_tables,
        )

        if not valid:
            return False, result

    return True, cleaned_sql
