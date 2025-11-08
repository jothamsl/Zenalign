"""
Token Management Service for Senalign.
Handles user token balances, purchases, and consumption tracking.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config.payment_config import FREE_TOKENS_FOR_NEW_USERS
from app.models.payment_schemas import (
    Currency,
    PaymentStatus,
    PaymentTransaction,
    ServiceType,
    TokenConsumptionRequest,
    TokenConsumptionResponse,
    TokenPricing,
    UserTokenBalance,
)

logger = logging.getLogger(__name__)


class TokenService:
    """
    Service for managing user token balances and transactions.
    Handles token purchases, consumption, and balance tracking.
    """

    def __init__(self, db_client: MongoClient, db_name: str = "senalign"):
        """
        Initialize Token Service.

        Args:
            db_client: MongoDB client instance
            db_name: Database name
        """
        self.db = db_client[db_name]
        self.users_collection = self.db["user_tokens"]
        self.transactions_collection = self.db["payment_transactions"]
        self.consumption_log = self.db["token_consumption_log"]

        # Default pricing configuration
        self.pricing = TokenPricing()

        # Ensure indexes
        self._ensure_indexes()

        logger.info("TokenService initialized")

    def _ensure_indexes(self):
        """Create database indexes for performance."""
        try:
            # Index on user_email for fast lookups
            self.users_collection.create_index("user_email", unique=True)

            # Index on transaction_reference for verification
            self.transactions_collection.create_index(
                "transaction_reference", unique=True
            )

            # Compound index for consumption log queries
            self.consumption_log.create_index([("user_email", 1), ("consumed_at", -1)])

            logger.debug("Database indexes created")
        except PyMongoError as e:
            logger.warning(f"Could not create indexes: {e}")

    def get_or_create_user_balance(self, user_email: str) -> UserTokenBalance:
        """
        Get user token balance or create new account with 100 free tokens.

        Args:
            user_email: User email address

        Returns:
            UserTokenBalance object

        Raises:
            Exception: If database operation fails
        """
        try:
            user_data = self.users_collection.find_one({"user_email": user_email})

            if user_data:
                # Remove MongoDB _id field
                user_data.pop("_id", None)
                return UserTokenBalance(**user_data)

            # Create new user account with free tokens (from config)
            new_user = UserTokenBalance(
                user_email=user_email,
                token_balance=FREE_TOKENS_FOR_NEW_USERS,
                total_purchased=FREE_TOKENS_FOR_NEW_USERS,  # Count free tokens as "purchased"
                total_consumed=0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            self.users_collection.insert_one(new_user.model_dump())
            logger.info(
                f"Created new token account for {user_email} with {FREE_TOKENS_FOR_NEW_USERS} free tokens"
            )

            return new_user

        except PyMongoError as e:
            logger.error(f"Database error getting user balance: {e}")
            raise Exception(f"Failed to get user balance: {str(e)}")

    def create_payment_transaction(
        self,
        transaction_reference: str,
        user_email: str,
        amount: float,
        token_amount: int,
        currency: Currency = Currency.NGN,
    ) -> PaymentTransaction:
        """
        Create a new payment transaction record.

        Args:
            transaction_reference: Unique transaction reference
            user_email: User email address
            amount: Payment amount
            token_amount: Number of tokens to be credited
            currency: Payment currency

        Returns:
            PaymentTransaction object

        Raises:
            Exception: If transaction creation fails
        """
        try:
            transaction = PaymentTransaction(
                transaction_reference=transaction_reference,
                user_email=user_email,
                amount=amount,
                currency=currency,
                token_amount=token_amount,
                status=PaymentStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

            self.transactions_collection.insert_one(transaction.model_dump())
            logger.info(
                f"Created payment transaction {transaction_reference} for {user_email}"
            )

            return transaction

        except PyMongoError as e:
            logger.error(f"Failed to create payment transaction: {e}")
            raise Exception(f"Failed to create transaction: {str(e)}")

    def get_transaction(
        self, transaction_reference: str
    ) -> Optional[PaymentTransaction]:
        """
        Get payment transaction by reference.

        Args:
            transaction_reference: Transaction reference to look up

        Returns:
            PaymentTransaction if found, None otherwise
        """
        try:
            transaction_data = self.transactions_collection.find_one(
                {"transaction_reference": transaction_reference}
            )

            if transaction_data:
                transaction_data.pop("_id", None)
                return PaymentTransaction(**transaction_data)

            return None

        except PyMongoError as e:
            logger.error(f"Error fetching transaction: {e}")
            return None

    def update_transaction_status(
        self,
        transaction_reference: str,
        status: PaymentStatus,
        gateway_response: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update payment transaction status.

        Args:
            transaction_reference: Transaction reference
            status: New payment status
            gateway_response: Raw gateway response data

        Returns:
            True if update successful, False otherwise
        """
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.now(timezone.utc),
            }

            if gateway_response:
                update_data["payment_gateway_response"] = gateway_response

            if status == PaymentStatus.SUCCESSFUL:
                update_data["completed_at"] = datetime.now(timezone.utc)

            result = self.transactions_collection.update_one(
                {"transaction_reference": transaction_reference}, {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(
                    f"Updated transaction {transaction_reference} to {status.value}"
                )
                return True

            return False

        except PyMongoError as e:
            logger.error(f"Failed to update transaction status: {e}")
            return False

    def credit_tokens(
        self,
        user_email: str,
        token_amount: int,
        transaction_reference: str,
    ) -> bool:
        """
        Credit tokens to user account after successful payment.

        Args:
            user_email: User email address
            token_amount: Number of tokens to credit
            transaction_reference: Reference to payment transaction

        Returns:
            True if tokens credited successfully, False otherwise
        """
        try:
            now = datetime.now(timezone.utc)

            # Update user balance
            result = self.users_collection.update_one(
                {"user_email": user_email},
                {
                    "$inc": {
                        "token_balance": token_amount,
                        "total_purchased": token_amount,
                    },
                    "$set": {
                        "last_purchase_date": now,
                        "updated_at": now,
                    },
                },
                upsert=True,
            )

            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"Credited {token_amount} tokens to {user_email}")
                return True

            return False

        except PyMongoError as e:
            logger.error(f"Failed to credit tokens: {e}")
            return False

    def consume_tokens(
        self, request: TokenConsumptionRequest
    ) -> TokenConsumptionResponse:
        """
        Consume tokens for a service.

        Args:
            request: Token consumption request

        Returns:
            TokenConsumptionResponse with result

        Raises:
            Exception: If user has insufficient balance or operation fails
        """
        try:
            # Get current user balance
            user_balance = self.get_or_create_user_balance(request.user_email)

            # Check if user has sufficient balance
            if user_balance.token_balance < request.tokens_to_consume:
                raise Exception(
                    f"Insufficient token balance. Required: {request.tokens_to_consume}, "
                    f"Available: {user_balance.token_balance}"
                )

            # Deduct tokens
            now = datetime.now(timezone.utc)
            result = self.users_collection.update_one(
                {
                    "user_email": request.user_email,
                    "token_balance": {"$gte": request.tokens_to_consume},
                },
                {
                    "$inc": {
                        "token_balance": -request.tokens_to_consume,
                        "total_consumed": request.tokens_to_consume,
                    },
                    "$set": {"updated_at": now},
                },
            )

            if result.modified_count == 0:
                raise Exception(
                    "Failed to deduct tokens - concurrent modification or insufficient balance"
                )

            # Log consumption
            consumption_log = {
                "user_email": request.user_email,
                "tokens_consumed": request.tokens_to_consume,
                "service_type": request.service_type.value,
                "dataset_id": request.dataset_id,
                "description": request.description,
                "consumed_at": now,
            }
            self.consumption_log.insert_one(consumption_log)

            # Calculate new balance
            new_balance = user_balance.token_balance - request.tokens_to_consume

            response = TokenConsumptionResponse(
                user_email=request.user_email,
                tokens_consumed=request.tokens_to_consume,
                remaining_balance=new_balance,
                service_type=request.service_type,
                consumed_at=now,
                success=True,
            )

            logger.info(
                f"Consumed {request.tokens_to_consume} tokens from {request.user_email} "
                f"for {request.service_type.value}. New balance: {new_balance}"
            )

            return response

        except Exception as e:
            logger.error(f"Token consumption failed: {e}")
            raise

    def get_user_consumption_history(
        self, user_email: str, limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Get user's token consumption history.

        Args:
            user_email: User email address
            limit: Maximum number of records to return

        Returns:
            List of consumption records
        """
        try:
            history = list(
                self.consumption_log.find({"user_email": user_email})
                .sort("consumed_at", -1)
                .limit(limit)
            )

            # Remove MongoDB _id field
            for record in history:
                record.pop("_id", None)

            return history

        except PyMongoError as e:
            logger.error(f"Failed to fetch consumption history: {e}")
            return []

    def calculate_token_amount(self, amount_ngn: float) -> int:
        """
        Calculate number of tokens for a given amount in NGN.

        Args:
            amount_ngn: Amount in Nigerian Naira

        Returns:
            Number of tokens
        """
        return self.pricing.calculate_token_amount(amount_ngn)

    def calculate_price(self, token_amount: int) -> float:
        """
        Calculate price in NGN for a given number of tokens.

        Args:
            token_amount: Number of tokens

        Returns:
            Price in Nigerian Naira
        """
        return self.pricing.calculate_amount(token_amount)

    def get_service_cost(self, service_type: ServiceType) -> int:
        """
        Get token cost for a specific service.

        Args:
            service_type: Type of service

        Returns:
            Token cost
        """
        return self.pricing.get_service_cost(service_type)

    def has_sufficient_balance(self, user_email: str, required_tokens: int) -> bool:
        """
        Check if user has sufficient token balance.

        Args:
            user_email: User email address
            required_tokens: Number of tokens required

        Returns:
            True if user has sufficient balance, False otherwise
        """
        try:
            user_balance = self.get_or_create_user_balance(user_email)
            return user_balance.token_balance >= required_tokens
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return False
