from sqlalchemy.engine import connection_memoize
from MigrateDataProject.config.database_config import get_database_config
from MigrateDataProject.databases.mysql_connect import MySQLConnect


def main(config):
    with MySQLConnect(config["mysql"].host, config["mysql"].port, config["mysql"].user, config["mysql"].password) as mysql_client:
        #create table
        connection, cursor = mysql_client.connection, mysql_client.cursor
        database = get_database_config()["mysql"].database
        connection.database = database
        cursor.execute("DROP TABLE IF EXISTS spark_table_temp;")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS spark_table_temp (repositories_id BIGINT ,name VARCHAR(255) ,url VARCHAR(255), PRIMARY KEY (repositories_id));")
        connection.commit()
        print("-----create table spark_table_temp to mysql------")

        #validate table
        cursor.execute("SHOW TABLES")
        tables = []
        row = cursor.fetchone()
        while row:
            tables.append(row[0])
            row = cursor.fetchone()

        if "spark_table_temp" not in tables:
            raise ValueError(f"-----table doesn't exist------")
        print("-------validated table successfully----")

if __name__ == '__main__':
    config = get_database_config()
    # print(config)
    main(config)
