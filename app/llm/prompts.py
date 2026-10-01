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

RULES
-----
1. Generate only SQL.
2. Do not use markdown code fences.
3. Use only tables and columns that exist in the schema.
4. Use PostgreSQL syntax.
5. Do not modify the database.
6. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE.
7. Prefer clear and simple SQL.
8. Answer the user's question directly.

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

ANSWER:
""".strip()
