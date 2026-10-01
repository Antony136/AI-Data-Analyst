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
