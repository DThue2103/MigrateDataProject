from pathlib import Path
from mysql.connector.errors import Error
from MigrateDataProject.databases.mysql_connect import MySQLConnect

SQL_FILE_PATH = Path("/home/huedt/Documents/PythonProjects/MigrateDataProject/sql/trigger.sql")
from MigrateDataProject.config.database_config import get_database_config
def built_mysql_trigger(connection, cursor):
    database = get_database_config()["mysql"].database
    table_name = get_database_config()["mysql"].table
    connection.database = database
    try:
        with open(SQL_FILE_PATH, "r") as file:
            sql_script = file.read().strip()
            # cursor.execute(sql_script)
            # print(f"-----Created MYSQL trigger for {table_name}-----")
            sql_commands = [cmd for cmd in sql_script.split("//")]
            for cmd in sql_commands:
                # print(cmd)
                cursor.execute(cmd)
                print(f"----executed mysql command----")
            connection.commit()
            print(f"-----Created MYSQL trigger for {table_name} successfully-----")
    except Error as e:
        connection.rollback()
        raise Exception(f"----Failed to create trigger----")

def main(config):
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user,
                      config["mysql"].password) as mysql_client:
        connection, cursor = mysql_client.connection, mysql_client.cursor
        built_mysql_trigger(connection, cursor)

if __name__ == '__main__':
    config = get_database_config()
    # print(config)
    main(config)
