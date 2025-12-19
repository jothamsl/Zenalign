"""
Payment Router for Senalign Token Purchase System.
Integrates with Interswitch Payment Gateway for token purchases.
"""

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pymongo import MongoClient

from app.models.payment_schemas import (
    Currency,
    PaymentInitiationRequest,
    PaymentStatus,
    TokenConsumptionRequest,
    TokenConsumptionResponse,
    TokenPricing,
    TokenPurchaseRequest,
    TokenPurchaseResponse,
    UserTokenBalance,
)
from app.services.interswitch_client import InterswitchClient
from app.services.token_service import TokenService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/payment", tags=["Payment"])

from app.services.db import init_db

# Global dependencies (set by main.py during startup)
_db_client: Optional[MongoClient] = None
_interswitch_client: Optional[InterswitchClient] = None
_token_service: Optional[TokenService] = None


def _ensure_services_initialized():
    """Attempt to initialize services if they are missing."""
    global _db_client, _interswitch_client, _token_service

    try:
        if _db_client is None:
            logger.info("Lazy initialization: Connecting to MongoDB...")
            _db_client = init_db()

        if _interswitch_client is None:
            logger.info("Lazy initialization: Creating Interswitch client...")
            _interswitch_client = InterswitchClient()

        if _token_service is None and _db_client is not None:
            logger.info("Lazy initialization: Creating Token service...")
            _token_service = TokenService(_db_client)
            
    except Exception as e:
        logger.error(f"Lazy initialization failed: {e}")
        # Don't raise here, let the specific dependency checks raise if they still fail


def get_token_service() -> TokenService:
    """Dependency to get token service instance."""
    if _token_service is None:
        _ensure_services_initialized()
        
    if _token_service is None:
        raise HTTPException(status_code=503, detail="Payment service not initialized")
    return _token_service


def get_interswitch_client() -> InterswitchClient:
    """Dependency to get Interswitch client instance."""
    if _interswitch_client is None:
        _ensure_services_initialized()
        
    if _interswitch_client is None:
        raise HTTPException(status_code=503, detail="Payment gateway not initialized")
    return _interswitch_client


@router.get("/pricing")
async def get_pricing():
    """
    Get token pricing information.

    Returns pricing details including cost per token and service costs.
    """
    try:
        pricing = TokenPricing()

        return {
            "tokens_per_naira": pricing.tokens_per_naira,
            "minimum_purchase_amount": pricing.minimum_purchase_amount,
            "maximum_purchase_amount": pricing.maximum_purchase_amount,
            "service_costs": {
                "analysis": pricing.analysis_cost,
                "transform": pricing.transform_cost,
                "premium_insights": pricing.premium_insights_cost,
            },
            "currency": "NGN",
            "examples": [
                {
                    "amount_ngn": 500,
                    "tokens": pricing.calculate_token_amount(500),
                    "analyses": int(
                        pricing.calculate_token_amount(500) / pricing.analysis_cost
                    ),
                },
                {
                    "amount_ngn": 1000,
                    "tokens": pricing.calculate_token_amount(1000),
                    "analyses": int(
                        pricing.calculate_token_amount(1000) / pricing.analysis_cost
                    ),
                },
                {
                    "amount_ngn": 5000,
                    "tokens": pricing.calculate_token_amount(5000),
                    "analyses": int(
                        pricing.calculate_token_amount(5000) / pricing.analysis_cost
                    ),
                },
            ],
        }
    except Exception as e:
        logger.error(f"Error fetching pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pricing information")


@router.post("/purchase", response_model=TokenPurchaseResponse)
async def purchase_tokens(
    request: TokenPurchaseRequest,
    token_service: TokenService = Depends(get_token_service),
    interswitch_client: InterswitchClient = Depends(get_interswitch_client),
):
    """
    Initiate token purchase via Interswitch payment gateway.

    Creates a payment transaction and returns payment URL for checkout.
    Users can complete payment using the returned URL (inline or redirect).
    """
    try:
        logger.info(
            f"Token purchase request: {request.token_amount} tokens for {request.user_email}"
        )

        # Calculate amount to pay
        pricing = TokenPricing()
        amount = pricing.calculate_amount(request.token_amount)

        # Validate amount is within limits
        if amount < pricing.minimum_purchase_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Amount ₦{amount:.2f} is below minimum purchase amount of ₦{pricing.minimum_purchase_amount:.2f}",
            )

        if amount > pricing.maximum_purchase_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Amount ₦{amount:.2f} exceeds maximum purchase amount of ₦{pricing.maximum_purchase_amount:.2f}",
            )

        # Generate unique transaction reference
        transaction_reference = interswitch_client.generate_transaction_reference()

        # Create payment transaction record
        transaction = token_service.create_payment_transaction(
            transaction_reference=transaction_reference,
            user_email=request.user_email,
            amount=amount,
            token_amount=request.token_amount,
            currency=request.currency,
        )

        # Initiate payment with Interswitch
        payment_request = PaymentInitiationRequest(
            amount=amount,
            currency=request.currency,
            customer_email=request.user_email,
            customer_name=request.user_email.split("@")[0],  # Use email prefix as name
            transaction_reference=transaction_reference,
            description=f"Senalign Token Purchase - {request.token_amount} tokens",
        )

        payment_response = interswitch_client.initiate_payment(payment_request)

        # Create response
        response = TokenPurchaseResponse.create(
            token_amount=request.token_amount,
            amount_paid=amount,
            payment_url=payment_response.payment_url,
            hours_valid=1,
        )

        logger.info(f"Token purchase initiated: {transaction_reference}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token purchase failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initiate token purchase: {str(e)}"
        )


