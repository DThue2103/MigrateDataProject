from pyspark.sql import SparkSession, DataFrame
from typing import Dict

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import get_database_config

from MigrateDataProject.databases.mongodb_connect import MongoDBConnect

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

    # def read_spark_mysql(self, table_name : str, jdbc_url : str, config : Dict):
    #     df_read = self.spark.read \
    #         .format("jdbc") \
    #         .option("url", jdbc_url) \
    #         .option("dbtable", f"(SELECT * FROM {table_name} WHERE spark_temp = 'spark_write') AS spark_temp") \
    #         .option("user", config["user"]) \
    #         .option("password", config["password"]) \
    #         .option("driver", "com.mysql.cj.jdbc.Driver") \
    #         .load()
    #     return df_read

    def validate_spark_mysql(self, df_write_table : DataFrame , table_name : str, jdbc_url : str, config : Dict, mode : str = "append"):
        try:
            df_read = self.spark.read \
                .format("jdbc") \
                .option("url", jdbc_url) \
                .option("dbtable", f"(SELECT * FROM {table_name} WHERE spark_temp = 'spark_write') AS spark_temp") \
                .option("user", config["user"]) \
                .option("password", config["password"]) \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .load()

            df_temp = df_write_table.exceptAll(df_read)
            # df_temp.show()
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
                print(f"------spark inserted missing data to mysql table: {table_name} successfully------")

            try:
                with MySQLConnect(config["host"], config["port"], config["user"],
                                  config["password"]) as mysql_client:
                    connection, cursor = mysql_client.connection, mysql_client.cursor
                    database = get_database_config()["mysql"].database
                    connection.database = database
                    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN spark_temp;")
                    connection.commit()
                    print("----- drop column spark_temp in mysql--------")
                    mysql_client.close()
            except Exception as e:
                raise Exception(f"-----failed to connect to mysql: {e}------")

            print(f"--------validate spark write data to mysql table {table_name} successfully-------")
        except Exception as e:
            raise Exception(f"-----Failed to write missing records to mysql: {e}---") from e

    def spark_write_mysql_primary_key(self, df : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode : str = "append"):
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

    def validate_spark_write_primary_key(self, df_write : DataFrame, table_name : str, jdbc_url : str, config : Dict, mode : str = "append"):
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

    def insert_data_mysql_primary_key(self, config : Dict):
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
                for rec in records:
                    try:
                        cursor.execute("INSERT INTO repositories (repositories_id, name, url) VALUES (%s, %s, %s)", rec)
                        connection.commit()
                        print(f"-----insert {rec} into mysql successfully-----")
                    except Exception as e:
                        print(f"Error inserting record {rec}: {str(e)}")
                        continue
            print("-----insert data into mysql successfully-----")

            with MySQLConnect(config["host"], config["port"], config["user"],
                              config["password"]) as mysql_client:
                connection, cursor = mysql_client.connection, mysql_client.cursor
                database = get_database_config()["mysql"].database
                connection.database = database
                cursor.execute("DROP TABLE spark_table_temp;")
                connection.commit()
                print("------drop table spark_table_temp successfully-----")

        except Exception as e:
            raise Exception(f"-----failed to connect to mysql: {e}------")

    def spark_write_mongodb(self, df : DataFrame, uri : str, database : str, collection : str, mode : str="append"):
        # try:
        #     with MongoDBConnect(uri, database) as mongodb_client:
        #         mongodb_client.db.repositories.update_many({}, {"$set": {"source": "spark_temp"}})
        #         print("-----insert spark_temp field into mongodb----")
        # except Exception as e:
        #     raise Exception(f"-----failed to connect to mongodb: {e}------")

        df.write \
            .format("mongo") \
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .mode(mode) \
            .save()
        print(f"------spark write data to mongodb collection: {collection} successfully----------")

    def validate_spark_mongodb(self, df_write : DataFrame, uri : str, database : str, collection : str, mode : str = "append"):
        try:
            df_read = self.spark.read \
                .format("mongo") \
                .option("uri", uri) \
                .option("database", database) \
                .option("collection", collection) \
                .option("pipeline", '[{ "$match": { "spark_temp": "spark_write" } }]') \
                .load()

            df_read = df_read.select("repositories_id", "name", "url", "spark_temp")
            # df_read.show()
            # df_write.show()

            df_temp = df_write.exceptAll(df_read)
            # df_temp.show()
            # print(df_temp.count())
            if df_temp.count() != 0:
                df_temp.write \
                    .format("mongo") \
                    .option("uri", uri) \
                    .option("database", database) \
                    .option("collection", collection) \
                    .mode(mode) \
                    .save()
                print(f"------spark inserted missing data to mongodb collection: {collection} successfully----------")

            try:
                with MongoDBConnect(uri, database) as mongodb_client:
                    mongodb_client.db.repositories.update_many({}, {"$unset": {"spark_temp": "spark_write"}})
            except Exception as e:
                raise Exception(f"-----failed to connect to mongodb: {e}------")

            print(f"--------validate spark write data to mongodb collection {collection} successfully-------")
        except Exception as e:
            raise Exception(f"-----Failed to write missing records to mongodb: {e}---") from e

    def spark_write_all_database(self, df: DataFrame, mode: str = "append"):
        self.spark_write_mysql(df, self.db_config["mysql"]["table"], self.db_config["mysql"]["jdbc_url"],
                               self.db_config["mysql"]["config"])
        self.spark_write_mongodb(df, self.db_config["mongodb"]["uri"], self.db_config["mongodb"]["database"],
                                 self.db_config["mongodb"]["collection"])
        print(f"----------spark write data to mysql, mongodb successfully--------")

    def spark_validate_all_database(self, df_write : DataFrame):
        self.validate_spark_mysql(df_write, self.db_config["mysql"]["table"], self.db_config["mysql"]["jdbc_url"], self.db_config["mysql"]["config"])
        self.validate_spark_mongodb(df_write, self.db_config["mongodb"]["uri"], self.db_config["mongodb"]["database"], self.db_config["mongodb"]["collection"])
        print(f"------spark validate data to mysql, mongodb successfully------")