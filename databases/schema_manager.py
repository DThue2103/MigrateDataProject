#mục tiêu của schema_manager: tạo schema và validate schema cho database
import re
from msilib.schema import tables
from operator import index
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
            # sql_commands = [cmd.strip() for cmd in sql_script.split(";") if cmd.strip()]
            sql_commands =[]
            for cmd in sql_script.strip().split(";"):
                if cmd.strip():
                    sql_commands.append(cmd)

            for cmd in sql_commands:
                cursor.execute(cmd)
                print(f"------Excuted mysql commands------")
            connection.commit()
            print("-------Created MySQL schema-------")

    except Error as e:
        connection.rollback()
        raise Exception(f"-----Failed to create MySQL schema: {e}---") from e

#validate data
"""
- validate table
- validate column
"""

def validate_mysql_schema(connection, cursor):
    #validate table
    cursor.execute("SHOW TABLES")
    #tables = [row[0] for row in cursor.fetchall()]  #table name in db

    #using fetchone()
    tables = []     #table name in db
    row = cursor.fetchone()
    while row:
        tables.append(row[0])
        row = cursor.fetchone()

    # print(tables)

    # kiểm tra bằng cách nông dân
    # if "users" not in tables or "repositories" not in tables:
    #     raise ValueError(f"------Tables doesn't exist----")
    #print("------Validated table successfully-----")

    #kiểm tra bằng cách tìm tables_name trong file:
    tables_name = []    #table name in file
    try:
        with open(SQL_FILE_PATH, "r") as file:
            sql_script = file.read().strip()
            sql_commands = [cmd.lower() for cmd in sql_script.split(" ")]
            # print(sql_commands)
            key = "exists"
            key1 = "table"
            for i  in range(len(sql_commands)):
                if sql_commands[i] == key:
                    table_name = re.sub(r'[^a-zA-Z0-9]', '', sql_commands[i + 1])
                    tables_name.append(table_name)

                elif sql_commands[i] == key1 and sql_commands[i + 1] != "if":
                    table_name = re.sub(r'[^a-zA-Z0-9]', '', sql_commands[i + 1])
                    tables_name.append(table_name)

            print(tables_name)

    except Error as e:
        print(f"-------Failed to open file {file}------")
    except FileNotFoundError:
        print(f"-----File {file} doesn't exist-------")

    for table in tables_name:
        if table not in tables:
            raise ValueError(f"------Tables doesn't exist----")

        # else:
        #     print(f"-----validated table {table} in database-------")

    # print("------Validated table successfully-----")

    #validate column
    cursor.execute("SELECT * FROM repositories WHERE repositories_id = 1")
    # print(cursor.fetchone())
    repository = cursor.fetchone()
    if not repository:
        raise ValueError("-------repository not found------")

    print("------Validated schema successfully------")

def create_mongodb_schema(db):
    db.drop_collection("repositories")
    db.create_collection("repositories", validator={
        "$jsonSchema": {
            "bsonType" : "object",
            "required": ["repositories_id", "name"],
            "properties":{
                "repositories_id": {
                    "bsonType": "int"},
                "name": {
                    "bsonType": "string"},
                "url": {
                    "bsonType": ["string", "null"]}
            }
        }
    })
    db.repositories.create_index("repositories_id")
    print("-----Created collection repositories in mongodb------")

def validate_mongodb_schema(db):
    collections = db.list_collection_names()
    # print(f"----collections: {collections}------")
    if "repositories" not in collections:
        raise ValueError("------collection doesn't exist-----")

    repository = db.repositories.find_one({"repositories_id": 1})
    # print(repository)
    if not repository:
        raise ValueError("---------repositories_id not found in MongoDB-----")

    print("----------Validated schema successfully-------")