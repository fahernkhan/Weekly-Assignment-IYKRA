data = {
    "id":1,
    "name": "Fariz Wakan",
    "start_date": "2020-01-01"
}

columns = ["id", "name","start_date"]
print([str(data[column]) for column in columns])
print(",".join([str(data[column]) for column in columns]))