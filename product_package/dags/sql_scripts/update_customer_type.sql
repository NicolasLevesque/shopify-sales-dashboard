-- 1) Create a Common Table Expression (CTE) that assigns each order a row number
--    based on the earliest order_date per customer_email.
WITH cte AS (
    SELECT 
        order_id,
        customer_email,
        order_date,
        ROW_NUMBER() OVER (
            PARTITION BY customer_email 
            ORDER BY order_date
        ) AS rn
    FROM real_orders
)

-- 2) Update each row in real_orders by joining to the CTE.
--    If the row_number (rn) is 1, that means it's the first (earliest) order for that email → "New".
--    Otherwise, it's "Returning".
UPDATE real_orders r
SET customer_type = CASE
    WHEN c.rn = 1 THEN 'New'
    ELSE 'Returning'
END
FROM cte c
WHERE r.order_id = c.order_id;
