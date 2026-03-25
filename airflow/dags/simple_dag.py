from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

def print_hello():
    print("Hello World!")

with DAG(
    dag_id='simple_dag',
    start_date=datetime(2026, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="print_hello",
        python_callable=print_hello(),
    )
