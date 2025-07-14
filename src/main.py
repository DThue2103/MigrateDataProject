from MySQLdb import connect
from bson import Int64

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import MySQLConfig, get_database_config
from MigrateDataProject.databases.schema_manager import create_mysql_schema, validate_mysql_schema, create_mongodb_schema, validate_mongodb_schema
from MigrateDataProject.config.database_config import MongoDBConfig
from MigrateDataProject.databases.mongodb_connect import MongoDBConnect
from MigrateDataProject.src.kafka.built_trigger import built_mysql_trigger


def main(config):
    #MYSQL
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user, config["mysql"].password) as mysql_client:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        tables_name = create_mysql_schema(connection, cursor)
        # print(tables_name)
        connection.commit()
        cursor.execute("INSERT INTO repositories(repositories_id, name, url) VALUES (%s, %s, %s)",
                       (1, "abc", "https://bfhfh.com"))
        connection.commit()
        print("-------Inserted data to MySQL------")
        validate_mysql_schema(tables_name,connection, cursor)
    # #TH có primary key
    # with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user, config["mysql"].password) as mysql_client:
    #     #create table
    #     connection, cursor = mysql_client.connection, mysql_client.cursor
    #     database = get_database_config()["mysql"].database
    #     connection.database = database
    #     cursor.execute("DROP TABLE IF EXISTS spark_table_temp;")
    #     cursor.execute(f"CREATE TABLE IF NOT EXISTS spark_table_temp (repositories_id BIGINT ,name VARCHAR(255) ,url VARCHAR(255));")
    #     connection.commit()
    #     print("-----create table spark_table_temp to mysql------")
    #
    #     #validate table
    #     cursor.execute("SHOW TABLES")
    #     tables = []
    #     row = cursor.fetchone()
    #     while row:
    #         tables.append(row[0])
    #         row = cursor.fetchone()
    #
    #     if "spark_table_temp" not in tables:
    #         raise ValueError(f"-----table doesn't exist------")
    #     print("-------validated table successfully----")
    #
    # #MONGODB
    # with MongoDBConnect(config["mongodb"].uri, config["mongodb"].db_name) as mongodb_client:
    #     create_mongodb_schema(mongodb_client.connect())
    #     mongodb_client.db.repositories.insert_one({
    #         "repositories_id": Int64(1),
    #         "name": "Hue",
    #         "url": "https://125jjvh.com"
    #     })
    #     print("-----insert one document to mongodb----")
    #     validate_mongodb_schema(mongodb_client.connect())
if __name__ == '__main__':
    config = get_database_config()
    # print(config)
    main(config)