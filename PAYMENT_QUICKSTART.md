# Payment Integration Quick Start Guide

Get started with the Senalign payment system in 5 minutes! 🚀

---

## Prerequisites

Before you begin, ensure you have:
- ✅ MongoDB running (`docker compose up -d mongodb`)
- ✅ Backend API running (`make run` or `uvicorn app.main:app --reload`)
- ✅ Python dependencies installed (`pip install -r requirements.txt`)

---

## Step 1: Verify Payment System is Running

Run the automated test suite:

```bash
python test_payment.py
```

You should see:
```
✓ Health Check
✓ Get Pricing
✓ Get Balance
✓ Purchase Tokens
✓ Get Transaction Status
✓ Consumption History
✓ Inline Checkout Config

Success Rate: 100%
✓ All tests passed! Payment integration is working correctly.
```

---

## Step 2: Test Payment Flow with API

### 2.1 Get Token Pricing

```bash
curl http://localhost:8000/api/v1/payment/pricing
```

Expected response:
```json
{
  "tokens_per_naira": 2.0,
  "service_costs": {
    "analysis": 10,
    "transform": 5,
    "premium_insights": 20
  },
  "examples": [
    {"amount_ngn": 500, "tokens": 1000, "analyses": 100},
    {"amount_ngn": 1000, "tokens": 2000, "analyses": 200}
  ]
}
```

### 2.2 Check Your Token Balance

```bash
curl http://localhost:8000/api/v1/payment/balance/your@email.com
```

Expected response (new user):
```json
{
  "user_email": "your@email.com",
  "token_balance": 0,
  "total_purchased": 0,
  "total_consumed": 0,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### 2.3 Purchase Tokens

```bash
curl -X POST http://localhost:8000/api/v1/payment/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "token_amount": 1000,
    "user_email": "your@email.com",
    "currency": "NGN"
  }'
```

Expected response:
```json
{
  "transaction_reference": "SEN_20240115120000_ABC123",
  "token_amount": 1000,
  "amount_paid": 500.0,
  "payment_url": "https://newwebpay.qa.interswitchng.com/collections/w/pay?...",
  "status": "pending",
  "expires_at": "2024-01-15T13:00:00Z"
}
```

**Save the `transaction_reference` - you'll need it for verification!**

### 2.4 Complete Payment (Test Mode)

1. Open the `payment_url` from step 2.3 in your browser
2. You'll see the Interswitch test payment page
3. Use these test card details:

```
Card Number: 5060990580000217499
Expiry Date: 03/50
CVV: 111
PIN: 1234
```

4. Complete the payment flow
5. You'll be redirected back (or can close the window)

### 2.5 Verify Payment & Credit Tokens

```bash
curl -X POST http://localhost:8000/api/v1/payment/verify/SEN_20240115120000_ABC123
```

Expected response (successful):
```json
{
  "transaction_reference": "SEN_20240115120000_ABC123",
  "status": "successful",
  "tokens_credited": 1000,
  "current_balance": 1000,
  "message": "Payment successful and tokens credited"
}
```

### 2.6 Verify Your New Balance

```bash
curl http://localhost:8000/api/v1/payment/balance/your@email.com
```

Expected response:
```json
{
  "user_email": "your@email.com",
  "token_balance": 1000,
  "total_purchased": 1000,
  "total_consumed": 0,
  "last_purchase_date": "2024-01-15T12:05:00Z"
}
```

**Success! You now have 1000 tokens = ~100 analyses** 🎉

---

## Step 3: Use Tokens for Analysis

### 3.1 Upload a Dataset

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@your_dataset.csv" \
  -F "problem_description=Predicting customer churn using behavioral data"
```

Response includes `dataset_id` - save this!

### 3.2 Run Analysis (Consumes Tokens)

```bash
curl -X POST http://localhost:8000/api/v1/analyze/YOUR_DATASET_ID \
  -H "user-email: your@email.com"
```

Expected response includes:
```json
{
  "dataset_id": "...",
  "quality_scores": {...},
  "recommendations": [...],
  "token_info": {
    "tokens_consumed": 10,
    "remaining_balance": 990
  }
}
```

**10 tokens consumed!** You now have 990 tokens remaining.

### 3.3 Check Consumption History

```bash
curl http://localhost:8000/api/v1/payment/balance/your@email.com/history
```

You'll see a log of your token usage:
```json
{
  "user_email": "your@email.com",
  "history": [
    {
      "tokens_consumed": 10,
      "service_type": "analysis",
      "dataset_id": "...",
      "consumed_at": "2024-01-15T12:10:00Z"
    }
  ],
  "total_records": 1
}
```

