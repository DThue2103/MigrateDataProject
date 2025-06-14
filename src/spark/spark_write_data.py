from pyspark.sql import SparkSession, DataFrame
from typing import Dict

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config



class SparkWriteDatabase:
    def __init__(self, spark : SparkSession, db_config : Dict):
        self.spark = spark
        self.db_config = db_config

    def spark_write_mysql(self, df : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode : str="append"):
        # python cursor add column spark_temp into mysql
        try:
            with MySQLConnect(config["host"], config["port"], config["user"],
                              config["password"]) as mysql_client:
                connection, cursor = mysql_client.connection, mysql_client.cursor
                database = get_database_config()["mysql"].database
                connection.database = database
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN spark_temp VARCHAR(255);")
                connection.commit()
                print("----- add column spark_temp to mysql--------")
                mysql_client.close()
        except Exception as e:
            raise Exception(f"-----failed to connect to mysql: {e}------")

        # spark write dataframe to mysql
        df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", table_name) \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode(mode) \
            .save()

        print(f"------spark write data to mysql table: {table_name} successfully------")

    def validate_spark_mysql(self, table_name : str, jdbc_url : str, config : Dict):
        df_read = self.spark.read \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", f"(SELECT * FROM {table_name} WHERE spark_temp = 'spark_write') AS spark_temp") \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .load()
        df_read.show()
        print(f"-------spark load data from mysql table: {table_name} successfully!!!!!!!")

    def spark_write_mongodb(self, df : DataFrame, uri : str, database : str, collection : str, mode : str="append"):
        df.write \
            .format("mongo") \
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .mode(mode) \
            .save()
        print(f"------spark write data to mongodb collection: {collection} successfully----------")

    def spark_write_all_database(self, df : DataFrame, mode : str="append"):
        self.spark_write_mysql(df, self.db_config["mysql"]["table"], self.db_config["mysql"]["jdbc_url"], self.db_config["mysql"]["config"])
        self.spark_write_mongodb(df, self.db_config["mongodb"]["uri"], self.db_config["mongodb"]["database"], self.db_config["mongodb"]["collection"])
        print(f"----------spark write data to mysql, mongodb successfully--------")