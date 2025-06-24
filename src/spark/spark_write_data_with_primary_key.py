from typing import Dict

from pyspark.sql import DataFrame, SparkSession

from MigrateDataProject.config.database_config import get_database_config
from MigrateDataProject.databases.mysql_connect import MySQLConnect


class SparkWriteDatabase:
    def __init__(self, spark : SparkSession, db_config : Dict):
        self.spark = spark
        self.db_config = db_config

    def spark_write_mysql(self, df : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode : str = "append"):
        df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", table_name) \
            .option("user", config["user"]) \
            .option("password", config["password"]) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .mode(mode) \
            .save()

        print(f"-----spark write data to mysql table: {table_name} successfully-------")

    def validate_spark_write(self, df_write : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode : str = "append"):
        try:
            df_read = self.spark.read \
                .format("jdbc") \
                .option("url", jdbc_url) \
                .option("dbtable", table_name) \
                .option("user", config["user"]) \
                .option("password", config["password"]) \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .load()
            # df_read.show()
            df_temp = df_write.exceptAll(df_read)
            # print(df_temp.count())
            if df_temp.count() != 0:
                df_temp.write \
                    .format("jdbc") \
                    .option("url", jdbc_url) \
                    .option("dbtable", table_name) \
                    .option("user", config["user"]) \
                    .option("password", config["password"]) \
                    .option("driver", "com.mysql.cj.jdbc.Driver") \
                    .mode(mode) \
                    .save()
            print(f"-------validate spark write data to mysql table {table_name} successfully------")
        except Exception as e:
            raise Exception(f"----failed to write missing record to spark_table_temp in mysql----")

    def insert_data_mysql(self, table_name : str, jdbc_url : str, config : Dict):
        try:
            with MySQLConnect(config["host"], config["port"], config["user"],
                          config["password"]) as mysql_client:
                connection, cursor = mysql_client.connection, mysql_client.cursor
                database = get_database_config()["mysql"].database
                connection.database = database
                cursor.execute("SELECT a. * FROM spark_table_temp a LEFT JOIN repositories b ON a.repositories_id = b.repositories_id WHERE b.repositories_id IS NULL;")
                records = []
                row = cursor.fetchone()
                # print(row)
                while row:
                    records.append(row)
                    row = cursor.fetchone()

                # print(records)
                values = ""
                for rec in records:
                    values += f"({rec[0]}, '{rec[1]}', '{rec[2]}'),"
                values = values.rstrip(',')
                # print(values)
                cursor.execute(f"INSERT INTO repositories (repositories_id, name, url) VALUES {values};")
                connection.commit()
            print("-----insert data into mysql successfully-----")

        except Exception as e:
            raise Exception(f"-----failed to connect to mysql: {e}------")