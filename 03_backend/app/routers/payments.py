from fastapi import APIRouter, HTTPException, Depends
from app.core.supabase import supabase
from app.middleware.auth import get_current_user

router = APIRouter()


@router.patch("/{payment_id}/confirm-delivery-payment")
def confirm_delivery_payment(payment_id: str, current_user=Depends(get_current_user)):

    response = (
        supabase.table("payments")
        .select("*")
        .eq("id", payment_id)
        .maybe_single()
        .execute()
    )

    payment = response.data

    if not payment:
        raise HTTPException(404, "Payment not found")

    # Idempotency
    if payment["payment_status"] == "PAID_ON_DELIVERY":
        return {"success": True, "message": "Already confirmed"}

    # Validate type
    if payment["payment_status"] != "PENDING_PAY_ON_DELIVERY":
        raise HTTPException(400, "Not a pay-on-delivery payment")

    # Update payment
    supabase.table("payments").update({
        "payment_status": "PAID_ON_DELIVERY"
    }).eq("id", payment_id).execute()

    # Update order
    supabase.table("orders").update({
        "status": "DELIVERED"
    }).eq("id", payment["order_id"]).execute()

    return {"success": True, "message": "Payment confirmed on delivery"}