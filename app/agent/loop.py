"""
Main agent loop for AI Data Analyst.

Connects planning, validation, schema retrieval, SQL generation,
SQL correction, tool execution, and final answer generation.
"""

from app.agent.answer_generator import generate_answer
from app.agent.executor import execute_tool
from app.agent.planner import plan_tools
from app.agent.sql_generator import (
    MAX_SQL_RETRIES,
    correct_sql,
    generate_sql,
)
from app.agent.state import AgentState
from app.guardrails.plan_validator import validate_plan
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
    # 2. Ask the LLM planner for a tool plan
    # --------------------------------------------------

    planned_tools = plan_tools(question)

    # --------------------------------------------------
    # 3. Validate the LLM-generated plan
    # --------------------------------------------------

    state.selected_tools = validate_plan(
        planned_tools
    )

    # --------------------------------------------------
    # 4. Generate SQL when database data is required
    # --------------------------------------------------

    if "sql_query" in state.selected_tools:
        state.sql = generate_sql(
            question=question,
            schema_text=state.schema_text,
        )

    # --------------------------------------------------
    # 5. Execute selected tools
    # --------------------------------------------------

    for tool_name in state.selected_tools:
        state.iteration += 1

        # --------------------------------------------------
        # SQL execution gets controlled retry handling.
        # --------------------------------------------------

        if tool_name == "sql_query":

            for attempt in range(
                MAX_SQL_RETRIES + 1
            ):
                try:
                    state = execute_tool(
                        tool_name=tool_name,
                        state=state,
                    )

                    # SQL executed successfully.
                    break

                except Exception as error:

                    # Store the error in agent state.
                    state.error = str(error)

                    # No retries remaining.
                    if attempt >= MAX_SQL_RETRIES:
                        raise RuntimeError(
                            "SQL execution failed after "
                            f"{MAX_SQL_RETRIES} retries. "
                            f"Last error: {error}"
                        ) from error

                    # Ask the LLM to correct the failed SQL.
                    state.sql = correct_sql(
                        question=state.question,
                        schema_text=state.schema_text,
                        failed_sql=state.sql,
                        error_message=str(error),
                    )

        else:
            state = execute_tool(
                tool_name=tool_name,
                state=state,
            )

    # --------------------------------------------------
    # 6. Generate final natural-language answer
    # --------------------------------------------------

    if state.sql and state.columns:
        state.answer = generate_answer(
            question=state.question,
            sql=state.sql,
            columns=state.columns,
            rows=state.rows,
        )

    return state
