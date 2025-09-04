from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerUpdate, SupplierUpdate, VehicleMake, VehicleModel, VehicleTrim
from uuid import UUID, uuid4
from deps import require_admin
from services.vehicle_service import add_make_service, update_make_service, add_model_service, update_model_service, add_trim_service, update_trim_service

router = APIRouter(prefix="/v1/admin/vehicle", tags=["Manage Vehicle"])


#vechile Make
@router.post("/make/")
async def add_make(make: VehicleMake, request: Request):
    return await add_make_service(make, request)

@router.put("/make/{make_id}")
async def update_make(make_id: UUID, make: VehicleMake, request: Request):
    return await update_make_service(make_id, make, request)


# --- Vehicle Model ---
@router.post("/model/")
async def add_model(model: VehicleModel, request: Request):
    return await add_model_service(model, request)
        

@router.put("/model/{model_id}")
async def update_model(model_id: UUID, model: VehicleModel, request: Request):
    return await update_model_service(model_id, model, request)
    

# --- Vehicle Trim ---
@router.post("/trim/")
async def add_trim(trim: VehicleTrim, request: Request):
    return await add_trim_service(trim, request)
        
@router.put("/trim/{trim_id}")
async def update_trim(trim_id: UUID, trim: VehicleTrim, request: Request):
    return await update_trim_service(trim_id, trim, request)
    