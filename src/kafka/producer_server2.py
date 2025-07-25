import json

from kafka import KafkaProducer
from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config
#truy vấn message

def get_data_trigger(mysql_client, last_log_id):
    connection, cursor = mysql_client.connection, mysql_client.cursor
    database = "github_data"
    connection.database = database

    query = ("SELECT repositories_id, name, url, log_id, stage, "
             " DATE_FORMAT(log_timestamp, '%Y-%m-%d %H:%i%s.%f') AS log_timestamp1"
             " FROM repository_log_before")

    if last_log_id:
        query += f" WHERE log_id > '{last_log_id}'"
        cursor.execute(query)
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    connection.commit()

    schema = ["repositories_id", "name", "url", "log_id", "stage", "log_timestamp"]
    data = [dict(zip(schema, row)) for row in rows]
    max_log_id = max((row["log_id"] for row in data), default=last_log_id) if data else last_log_id

    return data, max_log_id


def main():
    last_log_id = None
    config = get_database_config()
    while True:
        with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user,
                          config["mysql"].password) as mysql_client:

            producer = KafkaProducer(bootstrap_servers="localhost:9092"
                                     , value_serializer=lambda x: json.dumps(x).encode('utf-8')
                                     )
            while True:
                data, max_log_id = get_data_trigger(mysql_client, last_log_id)
                last_log_id = max_log_id
                print(f"----------last_log_id = {last_log_id}------------")
                for record in data:
                    producer.send("DE-ETL103", record)
                producer.flush()



if __name__ == "__main__":
    main()



