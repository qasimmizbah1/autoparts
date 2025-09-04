import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
import os


load_dotenv()


DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(**DB_CONFIG)

    async with app.state.pool.acquire() as conn:

        await conn.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_model ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                make_id UUID NOT NULL REFERENCES vehicle_make(id), 
                name TEXT NOT NULL, 
                UNIQUE(make_id, name) 
            )
        """)
        await conn.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_trim ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                model_id UUID NOT NULL REFERENCES vehicle_model(id), 
                year_from SMALLINT, 
                year_to SMALLINT, 
                trim TEXT
                )
        """)
        await conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS vehicle_trim_unique_idx 
                    ON vehicle_trim (
                    model_id, 
                    COALESCE(year_from, 0), 
                    COALESCE(year_to, 0), 
                    COALESCE(trim, '')
                    )
        """)

    yield
    await app.state.pool.close()
