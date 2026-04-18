from fastapi import APIRouter, Request, Header, HTTPException
from app.services.payments.providers.paystack import PaystackProvider
from app.services.payments.payment_service import update_payment_status

router = APIRouter()


@router.post("/paystack")
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(None)
):
    print("🔥 PAYSTACK WEBHOOK HIT")

    # 🔥 Read raw body (needed for signature verification)
    body = await request.body()

    provider = PaystackProvider()

    # ❌ Missing signature
    if not x_paystack_signature:
        print("❌ Missing signature header")
        raise HTTPException(status_code=400, detail="Missing signature")

    # 🔐 VERIFY SIGNATURE
    is_valid = provider.verify_webhook(body, x_paystack_signature)
    print("🔐 Signature valid:", is_valid)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()

    print("📦 PAYLOAD:", payload)
    print("📌 EVENT:", payload.get("event"))

    # 🔥 PARSE EVENT
    response = provider.parse_webhook(payload)

    print("🧠 PARSED RESPONSE:", response)

    # ❌ Ignore irrelevant events
    if not response.success:
        print("⚠️ Ignored event")
        return {"status": "ignored"}

    if not response.external_reference:
        print("❌ Missing reference in webhook")
        return {"status": "error", "message": "Missing reference"}

    # 🔥 UPDATE PAYMENT + ORDER
    await update_payment_status(
        reference=response.external_reference,
        status=response.status
    )

    print(f"✅ Payment updated → {response.external_reference} = {response.status}")

    return {"status": "ok"}