"""
Payment System Configuration
Centralized configuration for token pricing, free tokens, and payment settings.
"""

# ============================================================================
# Free Tokens Configuration
# ============================================================================

# Number of free tokens given to new users upon account creation
FREE_TOKENS_FOR_NEW_USERS = 100

# Analysis cost in tokens
TOKENS_PER_ANALYSIS = 10

# Free analyses available to new users
FREE_ANALYSES_FOR_NEW_USERS = FREE_TOKENS_FOR_NEW_USERS // TOKENS_PER_ANALYSIS  # 10


# ============================================================================
# Token Pricing Configuration
# ============================================================================

# Exchange rate: tokens per Nigerian Naira
TOKENS_PER_NAIRA = 2.0  # 2 tokens = ₦1

# Minimum and maximum purchase amounts (in NGN)
MIN_PURCHASE_AMOUNT_NGN = 250.0  # ₦250 minimum
MAX_PURCHASE_AMOUNT_NGN = 100000.0  # ₦100,000 maximum

# Minimum and maximum tokens that can be purchased
MIN_PURCHASE_TOKENS = int(MIN_PURCHASE_AMOUNT_NGN * TOKENS_PER_NAIRA)  # 500 tokens
MAX_PURCHASE_TOKENS = int(MAX_PURCHASE_AMOUNT_NGN * TOKENS_PER_NAIRA)  # 200,000 tokens


# ============================================================================
# Service Costs (in tokens)
# ============================================================================


class ServiceCosts:
    """Token costs for various services."""

    ANALYSIS = 10  # Basic dataset analysis
    TRANSFORM = 5  # Data transformation
    PREMIUM_INSIGHTS = 20  # Advanced AI insights

    # Future services (not yet implemented)
    EXPORT_REPORT = 2  # Export analysis report
    API_ACCESS = 1  # Per API call
    COLLABORATION = 15  # Share dataset with team


# ============================================================================
# Interswitch Configuration
# ============================================================================

# Payment gateway mode
PAYMENT_MODE = "TEST"  # "TEST" or "LIVE"

# Test credentials (used when env vars not set)
DEFAULT_TEST_CREDENTIALS = {
    "client_id": "IKIAB23A4E2756605C1ABC33CE3C287E27267F660D61",
    "secret_key": "secret",
    "merchant_code": "MX6072",
    "pay_item_id": "9405967",
}

# Payment timeout settings
PAYMENT_VERIFICATION_TIMEOUT_SECONDS = 600  # 10 minutes
PAYMENT_POLL_INTERVAL_SECONDS = 2  # Check every 2 seconds


# ============================================================================
# Token Balance Warnings
# ============================================================================

# Balance thresholds for warnings
LOW_BALANCE_THRESHOLD = 20  # Show warning when balance < 20 tokens
CRITICAL_BALANCE_THRESHOLD = 10  # Critical warning when balance < 10 tokens


# ============================================================================
# Promotional Settings (Future Use)
# ============================================================================

# Referral rewards
REFERRAL_BONUS_TOKENS = 50  # Tokens for referring a friend
REFERRAL_FRIEND_BONUS_TOKENS = 50  # Tokens for the referred friend

# First purchase bonus
FIRST_PURCHASE_BONUS_PERCENTAGE = 0.1  # 10% bonus on first purchase

# Bulk purchase discounts
BULK_PURCHASE_TIERS = {
    10000: 0.05,  # 5% bonus for 10,000+ tokens
    50000: 0.10,  # 10% bonus for 50,000+ tokens
    100000: 0.15,  # 15% bonus for 100,000+ tokens
}


# ============================================================================
# Helper Functions
# ============================================================================


def calculate_naira_from_tokens(tokens: int) -> float:
    """Calculate NGN amount from token count."""
    return tokens / TOKENS_PER_NAIRA


def calculate_tokens_from_naira(amount_ngn: float) -> int:
    """Calculate token count from NGN amount."""
    return int(amount_ngn * TOKENS_PER_NAIRA)


def get_free_tokens_message() -> str:
    """Get welcome message for new users."""
    return (
        f"You've received {FREE_TOKENS_FOR_NEW_USERS} free tokens! "
        f"That's {FREE_ANALYSES_FOR_NEW_USERS} free dataset analyses."
    )


def calculate_analyses_from_tokens(tokens: int) -> int:
    """Calculate number of analyses possible with given tokens."""
    return tokens // TOKENS_PER_ANALYSIS


def is_low_balance(balance: int) -> bool:
    """Check if balance is low."""
    return balance < LOW_BALANCE_THRESHOLD


def is_critical_balance(balance: int) -> bool:
    """Check if balance is critically low."""
    return balance < CRITICAL_BALANCE_THRESHOLD


# ============================================================================
# Environment-specific Settings
# ============================================================================

# These can be overridden by environment variables
import os

# Override free tokens from environment if set
FREE_TOKENS_FOR_NEW_USERS = int(
    os.getenv("FREE_TOKENS_FOR_NEW_USERS", FREE_TOKENS_FOR_NEW_USERS)
)

# Override payment mode from environment if set
PAYMENT_MODE = os.getenv("INTERSWITCH_MODE", PAYMENT_MODE).upper()
