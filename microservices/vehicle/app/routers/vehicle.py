from fastapi import Request, HTTPException, APIRouter
from uuid import UUID, uuid4
from models import VehicleMake, VehicleModel, VehicleTrim
from services.vechile_service import get_makes_service, get_models_service, get_trims_service

router = APIRouter(prefix="/v1", tags=["Vehicle"])

# --- Vehicle Make ---

@router.get("/vehicle/view/")
async def get_makes(request: Request):
    return await get_makes_service(request)
    
@router.get("/vehicle/model/")
async def get_models(request: Request):
    return await get_models_service(request)

@router.get("/vehicle/trim/")
async def get_trims(request: Request):
    return await get_trims_service(request)


