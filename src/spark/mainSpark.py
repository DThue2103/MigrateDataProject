from MigrateDataProject.config.spark_config import SparkConnect
from pyspark.sql import SparkSession
def main():
    spark_connect = SparkConnect(
        app_name="DE-103",
        master_url="local[*]",
        executor_memory="2g",
        executor_cores=1,
        driver_memory="2g",
        num_executor=1,
        log_level="INFO"
    )

    data = [["jack", 28],
            ["virus", 32],
            ["heu", 18]]

    df = spark_connect.spark.createDataFrame(data, ["name", "age"])
    df.show()

if __name__ == '__main__':
    main()
