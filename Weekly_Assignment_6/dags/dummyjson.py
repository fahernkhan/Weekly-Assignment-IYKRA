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

def transform_data(response, data_type):
    if data_type == 'users':
        users = response['users']
        return [
            {
                "userID": user["id"],
                "firstName": user["firstName"],
                "lastName": user["lastName"],
                "age": user["age"],
                "gender": user["gender"],
                "email": user["email"],
                "phoneNumber": user["phone"],
                "birthDate": user["birthDate"],
                "address": user["address"]["city"],
                "coin": user["crypto"]["coin"]
            }
            for user in users
        ]
    elif data_type == 'carts':
        carts = response['carts']
        return [
            {
                "cartID": cart["id"],
                "userID": cart["userId"],
                "total": cart["total"],
                "discountedTotal": cart["discountedTotal"],
                "totalProducts": cart["totalProducts"],
                "totalQuantity": cart["totalQuantity"],
                "products": json.dumps(cart["products"])  # Storing products as a JSON string
            }
            for cart in carts
        ]
    elif data_type == 'posts':
        posts = response['posts']
        return [
            {
                "postID": post["id"],
                "title": post["title"],
                "body": post["body"],
                "userID": post["userId"],
                "tags": json.dumps(post["tags"]),  # Storing tags as a JSON string
                "reactions": post["reactions"]
            }
            for post in posts
        ]
    elif data_type == 'todos':
        todos = response['todos']
        return [
            {
                "todoID": todo["id"],
                "todo": todo["todo"],
                "completed": todo["completed"],
                "userID": todo["userId"]
            }
            for todo in todos
        ]

def transform_generic_user(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='extract_user'))
    transformed_data = transform_data(response, 'users')
    ti.xcom_push(key='transformed_data', value=transformed_data)

def transform_generic_cart(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='extract_cart'))
    transformed_data = transform_data(response, 'carts')
    ti.xcom_push(key='transformed_data', value=transformed_data)

def transform_generic_post(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='extract_post'))
    transformed_data = transform_data(response, 'posts')
    ti.xcom_push(key='transformed_data', value=transformed_data)

def transform_generic_todo(**kwargs):
    ti = kwargs['ti']
    response = json.loads(ti.xcom_pull(task_ids='extract_todo'))
    transformed_data = transform_data(response, 'todos')
    ti.xcom_push(key='transformed_data', value=transformed_data)

def write_to_csv_generic(file_path, fieldnames, **kwargs):
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids=kwargs['transform_task'], key='transformed_data')
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transformed_data)
    logging.info("CSV file has been written successfully to %s.", file_path)

