from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: float
    image_url: Optional[str] = None

class MenuItemResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    description: Optional[str] = None
    category: str
    price: float
    image_url: Optional[str] = None
    is_available: bool
    created_at: datetime
    updated_at: datetime