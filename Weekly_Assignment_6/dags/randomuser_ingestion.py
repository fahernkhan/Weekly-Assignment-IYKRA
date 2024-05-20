import logging
import json

from datetime import datetime, timedelta

from airflow import DAG

from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.decorators import task
from airflow.operators.bash import BashOperator

def transform_user(**kwargs):
    ti = kwargs['ti']
    response = ti.xcom_pull(task_ids='extract_user')

    response = json.loads(response) #str to dict

    user = response['results'][0]

    return {
        "first_name": user["name"]["first"],
        "last_name": user["name"]["last"],
        "gender": user["gender"],
        "age": user["dob"]["age"],
        "country": user["location"]["country"],
        "email": user["email"]
    }
    # print(user, type(user))

def check_user_age(**kwargs):
    ti = kwargs['ti']
    user = ti.xcom_pull(task_ids='transform_user')

    if user["age"] >= 30:
        return "store_user_group_a"
    else:
        return "store_user_group_b"

    #print(response, type(response))

def store_user_group(**kwargs):
    ti = kwargs['ti']
    user = ti.xcom_pull(task_ids='transform_user')

    with open(kwargs["target_file"], "a") as f:
        f.write(f"{user["first_name"]},{user["last_name"]},{user["gender"]},{user["age"]},{user["country"]},{user["email"]}\n")

# def store_user_group_a(**kwargs):
#     ti = kwargs['ti']
#     user = ti.xcom_pull(task_ids='transform_user')

#     with open("/opt/airflow/dags/playground/target/randomuser/group_a.csv", "a") as f:
#         f.write(f"{user["first_name"]}, {user["last_name"]}, {user["gender"]}, {user["age"]}, {user["country"]}, {user["email"]}\n")

# def store_user_group_b(**kwargs):
#     ti = kwargs['ti']
#     user = ti.xcom_pull(task_ids='transform_user')

#     with open("/opt/airflow/dags/playground/target/randomuser/group_b.csv", "a") as f:
#         f.write(f"{user["first_name"]}, {user["last_name"]}, {user["gender"]}, {user["age"]}, {user["country"]}, {user["email"]}\n")

with DAG(dag_id="randomuser_ingestion", start_date=datetime(2024, 5, 1), schedule="@once", catchup=False) as dag:
    
    is_api_available = HttpSensor(
        task_id='is_api_available',
        http_conn_id='randomuser_api',
        endpoint='/api',
        dag=dag,
    )

    extract_user = SimpleHttpOperator(
        task_id='extract_user',
        http_conn_id='randomuser_api',
        method="GET",
        endpoint='/api',
        headers={"Content-Type": "application/json"},
        dag=dag,
    )

    transform_user = PythonOperator(
        task_id='transform_user', 
        python_callable=transform_user,
        provide_context=True,
        dag=dag
    )


    check_user_age = BranchPythonOperator(
        task_id='check_user_age',
        python_callable=check_user_age,
        provide_context=True,
        dag=dag
    )

    for group_id in ["a","b"]:
        sug = PythonOperator(
            task_id=f'store_user_group_{group_id}', 
            python_callable=store_user_group,
            provide_context=True,
            op_kwargs={"target_file": f"/opt/airflow/dags/playground/target/randomuser/group_{group_id}.csv"},
            dag=dag
        )

        check_user_age >> sug

    # store_user_group_a = PythonOperator(
    #     task_id='store_user_group_a', 
    #     python_callable=store_user_group,
    #     provide_context=True,
    #     op_kwargs={"target_file": "/opt/airflow/dags/playground/target/randomuser/group_a.csv"},
    #     dag=dag
    # )

    # store_user_group_b = PythonOperator(
    #     task_id='store_user_group_b', 
    #     python_callable=store_user_group,
    #     provide_context=True,
    #     op_kwargs={"target_file": "/opt/airflow/dags/playground/target/randomuser/group_b.csv"},
    #     dag=dag
    # )

    is_api_available >> extract_user >> transform_user >> check_user_age
    # check_user_age >> [store_user_group_a, store_user_group_b]
