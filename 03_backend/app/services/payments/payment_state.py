from enum import Enum


# =====================================================
# PAYMENT STATUS ENUM
# =====================================================

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


# =====================================================
# ALLOWED STATE TRANSITIONS
# =====================================================

ALLOWED_TRANSITIONS = {
    PaymentStatus.PENDING: {
        PaymentStatus.PROCESSING,
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
    },
    PaymentStatus.PROCESSING: {
        PaymentStatus.SUCCESSFUL,
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
    },
    PaymentStatus.SUCCESSFUL: set(),
    PaymentStatus.FAILED: set(),
    PaymentStatus.TIMEOUT: set(),
    PaymentStatus.CANCELLED: set(),
}


# =====================================================
# INTERNAL NORMALIZATION (CRITICAL)
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
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
    }


# =====================================================
# TRANSITION CHECK (SAFE)
# =====================================================

def can_transition(current_status: str, new_status: str) -> bool:
    current = _normalize(current_status)
    new = _normalize(new_status)

    return new in ALLOWED_TRANSITIONS.get(current, set())


# =====================================================
# MAIN VALIDATION FUNCTION (USE THIS EVERYWHERE)
# =====================================================

def validate_payment_update(current_status: str, new_status: str) -> bool:
    current = _normalize(current_status)
    new = _normalize(new_status)

    # -----------------------------------------
    # 1. Prevent duplicate success (webhook safety)
    # -----------------------------------------
    if current == PaymentStatus.SUCCESSFUL:
        return False  # silently ignore repeated success updates

    # -----------------------------------------
    # 2. Block updates from terminal states
    # -----------------------------------------
    if current in {
        PaymentStatus.FAILED,
        PaymentStatus.TIMEOUT,
        PaymentStatus.CANCELLED,
    }:
        raise Exception(
            f"Cannot transition from terminal state: {current.value}"
        )

    # -----------------------------------------
    # 3. Enforce allowed transitions
    # -----------------------------------------
    if new not in ALLOWED_TRANSITIONS.get(current, set()):
        raise Exception(
            f"Invalid payment transition: {current.value} → {new.value}"
        )

    return True