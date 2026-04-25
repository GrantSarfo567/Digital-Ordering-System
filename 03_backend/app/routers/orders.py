from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.models.order import OrderCreate
from app.services.order_service import (
    create_order,
    get_order,
    get_order_history,
    update_order_status,   # ✅ IMPORTANT
)
from app.middleware.auth import get_current_user
from app.core.supabase import supabase

router = APIRouter()


# -------------------------
# MODELS
# -------------------------
class StatusUpdate(BaseModel):
    status: str = Field(..., description="Target status")


# -------------------------
# CREATE ORDER
# -------------------------
@router.post("/")
def place_order(data: OrderCreate, current_user=Depends(get_current_user)):
    try:
        result = create_order(str(current_user.id), data.model_dump(mode="json"))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# ORDER HISTORY
# -------------------------
@router.get("/history")
def order_history(current_user=Depends(get_current_user)):
    try:
        result = get_order_history(str(current_user.id))
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# LIST ORDERS (ADMIN)
# -------------------------
@router.get("/")
def list_orders(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    current_user=Depends(get_current_user),
):
    try:
        query = supabase.table("orders").select("*").order("created_at", desc=True)

        if status:
            status = status.upper()
            query = query.eq("status", status)

        response = query.range(offset, offset + limit - 1).execute()

        return {
            "success": True,
            "data": response.data,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# GET SINGLE ORDER
# -------------------------
@router.get("/{order_id}")
def get_one(order_id: str, current_user=Depends(get_current_user)):
    try:
        order = get_order(order_id)

        if not order:
            raise HTTPException(404, "Order not found")

        if order["user_id"] != str(current_user.id):
            raise HTTPException(403, "Unauthorized")

        return {"success": True, "data": order}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -------------------------
# UPDATE ORDER STATUS (FIXED)
# -------------------------
@router.patch("/{order_id}/status")
def update_status(order_id: str, body: StatusUpdate, user=Depends(get_current_user)):
    return update_order_status(order_id, body.status, user.id)