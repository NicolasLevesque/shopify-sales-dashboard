CREATE TABLE hubspot_products AS
SELECT DISTINCT
    product_id,
    product AS product_name,
    sku,
    price,
    category,
    NOW() AS updated_at  -- adds a current timestamp if no existing updated_at
FROM synthetic_orders;