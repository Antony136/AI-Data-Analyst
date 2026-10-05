"""
API request and response schemas for AI Data Analyst.
"""

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Natural-language business question.",
    )


class AnalyzeResponse(BaseModel):
    question: str
    answer: str

    sql: str | None = None

    columns: list[str] = []
    rows: list[list[Any]] = []

    tools_used: list[str] = []

    chart_url: str | None = None

    trace: dict[str, Any] = {}
