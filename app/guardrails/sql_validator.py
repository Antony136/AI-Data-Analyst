"""
SQL validation guardrails for AI Data Analyst.

Validates generated SQL before it reaches the database.

The validator supports:
- SELECT queries
- WITH ... SELECT queries
- CTEs
- table aliases
- multiple JOINs
- EXTRACT(... FROM ...) expressions

It rejects:
- non-SELECT statements
- multiple statements
- comments
- unknown physical tables
- forbidden SQL operations
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
    Remove common LLM formatting around SQL.
    """

    sql = sql.strip()

    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"^```\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = re.sub(
        r"^(here is the sql|sql)\s*:\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    return sql.strip()


def extract_cte_names(sql: str) -> set[str]:
    """
    Extract CTE names from a WITH clause.
    """

    sql = sql.strip()

    if not re.match(
        r"^WITH\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return set()

    names = set()

    position = 4
    length = len(sql)

    while position < length:

        while position < length and sql[position].isspace():
            position += 1

        recursive_match = re.match(
            r"RECURSIVE\b",
            sql[position:],
            flags=re.IGNORECASE,
        )

        if recursive_match:
            position += recursive_match.end()

            while position < length and sql[position].isspace():
                position += 1

        name_match = re.match(
            r"([A-Za-z_][A-Za-z0-9_]*)",
            sql[position:],
        )

        if not name_match:
            break

        cte_name = name_match.group(1).lower()

        names.add(cte_name)

        position += name_match.end()

        as_match = re.match(
            r"\s+AS\s*\(",
            sql[position:],
            flags=re.IGNORECASE,
        )

        if not as_match:
            break

        position += as_match.end()

        depth = 1

        while position < length and depth > 0:

            if sql[position] == "(":
                depth += 1

            elif sql[position] == ")":
                depth -= 1

            position += 1

        if depth != 0:
            break

        while position < length and sql[position].isspace():
            position += 1

        if position < length and sql[position] == ",":
            position += 1
            continue

        break

    return names


def _is_inside_extract(sql: str, position: int) -> bool:
    """
    Return True when the given position is inside EXTRACT(...).

    This prevents:

        EXTRACT(YEAR FROM orders.order_date)

    from being interpreted as a table reference.

    Normal subqueries are still allowed because only parentheses
    belonging to EXTRACT are ignored.
    """

    stack: list[str | None] = []

    index = 0

    while index < position:

        character = sql[index]

        if character == "(":

            before_parenthesis = sql[:index]

            function_match = re.search(
                r"([A-Za-z_][A-Za-z0-9_]*)\s*$",
                before_parenthesis,
                flags=re.IGNORECASE,
            )

            if function_match:
                function_name = function_match.group(1).lower()
            else:
                function_name = None

            stack.append(function_name)

        elif character == ")":

            if stack:
                stack.pop()

        index += 1

    return any(
        function_name == "extract"
        for function_name in stack
    )


def extract_table_names(
    sql: str,
    cte_names: set[str],
) -> list[str]:
    """
    Extract physical table references from FROM and JOIN clauses.

    Handles:
    - normal FROM clauses
    - JOIN clauses
    - table aliases
    - subqueries
    - CTEs

    Does not treat the FROM inside EXTRACT(...) as a table reference.
    """

    table_names = []

    pattern = re.compile(
        r"""
        \b
        (?:FROM|JOIN)
        \s+
        (
            [A-Za-z_][A-Za-z0-9_]*
            (?:\.[A-Za-z_][A-Za-z0-9_]*)?
        )
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    for match in pattern.finditer(sql):

        keyword_position = match.start()

        if _is_inside_extract(
            sql,
            keyword_position,
        ):
            continue

        table_name = match.group(1).lower()

        if table_name in cte_names:
            continue

        table_names.append(table_name)

    return table_names


def validate_tables(
    sql: str,
    allowed_tables: set[str],
) -> tuple[bool, str]:

    cte_names = extract_cte_names(sql)

    table_names = extract_table_names(
        sql,
        cte_names=cte_names,
    )

    for table_name in table_names:

        physical_table = table_name.split(".")[-1]

        if physical_table not in allowed_tables:

            return (
                False,
                (
                    "Unknown table referenced in SQL: "
                    f"{physical_table}. "
                    "Valid tables are: "
                    + ", ".join(sorted(allowed_tables))
                ),
            )

    return True, sql


def validate_sql(
    sql: str,
    allowed_tables: set[str],
) -> tuple[bool, str]:

    sql = clean_sql(sql)

    if not sql:
        return False, "Generated SQL is empty."

    if "--" in sql:
        return False, "SQL comments are not allowed."

    if "/*" in sql or "*/" in sql:
        return False, "SQL block comments are not allowed."

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    if len(statements) != 1:
        return False, "Multiple SQL statements are not allowed."

    if not re.match(
        r"^\s*(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return False, "Only SELECT queries are allowed."

    for keyword in FORBIDDEN_KEYWORDS:

        if re.search(
            rf"\b{keyword}\b",
            sql,
            flags=re.IGNORECASE,
        ):
            return (
                False,
                f"Forbidden SQL operation detected: {keyword}",
            )

    valid, result = validate_tables(
        sql=sql,
        allowed_tables=allowed_tables,
    )

    if not valid:
        return False, result

    return True, result
