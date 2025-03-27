# generate_shopify_data.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
import random

fake = Faker()


def generate_and_save_orders():
    try:
        data = pd.read_csv("/opt/airflow/data/shopify_sales.csv")
        last_id = data["Order ID"].max() + 1
    except FileNotFoundError:
        data = pd.DataFrame()
        last_id = 1000

    new_orders = [
        {
            "Order ID": last_id + i,
            "Order Date": fake.date_between(start_date="-1d", end_date="today"),
            "Customer Name": fake.name(),
            "Customer Email": fake.email(),
            "Product": fake.word().capitalize(),
            "Quantity": random.randint(1, 5),
            "Price": round(random.uniform(10, 200), 2),
        }
        for i in range(random.randint(5, 15))
    ]

    for order in new_orders:
        order["Total"] = order["Quantity"] * order["Price"]

    data = pd.concat([data, pd.DataFrame(new_orders)], ignore_index=True)
    data.to_csv("/opt/airflow/data/shopify_sales.csv", index=False)


default_args = {
    "owner": "you",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),  # Adjust accordingly
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "daily_shopify_data_generation",
    default_args=default_args,
    schedule_interval="@daily",  # run daily
    catchup=False,
) as dag:
    task_generate_orders = PythonOperator(
        task_id="generate_fake_orders", python_callable=generate_and_save_orders
    )

task_generate_orders
