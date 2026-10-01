"""
Generate a realistic synthetic e-commerce dataset for the AI Data Analyst.

The dataset is:
- Deterministic when using the same seed.
- Large enough for realistic analytical queries.
- Designed with controlled business patterns.
- Compatible with the existing PostgreSQL schema.

Tables generated:
    customers
    products
    orders
    order_items
    payments

Important business concepts represented:
- Customer segments
- Regional differences
- Product categories and margins
- Seasonal sales
- Revenue trends
- Q3 2025 revenue decline
- Order cancellations and returns
- Payment failures/refunds
- Discounts
- Customer purchasing behavior

Random seed:
    42
"""

import os
import random
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import psycopg
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

CUSTOMER_COUNT = 5_000
PRODUCT_COUNT = 500
ORDER_COUNT = 100_000

START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)


# ============================================================
# BUSINESS DIMENSIONS
# ============================================================

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]

CUSTOMER_SEGMENTS = [
    "Consumer",
    "Small Business",
    "Enterprise",
]


CATEGORIES = {
    "Electronics": [
        "Laptops",
        "Smartphones",
        "Accessories",
        "Audio",
    ],
    "Home": [
        "Furniture",
        "Kitchen",
        "Decor",
        "Appliances",
    ],
    "Fashion": [
        "Men",
        "Women",
        "Footwear",
        "Accessories",
    ],
    "Sports": [
        "Fitness",
        "Outdoor",
        "Cycling",
        "Team Sports",
    ],
    "Office": [
        "Stationery",
        "Furniture",
        "Printers",
        "Supplies",
    ],
}


PAYMENT_METHODS = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Cash on Delivery",
]


ORDER_STATUSES = [
    "Completed",
    "Shipped",
    "Processing",
    "Cancelled",
    "Returned",
]


FIRST_NAMES = [
    "Arun",
    "Rahul",
    "Priya",
    "Ananya",
    "Vikram",
    "Karthik",
    "Divya",
    "Sneha",
    "Aditya",
    "Meera",
    "Rohan",
    "Neha",
    "Akhil",
    "Ishita",
    "Varun",
    "Nisha",
    "Sanjay",
    "Kavya",
    "Harish",
    "Pooja",
]


LAST_NAMES = [
    "Kumar",
    "Sharma",
    "Patel",
    "Singh",
    "Reddy",
    "Iyer",
    "Nair",
    "Gupta",
    "Mehta",
    "Rao",
    "Das",
    "Joshi",
    "Verma",
    "Menon",
    "Pillai",
]


# ============================================================
# CATEGORY CONFIGURATION
# ============================================================

# Product price ranges.
PRICE_RANGES = {
    "Electronics": (50, 2500),
    "Home": (20, 1500),
    "Fashion": (10, 500),
    "Sports": (15, 800),
    "Office": (5, 700),
}


# Approximate gross-margin ranges.
# The generated cost price will be based on these values.
MARGIN_RANGES = {
    "Electronics": (0.18, 0.32),
    "Home": (0.22, 0.38),
    "Fashion": (0.35, 0.55),
    "Sports": (0.28, 0.45),
    "Office": (0.25, 0.42),
}


# Relative probability of a category being selected.
# Electronics generates substantial revenue.
CATEGORY_WEIGHTS = {
    "Electronics": 28,
    "Home": 20,
    "Fashion": 22,
    "Sports": 15,
    "Office": 15,
}


# ============================================================
# CUSTOMER BEHAVIOR
# ============================================================

# Customer distribution.
SEGMENT_WEIGHTS = {
    "Consumer": 75,
    "Small Business": 20,
    "Enterprise": 5,
}


# Enterprise customers place orders more frequently.
SEGMENT_ORDER_WEIGHTS = {
    "Consumer": 1.0,
    "Small Business": 2.0,
    "Enterprise": 4.0,
}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def money(value) -> Decimal:
    """
    Convert a numeric value into a PostgreSQL-friendly
    Decimal with exactly two decimal places.
    """
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def random_date(
    rng: random.Random,
    start: date,
    end: date,
) -> date:
    """
    Generate a random date between start and end.
    """
    days = (end - start).days

    return start + timedelta(
        days=rng.randint(0, days)
    )


def weighted_choice(
    rng: random.Random,
    values,
    weights,
):
    """
    Return one value according to the supplied weights.
    """
    return rng.choices(
        values,
        weights=weights,
        k=1,
    )[0]


