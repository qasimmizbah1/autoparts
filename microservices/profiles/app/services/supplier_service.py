from fastapi import Request
from uuid import UUID

async def upsert_supplier_service(user_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO supplier_profile (user_id, supplier_name, company_name, kyc_status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                supplier_name = EXCLUDED.supplier_name,
                company_name = EXCLUDED.company_name,
                kyc_status = EXCLUDED.kyc_status,
                updated_at = now()
            RETURNING id, user_id, supplier_name, company_name, kyc_status, created_at, updated_at
        """, user_id, data.name, data.company_name, data.kyc_status)

        return {"type": "success", "msg": "Profile saved", "data": dict(row)}
    


#Add Address
async def supplier_address_service(supplier_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO supplier_address (supplier_id, line1, line2, city, province, postal_code, country)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, supplier_id, line1, line2, city, province, postal_code, country
        """, supplier_id, data.line1, data.line2, data.city, data.province, data.postal_code, data.country)

        return {"type": "success", "msg": "Address saved", "data": dict(row)}


#Update Address
async def supplier_update_address_service(address_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            UPDATE supplier_address
            SET line1 = $2,
                line2 = $3,
                city = $4,
                province = $5,
                postal_code = $6,
                country = $7
                WHERE id = $1
            RETURNING id, supplier_id, line1, line2, city, province, postal_code, country
        """, address_id, data.line1, data.line2, data.city, data.province, data.postal_code, data.country)

        return {"type": "success", "msg": "Address updated", "data": dict(row) if row else None}

    
