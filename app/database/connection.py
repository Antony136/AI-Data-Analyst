"""
PostgreSQL connection management for AI Data Analyst.
"""

import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """
    Create a PostgreSQL connection using the credentials
    configured for the AI Data Analyst application.
    """

    host = os.getenv(
        "DB_HOST",
        "localhost",
    )

    port = os.getenv(
        "DB_PORT",
        "5432",
    )

    database = os.getenv(
        "DB_NAME",
        "ai_data_analyst",
    )

    user = os.getenv(
        "DB_USER",
        "ai_analyst_readonly",
    )

    password = os.getenv(
        "DB_PASSWORD",
    )

    if not password:
        raise RuntimeError(
            "DB_PASSWORD is missing from .env"
        )

    return psycopg.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
    )
