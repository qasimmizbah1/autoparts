from fastapi import Request, UploadFile, APIRouter, Form, File, Depends
from uuid import UUID, uuid4
from models import VehicleMake, VehicleModel, VehicleTrim
from services.vechile_service import get_makes_service, get_models_service, get_trims_service
from services.part_request_service import create_part_request_service, get_parts_request_service, get_all_parts_request_service, delete_parts_request_service, update_part_request_service
from typing import Optional, List
from models import PartRequest, PartRequestInDB
from datetime import date
from deps import require_buyer

router = APIRouter(prefix="/v1/buyer", tags=["Part Requests"])



# --- Vehicle Make ---

# @router.get("/vehicle/make/")
# async def get_makes(request: Request):
#     return await get_makes_service(request)
    
# @router.get("/vehicle/model/{make_id}")
# async def get_models(make_id: str, request: Request):
#     return await get_models_service(make_id, request)

# @router.get("/vehicle/trim/{model_id}")
# async def get_trims(model_id: str, request: Request):
#     return await get_trims_service(model_id, request)


#Create Request
@router.post("/part-request", response_model=PartRequest, dependencies=[Depends(require_buyer)])
async def create_part_request(
    request: Request,
    user_id: UUID = Form(...),
    title: str = Form(...),
    urgency: str = Form(...),
    vehicle_make: str = Form(...),
    vehicle_model: str = Form(...),
    vehicle_model_trim: str = Form(...),
    required_by_date: Optional[date] = Form(None),
    description: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
):
    return await create_part_request_service(request,user_id,title,urgency,vehicle_make,vehicle_model,vehicle_model_trim,required_by_date,description,attachment)

#update Request
@router.put("/part-request/{part_request_id}", response_model=PartRequestInDB, dependencies=[Depends(require_buyer)])
async def update_part_request(
    part_request_id: UUID,
    request: Request,
    title: Optional[str] = Form(None),
    urgency: Optional[str] = Form(None),
    vehicle_make: Optional[str] = Form(None),
    vehicle_model: Optional[str] = Form(None),
    vehicle_model_trim: Optional[str] = Form(None),
    required_by_date: Optional[date] = Form(None),
    description: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
):
    return await update_part_request_service(request, part_request_id, title, urgency, vehicle_make, vehicle_model, vehicle_model_trim, required_by_date, description, attachment)

#view by user id
@router.get("/all/part-request/{user_id}", dependencies=[Depends(require_buyer)])
async def get_allparts_request(user_id:str, request: Request):
    return await get_all_parts_request_service(user_id, request)

#view by id
@router.get("/part-request/{part_request_id}", dependencies=[Depends(require_buyer)])
async def get_parts_request(part_request_id:str, request: Request):
    return await get_parts_request_service(part_request_id, request)

#delete by id
@router.delete("/part-request/{part_request_id}", dependencies=[Depends(require_buyer)])
async def delete_parts_request(part_request_id:str, request: Request):
    return await delete_parts_request_service(part_request_id, request)