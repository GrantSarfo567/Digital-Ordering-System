from abc import ABC, abstractmethod
from app.services.payments.payment_models import Payment, ProviderResponse


# =====================================================
# BASE PAYMENT PROVIDER (INTERFACE / CONTRACT)
# =====================================================

class PaymentProvider(ABC):
    """
    Abstract base class for all payment providers.

    Every provider (MTN, AirtelTigo, Paystack) MUST implement this interface.
    """

    # -----------------------------------------
    # INITIATE PAYMENT
    # -----------------------------------------
    @abstractmethod
    def initiate_payment(self, payment: Payment) -> ProviderResponse:
        """
        Sends payment request to external provider.

        Args:
            payment (Payment): Payment object

        Returns:
            ProviderResponse
        """
        pass

    # -----------------------------------------
    # VERIFY PAYMENT (OPTIONAL BUT IMPORTANT)
    # -----------------------------------------
    @abstractmethod
    def verify_payment(self, reference: str) -> ProviderResponse:
        """
        Verifies payment status with provider.

        Args:
            reference (str): external_reference or transaction_id

        Returns:
            ProviderResponse
        """
        pass

    # -----------------------------------------
    # HANDLE WEBHOOK (NORMALIZATION STEP)
    # -----------------------------------------
    @abstractmethod
    def parse_webhook(self, payload: dict) -> ProviderResponse:
        """
        Parses webhook payload into a normalized response.

        Args:
            payload (dict): Raw webhook payload

        Returns:
            ProviderResponse
        """
        pass