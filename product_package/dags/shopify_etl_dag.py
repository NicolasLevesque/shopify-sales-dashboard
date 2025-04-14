from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime


with DAG(
    dag_id="daily_real_shopify_data",
    schedule_interval="@daily",
    start_date=datetime(2025, 3, 29),
    catchup=False,
) as dag:

    fetch_real_data = BashOperator(
        task_id="fetch_real_shopify_orders",
        bash_command="python /opt/airflow/scripts/real_shopify_etl.py",
    )

    update_customer_type = SQLExecuteQueryOperator(
        task_id="update_customer_type",
        conn_id="postgres_default",  # ensure this matches your Airflow connection
        sql="sql_scripts/update_customer_type.sql",
    )

    update_real_orders_timestamp = SQLExecuteQueryOperator(
        task_id="update_real_orders_timestamp",
        conn_id="postgres_default",
        sql="""
            UPDATE real_orders
            SET updated_at = NOW();
        """,
    )
    fetch_real_data >> update_customer_type >> update_real_orders_timestamp
