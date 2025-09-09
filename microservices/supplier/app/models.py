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


class PartRequestInDB(PartRequest):
    id: UUID
    created_at: datetime
    updated_at: datetime

class QuoteCreate(BaseModel):
    request_id: UUID
    supplier_id: UUID
    price_cents: int
    currency: str = "ZAR"
    eta_days: Optional[int] = None
    terms: Optional[str] = None

class QuoteUpdate(BaseModel):
    price_cents: Optional[int] = None
    currency: Optional[str] = None
    eta_days: Optional[int] = None
    terms: Optional[str] = None


class PartRequestSearch(BaseModel):
    title: Optional[str] = None
    urgency: Optional[str] = None
    description: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None