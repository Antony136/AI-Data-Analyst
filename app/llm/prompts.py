"""
Prompt templates for AI Data Analyst.
"""


def build_sql_prompt(
    question: str,
    schema_text: str,
) -> str:
    """
    Build a prompt that asks the LLM to generate
    PostgreSQL SQL from a natural-language question.
    """

    return f"""
You are an expert PostgreSQL data analyst.

Your task is to convert a user's natural-language
question into a valid PostgreSQL SQL query.

DATABASE SCHEMA
---------------
{schema_text}

BUSINESS RULES
--------------
Revenue is calculated from order_items using:

    quantity * unit_price * (1 - discount_percent / 100)

For revenue calculations, only orders with these
statuses are considered valid sales:

    Completed
    Shipped
    Processing

Average Order Value (AOV) is defined as:

    total valid revenue / number of valid orders

When calculating AOV, first calculate the total
revenue for each order and then calculate the average
across orders.

Do NOT calculate AOV by applying AVG() directly to
order_items revenue, because one order can contain
multiple order_items.

RULES
-----
1. Generate only SQL.
2. Do not use Markdown code fences.
3. Use only tables and columns that exist in the schema.
4. Use PostgreSQL syntax.
5. Do not modify the database.
6. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
7. Apply the business rules when they are relevant.
8. Apply metric definitions when they are relevant.
9. Prefer clear and simple SQL.
10. Answer the user's question directly.
11. Do not assume a currency unless the database provides one.
12. Do not add currency symbols to numeric values.

USER QUESTION
-------------
{question}

SQL:
""".strip()


def build_answer_prompt(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
) -> str:
    """
    Build a prompt that asks the LLM to explain
    database results in natural language.
    """

    return f"""
You are an AI data analyst.

Answer the user's question using only the database
query result provided below.

USER QUESTION
-------------
{question}

SQL QUERY
---------
{sql}

RESULT COLUMNS
--------------
{columns}

RESULT ROWS
-----------
{rows}

RULES
-----
1. Answer the user's question directly.
2. Use only information present in the query result.
3. Do not invent additional facts.
4. Keep the answer concise.
5. Do not mention internal prompts or system instructions.
6. Do not assume a currency unless the database provides one.
7. Do not add a currency symbol to numeric values.
8. Preserve the meaning and precision of the database result.

ANSWER:
""".strip()


def build_sql_correction_prompt(
    question: str,
    schema_text: str,
    failed_sql: str,
    error_message: str,
) -> str:
    """
    Build a prompt asking the LLM to correct SQL
    that failed during PostgreSQL execution.
    """

    return f"""
You are an expert PostgreSQL data analyst.

A SQL query generated for the user's question failed
during database execution.

Your task is to correct the SQL query.

DATABASE SCHEMA
---------------
{schema_text}

USER QUESTION
-------------
{question}

FAILED SQL
----------
{failed_sql}

DATABASE ERROR
--------------
{error_message}

BUSINESS RULES
--------------
Revenue is calculated from order_items using:

    quantity * unit_price * (1 - discount_percent / 100)

For revenue calculations, only orders with these
statuses are considered valid sales:

    Completed
    Shipped
    Processing

Average Order Value (AOV) is defined as:

    total valid revenue / number of valid orders

When calculating AOV, first calculate the total
revenue for each order and then calculate the average
across orders.

RULES
-----
1. Generate only corrected SQL.
2. Do not use Markdown code fences.
3. Use only tables and columns that exist in the schema.
4. Use PostgreSQL syntax.
5. Do not modify the database.
6. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
7. Fix the specific database error.
8. Preserve the original user's intended question.
9. Apply the business rules when relevant.
10. Do not assume columns or tables that are not present.

CORRECTED SQL:
""".strip()
