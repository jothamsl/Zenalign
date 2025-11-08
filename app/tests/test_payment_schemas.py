"""
Tests for payment schemas and token management models.
Following TDD approach for Interswitch payment gateway integration.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.payment_schemas import (
    TokenPurchaseRequest,
    TokenPurchaseResponse,
    PaymentInitiationRequest,
    PaymentInitiationResponse,
    PaymentVerificationResponse,
    UserTokenBalance,
    PaymentTransaction,
    TokenConsumptionRequest,
)


class TestTokenPurchaseRequest:
    """Test token purchase request schema."""

    def test_valid_token_purchase_request(self):
        """Test creating valid token purchase request."""
        request = TokenPurchaseRequest(
            token_amount=100, user_email="test@example.com", currency="NGN"
        )
        assert request.token_amount == 100
        assert request.user_email == "test@example.com"
        assert request.currency == "NGN"

    def test_invalid_token_amount(self):
        """Test validation fails for invalid token amounts."""
        with pytest.raises(ValidationError):
            TokenPurchaseRequest(
                token_amount=0,  # Should be > 0
                user_email="test@example.com",
            )

        with pytest.raises(ValidationError):
            TokenPurchaseRequest(
                token_amount=-10,  # Should be positive
                user_email="test@example.com",
            )

    def test_invalid_email(self):
        """Test validation fails for invalid email."""
        with pytest.raises(ValidationError):
            TokenPurchaseRequest(
                token_amount=100,
                user_email="invalid-email",  # Invalid email format
            )

    def test_default_currency(self):
        """Test default currency is NGN."""
        request = TokenPurchaseRequest(token_amount=100, user_email="test@example.com")
        assert request.currency == "NGN"


class TestPaymentInitiationRequest:
    """Test payment initiation request schema."""

    def test_valid_payment_initiation(self):
        """Test creating valid payment initiation request."""
        request = PaymentInitiationRequest(
            amount=5000.00,
            currency="NGN",
            customer_email="test@example.com",
            customer_name="Test User",
            transaction_reference="TXN_123456",
            callback_url="https://example.com/callback",
        )
        assert request.amount == 5000.00
        assert request.currency == "NGN"
        assert request.customer_email == "test@example.com"

    def test_invalid_amount(self):
        """Test validation fails for invalid amounts."""
        with pytest.raises(ValidationError):
            PaymentInitiationRequest(
                amount=0,  # Should be > 0
                customer_email="test@example.com",
                customer_name="Test User",
                transaction_reference="TXN_123456",
            )


class TestUserTokenBalance:
    """Test user token balance schema."""

    def test_valid_user_token_balance(self):
        """Test creating valid user token balance."""
        balance = UserTokenBalance(
            user_email="test@example.com",
            token_balance=150,
            total_purchased=200,
            total_consumed=50,
        )
        assert balance.user_email == "test@example.com"
        assert balance.token_balance == 150
        assert balance.total_purchased == 200
        assert balance.total_consumed == 50

    def test_token_balance_calculation(self):
        """Test that token balance equals purchased minus consumed."""
        balance = UserTokenBalance(
            user_email="test@example.com",
            token_balance=150,
            total_purchased=200,
            total_consumed=50,
        )
        assert balance.token_balance == balance.total_purchased - balance.total_consumed


class TestPaymentTransaction:
    """Test payment transaction schema."""

    def test_valid_payment_transaction(self):
        """Test creating valid payment transaction."""
        transaction = PaymentTransaction(
            transaction_reference="TXN_123456",
            user_email="test@example.com",
            amount=5000.00,
            currency="NGN",
            token_amount=100,
            status="pending",
            payment_gateway_response={"response_code": "00"},
        )
        assert transaction.transaction_reference == "TXN_123456"
        assert transaction.user_email == "test@example.com"
        assert transaction.amount == 5000.00
        assert transaction.status == "pending"
        assert transaction.token_amount == 100

    def test_default_values(self):
        """Test default values in payment transaction."""
        transaction = PaymentTransaction(
            transaction_reference="TXN_123456",
            user_email="test@example.com",
            amount=5000.00,
            token_amount=100,
        )
        assert transaction.currency == "NGN"
        assert transaction.status == "pending"
        assert isinstance(transaction.created_at, datetime)


class TestTokenConsumptionRequest:
    """Test token consumption request schema."""

    def test_valid_token_consumption(self):
        """Test creating valid token consumption request."""
        request = TokenConsumptionRequest(
            user_email="test@example.com", tokens_to_consume=10, service_type="analysis"
        )
        assert request.user_email == "test@example.com"
        assert request.tokens_to_consume == 10
        assert request.service_type == "analysis"

    def test_invalid_token_consumption(self):
        """Test validation fails for invalid token consumption."""
        with pytest.raises(ValidationError):
            TokenConsumptionRequest(
                user_email="test@example.com",
                tokens_to_consume=0,  # Should be > 0
                service_type="analysis",
            )

    def test_valid_service_types(self):
        """Test valid service types."""
        valid_types = ["analysis", "transform", "premium_insights"]
        for service_type in valid_types:
            request = TokenConsumptionRequest(
                user_email="test@example.com",
                tokens_to_consume=10,
                service_type=service_type,
            )
            assert request.service_type == service_type


class TestPaymentResponses:
    """Test payment response schemas."""

    def test_payment_verification_response(self):
        """Test payment verification response schema."""
        response = PaymentVerificationResponse(
            transaction_reference="TXN_123456",
            status="successful",
            amount=5000.00,
            currency="NGN",
            gateway_response={
                "response_code": "00",
                "response_description": "Successful",
            },
        )
        assert response.transaction_reference == "TXN_123456"
        assert response.status == "successful"
        assert response.amount == 5000.00

    def test_token_purchase_response(self):
        """Test token purchase response schema."""
        from datetime import datetime, timedelta, timezone

        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        response = TokenPurchaseResponse(
            transaction_reference="TXN_123456",
            token_amount=100,
            amount_paid=5000.00,
            payment_url="https://gateway.interswitch.ng/payment/123456",
            status="pending",
            expires_at=expires_at,
        )
        assert response.transaction_reference == "TXN_123456"
        assert response.token_amount == 100
        assert response.amount_paid == 5000.00
        assert "gateway.interswitch.ng" in response.payment_url
