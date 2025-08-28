from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks, Body
from models import UserRegister, UserLogin, UserOut
from utils.security import create_access_token
from datetime import datetime, timedelta
from database import get_auth_service
from services.auth.app.services.register_service import AuthService
from utils.security import hash_password, verify_password, generate_verification_token  

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

async def send_verification_email(email: str, token: str, request: Request):
    """
    Send verification email - in development, we'll print to console
    """
    verification_url = f"{request.base_url}v1/auth/verify-email?token={token}"
    
    if os.getenv("ENVIRONMENT") == "production":
        # Actual email sending logic for production
        # Use SendGrid, Mailgun, etc.
        pass
    else:
        # Development mode - print to console
        print(f"Verification email for: {email}")
        print(f"Verification URL: {verification_url}")
        print(f"Token: {token}")

# Endpoint to Register
@router.post("/register", response_model=UserOut)
async def register_user(user: UserRegister, request: Request, background_tasks: BackgroundTasks):
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
        user_id = row["id"]
        # Generate verification token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Store verification token
        await conn.execute(
            """
            INSERT INTO verification_tokens (token, user_id, expires_at)
            VALUES ($1, $2, $3)
            """,
            verification_token, user_id, expires_at
        )

        # Send verification email in background
        background_tasks.add_task(send_verification_email, user.email, verification_token, request)
        return dict(row)

@router.get("/verify-email")
async def verify_email(token: str, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Check if token exists and is valid
        token_data = await conn.fetchrow(
            """
            SELECT vt.*, u.id as user_id, u.email 
            FROM verification_tokens vt
            JOIN app_user u ON vt.user_id = u.id
            WHERE vt.token = $1 AND vt.expires_at > NOW()
            """,
            token
        )
        
        if not token_data:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Activate user
        await conn.execute(
            "UPDATE app_user SET is_active = TRUE WHERE id = $1",
            token_data["user_id"]
        )
        
        # Delete used token
        await conn.execute(
            "DELETE FROM verification_tokens WHERE token = $1",
            token
        )
        
        return {"message": "Email verified successfully! You can now login."}

@router.post("/resend-verification")
async def resend_verification(email: str, request: Request, background_tasks: BackgroundTasks):
    async with request.app.state.pool.acquire() as conn:
        # Check if user exists and is not verified
        user = await conn.fetchrow(
            "SELECT id, is_active FROM app_user WHERE email = $1",
            email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user["is_active"]:
            raise HTTPException(status_code=400, detail="Email already verified")
        
        # Delete any existing tokens
        await conn.execute(
            "DELETE FROM verification_tokens WHERE user_id = $1",
            user["id"]
        )
        
        # Generate new token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        await conn.execute(
            "INSERT INTO verification_tokens (token, user_id, expires_at) VALUES ($1, $2, $3)",
            verification_token, user["id"], expires_at
        )
        
        # Resend email
        background_tasks.add_task(send_verification_email, email, verification_token, request)
        
        return {"message": "Verification email sent successfully"}
    
# Endpoint to Login
@router.post("/login")
async def login_user(user: UserLogin, request: Request):
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

# Endpoint to change password
@router.post("/change-password")
async def change_password(
    email: str = Body(..., embed=True),   # or use JWT later for authenticated user
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    confirm_new_password: str = Body(..., embed=True),
    request: Request = None
):
    if new_password != confirm_new_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    async with request.app.state.pool.acquire() as conn:
        # fetch user
        db_user = await conn.fetchrow("SELECT * FROM app_user WHERE email=$1", email)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # verify old password
        if not verify_password(old_password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Old password is incorrect")

        # hash new password
        hashed_password = hash_password(new_password)

        # update DB
        await conn.execute(
            "UPDATE app_user SET password_hash=$1 WHERE email=$2",
            hashed_password, email
        )

        return {"message": "Password changed successfully"}