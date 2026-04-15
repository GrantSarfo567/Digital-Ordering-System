from app.core.supabase import supabase
from app.services.payments.payment_dispatcher import route_payment
from app.services.payments.payment_state import validate_payment_update, PaymentStatus
from app.services.payments.payment_utils import (
    generate_idempotency_key,
    generate_external_reference,
    normalize_phone,
    validate_amount
)
from app.services.payments.payment_models import Payment
import uuid


def create_payment(order_id: str, user_id: str, phone: str):
    """
    ✅ FIXED:
    - Removed amount from input (now fetched from order)
    - Enforces order ownership
    """

    phone = normalize_phone(phone)

    # -------------------------
    # ✅ FIXED: FETCH ORDER FROM DB
    # -------------------------
    order_response = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not order_response.data:
        raise Exception("Order not found")

    order = order_response.data

    payment_method = order.get("payment_method", "momo")

    # -------------------------
    # ✅ FIXED: VERIFY USER OWNS ORDER
    # -------------------------
    if order["user_id"] != user_id:
        raise Exception("Unauthorized: cannot pay for another user's order")

    # -------------------------
    # ✅ FIXED: EXTRACT AMOUNT FROM ORDER
    # -------------------------
    amount = float(order["total"])  # adjust if needed
    validate_amount(amount)

    # -------------------------
    # GENERATE IDS
    # -------------------------
    idempotency_key = generate_idempotency_key(order_id)
    external_reference = generate_external_reference(order_id)
    payment_id = str(uuid.uuid4())

    payment_record = {
        "id": payment_id,
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "currency": "GHS",  # internal currency
        "phone": phone,
        "payment_status": PaymentStatus.PENDING.value,
        "idempotency_key": idempotency_key,
        "external_reference": external_reference,
        "payment_method": payment_method
    }

    # -------------------------
    # INSERT WITH IDEMPOTENCY
    # -------------------------
    try:
        insert_response = supabase.table("payments").insert(payment_record).execute()
    except Exception:
        existing = (
            supabase.table("payments")
            .select("*")
            .eq("idempotency_key", idempotency_key)
            .maybe_single()   # ✅ FIXED (was causing errors before)
            .execute()
        )

        if existing.data:
            return {
                "payment_id": existing.data["id"],
                "status": existing.data["payment_status"]
            }

        raise

    if not insert_response.data:
        raise Exception("Failed to create payment")

    payment_data = insert_response.data[0]
    payment = Payment(**payment_data)


        # -------------------------
    # ✅ FIXED: HANDLE CASH ON DELIVERY
    # -------------------------
    if payment_method == "cash":
        supabase.table("payments").update({
            "payment_status": "pending_cash"
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": "pending_cash"
        }

    # -------------------------
    # ROUTE PAYMENT
    # -------------------------
    try:
        provider_response = route_payment(payment)
    except Exception as e:
        supabase.table("payments").update({
            "payment_status": PaymentStatus.FAILED.value,
            "failure_reason": str(e)
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": "failed",
            "message": str(e)
        }

    if not provider_response or not provider_response.success:
        supabase.table("payments").update({
            "payment_status": PaymentStatus.FAILED.value,
            "failure_reason": provider_response.message if provider_response else "Unknown error"
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": "failed",
            "message": provider_response.message if provider_response else "Unknown error"
        }

    # -------------------------
    # TRANSITION → PROCESSING
    # -------------------------
    try:
        if validate_payment_update(
            PaymentStatus.PENDING.value,
            PaymentStatus.PROCESSING.value
        ):
            update_data = {
                "payment_status": PaymentStatus.PROCESSING.value
            }

            if provider_response.transaction_id:
                update_data["transaction_id"] = provider_response.transaction_id

            supabase.table("payments").update(update_data).eq("id", payment_id).execute()

    except Exception as e:
        supabase.table("payments").update({
            "payment_status": PaymentStatus.FAILED.value,
            "failure_reason": str(e)
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": "failed",
            "message": str(e)
        }

    return {
        "payment_id": payment_id,
        "status": "processing"
    }

def get_payment(payment_id: str):
    response = (
        supabase.table("payments")
        .select("*")
        .eq("id", payment_id)
        .maybe_single()   # ✅ safer
        .execute()
    )

    if not response.data:
        raise Exception("Payment not found")

    return response.data