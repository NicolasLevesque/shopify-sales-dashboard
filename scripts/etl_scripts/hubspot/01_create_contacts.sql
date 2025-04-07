CREATE TABLE hubspot_contacts AS
SELECT DISTINCT
    customer_id,
    SPLIT_PART(customer_name, ' ', 1) AS first_name,
    SPLIT_PART(customer_name, ' ', 2) AS last_name,
    customer_email AS email,
    phone,
    address,
    created_at,
    updated_at
FROM synthetic_orders
WHERE customer_email IS NOT NULL;  -- Exclude records without email to match HubSpot's mandatory email field
