"""
API request and response schemas for AI Data Analyst.
"""

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """
    Request body for the /analyze endpoint.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="Natural-language business question.",
    )


class AnalyzeResponse(BaseModel):
    """
    Response returned by the /analyze endpoint.
    """

    question: str
    answer: str

    sql: str | None = None

    columns: list[str] = []
    rows: list[list[Any]] = []

    tools_used: list[str] = []

    trace: dict[str, Any] = {}
