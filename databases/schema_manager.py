#mục tiêu của schema_manager: tạo schema và validate schema cho database

from pathlib import Path
from mysql.connector.errors import Error
SQL_FILE_PATH = Path("../sql/schema.sql")

#tạo schema
"""
cách để python tạo schema:
    b1: kết nối với mysql (connection)
    b2: thực thi câu lệnh trong file schema.sql (thông qua cursor)
"""
def create_mysql_schema(connection, cursor):
    database = "github_data" #databse name
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")   #drop db nếu đã tồn tại
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")  #tạo database
    connection.commit()
    print(f"--------create {database} successfully-------")
    connection.database = database  #kết nối vào database github_data

    try:
        with open(SQL_FILE_PATH, "r") as file:
            sql_script = file.read()
            sql_commands = [cmd.strip() for cmd in sql_script.split(";")]
            # sql_commands =[]
            # for cmd in sql_script.strip().split(";"):
            #     if cmd.strip():
            #         sql_commands.append(cmd)

            for cmd in sql_commands:
                cursor.execute(cmd)
                print(f"------Excuted mysql commands------")
            connection.commit()
            print("-------Created MySQL schema-------")

    except Error as e:
        connection.rollback()
        raise Exception(f"-----Failed to create MySQL schema: {e}---") from e