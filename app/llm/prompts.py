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
    return f"""
You are the final answer component of an AI data analyst.

Answer the user's question using ONLY the database result
provided below.

USER QUESTION
-------------
{question}

EXECUTED SQL
------------
{sql}

RESULT COLUMNS
--------------
{columns}

RESULT ROWS
-----------
{rows}

STRICT RULES
------------
1. Use ONLY the information present in RESULT ROWS.
2. Do not invent, estimate, round, scale, transform, or recalculate
   any numeric value.
3. Every numeric value you mention must match a value from RESULT ROWS.
4. Do not accidentally remove or add digits.
5. Preserve the magnitude of every number exactly.
6. You may add thousands separators for readability.
7. You may round a number ONLY if the rounded value is mathematically
   derived from the exact value in RESULT ROWS.
8. Do not change millions into thousands or thousands into millions.
9. Do not assume a currency.
10. Do not add a currency symbol.
11. Do not mention information that is not supported by the result.
12. Do not mention the SQL query, prompt, model, or internal system.
13. Answer concisely and directly.
14. If the result contains multiple rows, clearly identify the
    corresponding category or dimension for each value.

IMPORTANT:
The RESULT ROWS are authoritative.
The numbers in RESULT ROWS must be treated as exact source data.

FINAL ANSWER:
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
