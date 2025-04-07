CREATE TABLE hubspot_products AS
SELECT DISTINCT
    product_id,
    product AS product_name,
    sku,
    price,
    category
FROM synthetic_orders;