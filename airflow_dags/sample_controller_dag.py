from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "controller_sample",
    schedule_interval="@hourly",
    catchup=False,
    default_args=default_arguments,
    ) as dag:
    
    execute_data_ingestion = TriggerDagRunOperator(
        task_id = "execute_data_ingestion",
        trigger_dag_id = "ingestion_sample",
        execution_date='{{ execution_date }}'
    )
    
    sense_ingest_completion = ExternalTaskSensor(
        task_id ="sense_ingest_completion",
        external_dag_id = "ingestion_sample",
        external_task_id = "validate_loaded_data",
        allowed_states=['success'],
        timeout = 60,
        poke_interval = 15
    )
    
    execute_ml_workflow = TriggerDagRunOperator(
        task_id = "execute_ml_workflow",
        trigger_dag_id="ml_flow_sample",
        wait_for_completion = True,
        poke_interval= 10
    )
    
    execute_etl_workflow = TriggerDagRunOperator(
        task_id = "execute_etl_workflow",
        trigger_dag_id="ETL_sample",
        wait_for_completion = True,
        poke_interval= 10
    )
    
execute_data_ingestion >> sense_ingest_completion >> [execute_ml_workflow, execute_etl_workflow]
