"""
Prompt templates for AI Data Analyst.
"""


def build_sql_prompt(
    question: str,
    schema_text: str,
) -> str:

    return f"""
You are an expert PostgreSQL data analyst.

Generate ONE PostgreSQL SELECT query that retrieves
the data required to answer the user's question.

DATABASE SCHEMA
---------------
{schema_text}

USER QUESTION
-------------
{question}

BUSINESS RULES
--------------

REVENUE
-------
Revenue is calculated from order_items using:

    quantity * unit_price * (1 - discount_percent / 100)

For revenue calculations, only orders with these
statuses are considered valid sales:

    Completed
    Shipped
    Processing

IMPORTANT:
These revenue-valid statuses apply ONLY when calculating
revenue or metrics derived from revenue.

Do NOT automatically apply these statuses to ordinary
order-count questions.

ORDER COUNTS
------------
If the user asks:

- "How many orders were placed?"
- "How many orders?"
- "order count"
- "number of orders"

count orders using:

    COUNT(DISTINCT orders.order_id)

Do NOT add an order_status filter unless the user
explicitly specifies a status.

If the user explicitly asks for "completed orders",
use exactly:

    orders.order_status = 'Completed'

If the user explicitly asks for cancelled orders, use:

    orders.order_status = 'Cancelled'

If the user explicitly asks for returned orders, use:

    orders.order_status = 'Returned'

If the user explicitly asks for shipped orders, use:

    orders.order_status = 'Shipped'

If the user explicitly asks for processing orders, use:

    orders.order_status = 'Processing'

PAYMENTS
--------
Payment questions must use the payments table.

If the user asks for "paid" payments or "paid payment
amount", use:

    payments.payment_status = 'Paid'

For payment amount questions, use:

    SUM(payments.amount)

When grouping payment amounts by payment method, return:

    payment_method
    payment_amount

CUSTOMER REGION VS SHIPPING REGION
----------------------------------
The orders table contains:

    orders.shipping_region

The customers table contains:

    customers.region

If the question refers to:

- shipping region
- order region
- a region of orders
- revenue from a named region such as South, North,
  East, West, or Central

use:

    orders.shipping_region

IMPORTANT DISTINCTION:

If the user asks:

    "revenue by region"

this is a GROUPING request.

Use:

    SELECT orders.shipping_region, SUM(...) AS revenue
    ...
    GROUP BY orders.shipping_region

If the user asks:

    "revenue from the South region"

or:

    "revenue in the South region"

this is a FILTERING request.

Use:

    WHERE orders.shipping_region = 'South'

Do NOT group by every region when the user requested
one specific region.

For a named-region filter, if the question is asking
for the value of that region, include the requested
region column in SELECT when a grouped/dimensional
result is expected.

For example:

    SELECT
        orders.shipping_region,
        SUM(...) AS revenue
    FROM ...
    WHERE orders.shipping_region = 'South'
    GROUP BY orders.shipping_region

If the question explicitly refers to customer region,
customer geography, or customer location, use:

    customers.region

AVERAGE ORDER VALUE
-------------------
Average Order Value (AOV) is NOT the average of
order-item rows.

AOV MUST be calculated as:

    average of total revenue for each individual order

This means:

1. Calculate revenue separately for every order.
2. Group revenue by orders.order_id.
3. Then calculate AVG() over those order-level revenues.

For AOV questions, use this SQL structure:

    SELECT AVG(order_revenue) AS average_order_value
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
    ) AS order_totals;

DO NOT use:

    AVG(
        order_items.quantity
        * order_items.unit_price
        * (1 - order_items.discount_percent / 100)
    )

That calculates the average order-item revenue,
NOT Average Order Value.

Use the alias:

    average_order_value

The valid revenue statuses must be applied inside
the order-level subquery.

EXPLICIT AOV QUESTIONS
----------------------
Use the AOV calculation above when the user asks:

- average order value
- AOV
- average value per order
- average revenue per order
- typical revenue per order
- typical order value
- typical revenue per order in a given period

Do NOT interpret an ordinary "revenue" question as AOV.

Examples:

"What was the revenue in 2025?"

means total revenue.

"What was the typical revenue per order in 2025?"

means Average Order Value.

TIME PERIODS
------------
For year questions, filter the relevant date column
to the requested year.

For quarterly questions, carefully distinguish between:

1. A specific quarter:
   "revenue in Q4 2025"
   "revenue during the fourth quarter of 2025"
   "revenue for Q4 2025"

2. A quarterly breakdown:
   "quarterly revenue for 2025"
   "show revenue by quarter in 2025"

SPECIFIC QUARTER
----------------
When the user asks for ONE specific quarter, filter
orders.order_date to the exact three-month period.

Use these exact PostgreSQL date ranges:

Q1:
    orders.order_date >= 'YYYY-01-01'
    AND orders.order_date < 'YYYY-04-01'

Q2:
    orders.order_date >= 'YYYY-04-01'
    AND orders.order_date < 'YYYY-07-01'

Q3:
    orders.order_date >= 'YYYY-07-01'
    AND orders.order_date < 'YYYY-10-01'

Q4:
    orders.order_date >= 'YYYY-10-01'
    AND orders.order_date < 'YYYY+1-01-01'

Examples:

"revenue in Q3 2025"

must use:

    orders.order_date >= '2025-07-01'
    AND orders.order_date < '2025-10-01'

"revenue in Q4 2025"

must use:

    orders.order_date >= '2025-10-01'
    AND orders.order_date < '2026-01-01'

IMPORTANT:
Never interpret a specific quarter request as
the entire year.

Do NOT use:

    BETWEEN '2025-01-01' AND '2025-12-31'

for a Q1, Q2, Q3, or Q4 question.

Do NOT use the wrong chronological boundary.

QUARTERLY BREAKDOWN
-------------------
If the user asks for revenue by quarter or quarterly
revenue for a year, group by quarter.

A valid approach is:

    DATE_TRUNC('quarter', orders.order_date)

or:

    EXTRACT(QUARTER FROM orders.order_date)

Return the requested quarter dimension and revenue.

If using DATE_TRUNC, the resulting timestamp is acceptable.

If using EXTRACT, quarter values 1-4 are acceptable.

For benchmark-friendly output, prefer:

    CONCAT(
        'Q',
        EXTRACT(QUARTER FROM orders.order_date)::int
    ) AS quarter

when a textual quarter label is useful.

MONTHLY BREAKDOWN
-----------------
If the user asks for monthly revenue for a year,
group by month and return:

    month
    revenue

A valid PostgreSQL approach is:

    DATE_TRUNC('month', orders.order_date) AS month

Do not confuse monthly grouping with a full-year aggregate.

TIME FILTER SAFETY
------------------
When a time period is explicitly requested:

- Preserve the exact requested year.
- Preserve the exact requested quarter.
- Preserve the exact requested month.
- Do not widen a specific period into a larger period.
- Do not reverse the start and end dates.
- Prefer half-open date ranges:

    >= start_date
    AND < next_period_start

over ambiguous inclusive end-date logic.

SQL RESPONSIBILITY
------------------
SQL is responsible for RETRIEVING the required data.

If the question requires a derived analysis such as:

- percentage contribution
- percentage share
- statistical analysis
- summary statistics

retrieve the values required for that analysis, but
do not unnecessarily calculate the derived analysis
inside SQL.

The Python analysis tools will perform those
calculations after the SQL result is converted into
a DataFrame.

For example, for:

"What percentage of revenue came from each category?"

prefer returning:

    category
    revenue

rather than calculating the percentage inside SQL.

The Python percentage-analysis tool will calculate:

    category revenue / total revenue * 100

However, SQL SHOULD perform database-level aggregation
when that aggregation is naturally part of retrieving
the required data.

JOIN RULES
----------
1. Only JOIN a table when data from that table is
   actually required to answer the user's question.

2. Do NOT JOIN a table merely because it exists in
   the database schema.

3. Before adding a JOIN, identify the specific column
   or filter that requires the table.

4. Avoid unnecessary one-to-many JOINs when calculating
   SUM(), COUNT(), AVG(), or other aggregates.

5. A JOIN must not unintentionally multiply rows.

6. For revenue calculations, order_items must be joined
   to orders when order-level filters such as order_status
   or order_date are required.

7. Products should be joined when product attributes such
   as category, product name, or subcategory are required.

8. Payments should be joined ONLY when payment-related
   information or payment-related filtering is explicitly
   required.

9. Customers should be joined ONLY when customer-related
   information or customer-related filtering is explicitly
   required.

10. If the question can be answered using fewer tables,
    prefer the query using fewer tables.

11. Never add a JOIN simply to make the query appear more
    complete.

12. When calculating aggregates, reason about the row
    cardinality introduced by every JOIN.

PAYMENT JOIN WARNING
--------------------
Do NOT join payments for ordinary revenue questions.

Revenue does NOT require:

    payments.payment_status = 'Paid'

unless the user explicitly asks about payments or
explicitly asks for revenue associated with paid
payments.

For example:

"What percentage of revenue came from each category?"

must calculate normal revenue using order_items and
orders.

It must NOT automatically join payments.

CATEGORY QUESTIONS
------------------
If the user asks for product category:

1. JOIN products using:

    order_items.product_id = products.product_id

2. Use:

    products.category

3. Use a single clear alias, for example:

    products AS p

4. If an alias is assigned, use that alias consistently.

For example:

    JOIN products AS p
        ON order_items.product_id = p.product_id

    SELECT
        p.category,
        SUM(...) AS revenue

Never reference an alias that was not declared.

Never use two different aliases for the same table.

ALIAS RULES
-----------
Use predictable aliases:

- total revenue       -> revenue
- order count         -> order_count
- average order value -> average_order_value
- payment amount      -> payment_amount

Do not invent semantically different aliases when one
of these standard aliases applies.

GENERAL SQL RULES
-----------------
1. Return EXACTLY ONE SQL statement.
2. Return ONLY the SQL query.
3. Do NOT use Markdown code fences.
4. Use PostgreSQL syntax.
5. Use ONLY tables and columns present in the schema.
6. Preserve the user's intended question.
7. Apply the business rules above.
8. Use appropriate JOIN conditions.
9. Use unique table aliases.
10. Do not reference a table name after assigning it
    an alias; use the alias consistently.
11. Do not invent tables, columns, functions, or fields.
12. Do not use INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, CREATE, GRANT, or REVOKE.
13. Do not modify database data or database structure.
14. Do not assume a currency.
15. Do not add currency symbols.
16. Do not add unnecessary tables or JOINs.
17. Do not calculate derived Python-analysis metrics
    when the raw/aggregated values are sufficient.
18. Do not return multiple SELECT statements.
19. Do not return multiple statements separated by
    semicolons.
20. A WITH clause containing CTEs is allowed, but all
    CTEs and the final SELECT must form ONE SQL statement.
21. Do not place explanatory text before or after SQL.
22. Do not include comments in the generated SQL.

SINGLE-STATEMENT EXAMPLES
-------------------------
VALID:

    WITH revenue AS (
        SELECT ...
    )
    SELECT ...
    FROM revenue

INVALID:

    SELECT ...;
    SELECT ...

INVALID:

    SELECT ...;
    DROP TABLE ...

INVALID:

    -- explanation
    SELECT ...

FINAL CHECK
-----------
Before returning the SQL, verify:

- The query answers the exact user question.
- Revenue is not confused with AOV.
- AOV is calculated from per-order totals.
- AOV does NOT use AVG() directly on order_items rows.
- Order count is not confused with revenue-valid sales.
- "Completed orders" means exactly Completed.
- "Paid payments" means exactly Paid.
- Shipping region is not confused with customer region.
- "by region" means GROUP BY region.
- "from South region" means FILTER to South.
- A requested filtered region is returned when the question
  expects the region dimension in the result.
- A specific quarter uses exactly the requested
  three-month period.
- Q4 2025 ends before 2026-01-01.
- A quarterly breakdown groups by quarter rather than
  returning one full-year total.
- Payment questions use payments.
- Ordinary revenue questions do NOT unnecessarily use
  payments.
- Every referenced table exists in the schema.
- Every JOIN is necessary.
- Every JOIN has a valid relationship.
- No JOIN unnecessarily multiplies rows.
- Aggregate calculations are not distorted.
- Every alias is unique.
- Every alias is used consistently.
- Only required columns are selected.
- Exactly ONE SQL statement is returned.
- There is no explanatory text around the SQL.

OUTPUT
------
Return only executable PostgreSQL SQL.
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
AUTHORITATIVE DATABASE RESULT provided below.

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
1. The AUTHORITATIVE DATABASE RESULT is the source of truth.
2. Do not invent any numbers.
3. Do not estimate or guess values.
4. Do not change the magnitude of any number.
5. Do not add or remove digits.
6. You may use the numbers exactly as shown.
7. You may add natural-language explanation.
8. Do not introduce a currency symbol.
9. Do not assume a currency.
10. Do not convert units.
11. Do not calculate new percentages, differences,
    totals, averages, or other metrics unless those
    values are already present in the result.
12. Do not mention SQL, prompts, models, or internal systems.
13. Answer concisely and directly.
14. Clearly associate each value with its corresponding
    category or dimension.

IMPORTANT
---------
The AUTHORITATIVE DATABASE RESULT was generated
directly from the database by the application.

Do not modify its numeric values.

FINAL ANSWER:
""".strip()


