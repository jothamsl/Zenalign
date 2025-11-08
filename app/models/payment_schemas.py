"""
Pydantic schemas for payment processing and token management.
Interswitch payment gateway integration for Senalign monetization.
"""

from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import secrets


class Currency(str, Enum):
    """Supported currencies."""

    NGN = "NGN"
    USD = "USD"


class PaymentStatus(str, Enum):
    """Payment transaction statuses."""

    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceType(str, Enum):
    """Types of services that consume tokens."""

    ANALYSIS = "analysis"
    TRANSFORM = "transform"
    PREMIUM_INSIGHTS = "premium_insights"


class TokenPurchaseRequest(BaseModel):
    """Request model for purchasing tokens."""

    token_amount: int = Field(
        ..., gt=0, description="Number of tokens to purchase", examples=[100, 500, 1000]
    )
    user_email: EmailStr = Field(
        ..., description="Email address of the user purchasing tokens"
    )
    currency: Currency = Field(default=Currency.NGN, description="Currency for payment")


class TokenPurchaseResponse(BaseModel):
    """Response model for token purchase initiation."""

    transaction_reference: str = Field(..., description="Unique transaction reference")
    token_amount: int = Field(
        ..., description="Number of tokens to be credited after payment"
    )
    amount_paid: float = Field(
        ..., description="Amount to be paid in the specified currency"
    )
    payment_url: str = Field(
        ..., description="Interswitch payment gateway URL for completing payment"
    )
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING, description="Initial status of the transaction"
    )
    expires_at: datetime = Field(..., description="When the payment link expires")

    @staticmethod
    def generate_transaction_reference() -> str:
        """Generate a unique transaction reference."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(4).upper()
        return f"SEN_{timestamp}_{random_suffix}"

    @classmethod
    def create(
        cls,
        token_amount: int,
        amount_paid: float,
        payment_url: str,
        hours_valid: int = 1,
    ) -> "TokenPurchaseResponse":
        """Create a new token purchase response with auto-generated fields."""
        return cls(
            transaction_reference=cls.generate_transaction_reference(),
            token_amount=token_amount,
            amount_paid=amount_paid,
            payment_url=payment_url,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=hours_valid),
        )


class PaymentInitiationRequest(BaseModel):
    """Request model for initiating payment with Interswitch."""

    amount: float = Field(..., gt=0, description="Payment amount")
    currency: Currency = Field(default=Currency.NGN, description="Payment currency")
    customer_email: EmailStr = Field(..., description="Customer email address")
    customer_name: str = Field(
        ..., min_length=2, max_length=100, description="Customer full name"
    )
    transaction_reference: str = Field(..., description="Unique transaction reference")
    callback_url: Optional[str] = Field(
        default=None, description="URL for payment completion callback"
    )
    description: str = Field(
        default="Senalign Token Purchase", description="Payment description"
    )


class PaymentInitiationResponse(BaseModel):
    """Response model from Interswitch payment initiation."""

    payment_url: str = Field(..., description="URL to redirect user for payment")
    transaction_reference: str = Field(..., description="Transaction reference")
    gateway_reference: Optional[str] = Field(
        default=None, description="Payment gateway reference"
    )
    status: str = Field(..., description="Payment initiation status")


class PaymentVerificationResponse(BaseModel):
    """Response model for payment verification."""

    transaction_reference: str = Field(..., description="Transaction reference")
    status: PaymentStatus = Field(..., description="Payment status")
    amount: float = Field(..., description="Payment amount")
    currency: Currency = Field(default=Currency.NGN, description="Payment currency")
    gateway_response: Dict[str, Any] = Field(
        default_factory=dict, description="Raw response from payment gateway"
    )
    verified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when payment was verified",
    )


class UserTokenBalance(BaseModel):
    """Model for user token balance tracking."""

    user_email: EmailStr = Field(..., description="User email address")
    token_balance: int = Field(
        default=0, ge=0, description="Current available token balance"
    )
    total_purchased: int = Field(
        default=0, ge=0, description="Total tokens purchased by user"
    )
    total_consumed: int = Field(
        default=0, ge=0, description="Total tokens consumed by user"
    )
    last_purchase_date: Optional[datetime] = Field(
        default=None, description="Date of last token purchase"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )

    @field_validator("token_balance")
    @classmethod
    def validate_balance(cls, v, info):
        """Validate that token balance is consistent with purchased and consumed."""
        if "total_purchased" in info.data and "total_consumed" in info.data:
            expected_balance = (
                info.data["total_purchased"] - info.data["total_consumed"]
            )
            if v != expected_balance:
                raise ValueError(
                    f"Token balance {v} doesn't match purchased {info.data['total_purchased']} - consumed {info.data['total_consumed']} = {expected_balance}"
                )
        return v


class PaymentTransaction(BaseModel):
    """Model for payment transaction records."""

    transaction_reference: str = Field(..., description="Unique transaction reference")
    user_email: EmailStr = Field(..., description="User email address")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: Currency = Field(default=Currency.NGN, description="Payment currency")
    token_amount: int = Field(..., gt=0, description="Number of tokens to be credited")
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING, description="Transaction status"
    )
    payment_gateway_response: Optional[Dict[str, Any]] = Field(
        default=None, description="Raw response from payment gateway"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Transaction creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Transaction completion timestamp"
    )


class TokenConsumptionRequest(BaseModel):
    """Request model for consuming tokens."""

    user_email: EmailStr = Field(..., description="User email address")
    tokens_to_consume: int = Field(..., gt=0, description="Number of tokens to consume")
    service_type: ServiceType = Field(
        ..., description="Type of service consuming the tokens"
    )
    dataset_id: Optional[str] = Field(
        default=None, description="Dataset ID associated with the service"
    )
    description: Optional[str] = Field(
        default=None, max_length=500, description="Optional description of the service"
    )


class TokenConsumptionResponse(BaseModel):
    """Response model for token consumption."""

    user_email: EmailStr = Field(..., description="User email address")
    tokens_consumed: int = Field(..., description="Number of tokens consumed")
    remaining_balance: int = Field(
        ..., description="Remaining token balance after consumption"
    )
    service_type: ServiceType = Field(
        ..., description="Type of service that consumed tokens"
    )
    consumed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when tokens were consumed",
    )
    success: bool = Field(
        default=True, description="Whether the token consumption was successful"
    )


class TokenPricing(BaseModel):
    """Model for token pricing configuration."""

    tokens_per_naira: float = Field(
        default=2.0, gt=0, description="Number of tokens per 1 NGN"
    )
    minimum_purchase_amount: float = Field(
        default=500.0, gt=0, description="Minimum purchase amount in NGN"
    )
    maximum_purchase_amount: float = Field(
        default=100000.0, gt=0, description="Maximum purchase amount in NGN"
    )
    analysis_cost: int = Field(
        default=10, gt=0, description="Token cost for basic analysis"
    )
    transform_cost: int = Field(
        default=5, gt=0, description="Token cost for data transformation"
    )
    premium_insights_cost: int = Field(
        default=20, gt=0, description="Token cost for premium AI insights"
    )

    def calculate_token_amount(self, amount_ngn: float) -> int:
        """Calculate number of tokens for a given amount in NGN."""
        return int(amount_ngn * self.tokens_per_naira)

    def calculate_amount(self, token_amount: int) -> float:
        """Calculate amount in NGN for a given number of tokens."""
        return token_amount / self.tokens_per_naira

    def get_service_cost(self, service_type: ServiceType) -> int:
        """Get token cost for a specific service type."""
        costs = {
            ServiceType.ANALYSIS: self.analysis_cost,
            ServiceType.TRANSFORM: self.transform_cost,
            ServiceType.PREMIUM_INSIGHTS: self.premium_insights_cost,
        }
        return costs.get(service_type, self.analysis_cost)
