from fastapi import Request, Path, APIRouter, Form, File, Depends, BackgroundTasks
from uuid import UUID, uuid4
from models import OrderCreate, OrderUpdate
from services.order_service import get_makes_service
from typing import Optional, List
from models import ViewQuoteSchema, AcceptQuoteSchema
from datetime import date
from deps import require_buyer


router = APIRouter(prefix="/v1/order", tags=["Order"])


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

@router.post("/quote/by-request/")
async def get_quotes_by_request(
    request: Request,
    data: ViewQuoteSchema
):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM quote WHERE request_id = $1 ORDER BY created_at DESC",
            data.request_id  # use request_id from JSON body
        )
        return [dict(r) for r in rows]


# @router.put("/quote/accept")
# async def accept_quote(
#     request: Request,
#     data: AcceptQuoteSchema,
#     background_tasks: BackgroundTasks
# ):
#     async with request.app.state.pool.acquire() as conn:
#         # 1. Find the quote
#         quote_row = await conn.fetchrow(
#             "SELECT * FROM quote WHERE id = $1",
#             data.quote_id
#         )

#         if not quote_row:
#             return {"error": "Quote not found"}

#         request_id = quote_row["request_id"]

#         # 2. Check if another quote already accepted for same request
#         existing_accepted = await conn.fetchrow(
#             """
#             SELECT id FROM quote
#             WHERE request_id = $1 AND is_accepted = TRUE
#             """,
#             request_id
#         )

#         if existing_accepted and existing_accepted["id"] != str(data.quote_id):
#             return {
#                 "error": "Another quote has already been accepted for this request",
#                 "accepted_quote_id": existing_accepted["id"]
#             }

#         # 3. Mark all quotes for this request as not accepted
#         await conn.execute(
#             """
#             UPDATE quote
#             SET is_accepted = FALSE
#             WHERE request_id = $1
#             """,
#             request_id
#         )

#         # 4. Accept the selected quote
#         row = await conn.fetchrow(
#             """
#             UPDATE quote
#             SET is_accepted = TRUE
#             WHERE id = $1
#             RETURNING *
#             """,
#             data.quote_id
#         )

#         # 5. Fetch supplier email (same as before)
#         supplier_email_row = await conn.fetchrow(
#             """
#             SELECT u.email
#             FROM supplier_profile s
#             JOIN app_user u ON u.id = s.user_id
#             WHERE s.id = $1
#             """,
#             row["supplier_id"]
#         )

#         if supplier_email_row and supplier_email_row["email"]:
#             subject = "Your Quote Has Been Accepted"
#             body = f"Hello,\n\nYour quote with ID {row['id']} has been accepted.\n\nThanks!"

#             # Development mode: just print
#             print("📧 Debug Email Mode")
#             print("To:", supplier_email_row["email"])
#             print("Subject:", subject)
#             print("Body:\n", body)

#             # Production mode: uncomment when ready
#             # background_tasks.add_task(
#             #     send_email,
#             #     supplier_email_row["email"],
#             #     subject,
#             #     body
#             # )

#         return dict(row)
    
# @router.post("/orders")
# async def create_order(data: OrderCreate, request: Request):
#     query = """
#     INSERT INTO "order" 
#     (quote_id, buyer_id, supplier_id, shipping_to_address_id, shipping_from_address_id, status)
#     VALUES ($1,$2,$3,$4,$5,$6)
#     RETURNING *
#     """
#     async with request.app.state.pool.acquire() as conn:
#         row = await conn.fetchrow(
#             query,
#             data.quote_id,
#             data.buyer_id,
#             data.supplier_id,
#             data.shipping_to_address_id,
#             data.shipping_from_address_id,
#             data.status
#         )
#         return dict(row)    
    

@router.put("/quote/{quote_id}/accept")
async def accept_quote(quote_id: str,request: Request,data: AcceptQuoteSchema):
#async def accept_quote(request: Request, data: AcceptQuoteSchema):
    async with request.app.state.pool.acquire() as conn:
        # 1. Fetch quote
        quote_row = await conn.fetchrow(
            "SELECT * FROM quote WHERE id = $1",
            quote_id
        )
        if not quote_row:
            return {"error": "Quote not found"}

        # 2. Fetch part_request (to get buyer_id)
        part_request_row = await conn.fetchrow(
            "SELECT * FROM part_request WHERE id = $1",
            quote_row["request_id"]
        )
        if not part_request_row:
            return {"error": "Part request not found"}

        user_id = part_request_row["user_id"]

        buyer_profile_row = await conn.fetchrow(
        "SELECT id FROM buyer_profile WHERE user_id = $1",
        user_id
        )

        if not buyer_profile_row:
            return {"error": "Buyer profile not found"}

        buyer_id = buyer_profile_row["id"]
        supplier_id = quote_row["supplier_id"]

        print("Buyer ID:", buyer_id)
        print("Supplier ID:", supplier_id)

        # 3. Get buyer’s shipping address
        buyer_address = await conn.fetchrow(
            "SELECT id FROM buyer_address WHERE buyer_id = $1 LIMIT 1",
            buyer_id
        )

        # 4. Get supplier’s shipping address
        supplier_address = await conn.fetchrow(
            "SELECT id FROM supplier_address WHERE supplier_id = $1 LIMIT 1",
            supplier_id
        )

        # 5. Mark quote accepted
        await conn.execute(
            "UPDATE quote SET is_accepted = TRUE WHERE id = $1",
            quote_id
        )

        # 6. Create order
        order_row = await conn.fetchrow(
            """
            INSERT INTO "order"
            (quote_id, buyer_id, supplier_id, shipping_to_address_id, shipping_from_address_id, status)
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING *
            """,
            quote_row["id"],
            buyer_id,
            supplier_id,
            buyer_address["id"] if buyer_address else None,
            supplier_address["id"] if supplier_address else None,
            "PENDING_HOLD"
        )

        return dict(order_row)



@router.get("/orders/{order_id}")
async def get_order(order_id: str, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM \"order\" WHERE id = $1", order_id)
        if not row:
            return {"error": "Order not found"}
        return dict(row)
    
@router.put("/orders/{order_id}")
async def update_order(order_id: str, data: OrderUpdate, request: Request):
    set_clauses = []
    values = []
    idx = 1

    if data.status:
        set_clauses.append(f"status = ${idx}")
        values.append(data.status)
        idx += 1
    if data.shipping_to_address_id:
        set_clauses.append(f"shipping_to_address_id = ${idx}")
        values.append(data.shipping_to_address_id)
        idx += 1
    if data.shipping_from_address_id:
        set_clauses.append(f"shipping_from_address_id = ${idx}")
        values.append(data.shipping_from_address_id)
        idx += 1

    if not set_clauses:
        return {"error": "Nothing to update"}

    query = f"""
    UPDATE "order" SET {', '.join(set_clauses)}, updated_at = now()
    WHERE id = ${idx} RETURNING *
    """
    values.append(order_id)

    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(query, *values)
        if not row:
            return {"error": "Order not found"}
        return dict(row)