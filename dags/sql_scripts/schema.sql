CREATE TABLE IF NOT EXISTS synthetic_orders (
    order_id INT PRIMARY KEY,
    order_date DATE,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    product VARCHAR(255),
    quantity INT,
    price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    shipping_method VARCHAR(50),
    discount_code VARCHAR(50),
    taxes NUMERIC(10,2),
    shipping_cost NUMERIC(10,2),
    discount_amount NUMERIC(10,2),
    is_error BOOLEAN DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS daily_summary (
    summary_date DATE PRIMARY KEY,
    total_orders INT,
    total_quantity INT,
    total_revenue NUMERIC(10,2)
);
CREATE TABLE IF NOT EXISTS real_orders (
    order_id BIGINT PRIMARY KEY,
    order_date TIMESTAMP,
    customer_first_name VARCHAR(255),
    customer_last_name VARCHAR(255),
    customer_email VARCHAR(255),
    financial_status VARCHAR(50),
    fulfillment_status VARCHAR(50),
    currency VARCHAR(10),
    subtotal_price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    total_tax NUMERIC(10,2),
    total_discounts NUMERIC(10,2),
    total_shipping NUMERIC(10,2),
    gateway VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS real_daily_summary (
    summary_date DATE PRIMARY KEY,
    total_orders INT,
    total_quantity INT,
    total_revenue NUMERIC(10,2)
);

ALTER TABLE real_orders ALTER COLUMN order_date TYPE DATE USING order_date::DATE;
ALTER TABLE real_orders ALTER COLUMN subtotal_price TYPE NUMERIC(10,2) USING subtotal_price::NUMERIC(10,2);
ALTER TABLE real_orders ALTER COLUMN total_price TYPE NUMERIC(10,2) USING total_price::NUMERIC(10,2);
ALTER TABLE real_orders ALTER COLUMN total_tax TYPE NUMERIC(10,2) USING total_tax::NUMERIC(10,2);
ALTER TABLE real_orders ALTER COLUMN total_discounts TYPE NUMERIC(10,2) USING total_discounts::NUMERIC(10,2);
ALTER TABLE real_orders ALTER COLUMN total_shipping TYPE NUMERIC(10,2) USING total_shipping::NUMERIC(10,2);

ALTER TABLE real_orders 
ADD COLUMN customer_type VARCHAR(50);

ALTER TABLE synthetic_orders
ADD COLUMN customer_first_name TEXT,
ADD COLUMN customer_last_name TEXT;

ALTER TABLE synthetic_orders
ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
