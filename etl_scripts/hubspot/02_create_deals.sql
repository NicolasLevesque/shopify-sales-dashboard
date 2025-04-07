CREATE TABLE hubspot_deals AS
SELECT
    order_id,
    customer_email AS associated_contact_email,
    order_date AS deal_create_date,
    total_price AS amount,
    order_status AS deal_stage,
    payment_method
FROM synthetic_orders;