# MLOps development environment
Development environment running in docker containers, deployable on any VM in Public Cloud (Azure, AWS, GCP) to develop data analytical workflows.
## Tools
- Airflow
- MLflow
- Jupyter notebook
- PostgresDB
## Requirements
- Docker CE
- Docker compose
## Usage
1. Clone the repository
2. Create shared directories
```
mkdir airflow_dags airflow_logs airflow_plugins
chown 50000:0 airflow_dags airflow_logs airflow_plugins
mkdir notebooks
chown 1000:0 notebooks/
```
4. Deploy the environment
```
docker-compose -f docker-compose.yml up --build -d
```
## Web UIs
### Airflow
```
http://<IP/FQDN of VM>:8080
#Login
username: admin
password: start123
```
### MLflow
```
http://<IP/FQDN of VM>:5000
```
### JupyterLab
```
http://<IP/FQDN of VM>:8888
```