---

## Step 4: Frontend Integration

### 4.1 Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4.2 Start Frontend

```bash
npm run dev
```

Frontend opens at `http://localhost:3000`

### 4.3 Test Payment UI

1. Open the app in your browser
2. Look for the **Token Balance** widget in the header
3. Click **"Buy Tokens"** button
4. Select an amount (₦500, ₦1000, or custom)
5. Click **"Proceed to Payment"**
6. Complete payment in popup window
7. Watch your balance update automatically!

---

## Testing Scenarios

### Scenario 1: Successful Payment
- Card: `5060990580000217499`
- Result: ✅ Payment successful, tokens credited

### Scenario 2: Failed Payment
- Card: `6280511000000095`
- Result: ❌ Payment failed, no tokens credited

### Scenario 3: Insufficient Tokens
- Balance: 5 tokens
- Try to analyze (costs 10 tokens)
- Result: ❌ HTTP 402 error, purchase prompt

### Scenario 4: Sufficient Tokens
- Balance: 100 tokens
- Analyze dataset (costs 10 tokens)
- Result: ✅ Analysis runs, 90 tokens remaining

---

## Common Issues & Solutions

### Issue: "Payment service not initialized"

**Solution**: Ensure MongoDB is running
```bash
docker compose up -d mongodb
make run
```

### Issue: "Failed to authenticate with Interswitch"

**Solution**: Using test credentials by default. Check logs:
```bash
# Backend logs should show:
# "InterswitchClient initialized in TEST mode with merchant MX6072"
```

### Issue: Payment window doesn't open

**Solution**: Allow popups in your browser for `localhost:3000`

### Issue: Payment successful but tokens not credited

**Solution**: Manually verify the transaction:
```bash
curl -X POST http://localhost:8000/api/v1/payment/verify/TRANSACTION_REF
```

### Issue: "Insufficient token balance" but I have tokens

**Solution**: Refresh your balance:
```bash
curl http://localhost:8000/api/v1/payment/balance/your@email.com
```

---

## Environment Variables (Optional)

The system works with **default test credentials**. For production:

```bash
# Add to .env file
INTERSWITCH_CLIENT_ID=your_live_client_id
INTERSWITCH_SECRET_KEY=your_live_secret_key
INTERSWITCH_MERCHANT_CODE=your_live_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_live_pay_item_id
PAYMENT_CALLBACK_URL=https://yourdomain.com/payment/callback
```

---

## API Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/payment/pricing` | GET | Get token pricing |
| `/payment/purchase` | POST | Initiate purchase |
| `/payment/verify/{ref}` | POST | Verify payment |
| `/payment/balance/{email}` | GET | Get balance |
| `/payment/balance/{email}/history` | GET | Get history |
| `/payment/transaction/{ref}` | GET | Get transaction |
| `/analyze/{id}` | POST | Run analysis (costs tokens) |

---

## Token Economics

| Purchase | Tokens | Cost | Analyses |
|----------|--------|------|----------|
| ₦500 | 1,000 | ₦500 | ~100 |
| ₦1,000 | 2,000 | ₦1,000 | ~200 |
| ₦5,000 | 10,000 | ₦5,000 | ~1,000 |

**Rate**: 2 tokens per ₦1  
**Analysis Cost**: 10 tokens each  
**Transform Cost**: 5 tokens each  
**Premium Insights**: 20 tokens each

---

## Next Steps

1. ✅ Run `python test_payment.py` to verify setup
2. ✅ Test purchase flow with test cards
3. ✅ Upload a dataset and run analysis with tokens
4. ✅ Check balance and consumption history
5. ✅ Test frontend payment UI
6. 📚 Read full docs: [PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md)
7. 🚀 Deploy to production with live credentials

---

## Support

- **Documentation**: [PAYMENT_INTEGRATION.md](PAYMENT_INTEGRATION.md)
- **API Docs**: http://localhost:8000/docs
- **Test Script**: `python test_payment.py`
- **Interswitch Docs**: https://docs.interswitchgroup.com

---

## Test Cards Reference

| Card | Expiry | CVV | PIN | Result |
|------|--------|-----|-----|--------|
| 5060990580000217499 | 03/50 | 111 | 1234 | ✅ Success |
| 6280511000000095 | 10/50 | 111 | 1111 | ❌ Failed |

---

**Ready to go!** Start with `python test_payment.py` 🚀