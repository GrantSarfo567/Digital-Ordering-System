from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone: str
    logo_url: Optional[str] = None

class RestaurantResponse(BaseModel):
    id: UUID
    name: str
    address: str
    phone: str
    logo_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime