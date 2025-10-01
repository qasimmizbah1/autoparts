from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class PartRequest(BaseModel):
    user_id: UUID
    title: str
    description: Optional[str] = None
    urgency: str   # must be 'low', 'normal', 'high', or 'critical'
    required_by_date: Optional[date] = None
    vehicle_make: str
    vehicle_model: str
    vehicle_model_trim: str
    attachment: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PartRequestInDB(PartRequest):
    id: UUID
    created_at: datetime
    updated_at: datetime

class AcceptQuoteSchema(BaseModel):
    quote_id: str  # or UUID if you want

class ViewQuoteSchema(BaseModel):
    request_id: UUID  # UUID directly from JSON body


class OrderCreate(BaseModel):
    quote_id: UUID
    buyer_id: UUID
    supplier_id: UUID
    shipping_to_address_id: Optional[UUID] = None
    shipping_from_address_id: Optional[UUID] = None
    status: Optional[str] = "PENDING_HOLD"

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    shipping_to_address_id: Optional[UUID] = None
    shipping_from_address_id: Optional[UUID] = None

    