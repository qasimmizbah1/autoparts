from fastapi import Request, HTTPException, APIRouter
from services.vechile_service import get_makes_service, get_models_service, delete_make_service,delete_model_service,delete_trim_service
from uuid import UUID
router = APIRouter(prefix="/v1/vehicle", tags=["Vehicle"])

# --- Vehicle Make ---

@router.get("/view/")
async def get_makes(request: Request):
    return await get_makes_service(request)
    
@router.get("/model/{make_name}")
async def get_models(make_name: str, request: Request):
    return await get_models_service(make_name, request)


@router.delete("/make/{make_id}", status_code=200)
async def delete_make(make_id: UUID, request: Request):
    return await delete_make_service(make_id, request)


@router.delete("/model/{model_id}", status_code=200)
async def delete_model(model_id: UUID, request: Request):
    return await delete_model_service(model_id, request)


@router.delete("/trim/{trim_id}", status_code=200)
async def delete_trim(trim_id: UUID, request: Request):
    return await delete_trim_service(trim_id, request)


