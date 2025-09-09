from fastapi import Request, UploadFile, APIRouter, Form, File, HTTPException, BackgroundTasks
from uuid import UUID, uuid4
from models import VehicleMake, VehicleModel, VehicleTrim
from services.vechile_service import get_makes_service, get_models_service, get_trims_service
from typing import Optional, List
from models import PartRequest, PartRequestInDB
from datetime import date
import os
import aiosmtplib
from email.message import EmailMessage

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = "info@techbeeps.co.in"  # your SMTP email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname="smtp.example.com",
        port=587,
        username="your-email@example.com",
        password="your-password",
        start_tls=True,
    )


# #Create Quote resquset 
# async def create_quote_service(request, request_id, supplier_id, price_cents, currency, eta_days, terms):
#     async with request.app.state.pool.acquire() as conn:
#         row = await conn.fetchrow(
#             """
#             INSERT INTO quote (request_id, supplier_id, price_cents, currency, eta_days, terms)
#             VALUES ($1, $2, $3, $4, $5, $6)
#             RETURNING *
#             """,
#             request_id, supplier_id, price_cents, currency, eta_days, terms
#         )
        
#         return dict(row)

from fastapi import HTTPException

# Create Quote service with validation + "print email"
async def create_quote_service(request, request_id, supplier_id, price_cents, currency, eta_days, terms):
    async with request.app.state.pool.acquire() as conn:
        # 1. Check if this supplier already created a quote for this request
        existing_quote = await conn.fetchrow(
            """
            SELECT * FROM quote 
            WHERE request_id = $1 AND supplier_id = $2
            """,
            request_id, supplier_id
        )

        if existing_quote:
            # Return clean API error instead of 500
            raise HTTPException(
                status_code=400,
                detail="This supplier has already submitted a quote for this request."
            )

        # 2. Insert new quote
        row = await conn.fetchrow(
            """
            INSERT INTO quote (request_id, supplier_id, price_cents, currency, eta_days, terms)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            request_id, supplier_id, price_cents, currency, eta_days, terms
        )

        # 3. Fetch request -> get user_id
        request_row = await conn.fetchrow(
            "SELECT user_id FROM part_request WHERE id = $1",
            request_id
        )

        if request_row:
            user_id = request_row["user_id"]

            # 4. Fetch user -> get email
            user_row = await conn.fetchrow(
                "SELECT email FROM app_user WHERE id = $1",
                user_id
            )

            if user_row:
                email = user_row["email"]

                # 5. Local mode: print instead of sending email
                print("=== EMAIL SIMULATION ===")
                print(f"To: {email}")
                print(f"Subject: New Quote Created")
                print(
                    f"Body: A new quote has been created for your request {request_id}. "
                    f"Quote price: {price_cents / 100:.2f} {currency}, ETA: {eta_days} days, Terms: {terms}"
                )
                print("=========================")

        return dict(row)


#upadte Quote
async def update_quote_service(request, quote_id, price_cents, currency, eta_days, terms):
    async with request.app.state.pool.acquire() as conn:
        # Build dynamic query
        updates = []
        params = []

        if price_cents is not None:
            params.append(price_cents)
            updates.append(f"price_cents = ${len(params)}")
        if currency is not None:
            params.append(currency)
            updates.append(f"currency = ${len(params)}")
        if eta_days is not None:
            params.append(eta_days)
            updates.append(f"eta_days = ${len(params)}")
        if terms is not None:
            params.append(terms)
            updates.append(f"terms = ${len(params)}")
        

        if not updates:
            return {"error": "No fields to update"}

        params.append(quote_id)
        query = f"""
            UPDATE quote
            SET {', '.join(updates)}
            WHERE id = ${len(params)}
            RETURNING *
        """

        row = await conn.fetchrow(query, *params)
        return dict(row) if row else {"error": "Quote not found"}

#Browse all request
async def get_all_parts_request_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM part_request"
        )
        return [dict(r) for r in rows]

#Search Request Service function
async def search_part_request_service(request, title, urgency, description, vehicle_make, vehicle_model):
    async with request.app.state.pool.acquire() as conn:
        query = "SELECT * FROM part_request WHERE 1=1"
        params = []

        if title:
            params.append(f"%{title}%")
            query += f" AND title ILIKE ${len(params)}"
        if urgency:
            params.append(urgency)
            query += f" AND urgency = ${len(params)}"
        if description:
            params.append(f"%{description}%")
            query += f" AND description ILIKE ${len(params)}"
        if vehicle_make:
            params.append(f"%{vehicle_make}%")
            query += f" AND vehicle_make ILIKE ${len(params)}"
        if vehicle_model:
            params.append(f"%{vehicle_model}%")
            query += f" AND vehicle_model ILIKE ${len(params)}"

        rows = await conn.fetch(query, *params)

        if not rows:
            raise HTTPException(status_code=404, detail="Part request not found")
        
        return [dict(r) for r in rows]

    