@router.post("/verify/{transaction_reference}")
async def verify_payment(
    transaction_reference: str,
    background_tasks: BackgroundTasks,
    token_service: TokenService = Depends(get_token_service),
    interswitch_client: InterswitchClient = Depends(get_interswitch_client),
):
    """
    Verify payment status and credit tokens if successful.

    This endpoint should be called after payment completion to verify
    the transaction status with Interswitch and credit tokens to user account.
    """
    try:
        logger.info(f"Verifying payment: {transaction_reference}")

        # Get transaction from database
        transaction = token_service.get_transaction(transaction_reference)

        if not transaction:
            raise HTTPException(
                status_code=404, detail=f"Transaction {transaction_reference} not found"
            )

        # If already successful, return cached result
        if transaction.status == PaymentStatus.SUCCESSFUL:
            user_balance = token_service.get_or_create_user_balance(
                transaction.user_email
            )
            return {
                "transaction_reference": transaction_reference,
                "status": "successful",
                "tokens_credited": transaction.token_amount,
                "current_balance": user_balance.token_balance,
                "message": "Payment already verified and tokens credited",
            }

        # Verify payment with Interswitch
        verification = interswitch_client.verify_payment(
            transaction_reference=transaction_reference,
            amount=transaction.amount,
        )

        # Update transaction status
        token_service.update_transaction_status(
            transaction_reference=transaction_reference,
            status=verification.status,
            gateway_response=verification.gateway_response,
        )

        # If successful, credit tokens
        if verification.status == PaymentStatus.SUCCESSFUL:
            success = token_service.credit_tokens(
                user_email=transaction.user_email,
                token_amount=transaction.token_amount,
                transaction_reference=transaction_reference,
            )

            if success:
                user_balance = token_service.get_or_create_user_balance(
                    transaction.user_email
                )

                logger.info(
                    f"Payment verified and {transaction.token_amount} tokens credited to {transaction.user_email}"
                )

                return {
                    "transaction_reference": transaction_reference,
                    "status": "successful",
                    "tokens_credited": transaction.token_amount,
                    "current_balance": user_balance.token_balance,
                    "message": "Payment successful and tokens credited",
                }
            else:
                logger.error(f"Failed to credit tokens for {transaction_reference}")
                raise HTTPException(
                    status_code=500,
                    detail="Payment verified but failed to credit tokens",
                )

        elif verification.status == PaymentStatus.PENDING:
            return {
                "transaction_reference": transaction_reference,
                "status": "pending",
                "message": "Payment is still pending. Please try again later.",
            }

        else:  # FAILED or CANCELLED
            return {
                "transaction_reference": transaction_reference,
                "status": verification.status.value,
                "message": f"Payment {verification.status.value}",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to verify payment: {str(e)}"
        )


@router.get("/balance/{user_email}", response_model=UserTokenBalance)
async def get_token_balance(
    user_email: str,
    token_service: TokenService = Depends(get_token_service),
):
    """
    Get user's current token balance and purchase history.
    """
    try:
        balance = token_service.get_or_create_user_balance(user_email)
        return balance

    except Exception as e:
        logger.error(f"Failed to get token balance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get token balance")


@router.get("/balance/{user_email}/history")
async def get_consumption_history(
    user_email: str,
    limit: int = Query(default=50, ge=1, le=200),
    token_service: TokenService = Depends(get_token_service),
):
    """
    Get user's token consumption history.

    Returns recent token consumption records including service type,
    tokens consumed, and timestamps.
    """
    try:
        history = token_service.get_user_consumption_history(user_email, limit=limit)

        return {
            "user_email": user_email,
            "history": history,
            "total_records": len(history),
        }

    except Exception as e:
        logger.error(f"Failed to get consumption history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get consumption history")


@router.post("/consume", response_model=TokenConsumptionResponse)
async def consume_tokens(
    request: TokenConsumptionRequest,
    token_service: TokenService = Depends(get_token_service),
):
    """
    Consume tokens for a service (internal endpoint).

    This endpoint is called by other services (analyze, transform)
    to deduct tokens from user balance when they use a paid feature.
    """
    try:
        response = token_service.consume_tokens(request)
        return response

    except Exception as e:
        logger.error(f"Token consumption failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transaction/{transaction_reference}")
async def get_transaction_status(
    transaction_reference: str,
    token_service: TokenService = Depends(get_token_service),
):
    """
    Get payment transaction details and status.
    """
    try:
        transaction = token_service.get_transaction(transaction_reference)

        if not transaction:
            raise HTTPException(
                status_code=404, detail=f"Transaction {transaction_reference} not found"
            )

        return transaction

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transaction details")


@router.get("/inline-config")
async def get_inline_checkout_config(
    amount: float = Query(..., gt=0, description="Amount in NGN"),
    user_email: str = Query(..., description="User email address"),
    interswitch_client: InterswitchClient = Depends(get_interswitch_client),
):
    """
    Get configuration for Interswitch inline checkout widget.

    Returns configuration object that can be used directly with
    the inline-checkout.js script for client-side integration.
    """
    try:
        transaction_reference = interswitch_client.generate_transaction_reference()

        config = interswitch_client.get_inline_checkout_config(
            amount=amount,
            transaction_reference=transaction_reference,
            customer_email=user_email,
        )

        return {
            "transaction_reference": transaction_reference,
            "config": config,
            "script_url": "https://newwebpay.qa.interswitchng.com/inline-checkout.js"
            if interswitch_client.mode == "TEST"
            else "https://newwebpay.interswitchng.com/inline-checkout.js",
        }

    except Exception as e:
        logger.error(f"Failed to get inline config: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate inline checkout config"
        )
