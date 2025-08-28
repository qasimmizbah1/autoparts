from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerProfileData, SupplierProfileData
from uuid import UUID

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/")
async def view_profiles(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, created_at FROM app_user")
        return [dict(row) for row in rows]
     

    
@router.post("/user")
async def get_user(data: UserRequest, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, role, is_active, created_at FROM app_user WHERE id = $1",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)

    

# Upsert Buyer Profile
@router.post("/buyer/{user_id}")
async def upsert_buyer_profile(user_id: UUID, data: BuyerProfileData, request: Request):
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
    

# Upsert Buyer Profile
@router.post("/supplier/{user_id}")
async def upsert_supplier_profile(user_id: UUID, data: SupplierProfileData, request: Request):
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
