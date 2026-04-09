from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    phone: str

class UserResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    is_active: bool
    created_at: datetime