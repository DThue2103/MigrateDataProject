from pyspark.sql import SparkSession

from pyspark.sql.functions import col
from pyspark.sql.types import *

from MigrateDataProject.config.spark_config import SparkConnect
from MigrateDataProject.config.database_config import get_spark_config
from MigrateDataProject.src.spark.spark_write_data import SparkWriteDatabase
def main():
    jars = [
        "mysql:mysql-connector-java:8.0.33"
    ]

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
    df = spark_connect.spark.read.schema(schema).json(r"D:\PythonProject\MigrateDataProject\Data\2015-03-01-17.json")

    df_write_table = df.select(
        col("repo.id").alias("repositories_id"),
        col("repo.name").alias("name"),
        col("repo.url").alias("url")
    )
    # df_write_table.show()

    spark_configs = get_spark_config()
    df_write = SparkWriteDatabase(spark_connect.spark, spark_configs)
    df_write.spark_write_mysql(df_write_table, spark_configs["mysql"]["table"], spark_configs["mysql"]["jdbc_url"], spark_configs["mysql"]["config"])
if __name__ == '__main__':
    main()
