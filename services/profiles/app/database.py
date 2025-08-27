import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI

DB_CONFIG = {
    "user": "postgres",
    "password": "123",
    "database": "autoparts",
    "host": "localhost",
    "port": 5432,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(**DB_CONFIG)

    async with app.state.pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

    yield
    await app.state.pool.close()
