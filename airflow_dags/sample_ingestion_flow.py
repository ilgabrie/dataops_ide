from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "ingestion_sample",
    schedule_interval=None,
    catchup=False,
    default_args=default_arguments,
    ) as dag:
    
    extract_data = DummyOperator(
        task_id = "extract_data"
    )
    
    validate_extracted_data = DummyOperator(
        task_id ="validate_extracted_data"
    )
    
    load_data = DummyOperator(
        task_id = "load_data"
    )
    
    validate_loaded_data = DummyOperator(
        task_id = "validate_loaded_data"
    )
    
extract_data >> validate_extracted_data >> load_data >> validate_loaded_data
