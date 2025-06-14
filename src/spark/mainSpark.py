from pyspark.sql import SparkSession

from pyspark.sql.functions import col, lit
from pyspark.sql.types import *

from MigrateDataProject.config.spark_config import SparkConnect
from MigrateDataProject.config.database_config import get_spark_config
from MigrateDataProject.src.spark.spark_write_data import SparkWriteDatabase

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config


def main():
    jars = [
        "mysql:mysql-connector-java:8.0.33",
        "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1"
    ]
    #create spark context
    spark_connect = SparkConnect(
        app_name="DE-103",
        master_url="local[*]",
        executor_memory="2g",
        executor_cores=1,
        driver_memory="2g",
        num_executor=1,
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
    df = spark_connect.spark.read.schema(schema).json(r"D:\PythonProject\MigrateDataProject\Data\2015-03-01-17.json")

    df_write_table = df.withColumn("spark_temp", lit("spark_write")).select(
        col("repo.id").alias("repositories_id"),
        col("repo.name").alias("name"),
        col("repo.url").alias("url"),
        col("spark_temp").alias("spark_temp")
    )
    # df_write_table.show()

    spark_configs = get_spark_config()
    df_write = SparkWriteDatabase(spark_connect.spark, spark_configs)

    #write data to database
    # df_write.spark_write_mysql(df_write_table, spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
    # df_write.spark_write_mongodb(df_write_table, spark_configs["mongodb"]["uri"], spark_configs["mongodb"]["database"], spark_configs["mongodb"]["collection"])
    df_write.spark_write_all_database(df_write_table)
    # df_write_table.show()

    #validate data from database
    df_read = df_write.validate_spark_mysql(spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
    # df_read.show()

    #delete db to check
    with MySQLConnect(spark_configs["mysql"]["config"]["host"], spark_configs["mysql"]["config"]["port"], spark_configs["mysql"]["config"]["user"],
                      spark_configs["mysql"]["config"]["password"]) as mysql_client:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        database = get_database_config()["mysql"].database
        connection.database = database
        table_name = spark_configs["mysql"]["table"]
        cursor.execute(f"DELETE FROM {table_name} WHERE repositories_id = 31502849")
        connection.commit()
        print("------delete 1 record to check validate spark write data--------")
        mysql_client.close()


    #validate spark write mysql
    df_temp = df_write_table.subtract(df_read)
    df_temp.show()
    while df_temp.count() != 0:
        df_write.spark_write_mysql(df_temp, spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
        df_read = df_write.validate_spark_mysql(spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
        df_temp = df_write_table.subtract(df_read)
        df_temp.show()
    print(f"--------validate spark write data to mysql table {spark_configs['mysql']['table']} successfully-------")

if __name__ == '__main__':
    main()
