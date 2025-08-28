from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, UserUpdate
from uuid import UUID

router = APIRouter(prefix="/manage-users", tags=["Manage Users"])


@router.get("/buyer")
async def view_profiles(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,buyer_profile.buyer_name, buyer_profile.company_name, buyer_profile.vat_number FROM app_user JOIN buyer_profile ON app_user.id = buyer_profile.user_id WHERE app_user.role = 'buyer'")
        return [dict(row) for row in rows]

@router.get("/supplier")
async def view_profiles(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,supplier_profile.supplier_name, supplier_profile.company_name, supplier_profile.kyc_status FROM app_user JOIN supplier_profile ON app_user.id = supplier_profile.user_id WHERE app_user.role = 'supplier'")
        return [dict(row) for row in rows]   


@router.post("/buyer")
async def get_user(data: UserRequest, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,buyer_profile.buyer_name, buyer_profile.company_name, buyer_profile.vat_number FROM app_user JOIN buyer_profile ON app_user.id = buyer_profile.user_id WHERE app_user.id = $1 and app_user.role='buyer'",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    

@router.post("/supplier")
async def get_user(data: UserRequest, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,supplier_profile.supplier_name, supplier_profile.company_name, supplier_profile.kyc_status FROM app_user JOIN supplier_profile ON app_user.id = supplier_profile.user_id WHERE app_user.id = $1 and app_user.role='supplier'",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    


@router.delete("/{user_id}", status_code=204)
async def delete_log(user_id: UUID, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM app_user WHERE id = $1", str(user_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="User not found")
    return



@router.patch("/users/{user_id}", response_model=dict)
async def update_user(user_id: UUID, user_update: UserUpdate, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Fetch existing user
        existing_user = await conn.fetchrow("SELECT * FROM app_user WHERE id=$1", str(user_id))
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build dynamic update query
        update_fields = []
        values = []
        idx = 1

        if user_update.email is not None:
            update_fields.append(f"email = ${idx}")
            values.append(user_update.email)
            idx += 1
        if user_update.full_name is not None:
            update_fields.append(f"full_name = ${idx}")
            values.append(user_update.full_name)
            idx += 1
        if user_update.is_active is not None:
            update_fields.append(f"is_active = ${idx}")
            values.append(user_update.is_active)
            idx += 1

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(str(user_id))
        query = f"UPDATE app_user SET {', '.join(update_fields)} WHERE id=${idx} RETURNING *"
        
        updated_user = await conn.fetchrow(query, *values)
        
        return dict(updated_user)
