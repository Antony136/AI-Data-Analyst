"""
Schema tool for AI Data Analyst.

Provides the database schema in a format suitable
for the LLM and agent components.
"""

from app.database.schema import (
    format_schema_for_llm,
    get_schema,
)


def get_database_schema() -> str:
    """
    Retrieve and format the current database schema
    for use by the AI agent.
    """
    schema = get_schema()

    return format_schema_for_llm(schema)
