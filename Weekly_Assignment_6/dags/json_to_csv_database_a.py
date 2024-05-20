import os
import json
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="json_to_csv_database_a", start_date=datetime(2024, 5, 8), schedule="*/2 * * * *", catchup=False) as dag:

    configs = [
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

    # @task(task_id=f"{config["name"]}_extract")
    @task()
    def extract(source_path):
        source_path = source_path
        
        data = []

        filenames = os.listdir(source_path)
        for filename in filenames:
            with open(f"{source_path}/{filename}", 'r') as f:
                data.append(json.load(f))

        return data

    # @task(task_id=f"{config["name"]}_transform")
    @task()
    def transform(data, columns):
        o = ""
        for a in data:
            o += ",".join([str(a[column]) for column in columns]) + "\n"
        
        return o

    @task()
    # @task(task_id=f"{config["name"]}_load")
    def load(o, target_file):
        # target_file = config["target_file"]
        with open(target_file, 'a') as f:
            f.write(o)

    for config in configs:
        e = extract.override(task_id=f"{config["name"]}_extract")(config["source_path"])
        t = transform.override(task_id=f"{config["name"]}_transform")(e, config["columns"])
        l = load.override(task_id=f"{config["name"]}_load")(t, config["target_file"])

        l