from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os
from faker import Faker

default_args = {
    "owner": "you",
    "depends_on_past": False,
    "start_date": datetime(2024, 3, 25),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

fake = Faker("en_CA")
Faker.seed(1234)  # deterministic seed for consistency


def update_orders():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "airflow"),
        user=os.getenv("POSTGRES_USER", "airflow"),
        password=os.getenv("POSTGRES_PASSWORD", "airflow"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

    cur = conn.cursor()

    # Fetch distinct emails that need addresses
    cur.execute(
        "SELECT DISTINCT customer_email FROM synthetic_orders WHERE address IS NULL;"
    )
    emails = [row[0] for row in cur.fetchall()]

    for email in emails:
        Faker.seed(abs(hash(email)))
        address = (
            fake.street_address()
            + ", "
            + fake.city()
            + ", "
            + fake.province()
            + ", Canada, "
            + fake.postalcode()
        )
        phone = fake.phone_number()

        update_query = """
    UPDATE synthetic_orders
    SET address = %s,
        phone = %s,
        payment_method = (ARRAY['Credit Card', 'PayPal', 'Debit'])[floor(random()*3 + 1)],
        sku = 'SKU-' || LPAD(CAST((random() * 99999999)::int AS TEXT), 8, '0'),
        category = (ARRAY['Electronics', 'Home', 'Fashion', 'Books', 'Toys'])[floor(random()*5 + 1)],
        order_status = (ARRAY['completed', 'processing', 'shipped', 'cancelled'])[floor(random()*4 + 1)],
        created_at = order_date - interval '1 day' * (floor(random()*365 + 1)::int),
        customer_id = floor(random()*8999 + 1000)::int,
        product_id = floor(random()*899 + 100)::int
    WHERE customer_email = %s;
    """

        cur.execute(update_query, (address, phone, email))

    conn.commit()
    cur.close()
    conn.close()


with DAG(
    "update_synthetic_orders_daily",
    default_args=default_args,
    schedule_interval="30 0 * * *",
    catchup=False,
) as dag:

    update_task = PythonOperator(
        task_id="update_synthetic_orders_task", python_callable=update_orders
    )
