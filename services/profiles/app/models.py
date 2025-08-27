from pydantic import BaseModel, EmailStr
from typing import Literal
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: Literal["buyer", "supplier", "admin"] = "buyer"  # only allowed roles
    is_active: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str                 # UUID as string
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime


