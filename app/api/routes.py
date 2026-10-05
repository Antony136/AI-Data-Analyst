"""
FastAPI routes for AI Data Analyst.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse
from app.agent.loop import run_agent


router = APIRouter()


VISUALIZATION_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "visualizations"
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(
    request: AnalyzeRequest,
) -> AnalyzeResponse:

    try:
        state = run_agent(request.question)

        chart_url = None

        # --------------------------------------------------
        # Detect a generated visualization.
        #
        # The current visualization tool writes charts
        # into data/visualizations. The standard agent chart
        # is agent_chart.png.
        # --------------------------------------------------

        if "create_bar_chart" in state.selected_tools:
            chart_file = (
                VISUALIZATION_DIRECTORY
                / "agent_chart.png"
            )

            if chart_file.exists():
                chart_url = "/visualizations/agent_chart.png"

        elif "create_line_chart" in state.selected_tools:
            chart_file = (
                VISUALIZATION_DIRECTORY
                / "agent_chart.png"
            )

            if chart_file.exists():
                chart_url = "/visualizations/agent_chart.png"

        elif "create_pie_chart" in state.selected_tools:
            chart_file = (
                VISUALIZATION_DIRECTORY
                / "agent_chart.png"
            )

            if chart_file.exists():
                chart_url = "/visualizations/agent_chart.png"

        return AnalyzeResponse(
            question=state.question,
            answer=state.answer,
            sql=state.sql,
            columns=state.columns,
            rows=state.rows,
            tools_used=state.selected_tools,
            chart_url=chart_url,
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
