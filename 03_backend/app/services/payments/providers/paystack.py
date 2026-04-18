import httpx
import hmac
import hashlib

from app.config import settings  # 🔥 USE SETTINGS (NOT os.getenv)
from app.services.payments.payment_models import ProviderResponse, Payment
from app.services.payments.providers.base import PaymentProvider


class PaystackProvider(PaymentProvider):

    def __init__(self):
        self.base_url = settings.PAYSTACK_BASE_URL
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.webhook_secret = self.secret_key  # 🔥 PAYSTACK USES SECRET

    # -----------------------------------------
    # INITIATE PAYMENT
    # -----------------------------------------
    async def initiate_payment(self, payment: Payment, email: str) -> ProviderResponse:

        url = f"{self.base_url}/transaction/initialize"

  
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": email,
            "amount": int(payment.amount * 100),  # pesewas
            "currency": "GHS",
            "channels": ["mobile_money"],
            "metadata": {
                "order_id": str(payment.order_id),
                "payment_id": str(payment.id)
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        # ❌ FAILURE
        if not data.get("status"):
            return ProviderResponse(
                success=False,
                status="failed",
                message=data.get("message", "Paystack init failed"),
                provider="paystack",
                raw=data
            )

        # ✅ SUCCESS
        return ProviderResponse(
            success=True,
            status="processing",
            provider="paystack",
            external_reference=data["data"]["reference"],
            checkout_url=data["data"]["authorization_url"],
            raw=data
        )

    # -----------------------------------------
    # VERIFY PAYMENT
    # -----------------------------------------
    async def verify_payment(self, reference: str) -> ProviderResponse:

        url = f"{self.base_url}/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()

        if data["data"]["status"] == "success":
            return ProviderResponse(
                success=True,
                status="successful",
                provider="paystack",
                external_reference=reference,
                raw=data
            )

        return ProviderResponse(
            success=False,
            status="failed",
            provider="paystack",
            external_reference=reference,
            raw=data
        )

    # -----------------------------------------
    # VERIFY WEBHOOK SIGNATURE
    # -----------------------------------------
    def verify_webhook(self, body: bytes, signature: str) -> bool:
        computed_hash = hmac.new(
            self.secret_key.encode(),  # ✅ correct
            body,
            hashlib.sha512
        ).hexdigest()

        return computed_hash == signature

    # -----------------------------------------
    # PARSE WEBHOOK (OPTIONAL BUT GOOD)
    # -----------------------------------------
    def parse_webhook(self, payload: dict) -> ProviderResponse:

        event = payload.get("event")

        if event == "charge.success":
            data = payload["data"]

            return ProviderResponse(
                success=True,
                status="successful",
                provider="paystack",
                external_reference=data["reference"],
                amount=data.get("amount", 0) / 100,
                raw=payload
            )

        return ProviderResponse(
            success=False,
            status="failed",
            provider="paystack",
            raw=payload
        )