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
    # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Create verification_tokens table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS verification_tokens (
                id SERIAL PRIMARY KEY,
                token VARCHAR(255) NOT NULL UNIQUE,
                user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.execute("CREATE INDEX IF NOT EXISTS idx_verification_tokens_token ON verification_tokens(token)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_verification_tokens_user_id ON verification_tokens(user_id)")

    yield
    await app.state.pool.close()
