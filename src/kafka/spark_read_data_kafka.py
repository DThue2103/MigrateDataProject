from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

from MigrateDataProject.config.database_config import get_database_config
from MigrateDataProject.databases.mysql_connect import MySQLConnect
import builtins

import pandas as pd
def read_data_trigger(mysql_client, last_log_id):
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
    max_log_id = builtins.max((row["log_id"] for row in data), default=last_log_id) if data else last_log_id
    df = pd.DataFrame(data)
    print(df)
    return df, max_log_id

last_log_id = None

def validate_and_compare(batch_df, batch_id):
    global last_log_id
    config = get_database_config()
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user,
                      config["mysql"].password) as mysql_client:
        data, max_log_id = read_data_trigger(mysql_client, last_log_id)
        last_log_id = max_log_id

    # Convert Pandas DataFrame `data` thành Spark DataFrame
    spark = SparkSession.builder.getOrCreate()

    spark_schema = StructType([
        StructField("repositories_id", IntegerType(), nullable=True),
        StructField("name", StringType(), nullable=True),
        StructField("url", StringType(), nullable=True),
        StructField("log_id", IntegerType(), nullable=True),
        StructField("stage", StringType(), nullable=True),
        StructField("log_timestamp", StringType(), nullable=True)
    ])

    mysql_df = spark.createDataFrame(data, schema=spark_schema)

    # So sánh batch dữ liệu Kafka với MySQL batch
    df_diff = batch_df.exceptAll(mysql_df)
    batch_df.show()
    if df_diff.count() != 0:
        print("----Dữ liệu thiếu hoặc sai khác------")
        df_diff.show()
    else:
        print("------Dữ liệu Kafka đồng bộ với MySQL----")

def main():
    spark = SparkSession.builder \
        .appName("DE-ETL103") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.5.0") \
        .getOrCreate()

    schema = StructType([
        StructField("repositories_id", IntegerType(), nullable=True),
        StructField("name", StringType(), nullable=True),
        StructField("url", StringType(), nullable=True),
        StructField("log_id", IntegerType(), nullable=True),
        StructField("stage", StringType(), nullable=True),
        StructField("log_timestamp", StringType(), nullable=True)
    ])

    kafka_df = spark.readStream \
        .format("Kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("startingOffsets", "earliest") \
        .option("subscribe", "DE-ETL103") \
        .load()

    df_property = kafka_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    df_property.writeStream \
        .foreachBatch(validate_and_compare) \
        .option("checkpointLocation", "/tmp/checkpoint/etl103") \
        .outputMode("append") \
        .start() \
        .awaitTermination()

if __name__ == '__main__':
    main()