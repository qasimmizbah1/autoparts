from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class VehicleMake(BaseModel):
    name: str

class VehicleModel(BaseModel):
    make_id: UUID
    name: str

class VehicleTrim(BaseModel):
    model_id: UUID
    year_from: Optional[int]
    year_to: Optional[int]
    trim: Optional[str]


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

    