with DAG(dag_id="dummyjson", start_date=datetime(2024, 5, 1), schedule_interval="0 17 * * *", catchup=False, default_args=default_args) as dag:
   
    # Users DAG part
    is_user_api_available = HttpSensor(
        task_id='is_user_api_available',
        http_conn_id='dummyjson_api',
        endpoint='/users/',
        timeout=20,
        poke_interval=5,
    )   

    extract_user = SimpleHttpOperator(
        task_id='extract_user',
        http_conn_id='dummyjson_api',
        method="GET",
        endpoint='/users/',
        headers={"Content-Type": "application/json"},
    )

    transform_user = PythonOperator(
        task_id='transform_user', 
        python_callable=transform_generic_user,
        provide_context=True,
    )

    write_to_csv_user = PythonOperator(
        task_id='write_to_csv_user',
        python_callable=write_to_csv_generic,
        provide_context=True,
        op_kwargs={
            'file_path': '/opt/airflow/dags/playground/target/dummyjson/users.csv',
            'fieldnames': ["userID", "firstName", "lastName", "age", "gender", "email", "phoneNumber", "birthDate", "address", "coin"],
            'transform_task': 'transform_user'
        }
    )

    local_to_gcs_user = LocalFilesystemToGCSOperator(
        task_id='local_to_gcs_user',
        src='/opt/airflow/dags/playground/target/dummyjson/users.csv',
        dst='users.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCP'
    )

    gcs_to_bigquery_user = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery_user',
        bucket='weekly-assignment-6',
        source_objects=['users.csv'],
        destination_project_dataset_table='iconic-indexer-418610.weekly_assignment_6.users',
        schema_fields=[
            {'name': 'userID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'firstName', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'lastName', 'type': 'STRING', 'mode': 'NULLABLE'},
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

    # Carts DAG part
    is_cart_api_available = HttpSensor(
        task_id='is_cart_api_available',
        http_conn_id='dummyjson_api',
        endpoint='/carts/',
        timeout=20,
        poke_interval=5,
    )   

    extract_cart = SimpleHttpOperator(
        task_id='extract_cart',
        http_conn_id='dummyjson_api',
        method="GET",
        endpoint='/carts/',
        headers={"Content-Type": "application/json"},
    )

    transform_cart = PythonOperator(
        task_id='transform_cart', 
        python_callable=transform_generic_cart,
        provide_context=True,
    )

    write_to_csv_cart = PythonOperator(
        task_id='write_to_csv_cart',
        python_callable=write_to_csv_generic,
        provide_context=True,
        op_kwargs={
            'file_path': '/opt/airflow/dags/playground/target/dummyjson/carts.csv',
            'fieldnames': ["cartID", "userID", "total", "discountedTotal", "totalProducts", "totalQuantity", "products"],
            'transform_task': 'transform_cart'
        }
    )

    local_to_gcs_cart = LocalFilesystemToGCSOperator(
        task_id='local_to_gcs_cart',
        src='/opt/airflow/dags/playground/target/dummyjson/carts.csv',
        dst='carts.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCP'
    )

    gcs_to_bigquery_cart = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery_cart',
        bucket='weekly-assignment-6',
        source_objects=['carts.csv'],
        destination_project_dataset_table='iconic-indexer-418610.weekly_assignment_6.carts',
        schema_fields=[
            {'name': 'cartID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'userID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'total', 'type': 'FLOAT', 'mode': 'NULLABLE'},
            {'name': 'discountedTotal', 'type': 'FLOAT', 'mode': 'NULLABLE'},
            {'name': 'totalProducts', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'totalQuantity', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'products', 'type': 'STRING', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        source_format='CSV',
        field_delimiter=',',
        gcp_conn_id='airflowGCP'
    )

    # Posts DAG part
    is_post_api_available = HttpSensor(
        task_id='is_post_api_available',
        http_conn_id='dummyjson_api',
        endpoint='/posts/',
        timeout=20,
        poke_interval=5,
    )   

    extract_post = SimpleHttpOperator(
        task_id='extract_post',
        http_conn_id='dummyjson_api',
        method="GET",
        endpoint='/posts/',
        headers={"Content-Type": "application/json"},
    )

    transform_post = PythonOperator(
        task_id='transform_post', 
        python_callable=transform_generic_post,
        provide_context=True,
    )

    write_to_csv_post = PythonOperator(
        task_id='write_to_csv_post',
        python_callable=write_to_csv_generic,
        provide_context=True,
        op_kwargs={
            'file_path': '/opt/airflow/dags/playground/target/dummyjson/posts.csv',
            'fieldnames': ["postID", "title", "body", "userID", "tags", "reactions"],
            'transform_task': 'transform_post'
        }
    )

    local_to_gcs_post = LocalFilesystemToGCSOperator(
        task_id='local_to_gcs_post',
        src='/opt/airflow/dags/playground/target/dummyjson/posts.csv',
        dst='posts.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCP'
    )

    gcs_to_bigquery_post = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery_post',
        bucket='weekly-assignment-6',
        source_objects=['posts.csv'],
        destination_project_dataset_table='iconic-indexer-418610.weekly_assignment_6.posts',
        schema_fields=[
            {'name': 'postID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'title', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'body', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'userID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'tags', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'reactions', 'type': 'INTEGER', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        source_format='CSV',
        field_delimiter=',',
        gcp_conn_id='airflowGCP'
    )

    # Todos DAG part
    is_todo_api_available = HttpSensor(
        task_id='is_todo_api_available',
        http_conn_id='dummyjson_api',
        endpoint='/todos/',
        timeout=20,
        poke_interval=5,
    )   

    extract_todo = SimpleHttpOperator(
        task_id='extract_todo',
        http_conn_id='dummyjson_api',
        method="GET",
        endpoint='/todos/',
        headers={"Content-Type": "application/json"},
    )

    transform_todo = PythonOperator(
        task_id='transform_todo', 
        python_callable=transform_generic_todo,
        provide_context=True,
    )

    write_to_csv_todo = PythonOperator(
        task_id='write_to_csv_todo',
        python_callable=write_to_csv_generic,
        provide_context=True,
        op_kwargs={
            'file_path': '/opt/airflow/dags/playground/target/dummyjson/todos.csv',
            'fieldnames': ["todoID", "todo", "completed", "userID"],
            'transform_task': 'transform_todo'
        }
    )

    local_to_gcs_todo = LocalFilesystemToGCSOperator(
        task_id='local_to_gcs_todo',
        src='/opt/airflow/dags/playground/target/dummyjson/todos.csv',
        dst='todos.csv',
        bucket='weekly-assignment-6',
        gcp_conn_id='airflowGCP'
    )

    gcs_to_bigquery_todo = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery_todo',
        bucket='weekly-assignment-6',
        source_objects=['todos.csv'],
        destination_project_dataset_table='iconic-indexer-418610.weekly_assignment_6.todos',
        schema_fields=[
            {'name': 'todoID', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'todo', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'completed', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
            {'name': 'userID', 'type': 'STRING', 'mode': 'NULLABLE'}
        ],
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        source_format='CSV',
        field_delimiter=',',
        gcp_conn_id='airflowGCP'
    )

    # User Tasks
    is_user_api_available >> extract_user >> transform_user >> write_to_csv_user
    write_to_csv_user >> local_to_gcs_user >> gcs_to_bigquery_user

    # Cart Tasks
    is_cart_api_available >> extract_cart >> transform_cart >> write_to_csv_cart
    write_to_csv_cart >> local_to_gcs_cart >> gcs_to_bigquery_cart

    # Post Tasks
    is_post_api_available >> extract_post >> transform_post >> write_to_csv_post
    write_to_csv_post >> local_to_gcs_post >> gcs_to_bigquery_post

    # Todo Tasks
    is_todo_api_available >> extract_todo >> transform_todo >> write_to_csv_todo
    write_to_csv_todo >> local_to_gcs_todo >> gcs_to_bigquery_todo
