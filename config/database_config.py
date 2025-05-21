
from dotenv import load_dotenv
import os
from dataclasses import dataclass

@dataclass
class MySQLConfig():
    host : str
    port : int
    user : str
    password : str

def get_database_config():
    load_dotenv()

    config = {
        "mysql" : MySQLConfig(
            host=os.getenv("MYSQL_HOST"),
            port = os.getenv("MYSQL_PORT"),
            user = os.getenv("MYSQL_USER"),
            password = os.getenv("MYSQL_PASSWORD")
        )
    }
    return config

if __name__ == '__main__':
    config = get_database_config()
    print(config)

