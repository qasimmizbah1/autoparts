from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRegister, UserLogin, UserOut
from utils.security import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
async def register_user(user: UserRegister, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # check if user already exists
        exists = await conn.fetchrow("SELECT 1 FROM app_user WHERE email=$1", user.email)
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        # hash password
        hashed_password = hash_password(user.password)

        # insert new user
        row = await conn.fetchrow(
            """
            INSERT INTO app_user (email, password_hash, role, is_active)
            VALUES ($1, $2, $3, $4)
            RETURNING id::text, email, role, is_active, created_at
            """,
            user.email, hashed_password, user.role, user.is_active
        )

        return dict(row)

    async with request.app.state.pool.acquire() as conn:
        # check if user exists
        exists = await conn.fetchrow("SELECT * FROM app_user WHERE email=$1", user.email)
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = hash_password(user.password)
        row = await conn.fetchrow(
            """
            INSERT INTO app_user (email, password_hash, role)
            VALUES ($1, $2, $3)
            RETURNING id, email, role, is_active, created_at
            """,
            user.email, hashed_password, user.role
        )
        return dict(row)

@router.post("/login")
async def login_user(user: UserLogin, request: Request):
    async with request.app.state.pool.acquire() as conn:
        db_user = await conn.fetchrow("SELECT * FROM app_user WHERE email=$1", user.email)
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
