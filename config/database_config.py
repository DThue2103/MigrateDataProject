
from dotenv import load_dotenv
import os
from dataclasses import dataclass

@dataclass
class MySQLConfig():
    host : str
    port : int
    user : str
    password : str
    database : str
    table : str = "repositories"

@dataclass
class MongoDBConfig():
    uri: str
    db_name: str
    collection : str = "repositories"

def get_database_config():
    load_dotenv()

    config = {
        "mysql" : MySQLConfig(
            host=os.getenv("MYSQL_HOST"),
            port = os.getenv("MYSQL_PORT"),
            user = os.getenv("MYSQL_USER"),
            password = os.getenv("MYSQL_PASSWORD"),
            database = os.getenv("MYSQL_DATABASE")
        ),
        "mongodb": MongoDBConfig(
            uri = os.getenv("MONGO_URI"),
            db_name = os.getenv("MONGO_DB_NAME")
        )
    }
    return config

def get_spark_config():
    db_configs = get_database_config()
    return {
        "mysql" : {
            "table" : db_configs["mysql"].table,
            "jdbc_url" : "jdbc:mysql://{}:{}/{}".format(db_configs["mysql"].host, db_configs["mysql"].port, db_configs["mysql"].database),
            "config" : {
                "host" : db_configs["mysql"].host,
                "port" : db_configs["mysql"].port,
                "user" : db_configs["mysql"].user,
                "password" : db_configs["mysql"].password,
                "database" : db_configs["mysql"].database
            }
        },
        "mongodb" : {
            "uri" : db_configs["mongodb"].uri,
            "database" : db_configs["mongodb"].db_name,
            "collection": db_configs["mongodb"].collection
        },
        "redis" : {}

    }


if __name__ == '__main__':
    # config = get_database_config()
    config = get_spark_config()
    print(config)

