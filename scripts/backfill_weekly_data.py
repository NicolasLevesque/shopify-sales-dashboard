from faker import Faker
import psycopg2
import random
import datetime
import os

# Import shared config from product_config
from scripts.product_config import (
    PRODUCTS_AND_PRICES,
    SHIPPING_METHODS,
    SHIPPING_COSTS,
    DISCOUNT_CODES,
    DISCOUNT_MAP,
    TAX_RATES,
    ERROR_PROB,
)

fake = Faker()

# Read database credentials from env (same approach as daily DAG)
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "airflow")
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))


def backfill_weekly_data():
    """Insert about a week's worth of daily orders into synthetic_orders."""

    # Connect to Postgres
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cursor = conn.cursor()

    # Fetch the current max order_id so we know where to continue
    cursor.execute("SELECT MAX(order_id) FROM synthetic_orders;")
    result = cursor.fetchone()
    last_id = result[0] if result[0] is not None else 1000

    orders_data = []
    current_order_id = last_id + 1

    # For each of the past 7 days
    for days_ago in range(7, 0, -1):
        day_date = datetime.date.today() - datetime.timedelta(days=days_ago)

        # Generate random number of orders (say 5-15) for each day
        daily_orders_count = random.randint(5, 15)

        for _ in range(daily_orders_count):
            # Use Faker for random name/email
            customer_name = fake.name()
            customer_email = fake.email()

            # Pick a product & price from the PRODUCTS_AND_PRICES dict
            product, price = random.choice(list(PRODUCTS_AND_PRICES.items()))
            quantity = random.randint(1, 5)

            shipping_method = random.choice(SHIPPING_METHODS)
            shipping_cost = SHIPPING_COSTS[shipping_method]

            chosen_discount = random.choice(DISCOUNT_CODES)
            discount_rate = DISCOUNT_MAP.get(chosen_discount, 0.0)

            tax_rate = random.choice(TAX_RATES)

            # Basic calculations
            subtotal = quantity * price
            discount_amount = round(subtotal * discount_rate, 2)
            taxes = round((subtotal - discount_amount) * tax_rate, 2)
            total = round(subtotal - discount_amount + taxes + shipping_cost, 2)

            # By default, no error
            is_error = False

            # Maybe 10% chance of injecting a data error
            if random.random() < ERROR_PROB:
                is_error = True
                error_type = random.choice(
                    ["missing_price", "future_date", "negative_qty"]
                )

                if error_type == "missing_price":
                    price = None
                    subtotal = 0
                    discount_amount = 0
                    taxes = 0
                    total = 0
                elif error_type == "future_date":
                    # If we want to push it out ~2 weeks artificially
                    day_date = day_date + datetime.timedelta(days=14)
                elif error_type == "negative_qty":
                    quantity = -abs(quantity)
                    subtotal = 0
                    discount_amount = 0
                    taxes = 0
                    total = 0

            orders_data.append(
                (
                    current_order_id,
                    day_date,  # Use the fixed date for that day
                    customer_name,  # or use random names if you prefer
                    customer_email,  # likewise for email
                    product,
                    quantity,
                    price,
                    total,
                    shipping_method,
                    chosen_discount,
                    taxes,
                    shipping_cost,
                    discount_amount,
                    is_error,
                )
            )
            current_order_id += 1

    # Insert all at once
    insert_query = """
        INSERT INTO synthetic_orders (
            order_id, order_date, customer_name, customer_email,
            product, quantity, price, total,
            shipping_method, discount_code, taxes, shipping_cost, discount_amount,
            is_error
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, orders_data)
    conn.commit()

    cursor.close()
    conn.close()

    print(f"Inserted {len(orders_data)} rows spanning the past 7 days.")


if __name__ == "__main__":
    backfill_weekly_data()
