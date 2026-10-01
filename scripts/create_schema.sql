-- ============================================
-- AI Data Analyst — E-commerce Schema
-- ============================================

DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;


-- ============================================
-- CUSTOMERS
-- ============================================

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    signup_date DATE NOT NULL
);


-- ============================================
-- PRODUCTS
-- ============================================

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    cost_price NUMERIC(10, 2) NOT NULL
);


-- ============================================
-- ORDERS
-- ============================================

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL
        REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    shipping_region VARCHAR(50) NOT NULL
);


-- ============================================
-- ORDER ITEMS
-- ============================================

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL
        REFERENCES orders(order_id),
    product_id INTEGER NOT NULL
        REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    discount_percent NUMERIC(5, 2) NOT NULL DEFAULT 0
);


-- ============================================
-- PAYMENTS
-- ============================================

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL
        REFERENCES orders(order_id),
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(30) NOT NULL,
    payment_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
);


-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_orders_customer
    ON orders(customer_id);

CREATE INDEX idx_orders_date
    ON orders(order_date);

CREATE INDEX idx_orders_status
    ON orders(order_status);

CREATE INDEX idx_orders_region
    ON orders(shipping_region);

CREATE INDEX idx_order_items_order
    ON order_items(order_id);

CREATE INDEX idx_order_items_product
    ON order_items(product_id);

CREATE INDEX idx_payments_order
    ON payments(order_id);

CREATE INDEX idx_payments_date
    ON payments(payment_date);