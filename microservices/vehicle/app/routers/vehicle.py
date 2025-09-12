from fastapi import Request, HTTPException, APIRouter
from services.vechile_service import get_makes_service, get_models_service

router = APIRouter(prefix="/v1/vehicle", tags=["Vehicle"])

# --- Vehicle Make ---

@router.get("/view/")
async def get_makes(request: Request):
    return await get_makes_service(request)
    
@router.get("/model/{make_name}")
async def get_models(make_name: str, request: Request):
    return await get_models_service(make_name, request)



