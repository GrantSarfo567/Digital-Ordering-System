from app.core.supabase import supabase
from app.services.payments.payment_state import validate_payment_update, PaymentStatus
from app.services.payments.payment_utils import (
    generate_idempotency_key,
    generate_external_reference,
    normalize_phone,
    validate_amount,
    detect_network
)
from app.services.payments.payment_models import Payment
from app.services.payments.providers.paystack import PaystackProvider
from fastapi import HTTPException
from datetime import datetime, timezone

import uuid


# -------------------------
# CREATE PAYMENT
# -------------------------
async def create_payment(order_id: str, user_id: str, phone: str):

    phone = normalize_phone(phone)

    # -------------------------
    # FETCH ORDER
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

    # -------------------------
    # VERIFY OWNERSHIP
    # -------------------------
    if order["user_id"] != user_id:
        raise Exception("Unauthorized")

    amount = float(order["total"])
    validate_amount(amount)

    # -------------------------
    # 🔥 FIX: NORMALIZE PAYMENT METHOD
    # -------------------------
    payment_method = (order.get("payment_method") or "").strip().lower()

    if payment_method in ["pay on delivery", "pay_on_delivery", "cod"]:
        payment_method = "pay_on_delivery"
    elif payment_method in ["momo", "paystack"]:
        payment_method = "paystack"
    else:
        raise Exception(f"Unsupported payment method: {payment_method}")

    # -------------------------
    # IDS
    # -------------------------
    idempotency_key = generate_idempotency_key(order_id)
    payment_id = str(uuid.uuid4())

    network = detect_network(phone)

    # -------------------------
    # INITIAL VALUES
    # -------------------------
    external_reference = None
    provider_name = None

    if payment_method == "paystack":
        external_reference = generate_external_reference(order_id)
        provider_name = "paystack"

    payment_record = {
        "id": payment_id,
        "order_id": order_id,
        "user_id": user_id,
        "amount": amount,
        "currency": "GHS",
        "phone": phone,
        "network": network,
        "payment_status": PaymentStatus.PENDING.value,
        "idempotency_key": idempotency_key,
        "external_reference": external_reference,
        "payment_method": payment_method,
        "provider": provider_name
    }

    # -------------------------
    # INSERT (IDEMPOTENT)
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

        if existing and existing.data:
            return {
                "payment_id": existing.data["id"],
                "status": existing.data["payment_status"]
            }

        raise

    if not insert_response.data:
        raise Exception("Failed to create payment")

    payment_data = insert_response.data[0]
    payment = Payment(**payment_data)

    generated_email = f"user_{payment.user_id}@darks.app"

    # -------------------------
    # CASH HANDLING (COD)
    # -------------------------
    if payment_method == "pay_on_delivery":
        supabase.table("payments").update({
            "payment_status": PaymentStatus.PENDING_PAY_ON_DELIVERY.value
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": PaymentStatus.PENDING_PAY_ON_DELIVERY.value
        }

    # -------------------------
    # PAYSTACK INIT
    # -------------------------
    provider = PaystackProvider()

    try:
        provider_response = await provider.initiate_payment(payment, email=generated_email)
    except Exception as e:
        supabase.table("payments").update({
            "payment_status": PaymentStatus.FAILED.value,
            "failure_reason": str(e)
        }).eq("id", payment_id).execute()

        return {
            "payment_id": payment_id,
            "status": "FAILED",
            "message": str(e)
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
            "status": "FAILED",
            "message": provider_response.message if provider_response else "Unknown error"
        }

    # -------------------------
    # UPDATE → PROCESSING
    # -------------------------
    update_data = {
        "payment_status": PaymentStatus.PROCESSING.value
    }

    if provider_response.external_reference:
        update_data["external_reference"] = provider_response.external_reference

    supabase.table("payments").update(update_data).eq("id", payment_id).execute()

    return {
        "payment_id": payment_id,
        "status": "PROCESSING",
        "checkout_url": getattr(provider_response, "checkout_url", None)
    }


# -------------------------
# GET PAYMENT
# -------------------------
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


# -------------------------
# UPDATE PAYMENT (WEBHOOK)
# -------------------------
async def update_payment_status(reference: str, status: str):

    print("Looking for payment:", reference)

    response = (
        supabase.table("payments")
        .select("*")
        .eq("external_reference", reference)
        .maybe_single()
        .execute()
    )

    payment = response.data

    if not payment:
        print("⚠️ Payment not found:", reference)
        return

    # Ensure it's a Paystack payment
    if payment.get("provider") != "paystack":
        print("⚠️ Not a Paystack payment → ignoring")
        return

    status = status.upper()

    if status not in [
        PaymentStatus.SUCCESSFUL.value,
        PaymentStatus.FAILED.value
    ]:
        print("⚠️ Invalid status → ignoring")
        return

    # Idempotency
    if payment["payment_status"] == PaymentStatus.SUCCESSFUL.value:
        print("Already processed")
        return

    # Validate transition
    validate_payment_update(payment["payment_status"], status)

    # Update payment
    supabase.table("payments").update({
        "payment_status": status
    }).eq("id", payment["id"]).execute()

    print(f"✅ Payment {reference} → {status}")

    # -------------------------
    # ORDER SYNC(FIXED)
    # -------------------------

    if status in ["SUCCESS", "SUCCESSFUL", PaymentStatus.SUCCESSFUL.value]:

        now = datetime.now(timezone.utc).isoformat()

        supabase.table("orders").update({
            "status": "PAID",
            "paid_at": now
        }).eq("id", payment["order_id"]).execute()

        print(f"Order {payment['order_id']} → PAID (paid_at set)")


    elif status in ["FAILED", "FAILURE", PaymentStatus.FAILED.value]:

        supabase.table("orders").update({
            "status": "CANCELLED"
        }).eq("id", payment["order_id"]).execute()

        print(f"Order {payment['order_id']} → CANCELLED")


# -------------------------
# CONFIRM DELIVERY (RIDER)
# -------------------------
async def confirm_delivery(payment_id: str, user_id: str):

    # -------------------------
    # GET USER ROLE
    # -------------------------
    user_response = (
        supabase.table("users")
        .select("role")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if not user_response.data:
        raise HTTPException(status_code=404, detail="User not found")

    role = user_response.data.get("role")

    # 🔒 Only rider (and developer for testing) should do this
    if role not in ["rider", "developer"]:
        raise HTTPException(status_code=403, detail="Only rider can confirm delivery payment")

    # -------------------------
    # GET PAYMENT
    # -------------------------
    payment_response = (
        supabase.table("payments")
        .select("*")
        .eq("id", payment_id)
        .execute()
    )

    if not payment_response.data:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payment_response.data[0]

    # -------------------------
    # GET ORDER
    # -------------------------
    order_response = (
        supabase.table("orders")
        .select("*")
        .eq("id", payment["order_id"])
        .execute()
    )

    if not order_response.data:
        raise HTTPException(status_code=404, detail="Order not found")

    order = order_response.data[0]

    # -------------------------
    # PREVENT DOUBLE DELIVERY
    # -------------------------
    if order["status"] == "DELIVERED":
        raise HTTPException(status_code=400, detail="Order already delivered")

    # -------------------------
    # TIME
    # -------------------------
    now = datetime.now(timezone.utc).isoformat()

    # -------------------------
    # HANDLE PAY ON DELIVERY
    # -------------------------
    if payment["payment_method"] == "pay_on_delivery":

        if payment["payment_status"] not in [
            PaymentStatus.PENDING_PAY_ON_DELIVERY.value,
            PaymentStatus.PENDING.value
        ]:
            raise HTTPException(status_code=400, detail="Invalid payment state")

        # ✅ Update payment
        supabase.table("payments").update({
            "payment_status": PaymentStatus.SUCCESSFUL.value
        }).eq("id", payment_id).execute()

        # 🔥 FIX: Update order paid_at
        supabase.table("orders").update({
            "paid_at": now
        }).eq("id", order["id"]).execute()

    # -------------------------
    # MOMO / PAYSTACK
    # -------------------------
    else:
        if payment["payment_status"] != PaymentStatus.SUCCESSFUL.value:
            raise HTTPException(status_code=400, detail="Payment not completed")

        # 🔥 Ensure paid_at exists (fallback safety)
        if not order.get("paid_at"):
            supabase.table("orders").update({
                "paid_at": now
            }).eq("id", order["id"]).execute()

    # -------------------------
    # FINAL STEP → DELIVERED
    # -------------------------
    supabase.table("orders").update({
        "status": "DELIVERED",
        "delivered_at": now
    }).eq("id", order["id"]).execute()

    return {
        "message": "Delivery confirmed successfully",
        "order_id": order["id"]
    }