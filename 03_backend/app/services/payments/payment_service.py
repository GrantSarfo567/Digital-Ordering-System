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
from app.services.payments.payment_utils import detect_network  # 🔥 ADD IMPORT
import uuid


# 🔥 FIX: make function async (needed for provider calls)
async def create_payment(order_id: str, user_id: str, phone: str):
    """
    ✅ FIXED:
    - Removed amount from input (now fetched from order)
    - Enforces order ownership
    """

    phone = normalize_phone(phone)

    # -------------------------
    # FETCH ORDER FROM DB
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
    # VERIFY USER OWNS ORDER
    # -------------------------
    if order["user_id"] != user_id:
        raise Exception("Unauthorized: cannot pay for another user's order")

    # -------------------------
    # EXTRACT AMOUNT FROM ORDER
    # -------------------------
    amount = float(order["total"])
    validate_amount(amount)

    # -------------------------
    # GENERATE IDS
    # -------------------------
    idempotency_key = generate_idempotency_key(order_id)
    external_reference = generate_external_reference(order_id)
    payment_id = str(uuid.uuid4())

    network = detect_network(phone)

    payment_record = {
        "id": payment_id,
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "currency": "GHS",
        "phone": phone,
        "network": network,  # 🔥 ADD THIS LINE
        "payment_status": PaymentStatus.PENDING.value,
        "idempotency_key": idempotency_key,
        "external_reference": external_reference,
        "payment_method": payment_method,
        "provider": "paystack"
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
            .maybe_single()
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

    generated_email = f"user_{payment.user_id}@darks.app"  # 🔥 NEW

    # -------------------------
    # HANDLE CASH ON DELIVERY
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
        # 🔥 FIX: route_payment should now RETURN provider (not execute)
        provider = route_payment(payment)

        # 🔥 FIX: actually call provider (MTN or Paystack)
        provider_response = await provider.initiate_payment(payment, email=generated_email)

    except Exception as e:
        # 🔥 OPTIONAL FAILOVER: fallback to Paystack
        from app.services.payments.providers.paystack import PaystackProvider

        paystack_provider = PaystackProvider()

        try:
            provider_response = await paystack_provider.initiate_payment(payment, email=generated_email)
        except Exception as fallback_error:
            supabase.table("payments").update({
                "payment_status": PaymentStatus.FAILED.value,
                "failure_reason": str(fallback_error)
            }).eq("id", payment_id).execute()

            return {
                "payment_id": payment_id,
                "status": "failed",
                "message": str(fallback_error)
            }

    # -------------------------
    # HANDLE FAILURE RESPONSE
    # -------------------------
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

            # 🔥 FIX: handle both MTN + Paystack reference
            if hasattr(provider_response, "transaction_id") and provider_response.transaction_id:
                update_data["transaction_id"] = provider_response.transaction_id

            if hasattr(provider_response, "external_reference") and provider_response.external_reference:
                update_data["external_reference"] = provider_response.external_reference

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

    # -------------------------
    # RESPONSE TO CLIENT
    # -------------------------
    return {
        "payment_id": payment_id,
        "status": "processing",
        # 🔥 FIX: return Paystack checkout URL if available
        "checkout_url": getattr(provider_response, "checkout_url", None)
    }


def get_payment(payment_id: str):
    response = (
        supabase.table("payments")
        .select("*")
        .eq("id", payment_id)
        .maybe_single()
        .execute()
    )

    if not response.data:
        raise Exception("Payment not found")

    return response.data


async def update_payment_status(reference: str, status: str):
    """
    Called by webhook to update payment + order
    """

    # 1. Find payment by reference
    payment = (
        supabase.table("payments")
        .select("*")
        .eq("external_reference", reference)
        .maybe_single()
        .execute()
    )

    if not payment.data:
        print("Payment not found:", reference)
        return

    payment_data = payment.data

    # 2. Update payment
    supabase.table("payments").update({
        "payment_status": status
    }).eq("id", payment_data["id"]).execute()

    # 3. If successful → update order
    if status == "successful":
        supabase.table("orders").update({
            "status": "paid"
        }).eq("id", payment_data["order_id"]).execute()

    print(f"Payment {reference} updated → {status}")