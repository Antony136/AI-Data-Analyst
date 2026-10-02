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
    rows: str,
) -> str:
    return f"""
You are the final answer component of an AI data analyst.

Answer the user's question using ONLY the
AUTHORITATIVE DATABASE RESULT provided below.

USER QUESTION
-------------
{question}

EXECUTED SQL
------------
{sql}

RESULT COLUMNS
--------------
{columns}

AUTHORITATIVE DATABASE RESULT
-----------------------------
{rows}

STRICT RULES
------------
1. The AUTHORITATIVE DATABASE RESULT is the source of truth.
2. Do not invent any numbers.
3. Do not estimate or guess values.
4. Do not change the magnitude of any number.
5. Do not add or remove digits.
6. You may use the numbers exactly as shown.
7. You may add natural-language explanation.
8. Do not introduce a currency symbol.
9. Do not assume a currency.
10. Do not convert units.
11. Do not calculate new percentages, differences,
    totals, averages, or other metrics unless those
    values are already present in the result.
12. Do not mention SQL, prompts, models, or internal systems.
13. Answer concisely and directly.
14. Clearly associate each value with its corresponding
    category or dimension.

IMPORTANT
---------
The AUTHORITATIVE DATABASE RESULT was generated
directly from the database by the application.

Do not modify its numeric values.

FINAL ANSWER:
""".strip()



def build_sql_correction_prompt(
    question: str,
    schema_text: str,
    failed_sql: str,
    error_message: str,
) -> str:
    """
    Build a strict prompt asking the LLM to correct SQL
    that failed during PostgreSQL execution.
    """

    return f"""
You are an expert PostgreSQL data analyst.

A SQL query generated for the user's question failed
during PostgreSQL database execution.

Your task is to make the SMALLEST POSSIBLE CORRECTION
needed to fix the reported database error.

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

CORRECTION RULES
----------------
1. Return ONLY the corrected SQL.
2. Do NOT use Markdown code fences.
3. Use PostgreSQL syntax.
4. Use ONLY tables and columns present in the schema.
5. Preserve the user's original question and intended result.
6. Preserve the existing query structure whenever possible.
7. Make the smallest possible change required to fix
   the reported database error.
8. Do NOT add tables or JOINs unless they are required
   to fix the specific error.
9. Do NOT remove tables or JOINs unless they are
   responsible for the specific error.
10. Do NOT change the calculation logic unless the
    database error requires it.
11. Do NOT change filters unless the database error
    requires it.
12. Do NOT change GROUP BY logic unless the database
    error requires it.
13. Every table alias MUST be unique.
14. Never assign the same alias to two different tables.
15. Before returning the SQL, verify that every alias
    referenced in SELECT, JOIN, WHERE, GROUP BY, and
    ORDER BY is defined exactly once.
16. Do NOT introduce unnecessary tables such as payments
    when the question can be answered from the existing
    tables.
17. Do NOT invent functions that are not supported by
    PostgreSQL.
18. Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, CREATE, GRANT, or REVOKE.
19. Do NOT assume a currency.
20. Do NOT add currency symbols.

IMPORTANT
---------
The DATABASE ERROR tells you what is wrong.

Fix THAT error.

Do not redesign the query.

Do not rewrite a correct query unnecessarily.

Return only executable PostgreSQL SQL.

CORRECTED SQL:
""".strip()

def build_answer_correction_prompt(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
    failed_answer: str,
    error_message: str,
) -> str:
    """
    Build a strict correction prompt for an answer
    that failed deterministic validation.
    """

    return f"""
You are correcting a database-backed analytics answer.

The previous answer was rejected because it contained
information that did not exactly match the database result.

USER QUESTION
-------------
{question}

DATABASE RESULT COLUMNS
-----------------------
{columns}

DATABASE RESULT ROWS
--------------------
{rows}

PREVIOUS ANSWER
---------------
{failed_answer}

VALIDATION ERROR
----------------
{error_message}

CRITICAL NUMERIC RULE
---------------------
The DATABASE RESULT ROWS are the ONLY source of numeric facts.

You MUST NOT calculate, estimate, infer, approximate,
or invent any new numeric value.

You MUST copy numeric values from DATABASE RESULT ROWS.

The following numeric values are the ONLY numeric values
available for the answer:

{rows}

If a value is not present in DATABASE RESULT ROWS,
DO NOT mention it.

FORMATTING RULES
----------------
1. You may add thousands separators.
2. You may display decimal values rounded to two decimal places.
3. Do not change the magnitude of a number.
4. Do not introduce a currency symbol.
5. Do not assume a currency.
6. Do not convert units.
7. Do not calculate percentages or differences unless
   those values are already present in the result.
8. Do not add numbers from your own knowledge.
9. Do not mention unsupported information.
10. Answer the user's question directly.
11. Return only the corrected natural-language answer.

CORRECTED ANSWER:
""".strip()
