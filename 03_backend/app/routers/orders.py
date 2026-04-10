from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.models.order import OrderCreate, OrderResponse
from app.services.order_service import (
    create_order,
    get_order,
    get_order_history,
    update_order_status
)
from app.middleware.auth import get_current_user
from typing import List

router = APIRouter()

class StatusUpdate(BaseModel):
    status: str

@router.post("/")
def place_order(data: OrderCreate, current_user=Depends(get_current_user)):
    try:
        return create_order(str(current_user.id), data.model_dump(mode="json"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/history")
def order_history(current_user=Depends(get_current_user)):
    try:
        return get_order_history(str(current_user.id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}")
def get_one(order_id: str, current_user=Depends(get_current_user)):
    try:
        order = get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{order_id}/status")
def update_status(order_id: str, body: StatusUpdate, current_user=Depends(get_current_user)):
    try:
        return update_order_status(order_id, body.status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))