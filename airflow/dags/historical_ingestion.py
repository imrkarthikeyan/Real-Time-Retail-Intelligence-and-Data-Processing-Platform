from datetime import datetime

from airflow.operators.bash import BashOperator

from airflow import DAG

with DAG("retailpulse_historical_ingestion", start_date=datetime(2024, 1, 1),
         schedule="@daily", catchup=False, tags=["retailpulse"]) as dag:
    generate = BashOperator(task_id="generate_data",
                            bash_command="retailpulse-generate --customers 1000 --products 100 --orders 5000")
    batch = BashOperator(task_id="run_batch_etl",
                         bash_command="spark-submit jobs/batch/historical_ingestion.py --input data/generated")
    generate >> batch
