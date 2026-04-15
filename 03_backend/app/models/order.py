from pydantic import BaseModel, field_validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int
    price: float

class OrderCreate(BaseModel):
    restaurant_id: UUID
    items: List[OrderItemCreate]
    delivery_location: str
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    payment_method: Optional[str] = "momo"  # ✅ SAFE DEFAULT

    @field_validator("payment_method")
    def validate_payment_method(cls, v):
        if v not in ["momo", "cash"]:
            raise ValueError("payment_method must be 'momo' or 'cash'")
        return v

class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    restaurant_id: UUID
    total: float
    status: str
    delivery_location: str
    created_at: datetime
    updated_at: datetime