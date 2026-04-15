from dataclasses import dataclass
from typing import Optional
from datetime import datetime


# =====================================================
# PAYMENT BASE MODEL (CORE STRUCTURE)
# =====================================================

@dataclass
class Payment:
    id: str
    user_id: str
    order_id: str
    amount: float
    currency: str
    payment_status: str

    # Optional / dynamic fields
    provider: Optional[str] = None
    payment_method: Optional[str] = "mobile_money"
    transaction_id: Optional[str] = None
    external_reference: Optional[str] = None
    idempotency_key: Optional[str] = None
    phone: Optional[str] = None
    failure_reason: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# =====================================================
# PAYMENT CREATION INPUT MODEL
# =====================================================

@dataclass
class CreatePaymentInput:
    order_id: str
    user_id: str
    amount: float
    phone: str


# =====================================================
# PROVIDER RESPONSE MODEL (GENERIC)
# =====================================================

@dataclass
class ProviderResponse:
    success: bool
    message: Optional[str] = None
    transaction_id: Optional[str] = None
    external_reference: Optional[str] = None
    status: Optional[str] = None


# =====================================================
# WEBHOOK EVENT MODEL (NORMALIZED)
# =====================================================

@dataclass
class PaymentEvent:
    payment_id: str
    status: str
    transaction_id: Optional[str] = None
    provider: Optional[str] = None
    raw_payload: Optional[dict] = None


# =====================================================
# PAYMENT UPDATE MODEL (INTERNAL USE)
# =====================================================

@dataclass
class PaymentUpdate:
    payment_id: str
    new_status: str
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None