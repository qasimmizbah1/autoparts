from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerUpdate, SupplierUpdate
from uuid import UUID
from deps import require_admin
from services.users_service import view_buyer_service, view_supplier_service, get_user_buyer_service, get_user_sup_service, delete_user_service, update_buyer_service, update_supplier_service

router = APIRouter(prefix="/v1/admin/manage-users", tags=["Manage Users"])


@router.get("/buyer", dependencies=[Depends(require_admin)])
async def view_buyer_profiles(request: Request):
    return await view_buyer_service(request)

@router.get("/supplier", dependencies=[Depends(require_admin)])
async def view_supplier_profiles(request: Request):
    return await view_supplier_service(request)


@router.post("/buyer", dependencies=[Depends(require_admin)])
async def get_buy_user(data: UserRequest, request: Request):
    return await get_user_buyer_service(data, request)
    

@router.post("/supplier", dependencies=[Depends(require_admin)])
async def get_sup_user(data: UserRequest, request: Request):
    return await get_user_sup_service(data, request)
    


@router.delete("/{user_id}", status_code=200)
async def delete_log(user_id: UUID, request: Request):
    return await delete_user_service(user_id, request)



@router.patch("/buyer/{user_id}", response_model=dict, dependencies=[Depends(require_admin)])
async def update_buyer(user_id: UUID, user_update: BuyerUpdate, request: Request):
    return await update_buyer_service(user_id, user_update, request)


@router.patch("/supplier/{user_id}", response_model=dict, dependencies=[Depends(require_admin)])
async def update_supplier(user_id: UUID, supplier_update: SupplierUpdate, request: Request):
    return await update_supplier_service(user_id, supplier_update, request)
