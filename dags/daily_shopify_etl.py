from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
     # These two lines enable email alerts on task failure:
    #'email': ['levesquenicolas95@gmail.com'],  
    #'email_on_failure': True,   
}

with DAG(
    dag_id='daily_shopify_etl',
    default_args=default_args,
    description='Run my Shopify ETL script daily',
    start_date=datetime(2025, 3, 20),
    schedule_interval='@daily',  # or '0 */6 * * *' for every 6 hours
    catchup=False
) as dag:

    run_etl = BashOperator(
        task_id='run_etl_script',
        # Update path to match where your etl.py actually is
        bash_command='python /opt/airflow/scripts/etl.py'
    )
