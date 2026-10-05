"""
FastAPI routes for AI Data Analyst.
"""

from fastapi import APIRouter, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.agent.loop import run_agent


router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a natural-language business question
    using the AI Data Analyst agent.
    """

    try:
        state = run_agent(request.question)

        return AnalyzeResponse(
            question=state.question,
            answer=state.answer,
            sql=state.sql,
            columns=state.columns,
            rows=state.rows,
            tools_used=state.selected_tools,
            trace=state.trace.to_dict(),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid analysis request",
                "message": str(exc),
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": str(exc),
            },
        ) from exc
