from airflow import DAG
from airflow.utils.dates import days_ago
from great_expectations.data_context.types.base import DataContextConfig, DatasourceConfig, FilesystemStoreBackendDefaults
from great_expectations.data_context import BaseDataContext
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import datetime
import random
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowFailException

datasource = "https://ucfdataopstest.blob.core.windows.net/rawdata/CarPrice.csv?sp=r&st=2021-12-06T12:05:14Z&se=2021-12-06T20:05:14Z&spr=https&sv=2020-08-04&sr=b&sig=gbIK0thzrSfGuEJw3e9os2QCFOB4gTriqUrmpnBpCHU%3D"

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
            "path": datasource,
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

    def run_mlflow():
        import pandas as pd
        import numpy as np
        from sklearn import linear_model
        import mlflow
        import mlflow.pyfunc
        import mlflow.sklearn
        from mlflow.models.signature import infer_signature
        from mlflow.utils.environment import _mlflow_conda_env
        import cloudpickle
        from urllib.parse import urlparse

        df = pd.read_csv(datasource)

        split = np.random.rand(len(df)) < 0.8
        train = df[split]
        test = df[~split]
        regr = linear_model.LinearRegression()
        train_x_mpg = np.asanyarray(train[['enginesize']])
        train_y_price = np.asanyarray(train[['price']])

        mlflow.set_tracking_uri('http://mlflow:5000')
        mlflow.set_experiment("AirflowMLOpsDemo")

        mlflow.autolog(
            log_input_examples=False,
            log_model_signatures=True,
            log_models=True,
            disable=False,
            exclusive=True,
            disable_for_unsupported_versions=True,
            silent=True
        )

        with mlflow.start_run():

            regr.fit (train_x_mpg, train_y_price)

            from sklearn.metrics import r2_score

            test_x_mpg = np.asanyarray(test[['enginesize']])
            test_y_price = np.asanyarray(test[['price']])
            test_y_price_ = regr.predict(test_x_mpg)

            m_a_e = np.mean(np.absolute(test_y_price_ - test_y_price))
            m_s_e = np.mean((test_y_price_ - test_y_price) ** 2)
            r_squared = r2_score(test_y_price , test_y_price_)

            mlflow.log_metric("m_s_e", m_s_e)
            mlflow.log_metric("r_squared", r_squared)
            mlflow.log_metric("m_a_e", m_a_e)

            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(regr, "model", registered_model_name="LR_model")
            else:
                mlflow.sklearn.log_model(regr, "model")

    run_mlflow = PythonOperator(
        task_id = "run_mlflow_task",
        python_callable = run_mlflow,
        provide_context = True
        )

validate_data >> run_mlflow
