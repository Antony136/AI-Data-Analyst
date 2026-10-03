"""
Generate the golden evaluation dataset for AI Data Analyst.

The expected results are calculated directly from PostgreSQL using
trusted reference SQL. The AI agent's generated SQL is NOT used
to create the ground truth.

Output:
    evaluation/questions.json
"""

import json
from pathlib import Path

from app.database.connection import get_connection


OUTPUT_FILE = (
    Path(__file__).resolve().parent / "questions.json"
)


def run_query(query: str):
    """
    Execute trusted reference SQL and return columns + rows.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)

            columns = [
                description.name
                for description in cursor.description
            ]

            rows = cursor.fetchall()

            return columns, rows

    finally:
        connection.close()


def convert_value(value):
    """
    Convert PostgreSQL values into JSON-compatible values.
    """

    if hasattr(value, "isoformat"):
        return value.isoformat()

    if hasattr(value, "__float__"):
        return float(value)

    return value


def build_case(
    case_id: int,
    question: str,
    query: str,
):
    """
    Execute reference SQL and build one evaluation case.
    """

    columns, rows = run_query(query)

    return {
        "id": case_id,
        "question": question,
        "expected_columns": columns,
        "expected_rows": [
            [
                convert_value(value)
                for value in row
            ]
            for row in rows
        ],
    }


def main():

    print("=" * 70)
    print("GENERATING EVALUATION GROUND TRUTH")
    print("=" * 70)

    # --------------------------------------------------------
    # Revenue definition
    # --------------------------------------------------------
    #
    # Revenue =
    #
    # quantity
    # × unit_price
    # × (1 - discount_percent / 100)
    #
    # Only these order statuses count as revenue:
    #
    # Completed
    # Shipped
    # Processing
    #
    # --------------------------------------------------------

    revenue_expression = """
        oi.quantity
        * oi.unit_price
        * (1 - oi.discount_percent / 100.0)
    """

    revenue_join = f"""
        FROM orders o
        JOIN order_items oi
            ON oi.order_id = o.order_id
    """

    revenue_status_filter = """
        WHERE o.order_status IN (
            'Completed',
            'Shipped',
            'Processing'
        )
    """

    cases = []

    # --------------------------------------------------------
    # 1. Total revenue in 2025
    # --------------------------------------------------------

    cases.append(
        build_case(
            1,
            "What was the total revenue in 2025?",
            f"""
                SELECT
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                {revenue_status_filter}
                  AND o.order_date >= DATE '2025-01-01'
                  AND o.order_date < DATE '2026-01-01';
            """,
        )
    )

    # --------------------------------------------------------
    # 2. Total revenue in 2024
    # --------------------------------------------------------

    cases.append(
        build_case(
            2,
            "What was the total revenue in 2024?",
            f"""
                SELECT
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                {revenue_status_filter}
                  AND o.order_date >= DATE '2024-01-01'
                  AND o.order_date < DATE '2025-01-01';
            """,
        )
    )

    # --------------------------------------------------------
    # 3. Q3 2025 revenue
    # --------------------------------------------------------

    cases.append(
        build_case(
            3,
            "What was the revenue in Q3 2025?",
            f"""
                SELECT
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                {revenue_status_filter}
                  AND o.order_date >= DATE '2025-07-01'
                  AND o.order_date < DATE '2025-10-01';
            """,
        )
    )

    # --------------------------------------------------------
    # 4. Revenue by category
    # --------------------------------------------------------

    cases.append(
        build_case(
            4,
            "Show revenue by product category.",
            f"""
                SELECT
                    p.category,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                JOIN products p
                    ON p.product_id = oi.product_id
                {revenue_status_filter}
                GROUP BY p.category
                ORDER BY p.category;
            """,
        )
    )

    # --------------------------------------------------------
    # 5. Revenue by category in 2025
    # --------------------------------------------------------

    cases.append(
        build_case(
            5,
            "What was the revenue by category in 2025?",
            f"""
                SELECT
                    p.category,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                JOIN products p
                    ON p.product_id = oi.product_id
                {revenue_status_filter}
                  AND o.order_date >= DATE '2025-01-01'
                  AND o.order_date < DATE '2026-01-01'
                GROUP BY p.category
                ORDER BY p.category;
            """,
        )
    )

    # --------------------------------------------------------
    # 6. Revenue by region
    # --------------------------------------------------------

    cases.append(
        build_case(
            6,
            "What was the revenue by region?",
            f"""
                SELECT
                    o.shipping_region,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                {revenue_status_filter}
                GROUP BY o.shipping_region
                ORDER BY o.shipping_region;
            """,
        )
    )

    # --------------------------------------------------------
    # 7. Revenue by customer segment
    # --------------------------------------------------------

    cases.append(
        build_case(
            7,
            "What was the revenue by customer segment?",
            f"""
                SELECT
                    c.customer_segment,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                JOIN customers c
                    ON c.customer_id = o.customer_id
                {revenue_status_filter}
                GROUP BY c.customer_segment
                ORDER BY c.customer_segment;
            """,
        )
    )

    # --------------------------------------------------------
    # 8. Number of orders placed in 2025
    # --------------------------------------------------------

    cases.append(
        build_case(
            8,
            "How many orders were placed in 2025?",
            """
                SELECT
                    COUNT(*) AS order_count
                FROM orders
                WHERE order_date >= DATE '2025-01-01'
                  AND order_date < DATE '2026-01-01';
            """,
        )
    )

    # --------------------------------------------------------
    # 9. Revenue percentage by category
    # --------------------------------------------------------

    cases.append(
        build_case(
            9,
            "What percentage of revenue came from each category?",
            f"""
                WITH category_revenue AS (
                    SELECT
                        p.category,
                        SUM({revenue_expression}) AS revenue
                    {revenue_join}
                    JOIN products p
                        ON p.product_id = oi.product_id
                    {revenue_status_filter}
                    GROUP BY p.category
                )
                SELECT
                    category,
                    revenue,
                    ROUND(
                        revenue
                        / SUM(revenue) OVER ()
                        * 100,
                        2
                    ) AS percentage
                FROM category_revenue
                ORDER BY category;
            """,
        )
    )

    # --------------------------------------------------------
    # 10. Average order value in 2025
    # --------------------------------------------------------

    cases.append(
        build_case(
            10,
            "What was the average order value in 2025?",
            f"""
                WITH order_revenue AS (
                    SELECT
                        o.order_id,
                        SUM({revenue_expression}) AS revenue
                    {revenue_join}
                    {revenue_status_filter}
                      AND o.order_date >= DATE '2025-01-01'
                      AND o.order_date < DATE '2026-01-01'
                    GROUP BY o.order_id
                )
                SELECT
                    AVG(revenue) AS average_order_value
                FROM order_revenue;
            """,
        )
    )

    # --------------------------------------------------------
    # 11. Top 5 categories by 2025 revenue
    # --------------------------------------------------------

    cases.append(
        build_case(
            11,
            "Show the top 5 product categories by revenue in 2025.",
            f"""
                SELECT
                    p.category,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                JOIN products p
                    ON p.product_id = oi.product_id
                {revenue_status_filter}
                  AND o.order_date >= DATE '2025-01-01'
                  AND o.order_date < DATE '2026-01-01'
                GROUP BY p.category
                ORDER BY revenue DESC
                LIMIT 5;
            """,
        )
    )

    # --------------------------------------------------------
    # 12. Quarterly revenue in 2025
    # --------------------------------------------------------

    cases.append(
        build_case(
            12,
            "Show the quarterly revenue for 2025.",
            f"""
                SELECT
                    'Q' || EXTRACT(
                        QUARTER FROM o.order_date
                    )::int AS quarter,
                    SUM({revenue_expression}) AS revenue
                {revenue_join}
                {revenue_status_filter}
                  AND o.order_date >= DATE '2025-01-01'
                  AND o.order_date < DATE '2026-01-01'
                GROUP BY EXTRACT(
                    QUARTER FROM o.order_date
                )
                ORDER BY EXTRACT(
                    QUARTER FROM o.order_date
                );
            """,
        )
    )

    # --------------------------------------------------------
    # Write JSON
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            cases,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(
        f"\nGenerated {len(cases)} evaluation cases."
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print("\nEvaluation cases:")

    for case in cases:
        print(
            f"- {case['id']}: "
            f"{case['question']}"
        )

    print("\n" + "=" * 70)
    print("GROUND TRUTH GENERATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
