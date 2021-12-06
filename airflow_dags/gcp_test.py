from airflow import DAG
from airflow.utils.dates import days_ago
from great_expectations.data_context.types.base import DataContextConfig, DatasourceConfig, FilesystemStoreBackendDefaults
from great_expectations.data_context import BaseDataContext
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import datetime
import random
from airflow.providers.google.cloud.transfers.gcs_to_local import GCSToLocalFilesystemOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.exceptions import AirflowFailException

project_config = DataContextConfig(
    datasources={
        "local_datasource": {
            "data_asset_type": {
                "class_name": "PandasDataset",
                "module_name": "great_expectations.dataset",
            },
            "class_name": "PandasDatasource",
            "module_name": "great_expectations.datasource",
            "batch_kwargs_generators": {},
        }
    },
    store_backend_defaults=FilesystemStoreBackendDefaults(root_directory="/tmp/shared_data/great_expectations"),
    validation_operators={
         "action_list_operator": {
             "class_name": "ActionListValidationOperator",
             "action_list": [
                 {
                     "name": "store_validation_result",
                     "action": {"class_name": "StoreValidationResultAction"},
                 },
                 {
                     "name": "store_evaluation_params",
                     "action": {"class_name": "StoreEvaluationParametersAction"},
                 },
                 {
                     "name": "update_data_docs",
                     "action": {"class_name": "UpdateDataDocsAction"},
                 },
             ],
             "result_format": {'result_format': 'COMPLETE'},
         }
     }
)

context = BaseDataContext(project_config=project_config)

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "dataops_demo",
    schedule_interval="@daily",
    catchup=False,
    default_args=default_arguments,
    ) as dag:

    def run_validation(run_name, **kwargs):
        batch_kwargs = {
            "datasource": "local_datasource",
            "path": "https://ucfdataopstest.blob.core.windows.net/rawdata/CarPrice.csv?sp=r&st=2021-12-02T15:48:31Z&se=2021-12-02T23:48:31Z&spr=https&sv=2020-08-04&sr=b&sig=0aM70jzXPrQTI36Y3AjCVw3w3O2Q6eAfUrvsvbwaPhM%3D",
            "reader_method": "read_csv"
            }
        batch = context.get_batch(batch_kwargs, "validate_data")
        run_id = {
            "run_name": run_name + "_" + str(random.randint(10,99)),
            "run_time": datetime.datetime.now(datetime.timezone.utc)
        }
        results = context.run_validation_operator(
            "action_list_operator",
            assets_to_validate=[batch],
            run_id=run_id
        )
        if not results["success"]:
            raise AirflowFailException("Data validation failed!")

    validate_data = PythonOperator(
        task_id = "validate_input_data",
        python_callable=run_validation,
        op_kwargs={"run_name": "{{ task.task_id }}"},
        provide_context = True
    )


#list_landing_zone.set_downstream(check_for_csv_files)
#check_for_csv_files.set_downstream(validate_data)
