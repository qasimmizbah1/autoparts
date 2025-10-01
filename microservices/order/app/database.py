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
                CREATE TABLE IF NOT EXISTS part_request (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES app_user(id),
                title TEXT NOT NULL,
                description TEXT,
                urgency TEXT CHECK (urgency IN ('low','normal','high','critical')) NOT NULL,
                required_by_date DATE,
                vehicle_make TEXT NOT NULL,
                vehicle_model TEXT NOT NULL,
                vehicle_model_trim TEXT NOT NULL,
                attachment TEXT,
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

        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS buyer_address (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    buyer_id UUID NOT NULL REFERENCES buyer_profile(id) ON DELETE CASCADE,
                    line1 TEXT NOT NULL,
                    line2 TEXT,
                    city TEXT,
                    province TEXT,
                    postal_code TEXT,
                    country CHAR(2) NOT NULL DEFAULT 'ZA',
                    is_default BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
        """)

        await conn.execute("""
                        CREATE TABLE  IF NOT EXISTS supplier_address (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                supplier_id UUID NOT NULL REFERENCES supplier_profile(id) ON DELETE CASCADE,
                line1 TEXT NOT NULL,
                line2 TEXT,
                city TEXT,
                province TEXT,
                postal_code TEXT,
                country CHAR(2) NOT NULL DEFAULT 'ZA',
                is_default BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
        """)


        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS  "order" ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                quote_id UUID NOT NULL UNIQUE REFERENCES quote(id), 
                status TEXT NOT NULL CHECK (status IN 
                ('PENDING_HOLD','ON_HOLD','SHIPPED','DELIVERED','ACCEPTED','REJECTED','REFUNDED
                ')), 
                buyer_id UUID NOT NULL REFERENCES buyer_profile(id), 
                supplier_id UUID NOT NULL REFERENCES supplier_profile(id), 
                shipping_to_address_id UUID REFERENCES buyer_address(id), 
                shipping_from_address_id UUID REFERENCES supplier_address(id), 
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now() 
                )
        """)

        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS delivery_confirmation ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                order_id UUID NOT NULL UNIQUE REFERENCES "order"(id) ON DELETE CASCADE, 
                method TEXT NOT NULL CHECK (method IN ('email_otp','qr_scan')), 
                otp_hash TEXT, 
                verified_at TIMESTAMPTZ 
                )
        """)



        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS escrow_transaction ( 
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
            order_id UUID NOT NULL UNIQUE REFERENCES "order"(id) ON DELETE CASCADE, 
            state TEXT NOT NULL CHECK (state IN 
            ('INIT','AUTH_HELD','CAPTURED','RELEASED','REFUNDED','FAILED')), 
            amount_cents BIGINT NOT NULL, 
            currency CHAR(3) NOT NULL DEFAULT 'ZAR', 
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(), 
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now() 
                )
        """)


        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS  payfast_transaction ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                escrow_id UUID NOT NULL REFERENCES escrow_transaction(id), 
                provider_ref TEXT,         -- token / reference from PayFast 
                event TEXT,                -- 'AUTH', 'CAPTURE', 'RELEASE', 'REFUND', 'IPN' 
                status TEXT,               -- provider status 
                raw_payload JSONB, 
                created_at TIMESTAMPTZ NOT NULL DEFAULT now() 
                )
        """)

        
        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS attachment ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                owner_user_id UUID REFERENCES app_user(id), 
                purpose TEXT CHECK (purpose IN 
                ('request','quote','kyc','delivery_proof','invoice')), 
                filename TEXT NOT NULL, 
                content_type TEXT, 
                storage_path TEXT NOT NULL, 
                created_at TIMESTAMPTZ NOT NULL DEFAULT now() 
                )
        """)

        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS  kyc_document ( 
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                    supplier_id UUID NOT NULL REFERENCES supplier_profile(id), 
                    doc_type TEXT, 
                    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN 
                    ('pending','approved','rejected')), 
                    attachment_id UUID REFERENCES attachment(id), 
                    reviewed_by UUID REFERENCES app_user(id), 
                    reviewed_at TIMESTAMPTZ 
                    )
        """)

        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS notification ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                user_id UUID REFERENCES app_user(id), 
                channel TEXT NOT NULL CHECK (channel IN ('email')), 
                subject TEXT, 
                body TEXT, 
                send_after TIMESTAMPTZ, 
                sent_at TIMESTAMPTZ 
                )
        """)

        await conn.execute("""
            CREATE TABLE  IF NOT EXISTS audit_log ( 
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(), 
                actor_user_id UUID REFERENCES app_user(id), 
                action TEXT NOT NULL, 
                entity_type TEXT NOT NULL, 
                entity_id UUID, 
                metadata JSONB, 
                created_at TIMESTAMPTZ NOT NULL DEFAULT now() 
                )
        """)


    yield
    await app.state.pool.close()
