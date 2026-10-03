"""
Prompt templates for AI Data Analyst.
"""


def build_sql_prompt(
    question: str,
    schema_text: str,
) -> str:

    return f"""
You are an expert PostgreSQL data analyst.

Your job is to generate ONE PostgreSQL SELECT query that
directly answers the user's question.

DATABASE SCHEMA
---------------
{schema_text}

USER QUESTION
-------------
{question}

============================================================
STEP 1 — IDENTIFY THE EXACT REQUESTED METRIC
============================================================

Before writing SQL, determine what the user is asking for.

IMPORTANT:

The word "revenue" means TOTAL REVENUE unless the user
explicitly asks for another metric.

Revenue is calculated as:

    quantity * unit_price * (1 - discount_percent / 100)

Valid sales orders are ONLY:

    Completed
    Shipped
    Processing

------------------------------------------------------------
REVENUE
------------------------------------------------------------

If the user asks:

- total revenue
- revenue in 2025
- revenue in 2024
- revenue by category
- revenue by region
- revenue by customer segment
- quarterly revenue
- revenue for Q3
- revenue contribution

then calculate REVENUE.

For revenue, use:

    SUM(
        order_items.quantity
        * order_items.unit_price
        * (1 - order_items.discount_percent / 100)
    )

Do NOT use AVG for ordinary revenue questions.

Do NOT calculate Average Order Value for an ordinary
revenue question.

------------------------------------------------------------
AVERAGE ORDER VALUE
------------------------------------------------------------

Use AVERAGE ORDER VALUE only when the user explicitly asks
for:

- average order value
- AOV
- average value per order
- average revenue per order

AOV means:

    total valid revenue / number of valid orders

AOV MUST be calculated at the ORDER level.

Correct structure:

    SELECT AVG(order_revenue)
    FROM (
        SELECT
            orders.order_id,
            SUM(
                order_items.quantity
                * order_items.unit_price
                * (1 - order_items.discount_percent / 100)
            ) AS order_revenue
        FROM orders
        JOIN order_items
            ON orders.order_id = order_items.order_id
        WHERE ...
        GROUP BY orders.order_id
    ) AS order_totals

The inner query MUST GROUP BY the unique order identifier
before AVG is applied.

Never calculate:

    AVG(order_items.quantity * ...)

for AOV.

Never calculate:

    AVG(SUM(...))

without first grouping by order.

------------------------------------------------------------
ORDER COUNT
------------------------------------------------------------

If the user asks how many orders were placed:

    COUNT(DISTINCT orders.order_id)

Use DISTINCT when joins could otherwise duplicate orders.

------------------------------------------------------------
PERCENTAGE / SHARE
------------------------------------------------------------

If the user asks for:

- percentage of revenue
- revenue percentage
- revenue share
- contribution to revenue

SQL should normally return the underlying aggregated
revenue values.

For example:

    category
    revenue

The Python analysis layer can calculate the percentage.

Do NOT use window functions unless they are genuinely
required by the user's requested result.

------------------------------------------------------------
GROUPED REVENUE
------------------------------------------------------------

If the user asks for revenue grouped by a dimension:

Revenue by category:

    products.category,
    SUM(...) AS revenue

Revenue by region:

    orders.shipping_region,
    SUM(...) AS revenue

Revenue by customer segment:

    customers.customer_segment,
    SUM(...) AS revenue

Quarterly revenue:

    quarter,
    SUM(...) AS revenue

When the user asks for revenue, use the output alias:

    revenue

Do NOT rename it to:

    aov
    average_order_value
    quarter_revenue
    total_revenue

unless that specific name is necessary for a nested query
or explicitly requested.

------------------------------------------------------------
TIME FILTERS
------------------------------------------------------------

For year filtering, prefer:

    EXTRACT(YEAR FROM orders.order_date) = 2025

For quarter filtering, use the appropriate date range or
quarter extraction.

For quarterly revenue, the result should contain:

    quarter
    revenue

If using DATE_TRUNC:

    DATE_TRUNC('quarter', orders.order_date) AS quarter

and:

    SUM(...) AS revenue

------------------------------------------------------------
JOIN RULES
------------------------------------------------------------

Only JOIN tables that are actually required.

For revenue:

    order_items
        JOIN orders

because order status and order date belong to orders.

Join products ONLY when product information such as:

    category
    product_name
    subcategory

is required.

Join customers ONLY when customer information such as:

    customer_segment
    region/customer information

is required.

Join payments ONLY when the question explicitly requires
payment information or payment filtering.

Do NOT JOIN a table merely because it exists.

Be careful with one-to-many relationships.

Never introduce a JOIN that changes the intended aggregate.

------------------------------------------------------------
AGGREGATION RULES
------------------------------------------------------------

For ordinary revenue:

    SUM(order_items.quantity * ...)

For grouped revenue:

    GROUP BY the requested dimension.

For AOV:

    GROUP BY orders.order_id

inside the inner query before applying AVG outside it.

Do NOT use window functions unless the user's requested
result genuinely requires one.

Do NOT nest aggregate functions incorrectly.

For example, this is invalid:

    SUM(SUM(...))

unless used correctly as a window expression.

Do not generate aggregate/window combinations that
PostgreSQL will reject.

------------------------------------------------------------
SQL OUTPUT CONTRACT
------------------------------------------------------------

Use simple, predictable column aliases.

For revenue:

    AS revenue

For AOV:

    AS average_order_value

For category:

    category

For region:

    shipping_region

For customer segment:

    customer_segment

For quarterly revenue:

    quarter
    revenue

Do not unnecessarily rename source dimensions.

------------------------------------------------------------
GENERAL SQL RULES
------------------------------------------------------------

1. Return ONLY executable PostgreSQL SQL.
2. Do NOT use Markdown code fences.
3. Use ONLY tables and columns present in the schema.
4. Preserve the exact intent of the user's question.
5. Use valid PostgreSQL syntax.
6. Use unique table aliases.
7. Once a table has an alias, consistently use that alias.
8. Never reference an undefined alias.
9. Never use the same alias for different tables.
10. Do not invent tables or columns.
11. Do not use INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, CREATE, GRANT, or REVOKE.
12. Do not modify database data or structure.
13. Do not assume a currency.
14. Do not add currency symbols.
15. Do not add unnecessary JOINs.
16. Do not add unnecessary subqueries.
17. Do not add unnecessary window functions.
18. Do not solve a different metric than the user requested.
19. Do not turn a revenue question into an AOV question.
20. Do not turn an AOV question into ordinary row-level AVG.

============================================================
FINAL VERIFICATION
============================================================

Before returning SQL, mentally verify:

1. What exact metric did the user request?
2. Is this revenue, AOV, order count, percentage,
   or another metric?
3. If the question says revenue, did I use SUM rather than AVG?
4. If the question says AOV, did I GROUP BY order_id first?
5. Are all required tables present?
6. Are all JOINs necessary?
7. Are all aliases defined exactly once?
8. Are all aliases referenced consistently?
9. Are aggregate functions valid PostgreSQL?
10. Does the result column naming match the requested metric?
11. Does the query answer the user's exact question?

The user's question has priority over all examples and
business-rule explanations above.

Return ONLY the SQL.

SQL:
""".strip()


