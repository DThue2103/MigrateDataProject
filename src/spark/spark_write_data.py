from pyspark.sql import SparkSession, DataFrame
from typing import Dict

class SparkWriteDatabase:
    def __init__(self, spark : SparkSession, db_config : Dict):
        self.spark = spark
        self.db_config = db_config

    def spark_write_mysql(self, df : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode: str="append"):
        df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", table_name) \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode(mode) \
            .save()
        print(f"------spark write data to mysql table: {table_name} sucessfully------")

    def spark_write_mongodb(self, df : DataFrame, uri : str, database : str, collection : str, mode : str="append"):
        df.write \
            .format("mongo") \
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .mode(mode) \
            .save()
        print(f"------spark write data to mongodb collection: {collection} sucessfully----------")

    def spark_write_all_database(self, df : DataFrame, mode : str="append"):
        self.spark_write_mysql(df, self.db_config["mysql"]["table"], self.db_config["mysql"]["jdbc_url"], self.db_config["mysql"]["config"])
        self.spark_write_mongodb(df, self.db_config["mongodb"]["uri"], self.db_config["mongodb"]["database"], self.db_config["mongodb"]["collection"])
        print(f"----------spark write data to mysql, mongodb sucessfully--------")