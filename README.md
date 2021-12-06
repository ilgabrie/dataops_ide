# MLOps development environment
Development environment running in docker containers, deployable on any VM in Public Cloud (Azure, AWS, GCP) to develop data analytical workflows.
## Tools
- Airflow
- MLflow
- Jupyter notebook
- PostgresDB
- Nginx webserver
## Requirements
- Docker CE
- Docker compose
## Usage
1. Clone the repository
2. Create & modify permissions on shared directories
```
mkdir airflow_logs
chown 50000:0 airflow_dags airflow_logs airflow_plugins
chown 1000:0 notebooks/
chmod -R 777 shared_data
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
