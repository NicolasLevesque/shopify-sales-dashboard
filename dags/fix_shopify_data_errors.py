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
        WHERE order_date > CURRENT_DATE
    """
    )

    corrected_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Corrected {corrected_rows} rows with future date errors.")


def fix_negative_quantities():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "airflow"),
        user=os.getenv("DB_USER", "airflow"),
        password=os.getenv("DB_PASSWORD", "airflow"),
        port=os.getenv("DB_PORT", 5432),
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE synthetic_orders
        SET quantity = ABS(quantity), is_error = FALSE
        WHERE quantity < 0 AND is_error = TRUE;
        """
    )

    corrected_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Corrected {corrected_rows} rows with negative quantity errors.")


def fix_missing_prices():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "airflow"),
        user=os.getenv("DB_USER", "airflow"),
        password=os.getenv("DB_PASSWORD", "airflow"),
        port=os.getenv("DB_PORT", 5432),
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE synthetic_orders so
        SET price = sub.avg_price,
            total_price = so.quantity * sub.avg_price,
            is_error = FALSE
        FROM (
            SELECT product, AVG(price) AS avg_price
            FROM synthetic_orders
            WHERE price IS NOT NULL
            GROUP BY product
        ) AS sub
        WHERE so.product = sub.product
          AND so.price IS NULL
          AND so.is_error = TRUE;
        """
    )

    corrected_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Corrected {corrected_rows} rows with missing price errors.")


with DAG(
    "fix_shopify_data_errors",
    default_args=default_args,
    description="Fix errors in generated Shopify sales data",
    schedule_interval="@daily",
    catchup=False,
    tags=["shopify", "maintenance"],
) as dag:

    fix_date_errors_task = PythonOperator(
        task_id="fix_future_date_errors", python_callable=fix_future_date_errors
    )

    fix_negative_quantities_task = PythonOperator(
        task_id="fix_negative_quantities",
        python_callable=fix_negative_quantities,
    )

    fix_missing_prices_task = PythonOperator(
        task_id="fix_missing_prices",
        python_callable=fix_missing_prices,
    )

    # Task sequence
    fix_date_errors_task >> fix_negative_quantities_task >> fix_missing_prices_task
