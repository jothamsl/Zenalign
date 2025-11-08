# Frontend Payment Integration Guide

## Overview

The Senalign frontend now includes a fully integrated token-based payment system with Interswitch. Users can purchase tokens directly from the UI and use them to run dataset analyses.

---

## What's New in the UI

### 1. Token Balance Display (Header)

The header now shows your current token balance in the top-right corner, next to the "Log In" button.

**Visual Indicators**:
- 🟢 **Green badge** - Good balance (20+ tokens)
- 🟡 **Amber badge** - Low balance (< 20 tokens)
- **Click to buy** - Clicking the badge opens the purchase modal

**Example**:
```
[Senalign Logo]                    [💰 150 tokens] [Log In]
```

### 2. Token Purchase Modal

Click the token balance to open a beautiful purchase modal with:

**Features**:
- Real-time pricing information
- Quick select options (₦500, ₦1,000, ₦5,000)
- Custom amount input
- Live token calculation
- Analyses count preview
- Interswitch payment integration

**Flow**:
1. Click token balance → Modal opens
2. Select amount or enter custom
3. See preview: "₦1,000 = 2,000 tokens = ~200 analyses"
4. Click "Proceed to Payment"
5. Interswitch window opens
6. Complete payment
7. Tokens automatically credited
8. Balance updates in header

### 3. Insufficient Token Handling

When running an analysis without enough tokens:

**Before**:
```
Generic error: "Analysis failed"
```

**Now**:
```
⚠️ Insufficient tokens: You need 10 tokens but only have 5. 
Click the token balance in the header to purchase more tokens.
```

**What happens**:
- Upload dataset ✅
- Click analyze ✅
- System checks tokens ⚠️
- Shows helpful error with token count
- User clicks token badge → Buys tokens → Tries again ✅

---

## Components

### TokenBalance (in Header)

**Location**: `src/components/Header.tsx`

**Props**: None (uses default user email internally)

**State**:
- `tokenBalance` - Current token count
- `loading` - Fetch status
- `showPurchaseModal` - Modal visibility

**Features**:
- Auto-fetches balance on mount
- Refreshes after purchase
- Color-coded (green/amber)
- Hover effect
- Click to purchase

### TokenPurchase Modal

**Location**: `src/components/TokenPurchase.tsx`

**Props**:
```typescript
interface TokenPurchaseProps {
  userEmail: string;
  isOpen: boolean;
  onClose: () => void;
  onPurchaseComplete?: () => void;
}
```

**Features**:
- Pricing display (tokens per naira, cost per service)
- Quick select buttons
- Custom amount validation
- Real-time calculations
- Payment window integration
- Auto-verification polling
- Success/error feedback

**Usage**:
```tsx
<TokenPurchase
  userEmail="user@senalign.com"
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onPurchaseComplete={() => {
    // Refresh balance
    fetchBalance();
  }}
/>
```

---

## User Flow

### First-Time User Journey

1. **Land on homepage**
   - See token balance: `0 tokens` (amber/warning)
   - Balance automatically fetched

2. **Click token balance**
   - Purchase modal opens
   - See pricing: "₦500 = 1,000 tokens = ~100 analyses"

3. **Select ₦1,000**
   - Preview shows: "2,000 tokens = ~200 analyses"
   - Click "Proceed to Payment"

4. **Interswitch Window**
   - Popup opens with payment form
   - Enter test card: `5060990580000217499`
   - Complete payment

5. **Back to Senalign**
   - System verifies automatically
   - Success message: "Payment successful!"
   - Modal closes
   - Balance updates: `2,000 tokens` (green)

6. **Upload dataset**
   - Drag and drop CSV
   - Describe ML problem
   - Click "Analyze"

7. **Analysis runs**
   - System deducts 10 tokens
   - Analysis completes
   - Results show: "Tokens consumed: 10, Remaining: 1,990"

8. **Continue analyzing**
   - User can run 199 more analyses!

### Returning User Journey

1. **Land on homepage**
   - See balance: `1,990 tokens` (green)

2. **Upload and analyze**
   - No payment needed
   - Analysis runs immediately
   - Balance decrements automatically

