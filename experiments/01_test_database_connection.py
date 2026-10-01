from app.database.connection import get_connection


def main():
    print("Connecting to PostgreSQL...")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")

            version = cursor.fetchone()[0]

            print("\nConnected successfully!")
            print(f"PostgreSQL: {version}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
