import asyncio
import aiomysql
from MigrateDataProject.config.database_config import get_database_config

async def insert_one(repositories_id, name, url):
    config = get_database_config()
    conn = await aiomysql.connect(
        host=config["mysql"].host,
        port=int(config["mysql"].port),
        user=config["mysql"].user,
        password=config["mysql"].password,
        db=config["mysql"].database,
        autocommit=True
    )

    async with conn.cursor() as cursor:
        query = """
            INSERT INTO repositories (repositories_id, name, url)
            VALUES (%s, %s, %s)
        """
        await cursor.execute(query, (repositories_id, name, url))

    conn.close()

async def main():
    await asyncio.gather(
        insert_one(int(2), 'abc', 'https://bfhfh.com'),
        insert_one(int(3), 'abc', 'https://bfhfh.com'),
        insert_one(int(4), 'abc', 'https://bfhfh.com'),
        insert_one(int(5), 'abc', 'https://bfhfh.com'),
    )

asyncio.run(main())
