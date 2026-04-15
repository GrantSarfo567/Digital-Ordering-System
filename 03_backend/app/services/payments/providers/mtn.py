import requests
import uuid

from app.services.payments.providers.base import PaymentProvider
from app.services.payments.payment_models import Payment, ProviderResponse
from app.services.payments.payment_utils import generate_external_reference


MTN_BASE_URL = "https://sandbox.momodeveloper.mtn.com"
TARGET_ENV = "sandbox"


from app.config import settings

class MTNProvider:
    def __init__(self):
        # ✅ FIXED: load from settings
        self.subscription_key = settings.MTN_SUBSCRIPTION_KEY
        self.api_user = settings.MTN_API_USER
        self.api_key = settings.MTN_API_KEY

        self.base_url = "https://sandbox.momodeveloper.mtn.com"

    # =====================================================
    # GET TOKEN
    # =====================================================

    def _get_token(self) -> str:
        url = f"{MTN_BASE_URL}/collection/token/"

        response = requests.post(
            url,
            headers={
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            },
            auth=(self.api_user, self.api_key),
        )

        print("MTN TOKEN RESPONSE:", response.status_code, response.text)

        if response.status_code != 200:
            raise Exception(f"MTN Token Error: {response.text}")

        return response.json().get("access_token")

    # =====================================================
    # INITIATE PAYMENT
    # =====================================================

    def request_payment(self, payment: Payment) -> ProviderResponse:
        token = self._get_token()

        reference_id = str(uuid.uuid4())
        external_reference = generate_external_reference(payment.order_id)

        url = f"{MTN_BASE_URL}/collection/v1_0/requesttopay"

        payload = {
            "amount": str(int(payment.amount)),
            "currency": "EUR",
            "externalId": external_reference,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": payment.phone,
            },
            "payerMessage": "Payment for order",
            "payeeNote": "Darks Technologies",
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": TARGET_ENV,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json",
            "X-Callback-Url": "https://playful-float-food.ngrok-free.dev/webhooks/mtn"
        }

        response = requests.post(url, json=payload, headers=headers)

        # 🔥 DEBUG LOGGING
        print("MTN REQUEST PAYLOAD:", payload)
        print("MTN RESPONSE:", response.status_code, response.text)

        if response.status_code not in [200, 202]:
            return ProviderResponse(
                success=False,
                message=f"MTN Error {response.status_code}: {response.text}",
                external_reference=external_reference,
                status="failed"
            )

        return ProviderResponse(
            success=True,
            message="Request to pay initiated",
            transaction_id=reference_id,
            external_reference=external_reference,
            status="processing"
        )

    # =====================================================
    # VERIFY PAYMENT
    # =====================================================

    def verify_payment(self, reference: str) -> ProviderResponse:
        token = self._get_token()

        url = f"{MTN_BASE_URL}/collection/v1_0/requesttopay/{reference}"

        headers = {
            "Authorization": f"Bearer {token}",
            "X-Target-Environment": TARGET_ENV,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }

        response = requests.get(url, headers=headers)

        print("VERIFY RESPONSE:", response.status_code, response.text)

        if response.status_code != 200:
            return ProviderResponse(
                success=False,
                message=response.text
            )

        data = response.json()
        status = data.get("status")

        mapped_status = self._map_status(status)

        return ProviderResponse(
            success=(mapped_status == "successful"),
            status=mapped_status,
            transaction_id=reference
        )

    # =====================================================
    # WEBHOOK PARSER
    # =====================================================

    def parse_webhook(self, payload: dict) -> ProviderResponse:
        status = payload.get("status")

        mapped_status = self._map_status(status)

        return ProviderResponse(
            success=(mapped_status == "successful"),
            status=mapped_status,
            external_reference=payload.get("externalId"),
            )

    # =====================================================
    # STATUS MAPPING
    # =====================================================

    def _map_status(self, mtn_status: str) -> str:
        mapping = {
            "SUCCESSFUL": "successful",
            "FAILED": "failed",
            "PENDING": "processing",
        }

        return mapping.get(mtn_status, "failed")