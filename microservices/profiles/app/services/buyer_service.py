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


#view Address
async def buyer_view_address_service(buyer_id: int, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetch("""
            SELECT *
            FROM buyer_address
            WHERE buyer_id = $1
        """, buyer_id)

        if row:
            return {
                "type": "success",
                "msg": "Address retrieved",
                 "data": [dict(r) for r in row]
            }
        else:
            return {
                "type": "error",
                "msg": "Address not found",
                "data": []
            }


#Add Address
async def buyer_address_service(buyer_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO buyer_address (buyer_id, line1, line2, city, province, postal_code, country)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, buyer_id, line1, line2, city, province, postal_code, country
        """, buyer_id, data.line1, data.line2, data.city, data.province, data.postal_code, data.country)

        return {"type": "success", "msg": "Address saved", "data": dict(row)}


#Update Address
async def buyer_update_address_service(address_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            UPDATE buyer_address
            SET line1 = $2,
                line2 = $3,
                city = $4,
                province = $5,
                postal_code = $6,
                country = $7
                WHERE id = $1
            RETURNING id, buyer_id, line1, line2, city, province, postal_code, country
        """, address_id, data.line1, data.line2, data.city, data.province, data.postal_code, data.country)

        return {"type": "success", "msg": "Address updated", "data": dict(row) if row else None}

    