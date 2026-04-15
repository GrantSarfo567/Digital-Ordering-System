from app.services.payments.providers.mtn import MTNProvider
#from app.services.payments.providers.telecel import TelecelProvider
#from app.services.payments.providers.airteltigo import AirtelTigoProvider


def route_payment(payment):
    """
    Routes payment to correct provider
    """

    # 🔥 For now: default to MTN
    provider = MTNProvider()

    return provider.request_payment(payment)