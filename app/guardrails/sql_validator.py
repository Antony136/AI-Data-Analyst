"""
SQL validation and safety checks for AI Data Analyst.
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
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
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

    # Remove trailing Markdown code fences or whitespace.
    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    return sql.strip()


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate that the generated query is a safe SELECT statement.
    """

    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        return False, "SQL query is empty."

    normalized_sql = cleaned_sql.upper()

    if not normalized_sql.startswith("SELECT"):
        return False, "Only SELECT statements are allowed."

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, normalized_sql):
            return False, (
                f"Forbidden SQL keyword detected: {keyword}"
            )

    return True, cleaned_sql
