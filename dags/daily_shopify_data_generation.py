from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import random
from faker import Faker

# Fixed configurations for shipping costs, discount codes, and tax rates
SHIPPING_METHODS = ["Standard", "Express", "Overnight"]
SHIPPING_COSTS = {"Standard": 0.00, "Express": 10.00, "Overnight": 20.00}
DISCOUNT_CODES = [
    None,
    "WELCOME10",
    "SPRING15",
    None,
    None,
]  # None appears more frequently
DISCOUNT_MAP = {"WELCOME10": 0.10, "SPRING15": 0.15}  # 10%  # 15%
TAX_RATES = [0.05, 0.08, 0.13]  # e.g. 5%, 8%, 13%

# Probability of injecting a data error
ERROR_PROB = 0.1  # 10% chance

# PostgreSQL connection settings
POSTGRES_HOST = "postgres"
POSTGRES_DB = "airflow"
POSTGRES_USER = "airflow"
POSTGRES_PASSWORD = "airflow"
POSTGRES_PORT = 5432

fake = Faker()


def generate_and_save_orders():
    """
    Inserts random, realistic Shopify orders into the 'shopify_sales' table in Postgres.
    Columns required:
      - order_id (INT, PK)
      - order_date (DATE)
      - customer_name (VARCHAR)
      - customer_email (VARCHAR)
      - product (VARCHAR)
      - quantity (INT)
      - price (NUMERIC)
      - total (NUMERIC)
      - shipping_method (VARCHAR)
      - discount_code (VARCHAR)
      - taxes (NUMERIC)
      - shipping_cost (NUMERIC)
      - discount_amount (NUMERIC)
      - is_error (BOOLEAN)
    """
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()

    # Get the current max order_id so we know where to pick up
    cursor.execute("SELECT MAX(order_id) FROM shopify_sales;")
    result = cursor.fetchone()
    last_id = result[0] if result[0] is not None else 1000

    # Decide how many new orders to generate (5-15)
    new_orders_count = random.randint(5, 15)
    orders_data = []

    for i in range(new_orders_count):
        order_id = last_id + i + 1
        order_date = fake.date_between(start_date="-1d", end_date="today")
        customer_name = fake.name()
        customer_email = fake.email()
        product = fake.word().capitalize()

        quantity = random.randint(1, 5)
        price = round(random.uniform(10, 200), 2)

        # Shipping, discount, and tax
        shipping_method = random.choice(SHIPPING_METHODS)
        shipping_cost = SHIPPING_COSTS[shipping_method]

        chosen_discount = random.choice(DISCOUNT_CODES)
        discount_rate = DISCOUNT_MAP.get(chosen_discount, 0.0)  # 0.0 if None

        tax_rate = random.choice(TAX_RATES)

        # Compute pricing
        subtotal = quantity * price
        discount_amount = round(subtotal * discount_rate, 2)
        taxes = round((subtotal - discount_amount) * tax_rate, 2)
        total = round(subtotal - discount_amount + taxes + shipping_cost, 2)

        # By default, no error
        is_error = False

        # ~10% chance to break something
        if random.random() < ERROR_PROB:
            # Choose a random type of error
            error_type = random.choice(["missing_price", "future_date", "negative_qty"])
            is_error = True

            if error_type == "missing_price":
                # Make price None or negative if schema allows it
                price = None  # Or price = -1
                # Recompute total to something obviously wrong
                subtotal = 0
                discount_amount = 0
                taxes = 0
                total = 0

            elif error_type == "future_date":
                order_date = fake.date_between(start_date="+1d", end_date="+30d")

            elif error_type == "negative_qty":
                quantity = -quantity
                subtotal = 0
                discount_amount = 0
                taxes = 0
                total = 0

        orders_data.append(
            (
                order_id,
                order_date,
                customer_name,
                customer_email,
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

    # Insert new rows into shopify_sales
    insert_query = """
        INSERT INTO shopify_sales (
            order_id, order_date, customer_name, customer_email,
            product, quantity, price, total,
            shipping_method, discount_code, taxes, shipping_cost, discount_amount,
            is_error
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, orders_data)
    conn.commit()

    cursor.close()
    conn.close()

    # Count how many error we introduced
    errors_inserted = sum(1 for row in orders_data if row[-1] is True)
    print(
        f"Inserted {new_orders_count} new orders into shopify_sales with more realistic fields."
    )


def generate_daily_summary():
    conn = psycopg2.connect(
        host="postgres",
        database="airflow",
        user="airflow",
        password="airflow",
        port=5432,
    )
    cursor = conn.cursor()

    # Query daily totals from shopify_sales
    query = """
        SELECT
            order_date AS summary_date,
            COUNT(order_id) AS total_orders,
            SUM(quantity) AS total_quantity,
            SUM(total) AS total_revenue
        FROM shopify_sales
        GROUP BY order_date
        ORDER BY order_date;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Option A: Insert summary rows into another table
    insert_query = """
        INSERT INTO daily_summary (summary_date, total_orders, total_quantity, total_revenue)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (summary_date)
        DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_quantity = EXCLUDED.total_quantity,
            total_revenue = EXCLUDED.total_revenue
    """
    # 'ON CONFLICT' ensures that if a row for that date already exists, it gets updated instead of erroring.

    for row in rows:
        cursor.execute(insert_query, row)
    conn.commit()

    # Option B: Also write the same data to a CSV (optional, for quick checks)
    df_summary = pd.DataFrame(
        rows,
        columns=["summary_date", "total_orders", "total_quantity", "total_revenue"],
    )
    df_summary.to_csv("/opt/airflow/data/daily_summary.csv", index=False)

    cursor.close()
    conn.close()
    print("Daily summary updated in both daily_summary table and daily_summary.csv.")


#
# Define Airflow DAG and Tasks
#
default_args = {
    "owner": "you",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),  # Adjust date as needed
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "daily_shopify_data_generation",
    default_args=default_args,
    schedule_interval="@daily",  # run once daily
    catchup=False,
) as dag:

    task_generate_orders = PythonOperator(
        task_id="generate_fake_orders", python_callable=generate_and_save_orders
    )

    task_daily_summary = PythonOperator(
        task_id="generate_daily_summary", python_callable=generate_daily_summary
    )

    # Ensure summary runs after the orders are generated
    task_generate_orders >> task_daily_summary
