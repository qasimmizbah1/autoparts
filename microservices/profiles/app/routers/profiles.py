from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerProfileData, SupplierProfileData
from uuid import UUID
from services.profile_service import view_users_profile, get_user_profile
from services.buyer_service import upsert_buyer_service
from services.supplier_service import upsert_supplier_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/")
async def view_profiles(request: Request):
    return await view_users_profile(request)

    
@router.post("/user")
async def get_user(data: UserRequest, request: Request):
    return await get_user_profile(data, request)

    

# Upsert Buyer Profile
@router.post("/buyer/{user_id}")
async def upsert_buyer_profile(user_id: UUID, data: BuyerProfileData, request: Request):
    return await upsert_buyer_service(user_id,data, request)
    

# Upsert Buyer Profile
@router.post("/supplier/{user_id}")
async def upsert_supplier_profile(user_id: UUID, data: SupplierProfileData, request: Request):
    return await upsert_supplier_service(user_id,data, request)
