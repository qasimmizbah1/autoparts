from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRegister, UserLogin, UserOut

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/views")
async def view_profiles(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, created_at FROM app_user")
        return [dict(row) for row in rows]
     


