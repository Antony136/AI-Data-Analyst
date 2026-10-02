from app.agent.answer_generator import generate_answer


def main():
    print("=" * 70)
    print("ANSWER GENERATOR TEST")
    print("=" * 70)

    question = "What was the revenue by product category in 2025?"

    sql = """
    SELECT
        p.category,
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100)
        ) AS total_revenue
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE
        o.order_date >= '2025-01-01'
        AND o.order_date < '2026-01-01'
        AND o.order_status IN (
            'Completed',
            'Shipped',
            'Processing'
        )
    GROUP BY p.category
    ORDER BY total_revenue DESC;
    """.strip()

    columns = [
        "category",
        "total_revenue",
    ]

    rows = [
        ("Electronics", 41067364.604),
        ("Fashion", 6363825.7335),
        ("Home", 18083529.0395),
        ("Office", 7111185.4035),
        ("Sports", 7644990.3655),
    ]

    answer = generate_answer(
        question=question,
        sql=sql,
        columns=columns,
        rows=rows,
    )

    print("\nFINAL ANSWER")
    print("-" * 70)
    print(answer)

    print("\n" + "=" * 70)
    print("ANSWER GENERATOR TEST PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
