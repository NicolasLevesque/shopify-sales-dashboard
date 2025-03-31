from airflow import DAG
from airflow.operators.bash import BashOperator
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

    fetch_real_data
