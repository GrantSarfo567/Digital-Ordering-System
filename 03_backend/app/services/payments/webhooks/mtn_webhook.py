from fastapi import APIRouter, Request
from app.core.supabase import supabase
from app.services.payments.providers.mtn import MTNProvider
from app.services.payments.payment_state import validate_payment_update
from app.services.order_service import update_order_status
import os

router = APIRouter()

# =====================================================
# MTN PROVIDER (ENV CONFIG)
# =====================================================

mtn_provider = MTNProvider()


# =====================================================
# MTN WEBHOOK
# =====================================================

@router.post("/mtn")
async def handle_mtn_webhook(request: Request):

    # -----------------------------------------
    # SAFE JSON PARSING
    # -----------------------------------------
    try:
        payload = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    if not payload:
        return {"status": "empty_payload"}

    # -----------------------------------------
    # PARSE PROVIDER RESPONSE
    # -----------------------------------------
    provider_response = mtn_provider.parse_webhook(payload)

    if not provider_response or not provider_response.external_reference:
        return {"status": "ignored"}

    external_reference = provider_response.external_reference

    # -----------------------------------------
    # FIND PAYMENT (SAFE)
    # -----------------------------------------
    try:
        payment_query = (
            supabase.table("payments")
            .select("*")
            .eq("external_reference", external_reference)
            .single()
            .execute()
        )
    except Exception as e:
        return {"status": "db_error", "message": str(e)}

    if not payment_query.data:
        return {"status": "payment_not_found"}

    payment = payment_query.data
    current_status = payment["payment_status"]
    new_status = provider_response.status

    # -----------------------------------------
    # VALIDATE TRANSITION (IDEMPOTENT)
    # -----------------------------------------
    try:
        is_valid = validate_payment_update(current_status, new_status)
    except Exception:
        return {"status": "invalid_transition"}

    if not is_valid:
        return {"status": "ignored"}  # duplicate webhook

    # -----------------------------------------
    # BUILD UPDATE DATA SAFELY
    # -----------------------------------------
    update_data = {
        "payment_status": new_status
    }

    if provider_response.transaction_id:
        update_data["transaction_id"] = provider_response.transaction_id

    # -----------------------------------------
    # UPDATE PAYMENT (SAFE)
    # -----------------------------------------
    try:
        update_response = (
            supabase.table("payments")
            .update(update_data)
            .eq("id", payment["id"])
            .execute()
        )

        if not update_response.data:
            return {"status": "update_failed"}

    except Exception as e:
        return {"status": "db_update_error", "message": str(e)}

    # -----------------------------------------
    # CONFIRM ORDER (ONLY ON SUCCESS)
    # -----------------------------------------
    if new_status == "successful":
        try:
            update_order_status(payment["order_id"], "confirmed")
        except Exception as e:
            return {
                "status": "order_update_failed",
                "message": str(e)
            }

    return {"status": "processed"}