from abc import ABC, abstractmethod
from app.services.payments.payment_models import Payment, ProviderResponse


class PaymentProvider(ABC):

    @abstractmethod
    async def initiate_payment(self, payment: Payment, email: str) -> ProviderResponse:
        pass

    @abstractmethod
    async def verify_payment(self, reference: str) -> ProviderResponse:
        pass

    @abstractmethod
    def parse_webhook(self, payload: dict) -> ProviderResponse:
        pass