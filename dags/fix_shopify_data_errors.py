from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2
import os

# DAG configuration
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 30),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def fix_future_date_errors():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "airflow"),
        user=os.getenv("DB_USER", "airflow"),
        password=os.getenv("DB_PASSWORD", "airflow"),
        port=os.getenv("DB_PORT", 5432),
    )
    cursor = conn.cursor()

    # Correct future dates to today's date
    cursor.execute(
        """
        UPDATE synthetic_orders
        SET order_date = CURRENT_DATE, is_error = FALSE
        WHERE order_date > CURRENT_DATE AND is_error = TRUE
    """
    )

    corrected_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Corrected {corrected_rows} rows with future date errors.")


with DAG(
    "fix_shopify_data_errors",
    default_args=default_args,
    description="Fix errors in Shopify sales data",
    schedule_interval="@daily",
    catchup=False,
    tags=["shopify", "maintenance"],
) as dag:

    fix_date_errors_task = PythonOperator(
        task_id="fix_future_date_errors", python_callable=fix_future_date_errors
    )

    fix_date_errors_task
