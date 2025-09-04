from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerUpdate, SupplierUpdate
from uuid import UUID
from deps import require_admin


async def view_buyer_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,buyer_profile.buyer_name, buyer_profile.company_name, buyer_profile.vat_number FROM app_user JOIN buyer_profile ON app_user.id = buyer_profile.user_id WHERE app_user.role = 'buyer'")
        return [dict(row) for row in rows]


async def view_supplier_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,supplier_profile.supplier_name, supplier_profile.company_name, supplier_profile.kyc_status FROM app_user JOIN supplier_profile ON app_user.id = supplier_profile.user_id WHERE app_user.role = 'supplier'")
        return [dict(row) for row in rows]   


async def get_user_buyer_service(data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,buyer_profile.buyer_name, buyer_profile.company_name, buyer_profile.vat_number FROM app_user JOIN buyer_profile ON app_user.id = buyer_profile.user_id WHERE app_user.id = $1 and app_user.role='buyer'",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    

async def get_user_sup_service(data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,supplier_profile.supplier_name, supplier_profile.company_name, supplier_profile.kyc_status FROM app_user JOIN supplier_profile ON app_user.id = supplier_profile.user_id WHERE app_user.id = $1 and app_user.role='supplier'",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    


async def delete_log_service(user_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM app_user WHERE id = $1", str(user_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="User not found")
    return




async def update_buyer_service(user_id, user_update, request: Request):
    async with request.app.state.pool.acquire() as conn:
        async with conn.transaction():

            # Check if user exists
            existing_user = await conn.fetchrow(
                "SELECT * FROM app_user WHERE id=$1", str(user_id)
            )
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")

            # ---------- Update app_user ----------
            app_user_update_fields = []
            app_user_values = []
            idx = 1

            if user_update.is_active is not None:
                app_user_update_fields.append(f"is_active = ${idx}")
                app_user_values.append(user_update.is_active)
                idx += 1

            updated_user = None
            if app_user_update_fields:
                app_user_values.append(str(user_id))
                query = f"""
                    UPDATE app_user 
                    SET {', '.join(app_user_update_fields)} 
                    WHERE id=${idx} 
                    RETURNING *
                """
                updated_user = await conn.fetchrow(query, *app_user_values)
            else:
                updated_user = existing_user  # no changes to app_user

            # ---------- Update buyer_profile ----------
            profile_update_fields = []
            profile_values = []
            idx = 1

            if user_update.buyer_name is not None:
                profile_update_fields.append(f"buyer_name = ${idx}")
                profile_values.append(user_update.buyer_name)
                idx += 1

            if user_update.company_name is not None:
                profile_update_fields.append(f"company_name = ${idx}")
                profile_values.append(user_update.company_name)
                idx += 1

            if user_update.vat_number is not None:
                profile_update_fields.append(f"vat_number = ${idx}")
                profile_values.append(user_update.vat_number)
                idx += 1

            updated_profile = None
            if profile_update_fields:
                profile_values.append(str(user_id))
                query = f"""
                    UPDATE buyer_profile 
                    SET {', '.join(profile_update_fields)} 
                    WHERE user_id=${idx} 
                    RETURNING *
                """
                updated_profile = await conn.fetchrow(query, *profile_values)
            else:
                updated_profile = await conn.fetchrow(
                    "SELECT * FROM buyer_profile WHERE user_id=$1", str(user_id)
                )

            # ---------- Return merged response ----------
            return {
                "user": dict(updated_user),
                "buyer_profile": dict(updated_profile) if updated_profile else None,
            }




async def update_supplier_service(user_id, supplier_update, request: Request):
    async with request.app.state.pool.acquire() as conn:
        async with conn.transaction():

            # Check if user exists
            existing_user = await conn.fetchrow(
                "SELECT * FROM app_user WHERE id=$1", str(user_id)
            )
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")

            # ---------- Update app_user ----------
            app_user_update_fields = []
            app_user_values = []
            idx = 1

            if supplier_update.is_active is not None:
                app_user_update_fields.append(f"is_active = ${idx}")
                app_user_values.append(supplier_update.is_active)
                idx += 1

            updated_user = None
            if app_user_update_fields:
                app_user_values.append(str(user_id))
                query = f"""
                    UPDATE app_user 
                    SET {', '.join(app_user_update_fields)} 
                    WHERE id=${idx} 
                    RETURNING *
                """
                updated_user = await conn.fetchrow(query, *app_user_values)
            else:
                updated_user = existing_user  # no changes to app_user

            # ---------- Update supplier_profile ----------
            profile_update_fields = []
            profile_values = []
            idx = 1

            if supplier_update.supplier_name is not None:
                profile_update_fields.append(f"supplier_name = ${idx}")
                profile_values.append(supplier_update.supplier_name)
                idx += 1

            if supplier_update.company_name is not None:
                profile_update_fields.append(f"company_name = ${idx}")
                profile_values.append(supplier_update.company_name)
                idx += 1

            if supplier_update.kyc_status is not None:
                profile_update_fields.append(f"kyc_status = ${idx}")
                profile_values.append(supplier_update.kyc_status)
                idx += 1

            updated_profile = None
            if profile_update_fields:
                profile_values.append(str(user_id))
                query = f"""
                    UPDATE supplier_profile 
                    SET {', '.join(profile_update_fields)} 
                    WHERE user_id=${idx} 
                    RETURNING *
                """
                updated_profile = await conn.fetchrow(query, *profile_values)
            else:
                updated_profile = await conn.fetchrow(
                    "SELECT * FROM supplier_profile WHERE user_id=$1", str(user_id)
                )

            # ---------- Return merged response ----------
            return {
                "user": dict(updated_user),
                "supplier_profile": dict(updated_profile) if updated_profile else None,
            }
