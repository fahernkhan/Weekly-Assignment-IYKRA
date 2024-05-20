import os
import json
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="students", start_date=datetime(2024, 5, 7), schedule="*/2 * * * *", catchup=False) as dag:

    @task()
    def extract():
        source_path = "/opt/airflow/dags/playground/source"
        target_file = "/opt/airflow/dags/playground/target/students.csv"

        data = []

        filenames = os.listdir(source_path)
        for filename in filenames:
            with open(f"{source_path}/{filename}", 'r') as f:
            #     data = json.load(f)
                data.append(json.load(f))
        return data

            # with open(target_file, 'a') as f:
            #     f.write(f"{data['id']},{data['name']}\n")

    @task()
    def transform(data):
        o = ""
        for a in data:
            o += f"{a['id']},{a['name']}\n"
        
        return o

    @task()
    def load(o):
        target_file = "/opt/airflow/dags/playground/target/students.csv"
        with open(target_file, 'a') as f:
            f.write(o)

    e = extract()
    t = transform(e)
    load(t)