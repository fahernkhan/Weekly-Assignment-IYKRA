import logging
import json
import csv
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator


default_args = {
    "email": ["fathurrahmanhernanda@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 5,
    "retry_delay": timedelta(minutes=5)
}

def transform_user(**kwargs):
    ti = kwargs['ti']
    response = ti.xcom_pull(task_ids='extract_user')

    response = json.loads(response)  # str to dict
    users = response['users']

    transformed_users = []

    for user in users:
        transformed_users.append({
            "user_id": user["id"],
            "first_name": user["firstName"],
            "last_name": user["lastName"],
            "age": user["age"],
            "gender": user["gender"],
            "email": user["email"],
            "phoneNumber": user["phone"],
            "birthDate": user["birthDate"],
            "address": user["address"]["city"],
            "coin": user["crypto"]["coin"]
        })

    logging.info("Transformed Users: %s", transformed_users)
    ti.xcom_push(key='transformed_users', value=transformed_users)
    return transformed_users

def write_to_csv(**kwargs):
    ti = kwargs['ti']
    transformed_users = ti.xcom_pull(task_ids='transform_user', key='transformed_users')

    with open('/opt/airflow/dags/playground/target/dummyjson/users.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "user_id", "first_name", "last_name", "age", "gender", "email", "phoneNumber", "birthDate", "address", "coin"
        ])
        writer.writeheader()
        for user in transformed_users:
            writer.writerow(user)

    logging.info("CSV file has been written successfully.")

with DAG(dag_id="dummyjson_ingestion", start_date=datetime(2024, 5, 1), schedule="@once", catchup=False, default_args=default_args) as dag:
   
    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='dummyjson_api',
        endpoint='/users/',
        timeout=20,
        poke_interval=5,
        dag=dag
    )   

    extract_user = SimpleHttpOperator(
        task_id='extract_user',
        http_conn_id='dummyjson_api',
        method="GET",
        endpoint='/users/',
        headers={"Content-Type": "application/json"},
        dag=dag
    )

    transform_user = PythonOperator(
        task_id='transform_user', 
        python_callable=transform_user,
        provide_context=True,
        dag=dag
    )

    write_to_csv = PythonOperator(
        task_id='write_to_csv',
        python_callable=write_to_csv,
        provide_context=True,
        dag=dag
    )

    local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='local_to_gcs_task',
        src='/opt/airflow/dags/playground/target/dummyjson/users.csv',
        dst='users.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCP'
    )

    gcs_to_bigquery = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery',
        bucket='weekly-assignment-6',
        source_objects=['users.csv'],
        destination_project_dataset_table='iconic-indexer-418610.weekly_assignment_6.users',
        schema_fields=[
            {'name': 'user_id', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'first_name', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'last_name', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'age', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'gender', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'email', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'phoneNumber', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'birthDate', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'address', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'coin', 'type': 'STRING', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        source_format='CSV',
        field_delimiter=',',
        gcp_conn_id='airflowGCP'
    )

    is_api_available >> extract_user >> transform_user >> write_to_csv 
    write_to_csv >> local_to_gcs_task >> gcs_to_bigquery