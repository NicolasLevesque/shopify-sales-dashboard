CREATE TABLE IF NOT EXISTS shopify_sales (
    order_id INT PRIMARY KEY,
    order_date DATE,
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    product VARCHAR(255),
    quantity INT,
    price NUMERIC(10,2),
    total NUMERIC(10,2)
);
CREATE TABLE IF NOT EXISTS daily_summary (
    summary_date DATE PRIMARY KEY,
    total_orders INT,
    total_quantity INT,
    total_revenue NUMERIC(10,2)
);
ALTER TABLE shopify_sales
  ADD COLUMN shipping_method VARCHAR(50),
  ADD COLUMN discount_code VARCHAR(50),
  ADD COLUMN taxes NUMERIC(10,2),
  ADD COLUMN shipping_cost NUMERIC(10,2),
  ADD COLUMN discount_amount NUMERIC(10,2);
  ADD COLUMN is_error BOOLEAN DEFAULT FALSE;
