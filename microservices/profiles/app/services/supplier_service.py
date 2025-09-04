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
    



    
