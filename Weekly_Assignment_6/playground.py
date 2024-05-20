import os
import json

source_path = r"C:\Users\FHKHASAN\Downloads\Apache_Airflow\dags\playground\source"
target_file = r"C:\Users\FHKHASAN\Downloads\Apache_Airflow\dags\playground\target\students.csv"
filenames = os.listdir(source_path)
for filename in filenames:
    with open(f"{source_path}\{filename}", 'r') as f:
        data = json.load(f)

    with open(target_file, 'a') as f:
        f.write(f"{data['id']},{data['name']}\n")