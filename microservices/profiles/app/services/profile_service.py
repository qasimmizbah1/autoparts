import uuid
from fastapi import HTTPException, Request
from utils.security import verify_password
from utils.security import hash_password, verify_password 
from datetime import datetime, timedelta
import hashlib

async def view_users_profile(request: Request = None ):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, created_at FROM app_user")
        return [dict(row) for row in rows]


async def get_user_profile(data, request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, role, is_active, created_at FROM app_user WHERE id = $1",
            str(data.user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    