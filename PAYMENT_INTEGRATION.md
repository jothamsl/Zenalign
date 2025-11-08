# Payment Integration Documentation

## Interswitch Payment Gateway Integration for Senalign

This document provides comprehensive information about the token-based payment system integrated into Senalign using the Interswitch Payment Gateway.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [API Endpoints](#api-endpoints)
5. [Frontend Integration](#frontend-integration)
6. [Token System](#token-system)
7. [Testing](#testing)
8. [Production Deployment](#production-deployment)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Senalign now includes a token-based monetization system that allows users to purchase tokens and consume them for dataset analysis sessions. The payment processing is handled by **Interswitch**, a leading African payment gateway.

### Key Features

- ✅ **Token-based system** - Purchase tokens, use for analyses
- ✅ **Interswitch integration** - OAuth2 authentication + Web Checkout
- ✅ **Multiple payment methods** - Card, Transfer, USSD, Wallet, etc.
- ✅ **Real-time verification** - Automatic token crediting after successful payment
- ✅ **Balance tracking** - Complete purchase and consumption history
- ✅ **Test mode** - Full test credentials for development

### Token Pricing (Default)

| Service | Token Cost |
|---------|-----------|
| Dataset Analysis | 10 tokens |
| Data Transformation | 5 tokens |
| Premium Insights | 20 tokens |

**Token Purchase Rate**: 2 tokens per ₦1 (Nigerian Naira)

**Example**: ₦1,000 = 2,000 tokens = ~200 analyses

---

## Architecture

### Backend Components

```
app/
├── models/
│   └── payment_schemas.py          # Pydantic models for payment data
├── services/
│   ├── interswitch_client.py       # Interswitch API client
│   └── token_service.py            # Token balance & transaction management
└── routers/
    ├── payment.py                   # Payment API endpoints
    └── analyze.py                   # Updated with token consumption
```

### Database Collections

**MongoDB Collections**:
- `user_tokens` - User token balances
- `payment_transactions` - Payment transaction records
- `token_consumption_log` - Token usage history

### Integration Flow

```
┌─────────────┐
│   User UI   │
└─────┬───────┘
      │ 1. Request token purchase
      ▼
┌─────────────────┐
│  Payment API    │
└─────┬───────────┘
      │ 2. Create transaction
      │ 3. Generate payment URL
      ▼
┌──────────────────┐
│ Interswitch      │
│ Payment Gateway  │
└─────┬────────────┘
      │ 4. User completes payment
      ▼
┌─────────────────┐
│  Verification   │
│  API            │
└─────┬───────────┘
      │ 5. Verify with Interswitch
      │ 6. Credit tokens to user
      ▼
┌─────────────────┐
│  User Balance   │
│  Updated        │
└─────────────────┘
```

---

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Interswitch Configuration
INTERSWITCH_CLIENT_ID=your_client_id_here
INTERSWITCH_SECRET_KEY=your_secret_key_here
INTERSWITCH_MERCHANT_CODE=your_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_pay_item_id

# Optional: Callback URL for payment completion
PAYMENT_CALLBACK_URL=https://yourdomain.com/payment/callback
```

### Test Credentials (Default)

If environment variables are not set, the system uses these test credentials:

```
Client ID: IKIAB23A4E2756605C1ABC33CE3C287E27267F660D61
Secret Key: secret
Merchant Code: MX6072
Pay Item ID: 9405967
```

**Source**: [Interswitch Default Test Credentials](https://docs.interswitchgroup.com/docs/default-test-credentials)

### Test Cards

Use these cards for testing payments:

| Card Number | Expiry | CVV | PIN | Description |
|------------|--------|-----|-----|-------------|
| 5060990580000217499 | 03/50 | 111 | 1234 | Successful transaction |
| 6280511000000095 | 10/50 | 111 | 1111 | Failed transaction |

---

## API Endpoints

### Base URL

```
Development: http://localhost:8000/api/v1/payment
Production: https://your-domain.com/api/v1/payment
```

### Endpoints

#### 1. Get Pricing Information

```http
GET /pricing
```

**Response**:
```json
{
  "tokens_per_naira": 2.0,
  "minimum_purchase_amount": 500.0,
  "maximum_purchase_amount": 100000.0,
  "service_costs": {
    "analysis": 10,
    "transform": 5,
    "premium_insights": 20
  },
  "examples": [
    {
      "amount_ngn": 500,
      "tokens": 1000,
      "analyses": 100
    }
  ]
}
```

#### 2. Purchase Tokens

```http
POST /purchase
Content-Type: application/json

{
  "token_amount": 1000,
  "user_email": "user@example.com",
  "currency": "NGN"
}
```

**Response**:
```json
{
  "transaction_reference": "SEN_20231215120000_A1B2C3",
  "token_amount": 1000,
  "amount_paid": 500.0,
  "payment_url": "https://newwebpay.qa.interswitchng.com/collections/w/pay?...",
  "status": "pending",
  "expires_at": "2023-12-15T13:00:00Z"
}
```

#### 3. Verify Payment

```http
POST /verify/{transaction_reference}
```

**Response** (Successful):
```json
{
  "transaction_reference": "SEN_20231215120000_A1B2C3",
  "status": "successful",
  "tokens_credited": 1000,
  "current_balance": 1500,
  "message": "Payment successful and tokens credited"
}
```

#### 4. Get Token Balance

```http
GET /balance/{user_email}
```

**Response**:
```json
{
  "user_email": "user@example.com",
  "token_balance": 1500,
  "total_purchased": 2000,
  "total_consumed": 500,
  "last_purchase_date": "2023-12-15T12:00:00Z",
  "created_at": "2023-12-01T10:00:00Z",
  "updated_at": "2023-12-15T12:00:00Z"
}
```

#### 5. Get Consumption History

```http
GET /balance/{user_email}/history?limit=50
```

**Response**:
```json
{
  "user_email": "user@example.com",
  "history": [
    {
      "tokens_consumed": 10,
      "service_type": "analysis",
      "dataset_id": "64abc123...",
      "consumed_at": "2023-12-15T11:30:00Z"
    }
  ],
  "total_records": 1
}
```

#### 6. Get Transaction Status

```http
GET /transaction/{transaction_reference}
```

**Response**:
```json
{
  "transaction_reference": "SEN_20231215120000_A1B2C3",
  "user_email": "user@example.com",
  "amount": 500.0,
  "currency": "NGN",
  "token_amount": 1000,
  "status": "successful",
  "payment_gateway_response": {...},
  "created_at": "2023-12-15T12:00:00Z",
  "completed_at": "2023-12-15T12:05:00Z"
}
```

---

## Frontend Integration

### Required Components

The frontend includes two main payment components:

1. **TokenBalance.tsx** - Displays user's token balance
2. **TokenPurchase.tsx** - Modal for purchasing tokens

### Usage Example

```tsx
import { TokenBalance } from './components/TokenBalance';
import { TokenPurchase } from './components/TokenPurchase';
import { useState } from 'react';

function App() {
  const [showPurchase, setShowPurchase] = useState(false);
  const userEmail = "user@example.com"; // Get from auth

  return (
    <div>
      <TokenBalance 
        userEmail={userEmail}
        onPurchaseClick={() => setShowPurchase(true)}
      />
      
      <TokenPurchase
        userEmail={userEmail}
        isOpen={showPurchase}
        onClose={() => setShowPurchase(false)}
        onPurchaseComplete={() => {
          // Refresh balance, show success message
          console.log("Purchase completed!");
        }}
      />
    </div>
  );
}
```

### API Service Methods

The `api.ts` file includes these payment methods:

```typescript
// Get pricing
const pricing = await senalignAPI.getPricing();

// Purchase tokens
const response = await senalignAPI.purchaseTokens(1000, "user@example.com");

// Verify payment
const result = await senalignAPI.verifyPayment(transactionReference);

// Get balance
const balance = await senalignAPI.getTokenBalance("user@example.com");

// Get history
const history = await senalignAPI.getConsumptionHistory("user@example.com", 50);
```

### Interswitch Inline Checkout (Advanced)

For inline checkout (popup widget without redirect):

1. Add the Interswitch script to your `index.html`:

```html
<!-- TEST MODE -->
<script src="https://newwebpay.qa.interswitchng.com/inline-checkout.js"></script>

<!-- PRODUCTION MODE -->
<script src="https://newwebpay.interswitchng.com/inline-checkout.js"></script>
```

2. Use the inline checkout API:

```typescript
const config = await senalignAPI.getInlineCheckoutConfig(500, userEmail);

// Callback for payment result
function paymentCallback(response: any) {
  if (response.resp === "00") {
    // Payment successful
    verifyPayment(config.transaction_reference);
  }
}

// Initialize payment
window.webpayCheckout({
  ...config.config,
  onComplete: paymentCallback
});
```

---

## Token System

### Token Consumption

When a user runs an analysis, the system:

1. Checks if user has sufficient balance (10 tokens for analysis)
2. Deducts tokens from balance
3. Runs the analysis
4. Returns results with updated balance

**Example Request**:

```http
POST /api/v1/analyze/{dataset_id}
Headers:
  user-email: user@example.com
```

**Response includes**:
```json
{
  "dataset_id": "...",
  "quality_scores": {...},
  "recommendations": [...],
  "token_info": {
    "tokens_consumed": 10,
    "remaining_balance": 1490
  }
}
```

### Error Handling

**Insufficient Balance** (402 Payment Required):
```json
{
  "detail": {
    "error": "Insufficient token balance",
    "required_tokens": 10,
    "current_balance": 5,
    "message": "You need 10 tokens to run analysis but only have 5. Please purchase more tokens."
  }
}
```

### Service Costs

Customize token costs in `app/models/payment_schemas.py`:

```python
class TokenPricing(BaseModel):
    tokens_per_naira: float = Field(default=2.0, gt=0)
    analysis_cost: int = Field(default=10, gt=0)
    transform_cost: int = Field(default=5, gt=0)
    premium_insights_cost: int = Field(default=20, gt=0)
```

---

## Testing

### Backend Testing

1. **Start the server**:
```bash
make run
# or
uvicorn app.main:app --reload
```

2. **Test pricing endpoint**:
```bash
curl http://localhost:8000/api/v1/payment/pricing
```

3. **Test token purchase**:
```bash
curl -X POST http://localhost:8000/api/v1/payment/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "token_amount": 1000,
    "user_email": "test@example.com",
    "currency": "NGN"
  }'
```

4. **Test balance check**:
```bash
curl http://localhost:8000/api/v1/payment/balance/test@example.com
```

### Frontend Testing

1. **Run frontend**:
```bash
cd frontend
npm run dev
```

2. **Test flow**:
   - Click "Buy Tokens"
   - Select amount (₦1,000)
   - Click "Proceed to Payment"
   - Complete payment with test card
   - Verify tokens are credited

### Test Scenarios

| Scenario | Expected Result |
|----------|----------------|
| Purchase with test card (5060990580000217499) | Success, tokens credited |
| Purchase with failed card (6280511000000095) | Failed status |
| Analysis with sufficient tokens | Analysis runs, tokens deducted |
| Analysis with insufficient tokens | HTTP 402, error message |
| Verify pending transaction | Pending status returned |
| Verify successful transaction twice | Cached result, idempotent |

---

## Production Deployment

### 1. Update Environment Variables

```bash
# Production Interswitch credentials
INTERSWITCH_CLIENT_ID=your_live_client_id
INTERSWITCH_SECRET_KEY=your_live_secret_key
INTERSWITCH_MERCHANT_CODE=your_live_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_live_pay_item_id

# Set callback URL
PAYMENT_CALLBACK_URL=https://yourdomain.com/payment/callback
```

### 2. Update Frontend URLs

In `frontend/src/services/api.ts`, ensure production API URL is set:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.yourdomain.com";
```

### 3. Update Interswitch Mode

In `app/services/interswitch_client.py`, set mode to `LIVE`:

```python
interswitch_client = InterswitchClient(mode="LIVE")
```

Or use environment variable:

```bash
INTERSWITCH_MODE=LIVE
```

### 4. SSL/HTTPS

Interswitch **requires HTTPS** for all API requests. Ensure:
- SSL certificate is valid
- All API endpoints use HTTPS
- Redirect HTTP to HTTPS

### 5. Monitoring

Monitor these metrics:
- Payment success rate
- Token purchase volume
- Failed transactions
- Token consumption rate
- User balance trends

### 6. Database Backups

Backup MongoDB collections regularly:
```bash
mongodump --db senalign --collection user_tokens
mongodump --db senalign --collection payment_transactions
mongodump --db senalign --collection token_consumption_log
```

---

## Security Considerations

### 1. API Keys

- ✅ Store Interswitch credentials in environment variables
- ✅ Never commit credentials to version control
- ✅ Rotate secret keys periodically
- ✅ Use different credentials for test/production

### 2. Payment Verification

- ✅ Always verify payments server-side
- ✅ Check transaction amount matches expected value
- ✅ Validate transaction status with Interswitch API
- ✅ Implement idempotent token crediting

### 3. Rate Limiting

Add rate limits to payment endpoints:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.post("/purchase")
@limiter.limit("10/minute")
async def purchase_tokens(...):
    ...
```

### 4. User Authentication

- Require user authentication for all payment operations
- Validate user email in requests
- Use JWT tokens or session cookies
- Implement CSRF protection

### 5. Data Encryption

- Use TLS/SSL for all API communication
- Encrypt sensitive data at rest in MongoDB
- Never log payment card details
- Comply with PCI-DSS standards

### 6. Fraud Prevention

- Monitor unusual purchase patterns
- Implement maximum purchase limits
- Track IP addresses for suspicious activity
- Set up alerts for failed transactions

---

## Troubleshooting

### Issue: "Payment service not initialized"

**Solution**: Ensure MongoDB is running and accessible:
```bash
docker compose up -d mongodb
```

### Issue: "Failed to authenticate with Interswitch"

**Possible causes**:
1. Invalid credentials - Check environment variables
2. Network issues - Verify internet connectivity
3. Test mode URL wrong - Ensure using correct base URL

**Solution**:
```bash
# Test OAuth2 token generation
curl -X POST 'https://passport.k8.isw.la/passport/oauth/token' \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:SECRET_KEY' | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'grant_type=client_credentials'
```

### Issue: "Payment successful but tokens not credited"

**Solution**: Manually verify and credit tokens:
```bash
# Verify transaction
curl -X POST http://localhost:8000/api/v1/payment/verify/TRANSACTION_REF
```

### Issue: "Insufficient token balance" but user has tokens

**Possible causes**:
1. Cache issue - User balance not refreshed
2. Concurrent requests - Race condition

**Solution**:
```bash
# Check actual balance in database
mongo senalign --eval "db.user_tokens.findOne({user_email: 'user@example.com'})"
```

### Issue: "Payment window not opening"

**Possible causes**:
1. Popup blocked by browser
2. Invalid payment URL
3. Missing transaction reference

**Solution**:
- Allow popups for your domain
- Check browser console for errors
- Verify payment URL is generated correctly

### Issue: "Payment pending for too long"

**Solution**: Some payment methods (bank transfer, USSD) take longer to confirm.
- Wait 5-10 minutes
- Poll verification endpoint
- Contact Interswitch support if > 24 hours

---

## Additional Resources

### Interswitch Documentation

- [Authentication Guide](https://docs.interswitchgroup.com/docs/authentication)
- [Web Checkout Documentation](https://docs.interswitchgroup.com/docs/web-checkout)
- [Test Credentials](https://docs.interswitchgroup.com/docs/default-test-credentials)
- [Response Codes](https://docs.interswitchgroup.com/docs/response-codes)

### Code Examples

- **Python Backend**: `app/services/interswitch_client.py`
- **Token Service**: `app/services/token_service.py`
- **Payment Router**: `app/routers/payment.py`
- **React Components**: `frontend/src/components/Token*.tsx`

### Support

For Interswitch integration issues:
- Email: support@interswitchgroup.com
- Developer Console: https://developer.interswitchgroup.com

For Senalign payment issues:
- Check logs: `docker compose logs -f`
- Review MongoDB transactions: `mongo senalign`
- GitHub Issues: Create issue with payment integration tag

---

## Summary

The Interswitch payment integration provides a complete token-based monetization system for Senalign:

✅ **Easy Setup** - Default test credentials included  
✅ **Secure** - OAuth2 + HTTPS + Server-side verification  
✅ **Flexible** - Web redirect or inline checkout  
✅ **Complete** - Purchase, verification, balance tracking  
✅ **Production Ready** - Comprehensive error handling  

**Next Steps**:
1. Configure environment variables
2. Test with default credentials
3. Integrate UI components
4. Test purchase flow end-to-end
5. Deploy to production with live credentials

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