def build_sql_correction_prompt(
    question: str,
    schema_text: str,
    failed_sql: str,
    error_message: str,
) -> str:
    """
    Build a strict prompt asking the LLM to correct SQL
    that failed during PostgreSQL execution.
    """

    return f"""
You are an expert PostgreSQL data analyst.

A SQL query generated for the user's question failed
during PostgreSQL database execution.

Your task is to make the SMALLEST POSSIBLE CORRECTION
needed to fix the reported database error.

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
Revenue is calculated from order_items using:

    quantity * unit_price * (1 - discount_percent / 100)

For revenue calculations, only these order statuses
are valid sales:

    Completed
    Shipped
    Processing

These statuses apply ONLY to revenue calculations.

For ordinary order counts, do not add a status filter
unless the user explicitly requests one.

"Completed orders" means exactly:

    orders.order_status = 'Completed'

"Cancelled orders" means exactly:

    orders.order_status = 'Cancelled'

"Paid payments" means exactly:

    payments.payment_status = 'Paid'

AVERAGE ORDER VALUE
-------------------
AOV is the average of total revenue for each order.

For AOV, first calculate:

    SUM(
        order_items.quantity
        * order_items.unit_price
        * (1 - order_items.discount_percent / 100)
    )

GROUP BY:

    orders.order_id

Then calculate:

    AVG(order_revenue)

using an outer query.

Never calculate AOV by applying AVG() directly
to order_items revenue.

"Typical revenue per order" means AOV when the
question clearly asks for a typical per-order amount.

REGION RULES
------------
For order-region questions, use:

    orders.shipping_region

"revenue by region" means GROUP BY
orders.shipping_region.

"revenue from the South region" means:

    WHERE orders.shipping_region = 'South'

Do not replace a specific region filter with a
GROUP BY over every region.

TIME PERIOD RULES
-----------------
If the question specifies one quarter, preserve that
exact quarter.

Q1 = January through March
Q2 = April through June
Q3 = July through September
Q4 = October through December

For Q4 2025, the correct date range is:

    orders.order_date >= '2025-10-01'
    AND orders.order_date < '2026-01-01'

Never expand a specific quarter request into
the entire year.

Use these aliases when applicable:

    revenue
    order_count
    average_order_value
    payment_amount

CORRECTION RULES
----------------
1. Return EXACTLY ONE SQL statement.
2. Return ONLY the corrected SQL.
3. Do NOT use Markdown code fences.
4. Use PostgreSQL syntax.
5. Use ONLY tables and columns present in the schema.
6. Preserve the user's original question and intended result.
7. Preserve the existing query structure whenever possible.
8. Make the smallest possible change required to fix
   the reported database error.
9. Do NOT add tables or JOINs unless they are required
   to fix the specific error.
10. Do NOT remove tables or JOINs unless they are
    responsible for the specific error.
11. Do NOT change the calculation logic unless the
    database error requires it.
12. Do NOT change filters unless the database error
    requires it.
13. Do NOT change GROUP BY logic unless the database
    error requires it.
14. Every table alias MUST be unique.
15. Never assign the same alias to two different tables.
16. Before returning the SQL, verify every alias.
17. Do NOT introduce unnecessary tables.
18. Do NOT invent PostgreSQL functions.
19. Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER,
    TRUNCATE, CREATE, GRANT, or REVOKE.
20. Do NOT assume a currency.
21. Do NOT add currency symbols.
22. Do not return multiple SELECT statements.
23. Do not return multiple statements separated by
    semicolons.
24. Do not include explanatory text before or after SQL.
25. Do not include SQL comments.

IMPORTANT
---------
The DATABASE ERROR tells you what is wrong.

Fix THAT error.

Do not redesign the query.

Do not rewrite a correct query unnecessarily.

Return only executable PostgreSQL SQL.

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
    """
    Build a strict correction prompt for an answer
    that failed deterministic validation.
    """

    return f"""
You are correcting a database-backed analytics answer.

The previous answer was rejected because it contained
information that did not exactly match the database result.

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

CRITICAL NUMERIC RULE
---------------------
The DATABASE RESULT ROWS are the ONLY source of numeric facts.

You MUST NOT calculate, estimate, infer, approximate,
or invent any new numeric value.

You MUST copy numeric values from DATABASE RESULT ROWS.

The following numeric values are the ONLY numeric values
available for the answer:

{rows}

If a value is not present in DATABASE RESULT ROWS,
DO NOT mention it.

FORMATTING RULES
----------------
1. You may add thousands separators.
2. You may display decimal values rounded to two decimal places.
3. Do not change the magnitude of a number.
4. Do not introduce a currency symbol.
5. Do not assume a currency.
6. Do not convert units.
7. Do not calculate percentages or differences unless
   those values are already present in the result.
8. Do not add numbers from your own knowledge.
9. Do not mention unsupported information.
10. Answer the user's question directly.
11. Return only the corrected natural-language answer.

CORRECTED ANSWER:
""".strip()
