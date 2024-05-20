from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from datetime import datetime, timedelta
default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}
with DAG("local_to_gcs", start_date=datetime(2024, 5, 17),
         schedule_interval="0 23 * * *", default_args=default_args, catchup=False) as dag:
    
    todo_local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='todo_local_to_gcs_task',
        src='/opt/airflow/dags/users.csv',
        dst='users.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCS'
    )
    todo_local_to_gcs_task