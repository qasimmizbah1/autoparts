from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import re
from uuid import UUID


class UserRequest(BaseModel):
    user_id: UUID


class BuyerProfileData(BaseModel):
    name: str
    company_name: str 
    vat_number: str


class SupplierProfileData(BaseModel):
    name: str
    company_name: str
    kyc_status: str

class BuyerAddressSchema(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "ZA"

class SupplierAddressSchema(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "ZA"


    