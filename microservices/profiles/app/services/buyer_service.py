from fastapi import Request


async def upsert_buyer_service(user_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO buyer_profile (user_id, buyer_name, company_name, vat_number)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                buyer_name = EXCLUDED.buyer_name,
                company_name = EXCLUDED.company_name,
                vat_number = EXCLUDED.vat_number,
                updated_at = now()
            RETURNING id, user_id, buyer_name, company_name, vat_number, created_at, updated_at
        """, user_id, data.name, data.company_name, data.vat_number)

        return {"type": "success", "msg": "Profile saved", "data": dict(row)}
