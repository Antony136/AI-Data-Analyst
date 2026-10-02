"""
State definition for the AI Data Analyst agent.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """
    Stores information produced while the agent
    processes an analytics request.
    """

    question: str

    schema_text: str = ""

    selected_tools: list[str] = field(
        default_factory=list
    )

    sql: str = ""

    columns: list[str] = field(
        default_factory=list
    )

    rows: list[Any] = field(
        default_factory=list
    )

    analysis: dict[str, Any] = field(
        default_factory=dict
    )

    chart_path: str = ""

    answer: str = ""

    error: str = ""
