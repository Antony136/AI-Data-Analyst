"""
Main agent loop for AI Data Analyst.

Coordinates planning, SQL generation, tool execution,
retries, result handling, and final answer generation.
"""

from time import perf_counter

from app.agent.answer_generator import generate_answer
from app.agent.executor import execute_tool
from app.agent.planner import plan_tools
from app.agent.sql_generator import (
    MAX_SQL_RETRIES,
    correct_sql,
    generate_sql,
)
from app.agent.state import AgentState
from app.agent.trace import AgentTrace
from app.database.schema import format_schema_for_llm
from app.database.schema import get_schema
from app.guardrails.plan_validator import validate_plan


def run_agent(question: str) -> AgentState:
    state = AgentState(question=question)

    trace = AgentTrace(question=question)
    trace.start()
    state.trace = trace

    try:
        state.schema_text = format_schema_for_llm(get_schema())

        selected_tools = plan_tools(question)
        state.selected_tools = validate_plan(selected_tools)
        trace.selected_tools = state.selected_tools.copy()

        if "sql_query" in state.selected_tools:
            state.sql = generate_sql(
                question=question,
                schema_text=state.schema_text,
            )
            trace.sql = state.sql

        for tool_name in state.selected_tools:
            state.iteration += 1
            tool_start = perf_counter()

            try:
                execute_tool(
                    tool_name=tool_name,
                    state=state,
                )

                duration_ms = (
                    perf_counter() - tool_start
                ) * 1000

                if tool_name == "sql_query":
                    trace.sql = state.sql
                    trace.set_result(
                        columns=state.columns,
                        rows=state.rows,
                    )

                trace.add_tool_trace(
                    tool_name=tool_name,
                    success=True,
                    duration_ms=duration_ms,
                )

            except Exception as error:
                duration_ms = (
                    perf_counter() - tool_start
                ) * 1000

                trace.add_tool_trace(
                    tool_name=tool_name,
                    success=False,
                    duration_ms=duration_ms,
                    error=str(error),
                )

                trace.add_error(str(error))

                if tool_name != "sql_query":
                    raise

                last_error = error

                for retry_number in range(
                    1,
                    MAX_SQL_RETRIES + 1,
                ):
                    trace.sql_retries = retry_number
                    retry_start = perf_counter()

                    try:
                        state.sql = correct_sql(
                            question=question,
                            schema_text=state.schema_text,
                            failed_sql=state.sql,
                            error_message=str(last_error),
                        )

                        trace.sql = state.sql

                        execute_tool(
                            tool_name="sql_query",
                            state=state,
                        )

                        retry_duration_ms = (
                            perf_counter() - retry_start
                        ) * 1000

                        trace.set_result(
                            columns=state.columns,
                            rows=state.rows,
                        )

                        trace.add_tool_trace(
                            tool_name="sql_query_retry",
                            success=True,
                            duration_ms=retry_duration_ms,
                        )

                        break

                    except Exception as retry_error:
                        last_error = retry_error

                        retry_duration_ms = (
                            perf_counter() - retry_start
                        ) * 1000

                        trace.add_tool_trace(
                            tool_name="sql_query_retry",
                            success=False,
                            duration_ms=retry_duration_ms,
                            error=str(retry_error),
                        )

                        trace.add_error(
                            str(retry_error)
                        )

                        if retry_number == MAX_SQL_RETRIES:
                            raise

        if state.columns:
            state.answer = generate_answer(
                question=question,
                sql=state.sql,
                columns=state.columns,
                rows=state.rows,
            )
            trace.final_answer = state.answer

        return state

    except Exception as error:
        state.error = str(error)
        trace.add_error(str(error))
        raise

    finally:
        trace.finish()
