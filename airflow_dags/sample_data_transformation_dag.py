from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "ETL_sample",
    schedule_interval=None,
    catchup=False,
    default_args=default_arguments,
    ) as dag:
    
    clean_data = DummyOperator(
        task_id = "clean_data"
    )
    
    validate_cleaned_data = DummyOperator(
        task_id ="validate_cleaned_data"
    )
    
    aggregation_1 = DummyOperator(
        task_id = "aggregation_1"
    )
    
    store_aggregation_1 = DummyOperator(
        task_id = "store_aggregation_1"
    )
    
    aggregation_2 = DummyOperator(
        task_id = "aggregation_2"
    )
    
    store_aggregation_2 = DummyOperator(
        task_id = "store_aggregation_2"
    )
    
clean_data >> validate_cleaned_data >> [aggregation_1, aggregation_2]
aggregation_1 >> store_aggregation_1
aggregation_2 >> store_aggregation_2
