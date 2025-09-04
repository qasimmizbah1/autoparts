from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from typing import Optional, List


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
