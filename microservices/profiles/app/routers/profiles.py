from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerProfileData, SupplierProfileData, BuyerAddressSchema
from uuid import UUID
from services.profile_service import view_users_profile, get_user_profile
from services.buyer_service import upsert_buyer_service, buyer_address_service, buyer_update_address_service
from services.supplier_service import upsert_supplier_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/")
async def view_profiles(request: Request):
    return await view_users_profile(request)

    
@router.post("/user")
async def get_user(data: UserRequest, request: Request):
    return await get_user_profile(data, request)

    

# Upsert Buyer Profile
@router.patch("/buyer/{user_id}")
async def upsert_buyer_profile(user_id: UUID, data: BuyerProfileData, request: Request):
    return await upsert_buyer_service(user_id,data, request)
    

# Upsert Buyer Profile
@router.patch("/supplier/{user_id}")
async def upsert_supplier_profile(user_id: UUID, data: SupplierProfileData, request: Request):
    return await upsert_supplier_service(user_id,data, request)


#Add Address
@router.post("/address/{buyer_id}")
async def buyer_address(buyer_id: UUID, data: BuyerAddressSchema, request: Request):
    return await buyer_address_service(buyer_id,data, request)

#update Address
@router.patch("/address/{address_id}")
async def buyer_update_address(address_id: UUID, data: BuyerAddressSchema, request: Request):
    return await buyer_update_address_service(address_id,data, request)