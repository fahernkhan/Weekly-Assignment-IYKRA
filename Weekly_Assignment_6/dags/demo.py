import logging

from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'Farhurrahman Hernanda',
    'email': ['me@me.com'],
    'email_on_failure': True,
    'retries': 2,
    'email_on_retry': False,
    'retry_delay': timedelta(seconds=5)
}

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="demo", start_date=datetime(2024, 5, 1), schedule="0 0 * * *",default_args=default_args) as dag:
    # Tasks are represented as operators
    hello = BashOperator(task_id="hello", bash_command="echo hello")

    @task()
    def airflow():
        logger = logging.getLogger(__name__)
        
        print("airflow")
        print("TEST")
        logger.info("TEST")
        logger.info("Here is some standard text.")
        logger.info("::group::Non important details")
        logger.info("bla")
        logger.info("debug messages...")
        logger.info("::endgroup::")
        logger.info("Here is again some standard text.")

    # Set dependencies between tasks
    hello >> airflow()