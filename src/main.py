from MySQLdb import connect
from bson import Int64

from MigrateDataProject.databases.mysql_connect import MySQLConnect
from MigrateDataProject.config.database_config import MySQLConfig, get_database_config
from MigrateDataProject.databases.schema_manager import create_mysql_schema, validate_mysql_schema, create_mongodb_schema, validate_mongodb_schema
from MigrateDataProject.config.database_config import MongoDBConfig
from MigrateDataProject.databases.mongodb_connect import MongoDBConnect
def main(config):
    #MYSQL
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user, config["mysql"].password) as mysql_client:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        tables_name = create_mysql_schema(connection, cursor)
        connection.commit()
        cursor.execute("INSERT INTO repositories(repositories_id, name, url) VALUES (%s, %s, %s)",
                       (1, "abc", "https://bfhfh.com"))
        connection.commit()
        print("-------Inserted data to MySQL------")
        validate_mysql_schema(tables_name,connection, cursor)

    #MONGODB
    with MongoDBConnect(config["mongodb"].uri, config["mongodb"].db_name) as mongodb_client:
        create_mongodb_schema(mongodb_client.connect())
        mongodb_client.db.repositories.insert_one({
            "repositories_id": Int64(1),
            "name": "Hue",
            "url": "https://125jjvh.com"
        })
        print("-----insert one document to mongodb----")
        validate_mongodb_schema(mongodb_client.connect())
if __name__ == '__main__':
    config = get_database_config()
    # print(config)
    main(config)