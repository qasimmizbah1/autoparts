from fastapi import Request, HTTPException, APIRouter
from services.vechile_service import get_makes_service, get_models_service, delete_make_service
from uuid import UUID
router = APIRouter(prefix="/v1/vehicle", tags=["Vehicle"])

# --- Vehicle Make ---

@router.get("/view/")
async def get_makes(request: Request):
    return await get_makes_service(request)
    
@router.get("/model/{make_name}")
async def get_models(make_name: str, request: Request):
    return await get_models_service(make_name, request)


@router.delete("/{make_id}", status_code=200)
async def delete_make(make_id: UUID, request: Request):
    return await delete_make_service(make_id, request)



