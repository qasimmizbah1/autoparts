from fastapi import Request, UploadFile, APIRouter, Form, File, Depends, Query, BackgroundTasks
from uuid import UUID, uuid4
from services.browse_part_request_service import get_all_parts_request_service, search_part_request_service,create_quote_service, update_quote_service
from typing import Optional, List
from models import QuoteCreate, QuoteUpdate, PartRequestSearch
from datetime import date
from deps import require_supplier


router = APIRouter(prefix="/v1/supplier", tags=["Part Requests"])



#Create Quote
@router.post("/quote/")
async def create_quote(request: Request, data: QuoteCreate, background_tasks: BackgroundTasks):
     return await create_quote_service(
        request,
        data.request_id,
        data.supplier_id,
        data.price_cents,
        data.currency,
        data.eta_days,
        data.terms
    )


@router.put("/quote/{quote_id}")
async def update_quote(request: Request, quote_id: UUID, data: QuoteUpdate):
    return await update_quote_service(
        request,
        quote_id,
        data.price_cents,
        data.currency,
        data.eta_days,
        data.terms,
    )


#browse all request
@router.get("/all/part-request/")
async def get_allparts_request(request: Request):
    return await get_all_parts_request_service(request)


#search Request 
@router.post("/search/part-request/")
async def search_part_requests(request: Request, filters: PartRequestSearch):
    return await search_part_request_service(
        request,
        filters.title,
        filters.urgency,
        filters.description,
        filters.vehicle_make,
        filters.vehicle_model,
    )
