from datetime import timedelta
from fastapi import HTTPException, Request
from utils.security import verify_password, create_access_token

async def user_login_service(user, request: Request):
    async with request.app.state.pool.acquire() as conn:
        db_user = await conn.fetchrow("SELECT * FROM app_user WHERE is_active='true' and email=$1", user.email)
        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": db_user["email"]}, expires_delta=token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user["id"],
                "email": db_user["email"],
                "role": db_user["role"],
                "is_active": db_user["is_active"],
            }
        }
