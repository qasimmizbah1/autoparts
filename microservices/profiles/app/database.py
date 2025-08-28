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
    # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS buyer_profile (
                  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                    user_id UUID NOT NULL REFERENCES app_user(id) UNIQUE, 
                    buyer_name varchar(255),
                    company_name TEXT, 
                    vat_number TEXT, 
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now() 
            )
        """)
        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS supplier_profile ( 
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
            user_id UUID NOT NULL REFERENCES app_user(id) UNIQUE, 
            supplier_name varchar(255),
            company_name TEXT, 
            kyc_status TEXT NOT NULL DEFAULT 'pending' CHECK (kyc_status IN 
            ('pending','approved','rejected')), 
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now() 
            )
        """)


       
        


    yield
    await app.state.pool.close()
