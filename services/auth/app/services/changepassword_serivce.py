from fastapi import HTTPException, Request
from utils.security import verify_password
from utils.security import hash_password, verify_password 


async def user_change_password_service(
    email, old_password,new_password,confirm_new_password,request: Request = None
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