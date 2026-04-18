from app.services.payments.providers.mtn import MTNProvider
from app.services.payments.providers.paystack import PaystackProvider
# from app.services.payments.providers.telecel import TelecelProvider
# from app.services.payments.providers.airteltigo import AirtelTigoProvider


def route_payment(payment):
    """
    🔥 UPDATED:
    - Returns provider (does NOT execute)
    - Supports multi-provider routing
    """

    # 🔥 MTN stays direct
    if getattr(payment, "network", None) == "MTN":
        return MTNProvider()

    # 🔥 Paystack handles AirtelTigo + Telecel
    if getattr(payment, "network", None) in ["AIRTELTIGO", "TELECEL"]:
        return PaystackProvider()

    # 🔥 Fallback (VERY IMPORTANT)
    return PaystackProvider()