3. **Low balance warning**
   - When balance < 20: Badge turns amber
   - Visual reminder to top up

4. **Run out of tokens**
   - Try to analyze with 5 tokens
   - Get error: "Need 10, have 5"
   - Click balance → Buy more → Continue

---

## Configuration

### Default User Email

Currently hardcoded for demo purposes:

**File**: `src/components/Header.tsx`
```typescript
const DEFAULT_USER_EMAIL = "user@senalign.com";
```

**For Production**: Replace with auth context:
```typescript
import { useAuth } from './context/AuthContext';

export function Header() {
  const { user } = useAuth();
  const userEmail = user?.email || "user@senalign.com";
  // ...
}
```

### API Base URL

**File**: `src/services/api.ts`
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

**Environment Variable**: `.env`
```bash
VITE_API_URL=http://localhost:8000  # Development
VITE_API_URL=https://api.yourdomain.com  # Production
```

---

## Testing the UI

### 1. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:3000`

### 2. Test Token Display

- ✅ Token balance visible in header
- ✅ Shows "0 tokens" for new user
- ✅ Amber color for 0 balance
- ✅ Hover effect on badge

### 3. Test Purchase Flow

**Click token balance**:
- ✅ Modal opens
- ✅ Pricing information displayed
- ✅ Quick select options visible

**Select ₦1,000**:
- ✅ Amount highlighted
- ✅ Summary shows: "2,000 tokens, ~200 analyses"

**Click "Proceed to Payment"**:
- ✅ Interswitch popup opens
- ✅ Modal stays open with "Processing..." message

**Enter test card**:
```
Card: 5060990580000217499
Expiry: 03/50
CVV: 111
PIN: 1234
OTP: 123456
```

**Complete payment**:
- ✅ Popup closes
- ✅ Verification starts
- ✅ Success message appears
- ✅ Modal closes after 3 seconds
- ✅ Balance updates to 2,000 tokens
- ✅ Badge turns green

### 4. Test Analysis with Tokens

**Upload dataset**:
- ✅ CSV file accepted
- ✅ Problem description entered

**Click Analyze**:
- ✅ Balance check passes (2,000 > 10)
- ✅ Analysis runs
- ✅ Results show with token info
- ✅ Balance decrements to 1,990

### 5. Test Insufficient Tokens

**Method 1 - Empty account**:
- Use email: `empty@senalign.com`
- Try to analyze
- ✅ Error: "Need 10 tokens, have 0"

**Method 2 - Consume all tokens**:
- Run analyses until < 10 tokens
- Try one more analysis
- ✅ Error message with token counts
- ✅ Prompt to purchase more

---

## Styling & Design

### Color Scheme

**Token Balance**:
- Good balance: `bg-green-50 border-green-200 text-green-700`
- Low balance: `bg-amber-50 border-amber-200 text-amber-700`

**Modal**:
- Header: Blue gradient
- Selected option: Blue border
- Buttons: Blue primary, gray secondary
- Success: Green background
- Error: Red background

### Responsive Design

**Desktop** (> 768px):
- Token balance: Full display with icon and text
- Modal: 2xl max-width, centered
- Grid: 3 columns for quick select

**Mobile** (< 768px):
- Token balance: Icon + number only
- Modal: Full screen on small devices
- Grid: Single column stacked

### Animations

- **Badge hover**: Scale up slightly (1.05x)
- **Modal open**: Fade in + slide up
- **Balance update**: Number animation
- **Status changes**: Color transitions

---

## API Integration

### Updated API Methods

**File**: `src/services/api.ts`

```typescript
// Analysis now includes user email for token check
analyzeDataset: async (
  datasetId: string,
  userEmail: string = "user@senalign.com"
) => {
  const response = await api.post(`/api/v1/analyze/${datasetId}`, null, {
    headers: { "user-email": userEmail }
  });
  return response.data;
}

// New payment methods
getPricing: async () => { ... }
purchaseTokens: async (tokenAmount, userEmail) => { ... }
verifyPayment: async (transactionRef) => { ... }
getTokenBalance: async (userEmail) => { ... }
```

### Error Handling

