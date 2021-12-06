from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "ml_flow_sample",
    schedule_interval=None,
    catchup=False,
    default_args=default_arguments,
    ) as dag:
    
    data_preparation = DummyOperator(
        task_id = "data_preparation"
    )
    
    train_model = DummyOperator(
        task_id ="train_model"
    )
    
    tune_parameters = DummyOperator(
        task_id = "tune_parameters"
    )
    
    evaluate_model = DummyOperator(
        task_id = "evaluate_model"
    )
    
    registry_model = DummyOperator(
        task_id = "registry_model"
    )
    
data_preparation >> [train_model, tune_parameters] >> evaluate_model >> registry_model
