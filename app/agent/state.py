"""
Agent state for AI Data Analyst.
"""

from dataclasses import dataclass, field
from typing import Any

from app.agent.trace import AgentTrace


@dataclass
class AgentState:
    question: str

    schema_text: str = ""

    selected_tools: list[str] = field(default_factory=list)

    sql: str = ""

    columns: list[str] = field(default_factory=list)

    rows: list[Any] = field(default_factory=list)

    analysis: dict[str, Any] = field(default_factory=dict)

    chart_path: str = ""

    answer: str = ""

    error: str = ""

    iteration: int = 0

    trace: AgentTrace | None = None
