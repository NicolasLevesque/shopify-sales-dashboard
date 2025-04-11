UPDATE synthetic_orders
SET customer_first_name = SPLIT_PART(customer_name, ' ', 1),
    customer_last_name = SPLIT_PART(customer_name, ' ', 2);