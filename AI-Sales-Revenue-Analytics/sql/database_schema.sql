-- Database schema for RetailX Analytics
-- Use PostgreSQL or MySQL (types shown for PostgreSQL)

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    age INTEGER,
    gender VARCHAR(20),
    segment VARCHAR(50),
    city VARCHAR(100),
    state VARCHAR(50),
    region VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    unit_price NUMERIC(12,2),
    cost NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    order_date DATE,
    ship_date DATE,
    sales_channel VARCHAR(50),
    payment_mode VARCHAR(50),
    order_status VARCHAR(50),
    return_flag INTEGER
);

CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(order_id),
    product_id VARCHAR(50) REFERENCES products(product_id),
    quantity INTEGER,
    discount NUMERIC(8,4),
    sales NUMERIC(14,2),
    profit NUMERIC(14,2)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_details_product_id ON order_details(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region);
