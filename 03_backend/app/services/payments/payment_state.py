from enum import Enum


# =====================================================
# PAYMENT STATUS ENUM
# =====================================================

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"

    PENDING_PAY_ON_DELIVERY = "PENDING_PAY_ON_DELIVERY"
    PAID_ON_DELIVERY = "PAID_ON_DELIVERY"


# =====================================================
# ALLOWED STATE TRANSITIONS
# =====================================================

ALLOWED_TRANSITIONS = {
    PaymentStatus.PENDING: {
        PaymentStatus.PROCESSING,
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
        PaymentStatus.PENDING_PAY_ON_DELIVERY,   # NEW
    },
    PaymentStatus.PROCESSING: {
        PaymentStatus.SUCCESSFUL,
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
    },
    PaymentStatus.PENDING_PAY_ON_DELIVERY: {
        PaymentStatus.PAID_ON_DELIVERY,
        PaymentStatus.CANCELLED,
    },
    PaymentStatus.SUCCESSFUL: set(),
    PaymentStatus.PAID_ON_DELIVERY: set(),
    PaymentStatus.FAILED: set(),
    PaymentStatus.TIMEOUT: set(),
    PaymentStatus.CANCELLED: set(),
}


# =====================================================
# INTERNAL NORMALIZATION
# =====================================================

def _normalize(status: str) -> PaymentStatus:
    try:
        return PaymentStatus(status)
    except ValueError:
        raise Exception(f"Invalid payment status: {status}")


# =====================================================
# TERMINAL STATE CHECK
# =====================================================

def is_terminal(status: str) -> bool:
    status_enum = _normalize(status)

    return status_enum in {
        PaymentStatus.SUCCESSFUL,
        PaymentStatus.PAID_ON_DELIVERY,
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
    }


# =====================================================
# TRANSITION CHECK
# =====================================================

def can_transition(current_status: str, new_status: str) -> bool:
    current = _normalize(current_status)
    new = _normalize(new_status)

    return new in ALLOWED_TRANSITIONS.get(current, set())


# =====================================================
# VALIDATION
# =====================================================

def validate_payment_update(current_status: str, new_status: str) -> bool:
    current = _normalize(current_status)
    new = _normalize(new_status)

    if current in {PaymentStatus.SUCCESSFUL, PaymentStatus.PAID_ON_DELIVERY}:
        return False

    if current in {
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
    }:
        raise Exception(f"Cannot transition from terminal state: {current.value}")

    if new not in ALLOWED_TRANSITIONS.get(current, set()):
        raise Exception(f"Invalid payment transition: {current.value} → {new.value}")

    return True