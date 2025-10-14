from pydantic import BaseModel, Field, UUID4, EmailStr
from uuid import UUID
from typing import Literal
from datetime import datetime
import re
from typing import Optional, Dict, Any, Literal

class UserRequest(BaseModel):
    user_id: UUID4


class BuyerProfileData(BaseModel):
    name: str
    company_name: str 
    vat_number: str


class SupplierProfileData(BaseModel):
    name: str
    company_name: str
    kyc_status: str


LogLevel = Literal['DEBUG','INFO','WARNING','ERROR','CRITICAL','AUDIT']

class LogCreate(BaseModel):
    user_id: Optional[UUID4] = None
    level: LogLevel = 'INFO'
    action: str
    path: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class LogOut(BaseModel):
    id: UUID4
    user_id: Optional[UUID4]
    level: LogLevel
    action: str
    path: Optional[str]
    ip: Optional[str]
    user_agent: Optional[str]
    meta: Dict[str, Any]
    created_at: datetime

class LogListOut(BaseModel):
    items: list[LogOut]
    page: int
    page_size: int
    total: int
    pages: int

class BuyerUpdate(BaseModel):
    is_active: Optional[bool] = None
    buyer_name: Optional[str] = None
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    

class SupplierUpdate(BaseModel):
    is_active: Optional[bool] = None
    supplier_name: Optional[str] = None
    company_name: Optional[str] = None
    kyc_status: Optional[str] = None


class VehicleMake(BaseModel):
    name: str

class VehicleModel(BaseModel):
    make_id: UUID
    name: str

class VehicleTrim(BaseModel):
    make_id: UUID
    model_id: UUID
    year_from: Optional[int]
    year_to: Optional[int]
    trim: Optional[str]