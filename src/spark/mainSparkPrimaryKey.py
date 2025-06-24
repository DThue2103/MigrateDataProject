from pyspark.sql.functions import col
from pyspark.sql.types import *

from MigrateDataProject.config.database_config import get_spark_config
from MigrateDataProject.config.spark_config import SparkConnect
from MigrateDataProject.src.spark.spark_write_data_with_primary_key import SparkWriteDatabase


def main():
    jars = [
        "mysql:mysql-connector-java:8.0.33"
    ]

    #create spark context
    spark_connect = SparkConnect(
        app_name="DE-103",
        master_url="local[*]",
        executor_memory="2g",
        executor_cores=1,
        driver_memory="2g",
        jar_packages=jars,
        log_level="INFO"
    )

    #create schema
    schema = StructType([
        StructField("id", LongType(), True),
        StructField("name", StringType(), True),
        StructField("url", StringType(), True)
    ])
    #create df
    df = spark_connect.spark.read.schema(schema).json(r"/home/huedt/Documents/PythonProjects/MigrateDataProject/Data/test_primary_key.json")
    # df.show()
    df_write_table = df.select(
        col("id").alias("repositories_id"),
        col("name"),
        col("url")
    )
    # df_write_table.show()
    spark_configs = get_spark_config()
    df_write = SparkWriteDatabase(spark_connect.spark, spark_configs)
    df_write.spark_write_mysql(df_write_table, "spark_table_temp", spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
    df_write.validate_spark_write(df_write_table,"spark_table_temp", spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
    df_write.insert_data_mysql("spark_table_temp", spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])

if __name__ == '__main__':
    main()