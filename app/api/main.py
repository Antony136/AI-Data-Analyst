"""
FastAPI application entry point for AI Data Analyst.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="AI Data Analyst",
    description="Natural-language data analysis API.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():
    """
    Health check endpoint.
    """

    return {
        "name": "AI Data Analyst",
        "status": "running",
    }


@app.get("/health")
def health():
    """
    API health check.
    """

    return {
        "status": "healthy",
    }