def build_answer_prompt(
    question: str,
    sql: str,
    columns: list[str],
    rows: str,
) -> str:

    return f"""
You are the final answer component of an AI data analyst.

Answer the user's question using ONLY the
AUTHORITATIVE DATABASE RESULT below.

USER QUESTION
-------------
{question}

EXECUTED SQL
------------
{sql}

RESULT COLUMNS
--------------
{columns}

AUTHORITATIVE DATABASE RESULT
-----------------------------
{rows}

STRICT RULES
------------

1. The database result is the source of truth.
2. Do not invent numbers.
3. Do not estimate or guess.
4. Do not change numeric values.
5. Do not add or remove digits.
6. Do not assume a currency.
7. Do not add currency symbols.
8. Do not convert units.
9. Do not calculate new metrics unless they are already
   present in the database result.
10. Clearly associate every value with its corresponding
    category or dimension.
11. Answer concisely.
12. Do not mention SQL, prompts, models, or internal systems.

IMPORTANT
---------

The database result was generated directly from PostgreSQL.

Do not modify its numeric values.

FINAL ANSWER:
""".strip()


def build_sql_correction_prompt(
    question: str,
    schema_text: str,
    failed_sql: str,
    error_message: str,
) -> str:

    return f"""
You are an expert PostgreSQL data analyst correcting a
failed SQL query.

Your task is to make the SMALLEST correction necessary
to produce valid SQL that answers the user's ORIGINAL
question.

DATABASE SCHEMA
---------------
{schema_text}

USER QUESTION
-------------
{question}

FAILED SQL
----------
{failed_sql}

DATABASE ERROR
--------------
{error_message}

BUSINESS RULES
--------------

Revenue:

    quantity * unit_price * (1 - discount_percent / 100)

Valid revenue orders:

    Completed
    Shipped
    Processing

IMPORTANT METRIC RULE
---------------------

The user's question determines the metric.

If the question asks for ordinary revenue:

    use SUM(...)

Do NOT change ordinary revenue into AOV.

AOV is ONLY for questions explicitly asking for:

    average order value
    AOV
    average value per order
    average revenue per order

For AOV, calculate revenue per order first:

    GROUP BY orders.order_id

then:

    AVG(order_revenue)

Do not introduce AOV logic into a normal revenue query.

CORRECTION RULES
----------------

1. Return ONLY corrected PostgreSQL SQL.
2. Do NOT use Markdown code fences.
3. Preserve the user's original intent.
4. Fix the reported database error.
5. Do not redesign a correct query unnecessarily.
6. Do not introduce unnecessary JOINs.
7. Do not introduce unnecessary subqueries.
8. Do not introduce unnecessary window functions.
9. Do not change the requested metric.
10. Every alias must be defined exactly once.
11. Every referenced alias must exist.
12. Every table must exist in the schema.
13. Do not invent columns.
14. Do not invent functions.
15. Do not use INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, CREATE, GRANT, or REVOKE.
16. Do not assume a currency.
17. Do not add currency symbols.

FINAL CHECK
-----------

Before returning SQL verify:

- The query still answers the ORIGINAL question.
- Revenue questions use SUM.
- AOV questions use per-order GROUP BY before AVG.
- All aliases are valid.
- All JOINs are valid.
- All aggregate expressions are valid PostgreSQL.
- No unnecessary window functions were introduced.

Return ONLY executable PostgreSQL SQL.

CORRECTED SQL:
""".strip()


def build_answer_correction_prompt(
    question: str,
    sql: str,
    columns: list[str],
    rows: list,
    failed_answer: str,
    error_message: str,
) -> str:

    return f"""
You are correcting a database-backed analytics answer.

The previous answer was rejected because it did not
correctly match the database result.

USER QUESTION
-------------
{question}

DATABASE RESULT COLUMNS
-----------------------
{columns}

DATABASE RESULT ROWS
--------------------
{rows}

PREVIOUS ANSWER
---------------
{failed_answer}

VALIDATION ERROR
----------------
{error_message}

STRICT RULES
------------

1. DATABASE RESULT ROWS are the only source of numeric facts.
2. Do not invent numbers.
3. Do not estimate numbers.
4. Do not infer missing numbers.
5. Do not calculate new metrics.
6. Copy numeric values from the database result.
7. Do not assume a currency.
8. Do not add currency symbols.
9. Do not convert units.
10. Clearly associate values with their corresponding
    category or dimension.
11. Answer the user's question directly.
12. Return only the corrected natural-language answer.

CORRECTED ANSWER:
""".strip()