-- customers table
CREATE TABLE customers (
    shopify_customer_id BIGINT PRIMARY KEY,
    email VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- orders table
CREATE TABLE orders (
    shopify_order_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(shopify_customer_id),
    total_price DECIMAL(10,2),
    currency VARCHAR(10),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- products table
CREATE TABLE products (
    shopify_product_id BIGINT PRIMARY KEY,
    title VARCHAR(255),
    price DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
