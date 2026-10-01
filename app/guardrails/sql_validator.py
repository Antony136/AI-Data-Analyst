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
    Remove Markdown code fences and surrounding whitespace.
    """

    sql = sql.strip()

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

    return sql.strip()


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate generated SQL before execution.

    Returns:
        (True, cleaned_sql) if safe.
        (False, reason) if unsafe.
    """

    cleaned_sql = clean_sql(sql)

    if not cleaned_sql:
        return False, "SQL query is empty."

    normalized_sql = cleaned_sql.upper()

    if not normalized_sql.startswith("SELECT"):
        return (
            False,
            "Only SELECT statements are allowed.",
        )

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            normalized_sql,
        ):
            return (
                False,
                f"Forbidden SQL keyword detected: {keyword}",
            )

    return True, cleaned_sql