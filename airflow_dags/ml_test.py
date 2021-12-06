from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator

default_arguments = {
    "owner": "gabriel",
    "start_date": days_ago(1),
}

with DAG(
    "mlflow_demo",
    schedule_interval="@daily",
    catchup=False,
    default_args=default_arguments,
    ) as dag:

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

        df = pd.read_csv("https://ucfdataopstest.blob.core.windows.net/rawdata/CarPrice.csv?sp=r&st=2021-12-03T10:48:00Z&se=2021-12-04T18:48:00Z&spr=https&sv=2020-08-04&sr=b&sig=zDIrfOTtpUWRtJP0ec4MPp9SHQd6%2Bj%2FAhe%2B%2Frgy0yMo%3D")

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
        task_id = "run_mlflow",
        python_callable = run_mlflow,
        provide_context = True
        )
