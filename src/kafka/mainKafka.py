from datetime import datetime

import pymysql
import json
from kafka import KafkaProducer
import time

from MigrateDataProject.config.database_config import get_database_config
from MigrateDataProject.databases.mysql_connect import MySQLConnect

def main(config):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    last_log_time = datetime(2024, 1, 1, 12, 0, 0)
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user, config["mysql"].password) as mysql_client:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        database = get_database_config()["mysql"].database
        connection.database = database
        while True:
            query = """
                SELECT *
                FROM repository_log_before
                WHERE log_timestamp > %s
                ORDER BY log_timestamp ASC
            """
            cursor.execute(query, (last_log_time,))
            rows = cursor.fetchall()

            for row in rows:
                log_entry = {
                    "repositories_id": row[0],
                    "name": row[1],
                    "url": row[2],
                    "stage": row[3],
                    "log_timestamp": row[4].isoformat()
                }
                producer.send("repo-change-log", log_entry)
                print(f"----Sent to Kafka: {log_entry}------")

                # Cập nhật last_log_time sau mỗi bản ghi
                last_log_time = row[4]

            time.sleep(1)

if __name__ == '__main__':
    config = get_database_config()
    # print(config)
    main(config)