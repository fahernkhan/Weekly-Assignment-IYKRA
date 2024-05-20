import os
import json
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

with open("/opt/airflow/dags/playground/configs.json", "r") as f:
    dag_configs = json.load(f)

for dag_config in dag_configs:
    dag_id = dag_config["dag_id"]
    # start_date = dag_config["start_date"]
    start_date = datetime.strptime(dag_config["start_date"], '%Y-%m-%d')
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