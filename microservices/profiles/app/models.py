from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
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
