from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.providers.microsoft.azure.hooks.wasb import WasbHook

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "test_azure",
    schedule_interval="@daily",
    catchup=False,
    default_args=default_arguments,
    ) as dag:

    def list_adls(container):
        hook = WasbHook()
        file_exists = hook.get_blobs_list(container)

        return file_exists

    list_adls = PythonOperator(
            task_id = "list_adls",
            python_callable = list_adls,
            op_kwargs = {"container": "rawdata"},
            provide_context=True
            )
