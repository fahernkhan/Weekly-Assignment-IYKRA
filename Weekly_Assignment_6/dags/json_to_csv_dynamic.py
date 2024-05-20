import os
import json
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

dag_configs = [
    {
        "dag_id": "json2csv_a",
        "start_date": datetime(2024, 5, 8),
        "schedule": "*/2 * * * *",
        "task_configs": [
            {
                "name": "students",
                "source_path": "/opt/airflow/dags/playground/source/database_a/students",
                "columns": ["id", "name"],
                "target_file": "/opt/airflow/dags/playground/target/dataset_a/students.csv"
            },
            {
                "name": "teachers",
                "source_path": "/opt/airflow/dags/playground/source/database_a/teachers",
                "columns": ["id", "name", "start_date"],
                "target_file": "/opt/airflow/dags/playground/target/dataset_a/teachers.csv"
            },
            {
                "name": "courses",
                "source_path": "/opt/airflow/dags/playground/source/database_a/courses",
                "columns": ["id", "name", "level"],
                "target_file": "/opt/airflow/dags/playground/target/dataset_a/courses.csv"
            }
        ]
    },
    {
        "dag_id": "json2csv_b",
        "start_date": datetime(2024, 5, 8),
        "schedule": "*/5 * * * *",
        "task_configs": [
            {
                "name": "customers",
                "source_path": "/opt/airflow/dags/playground/source/database_b/customers",
                "columns": ["id", "name", "register_date"],
                "target_file": "/opt/airflow/dags/playground/target/dataset_b/customers.csv"
            },
        ]
    }
]

for dag_config in dag_configs:
    dag_id = dag_config["dag_id"]
    start_date = dag_config["start_date"]
    schedule = dag_config["schedule"]
    task_configs = dag_config["task_configs"]

    with DAG(dag_id, start_date=start_date, schedule=schedule, catchup=False) as dag:

        @task()
        def extract(source_path):

            data = []

            filenames = os.listdir(source_path)
            for filename in filenames:
                with open(f"{source_path}/{filename}", 'r') as f:
                    data.append(json.load(f))

            return data

        @task()
        def transform(data, columns):
            o = ""
            for a in data:
                o += ",".join([str(a[column]) for column in columns]) + "\n"
            
            return o

        @task()
        def load(o, target_file):
            with open(target_file, 'a') as f:
                f.write(o)

        for task_config in task_configs:
            e = extract.override(task_id=f"{task_config["name"]}_extract")(task_config["source_path"])
            t = transform.override(task_id=f"{task_config["name"]}_transform")(e, task_config["columns"])
            l = load.override(task_id=f"{task_config["name"]}_load")(t, task_config["target_file"])

            l