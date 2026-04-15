from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.payments.payment_service import create_payment, get_payment
from app.middleware.auth import get_current_user   # ✅ correct import

router = APIRouter(prefix="/payments", tags=["Payments"])


class CreatePaymentRequest(BaseModel):
    order_id: str
    phone: str


@router.post("/")
def create_payment_endpoint(
    request: CreatePaymentRequest,
    user=Depends(get_current_user)
):
    """
    ✅ FIXED:
    - Uses Supabase authenticated user
    - No user_id from client
    """

    result = create_payment(
        order_id=request.order_id,
        user_id=user.id,   # ✅ THIS IS CORRECT FOR YOUR AUTH
        phone=request.phone
    )

    return {
        "success": True,
        "message": "Payment initiated successfully",
        **result
    }


@router.get("/{payment_id}")
def get_payment_status(
    payment_id: str,
    user=Depends(get_current_user)
):
    payment = get_payment(payment_id)

    # ✅ FIXED: ownership check
    if payment["user_id"] != user.id:
        raise Exception("Unauthorized")

    return payment