def month_multiplier(
    order_date: date,
) -> float:
    """
    Introduce realistic seasonal purchasing patterns.

    December:
        Strong holiday demand.

    November:
        Strong promotional demand.

    January:
        Slightly weaker demand.

    Other months:
        Normal demand.
    """

    if order_date.month == 12:
        return 1.25

    if order_date.month == 11:
        return 1.15

    if order_date.month == 1:
        return 0.90

    return 1.00


def year_multiplier(
    order_date: date,
) -> float:
    """
    Introduce overall business growth from 2024 to 2025.
    """

    if order_date.year == 2025:
        return 1.12

    return 1.00


def q3_2025_multiplier(
    order_date: date,
) -> float:
    """
    Introduce a controlled Q3 2025 business slowdown.

    This creates a meaningful analytical problem for:

        "Why did revenue fall in Q3 2025?"

    The decline is not uniform across all dimensions.
    """

    if (
        order_date.year == 2025
        and order_date.month in (7, 8, 9)
    ):
        return 0.82

    return 1.00


def is_q3_2025(
    order_date: date,
) -> bool:
    """
    Check whether a date belongs to Q3 2025.
    """

    return (
        order_date.year == 2025
        and order_date.month in (7, 8, 9)
    )


def is_valid_revenue_status(
    order_status: str,
) -> bool:
    """
    Determine whether an order contributes to normal
    recognized sales revenue.

    Processing and Shipped orders are included because
    this synthetic business treats them as active sales.

    Cancelled and Returned orders are excluded.
    """

    return order_status in {
        "Completed",
        "Shipped",
        "Processing",
    }


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a PostgreSQL connection using .env values.
    """

    load_dotenv()

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
        "postgres",
    )

    password = os.getenv(
        "DB_PASSWORD",
    )

    if not password:
        raise RuntimeError(
            "DB_PASSWORD is missing from .env. "
            "Add your PostgreSQL password before running this script."
        )

    return psycopg.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password,
    )


# ============================================================
# CUSTOMERS
# ============================================================

def generate_customers(
    rng: random.Random,
):
    """
    Generate customer records.

    Enterprise customers are intentionally rarer.
    """

    rows = []

    for customer_id in range(
        1,
        CUSTOMER_COUNT + 1,
    ):
        first_name = rng.choice(
            FIRST_NAMES
        )

        last_name = rng.choice(
            LAST_NAMES
        )

        email = (
            f"customer"
            f"{customer_id}"
            f"@example.com"
        )

        region = weighted_choice(
            rng,
            REGIONS,
            [22, 25, 18, 20, 15],
        )

        customer_segment = weighted_choice(
            rng,
            CUSTOMER_SEGMENTS,
            [
                SEGMENT_WEIGHTS["Consumer"],
                SEGMENT_WEIGHTS["Small Business"],
                SEGMENT_WEIGHTS["Enterprise"],
            ],
        )

        signup_date = random_date(
            rng,
            date(2023, 1, 1),
            date(2025, 6, 30),
        )

        rows.append(
            (
                first_name,
                last_name,
                email,
                region,
                customer_segment,
                signup_date,
            )
        )

    return rows


# ============================================================
# PRODUCTS
# ============================================================

def random_product_price(
    rng: random.Random,
    category: str,
) -> float:
    """
    Generate a product price according to category.
    """

    low, high = PRICE_RANGES[category]

    return round(
        rng.uniform(
            low,
            high,
        ),
        2,
    )


def generate_products(
    rng: random.Random,
):
    """
    Generate product records.

    Products have category-specific prices and margins.
    """

    rows = []

    category_names = list(
        CATEGORIES.keys()
    )

    category_weights = [
        CATEGORY_WEIGHTS[category]
        for category in category_names
    ]

    for product_id in range(
        1,
        PRODUCT_COUNT + 1,
    ):
        category = weighted_choice(
            rng,
            category_names,
            category_weights,
        )

        subcategory = rng.choice(
            CATEGORIES[category]
        )

        price = random_product_price(
            rng,
            category,
        )

        min_margin, max_margin = (
            MARGIN_RANGES[category]
        )

        margin = rng.uniform(
            min_margin,
            max_margin,
        )

        cost = price * (
            1 - margin
        )

        product_name = (
            f"{subcategory} "
            f"Product {product_id}"
        )

        rows.append(
            (
                product_name,
                category,
                subcategory,
                money(price),
                money(cost),
            )
        )

    return rows


# ============================================================
# ORDERS
# ============================================================

def build_customer_profiles(
    customers,
):
    """
    Build a quick customer lookup dictionary.
    """

    profiles = {}

    for customer_id, customer in enumerate(
        customers,
        start=1,
    ):
        profiles[customer_id] = {
            "region": customer[3],
            "segment": customer[4],
        }

    return profiles


def choose_customer(
    rng: random.Random,
    customer_profiles,
):
    """
    Select a customer using segment-based purchasing behavior.

    Enterprise customers have a higher probability of placing
    orders than ordinary consumers.
    """

    customer_ids = list(
        customer_profiles.keys()
    )

    weights = [
        SEGMENT_ORDER_WEIGHTS[
            customer_profiles[customer_id][
                "segment"
            ]
        ]
        for customer_id in customer_ids
    ]

    return rng.choices(
        customer_ids,
        weights=weights,
        k=1,
    )[0]


def choose_order_status(
    rng: random.Random,
    order_date: date,
    region: str,
):
    """
    Generate an order status.

    Q3 2025 has a slightly elevated cancellation/return rate.
    """

    if is_q3_2025(order_date):

        # South is intentionally affected more strongly.
        if region == "South":
            values = [
                "Completed",
                "Shipped",
                "Processing",
                "Cancelled",
                "Returned",
            ]

            weights = [
                52,
                18,
                8,
                15,
                7,
            ]

            return weighted_choice(
                rng,
                values,
                weights,
            )

        values = [
            "Completed",
            "Shipped",
            "Processing",
            "Cancelled",
            "Returned",
        ]

        weights = [
            56,
            20,
            8,
            11,
            5,
        ]

        return weighted_choice(
            rng,
            values,
            weights,
        )

    values = [
        "Completed",
        "Shipped",
        "Processing",
        "Cancelled",
        "Returned",
    ]

    weights = [
        58,
        20,
        10,
        8,
        4,
    ]

    return weighted_choice(
        rng,
        values,
        weights,
    )


def generate_orders(
    rng: random.Random,
    customers,
):
    """
    Generate order records.

    The distribution intentionally introduces:

    - overall 2025 growth
    - seasonal demand
    - Q3 2025 slowdown
    - stronger Q3 impact in South
    """

    rows = []

    customer_profiles = (
        build_customer_profiles(
            customers
        )
    )

    customer_ids = list(
        customer_profiles.keys()
    )

    base_customer_weights = [
        SEGMENT_ORDER_WEIGHTS[
            customer_profiles[customer_id][
                "segment"
            ]
        ]
        for customer_id in customer_ids
    ]

    for _ in range(
        ORDER_COUNT
    ):
        customer_id = rng.choices(
            customer_ids,
            weights=base_customer_weights,
            k=1,
        )[0]

        profile = customer_profiles[
            customer_id
        ]

        # ----------------------------------------------------
        # Generate date with controlled business seasonality.
        # ----------------------------------------------------

        while True:
            order_date = random_date(
                rng,
                START_DATE,
                END_DATE,
            )

            demand_multiplier = (
                month_multiplier(
                    order_date
                )
                * year_multiplier(
                    order_date
                )
                * q3_2025_multiplier(
                    order_date
                )
            )

            # South is intentionally affected more strongly
            # during Q3 2025.
            if (
                profile["region"] == "South"
                and is_q3_2025(order_date)
            ):
                demand_multiplier *= 0.80

            # Accept/reject sampling creates the desired
            # temporal demand pattern.
            if (
                rng.random()
                < min(
                    demand_multiplier / 1.25,
                    1.0,
                )
            ):
                break

        order_status = choose_order_status(
            rng,
            order_date,
            profile["region"],
        )

        shipping_region = profile[
            "region"
        ]

        rows.append(
            (
                customer_id,
                order_date,
                order_status,
                shipping_region,
            )
        )

    return rows


# ============================================================
# ORDER ITEMS
# ============================================================

def choose_product_category(
    rng: random.Random,
    order_date: date,
):
    """
    Choose a product category.

    Electronics is intentionally affected more strongly during
    the Q3 2025 slowdown.
    """

    category_names = list(
        CATEGORY_WEIGHTS.keys()
    )

    weights = [
        CATEGORY_WEIGHTS[category]
        for category in category_names
    ]

    if is_q3_2025(order_date):
        # Reduce Electronics share in Q3.
        electronics_index = (
            category_names.index(
                "Electronics"
            )
        )

        weights[
            electronics_index
        ] *= 0.65

    return weighted_choice(
        rng,
        category_names,
        weights,
    )


def generate_order_items(
    rng: random.Random,
    orders,
    products,
):
    """
    Generate order item records.

    Each order receives between 1 and 5 products.
    """

    rows = []

    product_info = {
        product_id + 1: {
            "category": product[1],
            "price": float(product[3]),
        }
        for product_id, product
        in enumerate(products)
    }

    products_by_category = defaultdict(
        list
    )

    for product_id, info in product_info.items():
        products_by_category[
            info["category"]
        ].append(product_id)

    for order_id, order in enumerate(
        orders,
        start=1,
    ):
        (
            _customer_id,
            order_date,
            _order_status,
            _region,
        ) = order

        item_count = rng.choices(
            [1, 2, 3, 4, 5],
            weights=[
                45,
                30,
                15,
                7,
                3,
            ],
            k=1,
        )[0]

        selected_products = set()

        while len(
            selected_products
        ) < item_count:

            category = (
                choose_product_category(
                    rng,
                    order_date,
                )
            )

            product_id = rng.choice(
                products_by_category[
                    category
                ]
            )

            selected_products.add(
                product_id
            )

        for product_id in selected_products:

            # Enterprise customers tend to purchase
            # slightly larger quantities.
            customer_id = order[0]

            quantity = rng.choices(
                [1, 2, 3, 4],
                weights=[
                    65,
                    25,
                    8,
                    2,
                ],
                k=1,
            )[0]

            base_price = product_info[
                product_id
            ]["price"]

            price_variation = rng.uniform(
                0.95,
                1.05,
            )

            unit_price = money(
                base_price
                * price_variation
            )

            # Higher discounts around November/December.
            if order_date.month in (
                11,
                12,
            ):
                discount_percent = weighted_choice(
                    rng,
                    [0, 5, 10, 15, 20, 25],
                    [25, 25, 20, 15, 10, 5],
                )

            else:
                discount_percent = weighted_choice(
                    rng,
                    [0, 5, 10, 15, 20],
                    [45, 25, 18, 9, 3],
                )

            rows.append(
                (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    money(
                        discount_percent
                    ),
                )
            )

    return rows


# ============================================================
# ORDER AMOUNTS
# ============================================================

def calculate_order_amounts(
    order_items,
):
    """
    Calculate every order amount in one pass.

    This replaces the original O(orders × order_items)
    implementation.

    Complexity:
        O(number of order items)

    instead of approximately:
        O(number of orders × number of order items)
    """

    amounts = defaultdict(
        lambda: Decimal("0.00")
    )

    for item in order_items:

        (
            order_id,
            _product_id,
            quantity,
            unit_price,
            discount_percent,
        ) = item

        subtotal = (
            Decimal(quantity)
            * unit_price
            * (
                Decimal("100")
                - discount_percent
            )
            / Decimal("100")
        )

        amounts[
            order_id
        ] += subtotal

    for order_id in amounts:
        amounts[
            order_id
        ] = amounts[
            order_id
        ].quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    return amounts


# ============================================================
# PAYMENTS
# ============================================================

def generate_payments(
    rng: random.Random,
    orders,
    order_amounts,
):
    """
    Generate one payment record per order.

    Payment behavior is correlated with order status.
    """

    rows = []

    for order_id, order in enumerate(
        orders,
        start=1,
    ):
        (
            _customer_id,
            order_date,
            order_status,
            _region,
        ) = order

        amount = order_amounts.get(
            order_id,
            Decimal("0.00"),
        )

        if order_status == "Cancelled":

            payment_status = weighted_choice(
                rng,
                [
                    "Failed",
                    "Refunded",
                ],
                [
                    70,
                    30,
                ],
            )

        elif order_status == "Returned":

            payment_status = "Refunded"

        elif order_status == "Processing":

            payment_status = weighted_choice(
                rng,
                [
                    "Paid",
                    "Pending",
                ],
                [
                    85,
                    15,
                ],
            )

        else:

            payment_status = weighted_choice(
                rng,
                [
                    "Paid",
                    "Pending",
                ],
                [
                    96,
                    4,
                ],
            )

        payment_method = weighted_choice(
            rng,
            PAYMENT_METHODS,
            [
                30,
                20,
                30,
                10,
                10,
            ],
        )

        # Small payment-date delay for shipped/completed orders.
        if order_status in {
            "Completed",
            "Shipped",
        }:
            payment_date = min(
                order_date
                + timedelta(
                    days=rng.randint(
                        0,
                        3,
                    )
                ),
                END_DATE,
            )
        else:
            payment_date = order_date

        rows.append(
            (
                order_id,
                payment_method,
                payment_status,
                payment_date,
                amount,
            )
        )

    return rows


# ============================================================
# DATABASE INSERTION
# ============================================================

def insert_data(
    connection,
    customers,
    products,
    orders,
    order_items,
    payments,
):
    """
    Insert all generated records into PostgreSQL.
    """

    with connection.cursor() as cur:

        print(
            "\nInserting customers..."
        )

        cur.executemany(
            """
            INSERT INTO customers
            (
                first_name,
                last_name,
                email,
                region,
                customer_segment,
                signup_date
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            customers,
        )

        print(
            "Inserting products..."
        )

        cur.executemany(
            """
            INSERT INTO products
            (
                product_name,
                category,
                subcategory,
                unit_price,
                cost_price
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            products,
        )

        print(
            "Inserting orders..."
        )

        cur.executemany(
            """
            INSERT INTO orders
            (
                customer_id,
                order_date,
                order_status,
                shipping_region
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            orders,
        )

        print(
            f"Inserting "
            f"{len(order_items):,} "
            f"order items..."
        )

        cur.executemany(
            """
            INSERT INTO order_items
            (
                order_id,
                product_id,
                quantity,
                unit_price,
                discount_percent
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            order_items,
        )

        print(
            "Inserting payments..."
        )

        cur.executemany(
            """
            INSERT INTO payments
            (
                order_id,
                payment_method,
                payment_status,
                payment_date,
                amount
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            payments,
        )

    connection.commit()


# ============================================================
# MAIN
# ============================================================

def main():

    rng = random.Random(
        SEED
    )

    print("=" * 70)
    print(
        "AI DATA ANALYST"
    )
    print(
        "Synthetic E-commerce Data Generator"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Generate customers
    # --------------------------------------------------------

    print(
        "\nGenerating customers..."
    )

    customers = generate_customers(
        rng
    )

    # --------------------------------------------------------
    # Generate products
    # --------------------------------------------------------

    print(
        "Generating products..."
    )

    products = generate_products(
        rng
    )

    # --------------------------------------------------------
    # Generate orders
    # --------------------------------------------------------

    print(
        "Generating orders..."
    )

    orders = generate_orders(
        rng,
        customers,
    )

    # --------------------------------------------------------
    # Generate order items
    # --------------------------------------------------------

    print(
        "Generating order items..."
    )

    order_items = (
        generate_order_items(
            rng,
            orders,
            products,
        )
    )

    # --------------------------------------------------------
    # Calculate order amounts
    # --------------------------------------------------------

    print(
        "Calculating order amounts..."
    )

    order_amounts = (
        calculate_order_amounts(
            order_items
        )
    )

    # --------------------------------------------------------
    # Generate payments
    # --------------------------------------------------------

    print(
        "Generating payments..."
    )

    payments = generate_payments(
        rng,
        orders,
        order_amounts,
    )

    # --------------------------------------------------------
    # Print generation summary
    # --------------------------------------------------------

    print(
        "\nGenerated:"
    )

    print(
        f"  Customers:   "
        f"{len(customers):,}"
    )

    print(
        f"  Products:    "
        f"{len(products):,}"
    )

    print(
        f"  Orders:      "
        f"{len(orders):,}"
    )

    print(
        f"  Order Items: "
        f"{len(order_items):,}"
    )

    print(
        f"  Payments:    "
        f"{len(payments):,}"
    )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    print(
        "\nConnecting to PostgreSQL..."
    )

    connection = get_connection()

    try:

        insert_data(
            connection,
            customers,
            products,
            orders,
            order_items,
            payments,
        )

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()

    print(
        "\nData generation completed successfully."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()