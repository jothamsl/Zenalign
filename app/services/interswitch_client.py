"""
Interswitch Payment Gateway Client for Senalign.
Implements OAuth2 authentication and Web Checkout integration.
"""

import base64
import hashlib
import logging
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from app.models.payment_schemas import (
    Currency,
    PaymentInitiationRequest,
    PaymentInitiationResponse,
    PaymentStatus,
    PaymentVerificationResponse,
)

logger = logging.getLogger(__name__)


class InterswitchClient:
    """
    Client for Interswitch Payment Gateway integration.
    Supports OAuth2 authentication and Web Checkout (inline/redirect).
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        merchant_code: Optional[str] = None,
        pay_item_id: Optional[str] = None,
        mode: str = "TEST",
    ):
        """
        Initialize Interswitch client.

        Args:
            client_id: Interswitch client ID
            secret_key: Interswitch secret key
            merchant_code: Merchant code from Quickteller Business
            pay_item_id: Pay item ID from Quickteller Business
            mode: 'TEST' or 'LIVE'
        """
        # Use provided values or fall back to environment variables or test credentials
        self.client_id = client_id or os.getenv(
            "INTERSWITCH_CLIENT_ID", "IKIAB23A4E2756605C1ABC33CE3C287E27267F660D61"
        )
        self.secret_key = secret_key or os.getenv("INTERSWITCH_SECRET_KEY", "secret")
        self.merchant_code = merchant_code or os.getenv(
            "INTERSWITCH_MERCHANT_CODE", "MX6072"
        )
        self.pay_item_id = pay_item_id or os.getenv(
            "INTERSWITCH_PAY_ITEM_ID", "9405967"
        )
        self.mode = mode.upper()

        # Validate credentials are not placeholders
        self._validate_credentials()

        # Set base URLs based on mode
        if self.mode == "LIVE":
            self.passport_url = "https://passport.interswitchng.com"
            self.payment_url = "https://newwebpay.interswitchng.com"
            self.api_url = "https://webpay.interswitchng.com"
        else:  # TEST mode
            self.passport_url = "https://passport.k8.isw.la"
            self.payment_url = "https://newwebpay.qa.interswitchng.com"
            self.api_url = "https://qa.interswitchng.com"

        # Cache for access token
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

        logger.info(
            f"InterswitchClient initialized in {self.mode} mode with merchant {self.merchant_code}"
        )

    def _validate_credentials(self) -> None:
        """
        Validate that credentials are not placeholder values.
        
        Raises:
            ValueError: If placeholder credentials are detected
        """
        placeholders = [
            "your_client_id", "your_secret_key", "your_merchant_code", 
            "your_pay_item_id", "your_live_", "your_test_"
        ]
        
        credentials_to_check = {
            "INTERSWITCH_CLIENT_ID": self.client_id,
            "INTERSWITCH_SECRET_KEY": self.secret_key,
            "INTERSWITCH_MERCHANT_CODE": self.merchant_code,
            "INTERSWITCH_PAY_ITEM_ID": self.pay_item_id,
        }
        
        for cred_name, cred_value in credentials_to_check.items():
            for placeholder in placeholders:
                if placeholder.lower() in cred_value.lower():
                    raise ValueError(
                        f"\n{'='*80}\n"
                        f"ERROR: Invalid Interswitch Configuration\n"
                        f"{'='*80}\n\n"
                        f"The {cred_name} contains placeholder text: '{cred_value}'\n\n"
                        f"You must update your .env file with actual credentials from Interswitch.\n\n"
                        f"Steps to fix:\n"
                        f"  1. Get your credentials from: https://developer.interswitchgroup.com\n"
                        f"  2. Update your .env file (see .env.example for template)\n"
                        f"  3. Set INTERSWITCH_MODE=TEST for testing or LIVE for production\n"
                        f"  4. Restart the backend server\n\n"
                        f"{'='*80}\n"
                    )
        
        logger.debug("Credential validation passed")

    def _encode_credentials(self) -> str:
        """
        Encode client ID and secret key to Base64 for OAuth2.

        Returns:
            Base64 encoded string of clientId:secretKey
        """
        credentials = f"{self.client_id}:{self.secret_key}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return encoded

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token. Uses cached token if still valid.

        Returns:
            Valid access token

        Raises:
            Exception: If token generation fails
        """
        # Return cached token if still valid (with 5 minute buffer)
        if self._access_token and self._token_expires_at:
            if datetime.now(timezone.utc) < self._token_expires_at:
                logger.debug("Using cached access token")
                return self._access_token

        # Generate new token
        logger.info("Generating new access token from Interswitch")
        url = f"{self.passport_url}/passport/oauth/token"
        encoded_credentials = self._encode_credentials()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Calculate expiry time (expires_in is in seconds)
            expires_in = token_data.get("expires_in", 86400)  # Default 24 hours
            self._token_expires_at = datetime.now(timezone.utc).replace(
                tzinfo=None
            ) + __import__("datetime").timedelta(seconds=expires_in - 300)

            logger.info(f"Access token generated, expires in {expires_in} seconds")
            return self._access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise Exception(f"Failed to authenticate with Interswitch: {str(e)}")

    def generate_transaction_reference(self) -> str:
        """
        Generate a unique transaction reference.

        Returns:
            Unique transaction reference string
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(6).upper()
        return f"SEN{timestamp}{random_suffix}"

    def get_payment_url(
        self,
        amount: float,
        transaction_reference: str,
        customer_email: str,
        customer_name: Optional[str] = None,
        currency_code: str = "566",  # NGN ISO 4217 numeric code
        site_redirect_url: Optional[str] = None,
    ) -> str:
        """
        Generate payment URL for Web Checkout (inline or redirect).

        Args:
            amount: Amount in major currency units (e.g., 1000 for ₦1,000)
            transaction_reference: Unique transaction reference
            customer_email: Customer email address
            customer_name: Customer name (optional)
            currency_code: ISO 4217 numeric currency code (566 for NGN)
            site_redirect_url: URL to redirect after payment completion

        Returns:
            Payment URL for inline checkout or redirect
        """
        # Convert amount to minor units (kobo for NGN)
        amount_minor = int(amount * 100)

        # Build payment URL with query parameters
        params = {
            "merchant_code": self.merchant_code,
            "pay_item_id": self.pay_item_id,
            "txn_ref": transaction_reference,
            "amount": amount_minor,
            "currency": currency_code,
            "cust_email": customer_email,
        }

        if customer_name:
            params["cust_name"] = customer_name

        if site_redirect_url:
            params["site_redirect_url"] = site_redirect_url

        # Build URL
        base_url = f"{self.payment_url}/collections/w/pay"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        payment_url = f"{base_url}?{query_string}"

        logger.info(
            f"Generated payment URL for transaction {transaction_reference}, amount: {amount}"
        )
        return payment_url

    def initiate_payment(
        self, request: PaymentInitiationRequest
    ) -> PaymentInitiationResponse:
        """
        Initiate payment with Interswitch Web Checkout.

        Args:
            request: Payment initiation request

        Returns:
            Payment initiation response with payment URL

        Raises:
            Exception: If payment initiation fails
        """
        try:
            # Generate payment URL
            currency_code = "566" if request.currency == Currency.NGN else "840"  # USD
            # Set default callback URL based on mode
            default_callback = "https://senalign.com/payment/callback"
            if self.mode == "TEST":
                default_callback = "http://localhost:3000/payment-success"

            site_redirect_url = request.callback_url or os.getenv(
                "PAYMENT_CALLBACK_URL", default_callback
            )

            payment_url = self.get_payment_url(
                amount=request.amount,
                transaction_reference=request.transaction_reference,
                customer_email=request.customer_email,
                customer_name=request.customer_name,
                currency_code=currency_code,
                site_redirect_url=site_redirect_url,
            )

            response = PaymentInitiationResponse(
                payment_url=payment_url,
                transaction_reference=request.transaction_reference,
                status="initiated",
            )

            logger.info(
                f"Payment initiated: {request.transaction_reference} for {request.amount} {request.currency}"
            )
            return response

        except Exception as e:
            logger.error(f"Payment initiation failed: {e}")
            raise Exception(f"Failed to initiate payment: {str(e)}")

    def verify_payment(
        self, transaction_reference: str, amount: float
    ) -> PaymentVerificationResponse:
        """
        Verify payment status by querying Interswitch API.

        Args:
            transaction_reference: Transaction reference to verify
            amount: Expected payment amount

        Returns:
            Payment verification response

        Raises:
            Exception: If verification fails
        """
        try:
            # Convert amount to minor units
            amount_minor = int(amount * 100)

            # Build verification URL
            url = f"{self.api_url}/collections/api/v1/gettransaction.json"
            params = {
                "merchantcode": self.merchant_code,
                "transactionreference": transaction_reference,
                "amount": amount_minor,
            }

            headers = {"Content-Type": "application/json"}

            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Parse response code
            response_code = data.get("ResponseCode", "")

            # Map Interswitch response codes to our status
            if response_code == "00":
                status = PaymentStatus.SUCCESSFUL
            elif response_code in ["09", "Z1"]:  # Pending codes
                status = PaymentStatus.PENDING
            else:
                status = PaymentStatus.FAILED

            # Verify amount matches
            returned_amount = data.get("Amount", 0)
            if status == PaymentStatus.SUCCESSFUL and returned_amount != amount_minor:
                logger.warning(
                    f"Amount mismatch for {transaction_reference}: expected {amount_minor}, got {returned_amount}"
                )
                status = PaymentStatus.FAILED

            verification_response = PaymentVerificationResponse(
                transaction_reference=transaction_reference,
                status=status,
                amount=amount,
                currency=Currency.NGN,
                gateway_response=data,
                verified_at=datetime.now(timezone.utc),
            )

            logger.info(
                f"Payment verified: {transaction_reference} - Status: {status.value}"
            )
            return verification_response

        except requests.exceptions.RequestException as e:
            logger.error(f"Payment verification failed: {e}")
            raise Exception(f"Failed to verify payment: {str(e)}")

    def get_inline_checkout_config(
        self,
        amount: float,
        transaction_reference: str,
        customer_email: str,
        customer_name: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate configuration for inline checkout (JavaScript widget).

        Args:
            amount: Amount in major currency units
            transaction_reference: Unique transaction reference
            customer_email: Customer email
            customer_name: Customer name (optional)
            callback_url: Redirect URL after payment (optional)

        Returns:
            Dictionary with inline checkout configuration
        """
        # Convert amount to minor units (kobo)
        amount_minor = int(amount * 100)

        config = {
            "merchant_code": self.merchant_code,
            "pay_item_id": self.pay_item_id,
            "txn_ref": transaction_reference,
            "amount": amount_minor,
            "currency": 566,  # NGN
            "cust_email": customer_email,
            "mode": self.mode,
        }

        if customer_name:
            config["cust_name"] = customer_name

        if callback_url:
            config["site_redirect_url"] = callback_url

        return config
