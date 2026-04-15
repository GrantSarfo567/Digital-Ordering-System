import re
import uuid
import time
from typing import Final


# =====================================================
# CONSTANTS
# =====================================================

GHANA_COUNTRY_CODE: Final[str] = "233"

MTN_PREFIXES: Final[set] = {"23324", "23325", "23354", "23355", "23359"}
AT_PREFIXES: Final[set] = {"23326", "23327", "23356", "23357"}
TELECEL_PREFIXES: Final[set] = {"23320", "23350"}


# =====================================================
# PHONE NORMALIZATION (STRICT + SAFE)
# =====================================================

def normalize_phone(phone: str) -> str:
    """
    Normalize Ghana phone numbers to:
    233XXXXXXXXX

    Rejects invalid formats strictly.
    """

    if not phone or not isinstance(phone, str):
        raise Exception("Phone number must be a valid string")

    # Remove spaces, dashes, etc.
    phone = re.sub(r"[^\d+]", "", phone.strip())

    # Remove "+"
    if phone.startswith("+"):
        phone = phone[1:]

    # Convert local → international
    if phone.startswith("0"):
        phone = GHANA_COUNTRY_CODE + phone[1:]

    # Validate strict format
    if not re.fullmatch(rf"{GHANA_COUNTRY_CODE}\d{{9}}", phone):
        raise Exception(f"Invalid Ghana phone number: {phone}")

    return phone


# =====================================================
# NETWORK DETECTION (DETERMINISTIC)
# =====================================================

def detect_network(phone: str) -> str:
    """
    Returns:
    mtn | airteltigo | telecel | unknown
    """

    phone = normalize_phone(phone)
    prefix = phone[:5]

    if prefix in MTN_PREFIXES:
        return "mtn"
    if prefix in AT_PREFIXES:
        return "airteltigo"
    if prefix in TELECEL_PREFIXES:
        return "telecel"

    return "unknown"


# =====================================================
# IDEMPOTENCY KEY (STABLE + SAFE)
# =====================================================

def generate_idempotency_key(order_id: str) -> str:
    """
    Stable key for preventing duplicate payments.
    Must be deterministic per order attempt.
    """

    if not order_id:
        raise Exception("Order ID is required for idempotency")

    return f"payment::{order_id}"


# =====================================================
# EXTERNAL REFERENCE (TRACEABLE + UNIQUE)
# =====================================================

def generate_external_reference(order_id: str) -> str:
    """
    MTN REQUIREMENT:
    - Must be simple
    - No special characters like ::
    - Keep it short

    Safest option = UUID
    """
    return str(uuid.uuid4())


# =====================================================
# INTERNAL TRANSACTION ID (FALLBACK)
# =====================================================

def generate_transaction_id() -> str:
    """
    Internal fallback if provider does not return one.
    """

    return f"txn::{uuid.uuid4().hex}"


# =====================================================
# AMOUNT VALIDATION (STRICT FINANCIAL SAFETY)
# =====================================================

def validate_amount(amount: float):
    """
    Ensures amount is safe and valid.
    """

    if amount is None:
        raise Exception("Amount is required")

    if not isinstance(amount, (int, float)):
        raise Exception("Amount must be a number")

    if amount <= 0:
        raise Exception("Amount must be greater than zero")

    # Safety cap (protect system abuse)
    if amount > 20000:
        raise Exception("Amount exceeds allowed limit")


# =====================================================
# OPTIONAL: SANITIZE STRING INPUT (DEFENSIVE)
# =====================================================

def sanitize_string(value: str) -> str:
    """
    Basic sanitization helper (optional use).
    """

    if not value:
        return ""

    return value.strip()