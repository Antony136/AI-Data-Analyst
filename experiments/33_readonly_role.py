"""
Test PostgreSQL read-only permissions for AI Data Analyst.
"""

import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


READONLY_USER = "ai_analyst_readonly"
READONLY_PASSWORD = os.getenv(
    "AI_ANALYST_READONLY_PASSWORD"
)


def get_connection():
    """
    Connect to PostgreSQL using the dedicated
    read-only AI analyst role.
    """

    if not READONLY_PASSWORD:
        raise RuntimeError(
            "AI_ANALYST_READONLY_PASSWORD is missing "
            "from .env"
        )

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ai_data_analyst"),
        user=READONLY_USER,
        password=READONLY_PASSWORD,
    )


def test_select():
    """
    Verify that SELECT is allowed.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM orders"
            )

            result = cursor.fetchone()

            assert result[0] == 100000

            print(
                "PASS: SELECT permission works"
            )

    finally:
        connection.close()


def test_insert_blocked():
    """
    Verify that INSERT is blocked.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO customers (
                        first_name,
                        last_name,
                        email,
                        region,
                        customer_segment,
                        signup_date
                    )
                    VALUES (
                        'Test',
                        'User',
                        'readonly-test@example.com',
                        'Test',
                        'Test',
                        CURRENT_DATE
                    )
                    """
                )

                raise AssertionError(
                    "INSERT was unexpectedly allowed"
                )

            except psycopg.errors.InsufficientPrivilege:
                connection.rollback()

                print(
                    "PASS: INSERT permission blocked"
                )

    finally:
        connection.close()


def test_update_blocked():
    """
    Verify that UPDATE is blocked.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    UPDATE customers
                    SET first_name = 'Blocked'
                    WHERE customer_id = 1
                    """
                )

                raise AssertionError(
                    "UPDATE was unexpectedly allowed"
                )

            except psycopg.errors.InsufficientPrivilege:
                connection.rollback()

                print(
                    "PASS: UPDATE permission blocked"
                )

    finally:
        connection.close()


def test_delete_blocked():
    """
    Verify that DELETE is blocked.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    DELETE FROM customers
                    WHERE customer_id = 1
                    """
                )

                raise AssertionError(
                    "DELETE was unexpectedly allowed"
                )

            except psycopg.errors.InsufficientPrivilege:
                connection.rollback()

                print(
                    "PASS: DELETE permission blocked"
                )

    finally:
        connection.close()


def main():
    print("=" * 70)
    print("READ-ONLY DATABASE ROLE TEST")
    print("=" * 70)

    test_select()
    test_insert_blocked()
    test_update_blocked()
    test_delete_blocked()

    print("\n" + "=" * 70)
    print("READ-ONLY ROLE TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
