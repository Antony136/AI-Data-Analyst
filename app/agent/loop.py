"""
Main agent loop for AI Data Analyst.

Connects planning, schema retrieval, SQL generation,
tool execution, and final answer generation.
"""

from app.agent.answer_generator import generate_answer
from app.agent.executor import execute_tool
from app.agent.planner import plan_tools
from app.agent.sql_generator import generate_sql
from app.agent.state import AgentState
from app.tools.schema_tool import get_database_schema


def run_agent(question: str) -> AgentState:
    """
    Run the complete analytics agent for a user question.
    """

    state = AgentState(
        question=question,
    )

    # --------------------------------------------------
    # 1. Get database schema
    # --------------------------------------------------

    state.schema_text = get_database_schema()

    # --------------------------------------------------
    # 2. Plan which tools are required
    # --------------------------------------------------

    state.selected_tools = plan_tools(question)

    # --------------------------------------------------
    # 3. Generate SQL when database data is required
    # --------------------------------------------------

    if "sql_query" in state.selected_tools:
        state.sql = generate_sql(
            question=question,
            schema_text=state.schema_text,
        )

    # --------------------------------------------------
    # 4. Execute selected tools
    # --------------------------------------------------

    for tool_name in state.selected_tools:
        state.iteration += 1

        state = execute_tool(
            tool_name=tool_name,
            state=state,
        )

    # --------------------------------------------------
    # 5. Generate final natural-language answer
    # --------------------------------------------------

    if state.sql and state.columns:
        state.answer = generate_answer(
            question=state.question,
            sql=state.sql,
            columns=state.columns,
            rows=state.rows,
        )

    return state
