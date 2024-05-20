import logging
import requests
import csv
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator


default_args = {
    "email": ["your_email@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

def extract_products_from_api():
    url = "https://dummyjson.com/carts"
    response = requests.get(url)
    data = response.json()
    return data["carts"]

def extract_products_and_write_to_csv():
    carts = extract_products_from_api()
    fieldnames = ["cartID", "productID", "title", "price", "quantity", "total", "discountPercentage", "discountedPrice", "thumbnail"]
    with open("/opt/airflow/dags/playground/target/dummyjson/products.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cart in carts:
            cart_id = cart["id"]
            products = cart["products"]
            for product in products:
                writer.writerow({
                    "cartID": cart_id,
                    "productID": product["id"],
                    "title": product["title"],
                    "price": product["price"],
                    "quantity": product["quantity"],
                    "total": product["total"],
                    "discountPercentage": product["discountPercentage"],
                    "discountedPrice": product["discountedPrice"],
                    "thumbnail": product["thumbnail"]
                })
    logging.info("Products extracted and written to CSV successfully.")

def upload_to_gcs():
    task = LocalFilesystemToGCSOperator(
        task_id="upload_to_gcs",
        src="/opt/airflow/dags/playground/target/dummyjson/products.csv",
        dst="products.csv",
        bucket="weekly-assignment-6",
        gcp_conn_id="airflowGCP",
    )
    return task.execute(context=None)

def gcs_to_bigquery():
    return GCSToBigQueryOperator(
        task_id="load_to_bigquery",
        bucket="weekly-assignment-6",
        source_objects=["products.csv"],
        destination_project_dataset_table="iconic-indexer-418610.weekly_assignment_6.products",
        schema_fields=[
            {"name": "cartID", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "productID", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "title", "type": "STRING", "mode": "NULLABLE"},
            {"name": "price", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "quantity", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "total", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "discountPercentage", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "discountedPrice", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "thumbnail", "type": "STRING", "mode": "NULLABLE"},
        ],
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=1,
        source_format="CSV",
        field_delimiter=",",
        gcp_conn_id="airflowGCP"
    )

with DAG(
    dag_id="extract_products_from_api",
    start_date=datetime(2024, 5, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    extract_and_write_task = PythonOperator(
        task_id="extract_and_write_to_csv",
        python_callable=extract_products_and_write_to_csv,
    )

    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
    )

    load_to_bigquery_task = gcs_to_bigquery()

    extract_and_write_task >> upload_to_gcs_task >> load_to_bigquery_task