**HTTP 402 - Payment Required**:
```typescript
if (err.response?.status === 402) {
  const { required_tokens, current_balance } = err.response.data.detail;
  setError(`Need ${required_tokens} tokens, have ${current_balance}`);
}
```

**Network Errors**:
```typescript
catch (err: any) {
  setError(err.response?.data?.detail || "Failed to connect");
}
```

---

## Common Issues

### Issue: Balance not showing

**Symptoms**: Header shows "..." forever

**Causes**:
1. Backend not running
2. MongoDB not running
3. Wrong API URL

**Solution**:
```bash
# Terminal 1: Start MongoDB
docker compose up -d mongodb

# Terminal 2: Start backend
make run

# Terminal 3: Start frontend
cd frontend && npm run dev

# Check API URL in .env
echo $VITE_API_URL
```

### Issue: Payment window not opening

**Symptoms**: Click "Proceed to Payment", nothing happens

**Causes**:
1. Popup blocked by browser
2. Interswitch URL error

**Solution**:
```
1. Check browser console for errors
2. Allow popups for localhost:3000
3. Check backend logs: docker compose logs -f
```

### Issue: Tokens not credited after payment

**Symptoms**: Payment successful but balance unchanged

**Causes**:
1. Verification failed
2. Backend error
3. Database issue

**Solution**:
```bash
# Check transaction status
curl http://localhost:8000/api/v1/payment/transaction/TRANSACTION_REF

# Manually verify
curl -X POST http://localhost:8000/api/v1/payment/verify/TRANSACTION_REF

# Check MongoDB
mongo senalign --eval "db.user_tokens.findOne({user_email: 'user@senalign.com'})"
```

### Issue: Analysis fails with tokens available

**Symptoms**: Have 100 tokens but analysis fails

**Causes**:
1. User email mismatch
2. Backend not checking tokens
3. Cache issue

**Solution**:
```bash
# Check balance with correct email
curl http://localhost:8000/api/v1/payment/balance/user@senalign.com

# Check backend logs for token check
# Should see: "Checking token balance for user@senalign.com"

# Restart backend
make stop && make run
```

---

## Production Checklist

### Before Deployment

- [ ] Replace hardcoded email with auth context
- [ ] Update VITE_API_URL to production URL
- [ ] Test with live Interswitch credentials
- [ ] Verify SSL/HTTPS on all endpoints
- [ ] Test payment flow end-to-end
- [ ] Test error scenarios
- [ ] Check mobile responsiveness
- [ ] Verify token calculations are correct
- [ ] Add analytics tracking
- [ ] Test with different browsers
- [ ] Load test payment flow
- [ ] Set up monitoring/alerts

### Environment Variables

```bash
# .env.production
VITE_API_URL=https://api.yourdomain.com
VITE_ENABLE_ANALYTICS=true
```

### Build for Production

```bash
cd frontend
npm run build
# Output in: dist/
```

---

## Future Enhancements

### Planned Features

1. **Token Packages**
   - Starter: ₦500 (1,000 tokens)
   - Pro: ₦2,000 (5,000 tokens + 10% bonus)
   - Enterprise: ₦10,000 (30,000 tokens + 20% bonus)

2. **Token History**
   - Detailed consumption log
   - Purchase history
   - Export to CSV

3. **Notifications**
   - Email on purchase success
   - Low balance warnings
   - Usage analytics

4. **User Authentication**
   - Sign up / Sign in
   - Token balances per user
   - Secure sessions

5. **Payment Methods**
   - Save card for quick purchase
   - Auto top-up when balance low
   - Subscription plans

---

## Summary

✅ **Integrated Features**:
- Token balance in header
- Purchase modal with Interswitch
- Insufficient token handling
- Auto-refresh after purchase
- Error messages with guidance

✅ **User Experience**:
- One-click purchase access
- Visual balance indicators
- Helpful error messages
- Smooth payment flow
- Automatic verification

✅ **Developer Experience**:
- Clean component architecture
- Reusable API methods
- TypeScript types
- Error handling
- Documentation

---

**Ready to test!** Start with clicking the token balance in the header. 🚀