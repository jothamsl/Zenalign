# Payment Integration Quick Reference Card

## 🚀 Quick Start

```bash
# 1. Start services
docker compose up -d mongodb
make run

# 2. Start frontend
cd frontend && npm run dev

# 3. Test
python test_payment.py
```

---

## 💰 Token Economics

| Item | Value |
|------|-------|
| **Rate** | 2 tokens per ₦1 |
| **Analysis Cost** | 10 tokens (₦5) |
| **Min Purchase** | ₦500 (1,000 tokens) |
| **Example** | ₦1,000 = 2,000 tokens = ~200 analyses |

---

## 🎯 User Flow

### Purchase Tokens
1. Click token balance in header → Modal opens
2. Select ₦1,000 → Shows "2,000 tokens"
3. Click "Proceed to Payment" → Interswitch opens
4. Complete payment → Tokens credited
5. Balance updates automatically

### Run Analysis
1. Upload dataset
2. Click "Analyze"
3. System checks tokens (needs 10)
4. Deducts 10 tokens → Runs analysis
5. Shows results + remaining balance

---

## 🧪 Test Credentials

**API Credentials** (Built-in):
```
Client ID: IKIAB23A4E2756605C1ABC33CE3C287E27267F660D61
Secret: secret
Merchant: MX6072
Pay Item: 9405967
```

**Test Card**:
```
Card: 5060990580000217499
Expiry: 03/50
CVV: 111
PIN: 1234
```

---

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/payment/pricing` | GET | Get pricing info |
| `/payment/purchase` | POST | Buy tokens |
| `/payment/verify/{ref}` | POST | Verify payment |
| `/payment/balance/{email}` | GET | Get balance |
| `/analyze/{id}` | POST | Run analysis (costs 10 tokens) |

**Base URL**: `http://localhost:8000/api/v1`

---

## 🎨 Frontend Components

### Header (Token Display)
```tsx
// Location: src/components/Header.tsx
<button onClick={openModal}>
  <Coins /> {tokenBalance} tokens
</button>
```

### Purchase Modal
```tsx
// Location: src/components/TokenPurchase.tsx
<TokenPurchase
  userEmail="user@senalign.com"
  isOpen={show}
  onClose={handleClose}
  onPurchaseComplete={refresh}
/>
```

---

## 🐛 Troubleshooting

### Balance not showing?
```bash
# Check backend
curl http://localhost:8000/health

# Check MongoDB
docker compose ps

# Restart all
make stop && make run
```

### Payment not crediting?
```bash
# Verify manually
curl -X POST http://localhost:8000/api/v1/payment/verify/TRANSACTION_REF

# Check balance
curl http://localhost:8000/api/v1/payment/balance/user@senalign.com
```

### Analysis fails with tokens?
```bash
# Check you're passing user-email header
# Header: "user-email: user@senalign.com"

# Check backend logs
docker compose logs -f
```

---

## 📊 Database Collections

```javascript
// user_tokens
{
  user_email: "user@senalign.com",
  token_balance: 1990,
  total_purchased: 2000,
  total_consumed: 10
}

// payment_transactions
{
  transaction_reference: "SEN_20231215120000_ABC",
  status: "successful",
  amount: 1000,
  token_amount: 2000
}

// token_consumption_log
{
  user_email: "user@senalign.com",
  tokens_consumed: 10,
  service_type: "analysis",
  consumed_at: "2023-12-15T12:00:00Z"
}
```

---

## ⚙️ Configuration

### Backend (.env)
```bash
# Optional - uses test credentials by default
INTERSWITCH_CLIENT_ID=your_client_id
INTERSWITCH_SECRET_KEY=your_secret_key
INTERSWITCH_MERCHANT_CODE=your_merchant_code
INTERSWITCH_PAY_ITEM_ID=your_pay_item_id
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing Commands

```bash
# Automated test suite
python test_payment.py

# Get pricing
curl http://localhost:8000/api/v1/payment/pricing

# Purchase tokens
curl -X POST http://localhost:8000/api/v1/payment/purchase \
  -H "Content-Type: application/json" \
  -d '{"token_amount": 1000, "user_email": "test@example.com", "currency": "NGN"}'

# Check balance
curl http://localhost:8000/api/v1/payment/balance/test@example.com

# Analyze (with tokens)
curl -X POST http://localhost:8000/api/v1/analyze/DATASET_ID \
  -H "user-email: test@example.com"
```

---

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| `PAYMENT_QUICKSTART.md` | 5-minute setup guide |
| `PAYMENT_INTEGRATION.md` | Complete integration guide (745 lines) |
| `PAYMENT_UI_GUIDE.md` | Frontend integration details |
| `PAYMENT_IMPLEMENTATION_SUMMARY.md` | What was built |
| `FRONTEND_PAYMENT_CHANGES.md` | Frontend changes summary |

---

## 🔒 Security Checklist

- ✅ OAuth2 authentication
- ✅ Server-side verification
- ✅ HTTPS required (production)
- ✅ Environment variables for credentials
- ✅ Atomic database operations
- ✅ Transaction idempotency
- ✅ Comprehensive logging

---

## 🎯 Key Files

**Backend**:
- `app/services/interswitch_client.py` - Payment gateway client
- `app/services/token_service.py` - Token management
- `app/routers/payment.py` - Payment API endpoints
- `app/routers/analyze.py` - Analysis with token consumption

**Frontend**:
- `src/components/Header.tsx` - Token balance display
- `src/components/TokenPurchase.tsx` - Purchase modal
- `src/components/TokenBalance.tsx` - Balance component
- `src/services/api.ts` - Payment API methods

**Testing**:
- `test_payment.py` - Automated test suite

---

## ✅ Status

- **Backend**: ✅ Complete (3 services, 7 endpoints)
- **Frontend**: ✅ Complete (3 components, 7 API methods)
- **Database**: ✅ Complete (3 collections with indexes)
- **Documentation**: ✅ Complete (6 docs, 2,000+ lines)
- **Testing**: ✅ Complete (automated + manual tests)
- **Production Ready**: ✅ Yes (needs live credentials)

---

## 🚀 Next Steps

1. **Test locally**: `python test_payment.py` ✅
2. **Try the UI**: Click token balance → Buy tokens
3. **Run analysis**: Upload dataset → Analyze with tokens
4. **Review docs**: Read `PAYMENT_INTEGRATION.md`
5. **Go live**: Add production Interswitch credentials

---

## 📞 Support

- **Quick Start**: `PAYMENT_QUICKSTART.md`
- **Full Guide**: `PAYMENT_INTEGRATION.md`
- **API Docs**: http://localhost:8000/docs
- **Interswitch**: https://docs.interswitchgroup.com

---

**🎉 Payment system is ready to use!**

**Start**: Click the token balance in the header → Buy tokens → Analyze datasets