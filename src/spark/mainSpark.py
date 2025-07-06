from pyspark.sql import SparkSession

from pyspark.sql.functions import col, lit
from pyspark.sql.types import *

from MigrateDataProject.config.spark_config import SparkConnect
from MigrateDataProject.config.database_config import get_spark_config
from MigrateDataProject.src.spark.spark_write_data import SparkWriteDatabase

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config
from MigrateDataProject.databases.mongodb_connect import MongoDBConnect


def main():
    jars = [
        "mysql:mysql-connector-java:8.0.33",
        "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1"
    ]
    #create spark context
    spark_connect = SparkConnect(
        app_name="DE-103",
        master_url="local[*]",
        executor_memory="4g",
        executor_cores=2,
        driver_memory="4g",
        num_executor=2,
        jar_packages = jars,
        log_level="INFO"
    )

    #create schema
    schema = StructType([
        StructField("actor", StructType([
            StructField("id", LongType(), True),
            StructField("login", StringType(), True),
            StructField("gravatar_id", LongType(), True),
            StructField("url", StringType(), True),
            StructField("avatar_url", StringType(), True)]
        ), True),
        StructField("repo", StructType([
            StructField("id", LongType(), True),
            StructField("name", StringType(), True),
            StructField("url", StringType(), True)
        ]), True)
    ])

    #create df
    df = spark_connect.spark.read.schema(schema).json(r"/home/huedt/Documents/PythonProjects/MigrateDataProject/Data/2015-03-01-17.json")

    # df_write_table = df.select(
    #     col("repo.id").alias("repositories_id"),
    #     col("repo.name").alias("name"),
    #     col("repo.url").alias("url")
    # )

    df_write_table = df.withColumn("spark_temp", lit("spark_write")).select(
        col("repo.id").alias("repositories_id"),
        col("repo.name").alias("name"),
        col("repo.url").alias("url"),
        col("spark_temp").alias("spark_temp")
    )

    # df_write_table.show()

    spark_configs = get_spark_config()
    # print(spark_configs)
    df_write = SparkWriteDatabase(spark_connect.spark, spark_configs)

    #write data to database
    # df_write.spark_write_mysql(df_write_table, spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
    # df_write.spark_write_mongodb(df_write_table, spark_configs["mongodb"]["uri"], spark_configs["mongodb"]["database"], spark_configs["mongodb"]["collection"])
    df_write.spark_write_all_database(df_write_table)
    # df_write_table.show()

    # #delete db to check
    # with MySQLConnect(spark_configs["mysql"]["config"]["host"], spark_configs["mysql"]["config"]["port"], spark_configs["mysql"]["config"]["user"],
    #                   spark_configs["mysql"]["config"]["password"]) as mysql_client:
    #     connection, cursor = mysql_client.connection, mysql_client.cursor
    #     database = get_database_config()["mysql"].database
    #     connection.database = database
    #     table_name = spark_configs["mysql"]["table"]
    #     cursor.execute(f"DELETE FROM {table_name} WHERE spark_temp = 'spark_write' LIMIT 600")
    #     connection.commit()
    #     print("------delete records to check validate spark write data--------")
    #     mysql_client.close()

    #validate spark write data into mysql
    # df_write.validate_spark_mysql(df_write_table, spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])

    """
    TH có primary key và trong mysql đã có data:
    1. tạo table spark_table_temp trong mysql, validate table
    2. ghi, validate data vào spark_table_temp 
    3. Join 2 bảng spark_table_temp và repositories để tìm ra những bản ghi chưa có trong bảng repositories
    4. insert các bản ghi đó vào bảng repositories
    5. delete bảng spark_table_temp
    """
    #
    # df_write.spark_write_mysql_primary_key(df_write_table, "spark_table_temp", spark_configs["mysql"]["jdbc_url"],
    #                            spark_configs["mysql"]["config"])
    # df_write.validate_spark_write_primary_key(df_write_table, "spark_table_temp", spark_configs["mysql"]["jdbc_url"],
    #                               spark_configs["mysql"]["config"])
    # df_write.insert_data_mysql_primary_key(spark_configs["mysql"]["config"])
    #
    # # validate spark write data into mongodb

    # #delete db to check
    # with MongoDBConnect(spark_configs["mongodb"]["uri"], spark_configs["mongodb"]["database"]) as mongodb_client:
    #     docs_to_delete = mongodb_client.db.repositories.find(
    #                 {"spark_temp": "spark_write"},
    #                 {"_id": 1}
    #             ).limit(600)
    #
    #     ids = [doc["_id"] for doc in docs_to_delete]
    #
    #     # Xoá chúng
    #     if ids:
    #         result = mongodb_client.db.repositories.delete_many({"_id": {"$in": ids}})
    #     print("-----delete records to check validate spark write data into mongodb--------")
    #
    # df_write.validate_spark_mongodb(df_write_table, spark_configs["mongodb"]["uri"], spark_configs["mongodb"]["database"], spark_configs["mongodb"]["collection"])
    df_write.spark_validate_all_database(df_write_table)
if __name__ == '__main__':
    main()
