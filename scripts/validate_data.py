"""
Validate the synthetic e-commerce dataset for the AI Data Analyst.

Checks:
1. Row counts
2. Orders by year
3. Orders by quarter
4. Order status distribution
5. Customer segments
6. Customers by region
7. Products by category
8. Revenue by year
9. Revenue by quarter
10. Q3 2025 revenue by region
11. Q2 vs Q3 2025 order volume
12. Q2 vs Q3 2025 order status
13. Payment status distribution
"""

import os

import psycopg
from dotenv import load_dotenv


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    load_dotenv()

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ai_data_analyst"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


# ============================================================
# DISPLAY HELPERS
# ============================================================

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_rows(cursor):
    columns = [desc.name for desc in cursor.description]

    print(" | ".join(columns))
    print("-" * 70)

    for row in cursor.fetchall():
        print(" | ".join(str(value) for value in row))


def run_query(cursor, title, query):
    print_section(title)

    cursor.execute(query)
    print_rows(cursor)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("AI DATA ANALYST")
    print("Synthetic Data Validation")
    print("=" * 70)

    print("\nConnecting to PostgreSQL...")

    connection = get_connection()

    try:

        with connection.cursor() as cursor:

            # ------------------------------------------------
            # 1. ROW COUNTS
            # ------------------------------------------------

            run_query(
                cursor,
                "1. TABLE ROW COUNTS",
                """
                SELECT 'customers' AS table_name, COUNT(*) AS row_count
                FROM customers

                UNION ALL

                SELECT 'products', COUNT(*)
                FROM products

                UNION ALL

                SELECT 'orders', COUNT(*)
                FROM orders

                UNION ALL

                SELECT 'order_items', COUNT(*)
                FROM order_items

                UNION ALL

                SELECT 'payments', COUNT(*)
                FROM payments;
                """,
            )

            # ------------------------------------------------
            # 2. ORDERS BY YEAR
            # ------------------------------------------------

            run_query(
                cursor,
                "2. ORDERS BY YEAR",
                """
                SELECT
                    EXTRACT(YEAR FROM order_date)::INT AS year,
                    COUNT(*) AS orders
                FROM orders
                GROUP BY year
                ORDER BY year;
                """,
            )

            # ------------------------------------------------
            # 3. ORDERS BY QUARTER
            # ------------------------------------------------

            run_query(
                cursor,
                "3. ORDERS BY QUARTER",
                """
                SELECT
                    EXTRACT(YEAR FROM order_date)::INT AS year,
                    EXTRACT(QUARTER FROM order_date)::INT AS quarter,
                    COUNT(*) AS orders
                FROM orders
                GROUP BY year, quarter
                ORDER BY year, quarter;
                """,
            )

            # ------------------------------------------------
            # 4. ORDER STATUS
            # ------------------------------------------------

            run_query(
                cursor,
                "4. ORDER STATUS DISTRIBUTION",
                """
                SELECT
                    order_status,
                    COUNT(*) AS orders,
                    ROUND(
                        COUNT(*) * 100.0
                        / SUM(COUNT(*)) OVER (),
                        2
                    ) AS percentage
                FROM orders
                GROUP BY order_status
                ORDER BY orders DESC;
                """,
            )

            # ------------------------------------------------
            # 5. CUSTOMER SEGMENTS
            # ------------------------------------------------

            run_query(
                cursor,
                "5. CUSTOMER SEGMENTS",
                """
                SELECT
                    customer_segment,
                    COUNT(*) AS customers,
                    ROUND(
                        COUNT(*) * 100.0
                        / SUM(COUNT(*)) OVER (),
                        2
                    ) AS percentage
                FROM customers
                GROUP BY customer_segment
                ORDER BY customers DESC;
                """,
            )

            # ------------------------------------------------
            # 6. CUSTOMERS BY REGION
            # ------------------------------------------------

            run_query(
                cursor,
                "6. CUSTOMERS BY REGION",
                """
                SELECT
                    region,
                    COUNT(*) AS customers
                FROM customers
                GROUP BY region
                ORDER BY customers DESC;
                """,
            )

            # ------------------------------------------------
            # 7. PRODUCTS BY CATEGORY
            # ------------------------------------------------

            run_query(
                cursor,
                "7. PRODUCTS BY CATEGORY",
                """
                SELECT
                    category,
                    COUNT(*) AS products
                FROM products
                GROUP BY category
                ORDER BY products DESC;
                """,
            )

            # ------------------------------------------------
            # 8. REVENUE BY YEAR
            # ------------------------------------------------

            run_query(
                cursor,
                "8. REVENUE BY YEAR",
                """
                SELECT
                    EXTRACT(YEAR FROM o.order_date)::INT AS year,
                    ROUND(
                        SUM(
                            oi.quantity
                            * oi.unit_price
                            * (
                                1
                                - oi.discount_percent / 100
                            )
                        ),
                        2
                    ) AS revenue
                FROM orders o
                JOIN order_items oi
                    ON o.order_id = oi.order_id
                WHERE o.order_status IN (
                    'Completed',
                    'Shipped',
                    'Processing'
                )
                GROUP BY year
                ORDER BY year;
                """,
            )

            # ------------------------------------------------
            # 9. REVENUE BY QUARTER
            # ------------------------------------------------

            run_query(
                cursor,
                "9. REVENUE BY QUARTER",
                """
                SELECT
                    EXTRACT(YEAR FROM o.order_date)::INT
                        AS year,

                    EXTRACT(QUARTER FROM o.order_date)::INT
                        AS quarter,

                    ROUND(
                        SUM(
                            oi.quantity
                            * oi.unit_price
                            * (
                                1
                                - oi.discount_percent / 100
                            )
                        ),
                        2
                    ) AS revenue

                FROM orders o

                JOIN order_items oi
                    ON o.order_id = oi.order_id

                WHERE o.order_status IN (
                    'Completed',
                    'Shipped',
                    'Processing'
                )

                GROUP BY year, quarter
                ORDER BY year, quarter;
                """,
            )

            # ------------------------------------------------
            # 10. Q3 2025 REVENUE BY REGION
            # ------------------------------------------------

            run_query(
                cursor,
                "10. Q3 2025 REVENUE BY REGION",
                """
                SELECT
                    o.shipping_region AS region,

                    ROUND(
                        SUM(
                            oi.quantity
                            * oi.unit_price
                            * (
                                1
                                - oi.discount_percent / 100
                            )
                        ),
                        2
                    ) AS revenue

                FROM orders o

                JOIN order_items oi
                    ON o.order_id = oi.order_id

                WHERE o.order_status IN (
                    'Completed',
                    'Shipped',
                    'Processing'
                )

                AND o.order_date >= DATE '2025-07-01'
                AND o.order_date < DATE '2025-10-01'

                GROUP BY o.shipping_region
                ORDER BY revenue DESC;
                """,
            )

            # ------------------------------------------------
            # 11. Q2 VS Q3 ORDER VOLUME
            # ------------------------------------------------

            run_query(
                cursor,
                "11. Q2 VS Q3 2025 ORDER VOLUME",
                """
                SELECT
                    CASE
                        WHEN order_date >= DATE '2025-04-01'
                         AND order_date < DATE '2025-07-01'
                            THEN 'Q2 2025'

                        WHEN order_date >= DATE '2025-07-01'
                         AND order_date < DATE '2025-10-01'
                            THEN 'Q3 2025'
                    END AS quarter,

                    COUNT(*) AS orders

                FROM orders

                WHERE order_date >= DATE '2025-04-01'
                  AND order_date < DATE '2025-10-01'

                GROUP BY quarter
                ORDER BY quarter;
                """,
            )

            # ------------------------------------------------
            # 12. Q2 VS Q3 STATUS DISTRIBUTION
            # ------------------------------------------------

            run_query(
                cursor,
                "12. Q2 VS Q3 2025 ORDER STATUS",
                """
                SELECT
                    CASE
                        WHEN order_date >= DATE '2025-04-01'
                         AND order_date < DATE '2025-07-01'
                            THEN 'Q2 2025'

                        ELSE 'Q3 2025'
                    END AS quarter,

                    order_status,

                    COUNT(*) AS orders

                FROM orders

                WHERE order_date >= DATE '2025-04-01'
                  AND order_date < DATE '2025-10-01'

                GROUP BY quarter, order_status
                ORDER BY quarter, orders DESC;
                """,
            )

            # ------------------------------------------------
            # 13. PAYMENT STATUS
            # ------------------------------------------------

            run_query(
                cursor,
                "13. PAYMENT STATUS DISTRIBUTION",
                """
                SELECT
                    payment_status,
                    COUNT(*) AS payments,

                    ROUND(
                        COUNT(*) * 100.0
                        / SUM(COUNT(*)) OVER (),
                        2
                    ) AS percentage

                FROM payments

                GROUP BY payment_status
                ORDER BY payments DESC;
                """,
            )

            # ------------------------------------------------
            # 14. ORDER / PAYMENT CONSISTENCY
            # ------------------------------------------------

            run_query(
                cursor,
                "14. ORDER STATUS VS PAYMENT STATUS",
                """
                SELECT
                    o.order_status,
                    p.payment_status,
                    COUNT(*) AS count

                FROM orders o

                JOIN payments p
                    ON o.order_id = p.order_id

                GROUP BY
                    o.order_status,
                    p.payment_status

                ORDER BY
                    o.order_status,
                    count DESC;
                """,
            )

            # ------------------------------------------------
            # 15. FOREIGN KEY INTEGRITY
            # ------------------------------------------------

            run_query(
                cursor,
                "15. ORPHAN ORDER ITEMS",
                """
                SELECT COUNT(*) AS orphan_order_items
                FROM order_items oi
                LEFT JOIN orders o
                    ON oi.order_id = o.order_id
                WHERE o.order_id IS NULL;
                """,
            )

            run_query(
                cursor,
                "16. ORPHAN PAYMENTS",
                """
                SELECT COUNT(*) AS orphan_payments
                FROM payments p
                LEFT JOIN orders o
                    ON p.order_id = o.order_id
                WHERE o.order_id IS NULL;
                """,
            )

            run_query(
                cursor,
                "17. ORPHAN PRODUCTS",
                """
                SELECT COUNT(*) AS orphan_product_references
                FROM order_items oi
                LEFT JOIN products p
                    ON oi.product_id = p.product_id
                WHERE p.product_id IS NULL;
                """,
            )

    finally:

        connection.close()

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
