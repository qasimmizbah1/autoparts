from fastapi import Request, Path, APIRouter, Form, File, Depends, BackgroundTasks
from uuid import UUID, uuid4
from models import VehicleMake, VehicleModel, VehicleTrim
from services.vechile_service import get_makes_service, get_models_service, get_trims_service
from services.part_request_service import create_part_request_service, get_parts_request_service, get_all_parts_request_service, delete_parts_request_service, update_part_request_service
from typing import Optional, List
from models import ViewQuoteSchema, AcceptQuoteSchema
from datetime import date
from deps import require_buyer


router = APIRouter(prefix="/v1/buyer", tags=["Quote for Part Requests"])


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


@router.put("/quote/accept")
async def accept_quote(
    request: Request,
    data: AcceptQuoteSchema,
    background_tasks: BackgroundTasks
):
    async with request.app.state.pool.acquire() as conn:
        # 1. Find the quote
        quote_row = await conn.fetchrow(
            "SELECT * FROM quote WHERE id = $1",
            data.quote_id
        )

        if not quote_row:
            return {"error": "Quote not found"}

        request_id = quote_row["request_id"]

        # 2. Check if another quote already accepted for same request
        existing_accepted = await conn.fetchrow(
            """
            SELECT id FROM quote
            WHERE request_id = $1 AND is_accepted = TRUE
            """,
            request_id
        )

        if existing_accepted and existing_accepted["id"] != str(data.quote_id):
            return {
                "error": "Another quote has already been accepted for this request",
                "accepted_quote_id": existing_accepted["id"]
            }

        # 3. Mark all quotes for this request as not accepted
        await conn.execute(
            """
            UPDATE quote
            SET is_accepted = FALSE
            WHERE request_id = $1
            """,
            request_id
        )

        # 4. Accept the selected quote
        row = await conn.fetchrow(
            """
            UPDATE quote
            SET is_accepted = TRUE
            WHERE id = $1
            RETURNING *
            """,
            data.quote_id
        )

        # 5. Fetch supplier email (same as before)
        supplier_email_row = await conn.fetchrow(
            """
            SELECT u.email
            FROM supplier_profile s
            JOIN app_user u ON u.id = s.user_id
            WHERE s.id = $1
            """,
            row["supplier_id"]
        )

        if supplier_email_row and supplier_email_row["email"]:
            subject = "Your Quote Has Been Accepted"
            body = f"Hello,\n\nYour quote with ID {row['id']} has been accepted.\n\nThanks!"

            # Development mode: just print
            print("📧 Debug Email Mode")
            print("To:", supplier_email_row["email"])
            print("Subject:", subject)
            print("Body:\n", body)

            # Production mode: uncomment when ready
            # background_tasks.add_task(
            #     send_email,
            #     supplier_email_row["email"],
            #     subject,
            #     body
            # )

        return dict(row)