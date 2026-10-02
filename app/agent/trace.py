"""
Execution tracing for AI Data Analyst.

Records observable agent execution details for debugging,
monitoring, and evaluation.

This trace intentionally does not store hidden chain-of-thought.
"""

from dataclasses import dataclass, field
from typing import Any
from time import perf_counter


@dataclass
class ToolTrace:
    """
    Records the execution of one registered tool.
    """

    tool_name: str
    success: bool = False
    duration_ms: float = 0.0
    error: str = ""


@dataclass
class AgentTrace:
    """
    Records the observable execution of one agent request.
    """

    question: str

    selected_tools: list[str] = field(
        default_factory=list
    )

    sql: str = ""

    sql_retries: int = 0

    result_rows: int = 0

    result_columns: int = 0

    tool_traces: list[ToolTrace] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    total_duration_ms: float = 0.0

    final_answer: str = ""

    _start_time: float = field(
        default=0.0,
        repr=False,
    )

    def start(self) -> None:
        """
        Start the execution timer.
        """

        self._start_time = perf_counter()

    def finish(self) -> None:
        """
        Stop the execution timer and store total duration.
        """

        if self._start_time == 0:
            return

        self.total_duration_ms = (
            perf_counter() - self._start_time
        ) * 1000

    def add_tool_trace(
        self,
        tool_name: str,
        success: bool,
        duration_ms: float,
        error: str = "",
    ) -> None:
        """
        Record one tool execution.
        """

        self.tool_traces.append(
            ToolTrace(
                tool_name=tool_name,
                success=success,
                duration_ms=duration_ms,
                error=error,
            )
        )

    def add_error(
        self,
        error: str,
    ) -> None:
        """
        Record an execution error.
        """

        self.errors.append(error)

    def set_result(
        self,
        columns: list[str],
        rows: list[Any],
    ) -> None:
        """
        Record database result metadata.
        """

        self.result_columns = len(columns)
        self.result_rows = len(rows)

    def to_dict(self) -> dict:
        """
        Convert the trace into a serializable dictionary.
        """

        return {
            "question": self.question,
            "selected_tools": self.selected_tools,
            "sql": self.sql,
            "sql_retries": self.sql_retries,
            "result_rows": self.result_rows,
            "result_columns": self.result_columns,
            "tool_traces": [
                {
                    "tool_name": trace.tool_name,
                    "success": trace.success,
                    "duration_ms": round(
                        trace.duration_ms,
                        2,
                    ),
                    "error": trace.error,
                }
                for trace in self.tool_traces
            ],
            "errors": self.errors,
            "total_duration_ms": round(
                self.total_duration_ms,
                2,
            ),
            "final_answer": self.final_answer,
        }
