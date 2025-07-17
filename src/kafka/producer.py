import json

from kafka import KafkaProducer
from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config
#truy vấn message

def get_log_timestamp(mysql_client, last_log_timestamp):
    connection, cursor = mysql_client.connection, mysql_client.cursor
    database = "github_data"
    connection.database = database
    query = ("SELECT repositories_id, name, url, stage, "
             " DATE_FORMAT(log_timestamp, '%Y-%m-%d %H:%i:%s.%f') AS log_timestamp1"
             " FROM repository_log_after")

    if last_log_timestamp:
        query += f" WHERE DATE_FORMAT(log_timestamp, '%Y-%m-%d %H:%i:%s.%f') > '{last_log_timestamp}'"
        cursor.execute(query)

    else:
        cursor.execute(query)

    messages = cursor.fetchall()
    connection.commit()

    if messages:
        last_log_timestamp = messages[-1][4]

    return messages, last_log_timestamp

def main():
    config = get_database_config()
    last_log_timestamp = None
    while True:
        with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user,
                          config["mysql"].password) as mysql_client:
            producer = KafkaProducer(bootstrap_servers="localhost:9092",
                                     value_serializer=lambda x: json.dumps(x).encode("utf-8"))
            while True:
                messages, log_timestamp = get_log_timestamp(mysql_client, last_log_timestamp)
                last_log_timestamp = log_timestamp
                print(f"----------last_timestamp = {last_log_timestamp}------------")

                for message in messages:
                    producer.send("DE-ETL103", message)
                    print(message)
                    producer.flush()
            # print(data)
            # connection.commit()

if __name__ == '__main__':
    main()


