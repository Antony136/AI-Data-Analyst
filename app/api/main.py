"""
FastAPI application entry point for AI Data Analyst.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


# ------------------------------------------------------------
# Application
# ------------------------------------------------------------

app = FastAPI(
    title="AI Data Analyst",
    description="Natural-language data analysis API.",
    version="1.0.0",
)


# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Static visualization files
# ------------------------------------------------------------

VISUALIZATION_DIRECTORY = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "visualizations"
)

VISUALIZATION_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/visualizations",
    StaticFiles(directory=VISUALIZATION_DIRECTORY),
    name="visualizations",
)


# ------------------------------------------------------------
# API routes
# ------------------------------------------------------------

app.include_router(router)


# ------------------------------------------------------------
# Basic routes
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "AI Data Analyst",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
