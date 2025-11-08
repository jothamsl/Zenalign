# Frontend Payment Integration - Changes Summary

## Overview

The Senalign frontend has been updated to integrate the token-based payment system. Users can now see their token balance in the header and purchase tokens with a single click.

---

## Changes Made

### 1. Header Component (`src/components/Header.tsx`)

**Before**:
```tsx
<header>
  <div>Senalign Logo</div>
  <button>Log In</button>
</header>
```

**After**:
```tsx
<header>
  <div>Senalign Logo</div>
  
  {/* NEW: Token Balance Display */}
  <button onClick={() => openPurchaseModal()}>
    <Coins icon />
    {tokenBalance} tokens
  </button>
  
  <button>Log In</button>
</header>

{/* NEW: Purchase Modal */}
<TokenPurchase 
  isOpen={showModal}
  onClose={closeModal}
  onPurchaseComplete={refreshBalance}
/>
```

**Features Added**:
- ✅ Real-time token balance display
- ✅ Color-coded badge (green = good, amber = low)
- ✅ Click to open purchase modal
- ✅ Auto-refresh after purchase
- ✅ Loading states
- ✅ Error handling

**State Management**:
```typescript
const [showPurchaseModal, setShowPurchaseModal] = useState(false);
const [tokenBalance, setTokenBalance] = useState<number | null>(null);
const [loading, setLoading] = useState(true);

// Auto-fetch balance on mount
useEffect(() => {
  fetchBalance();
}, []);

// Refresh after purchase
const handlePurchaseComplete = () => {
  fetchBalance();
};
```

**Visual States**:
- **Good Balance (≥20 tokens)**: Green badge with green icon
- **Low Balance (<20 tokens)**: Amber badge with amber icon
- **Loading**: Shows "..." while fetching
- **Hover**: Scales up slightly (1.05x)

---

### 2. API Service (`src/services/api.ts`)

**Changes**:

#### Updated `analyzeDataset` Method
```typescript
// BEFORE
analyzeDataset: async (datasetId: string) => {
  const response = await api.post(`/api/v1/analyze/${datasetId}`);
  return response.data;
}

// AFTER
analyzeDataset: async (
  datasetId: string,
  userEmail: string = "user@senalign.com"
) => {
  const response = await api.post(
    `/api/v1/analyze/${datasetId}`,
    null,
    {
      headers: {
        "user-email": userEmail,  // Required for token consumption
      },
    }
  );
  return response.data;
}
```

#### New Payment Methods
```typescript
// Get token pricing
getPricing: async () => {
  const response = await api.get("/api/v1/payment/pricing");
  return response.data;
}

// Purchase tokens
purchaseTokens: async (tokenAmount: number, userEmail: string) => {
  const response = await api.post("/api/v1/payment/purchase", {
    token_amount: tokenAmount,
    user_email: userEmail,
    currency: "NGN",
  });
  return response.data;
}

// Verify payment
verifyPayment: async (transactionReference: string) => {
  const response = await api.post(
    `/api/v1/payment/verify/${transactionReference}`
  );
  return response.data;
}

// Get token balance
getTokenBalance: async (userEmail: string) => {
  const response = await api.get(`/api/v1/payment/balance/${userEmail}`);
  return response.data;
}

// Get consumption history
getConsumptionHistory: async (userEmail: string, limit: number = 50) => {
  const response = await api.get(
    `/api/v1/payment/balance/${userEmail}/history?limit=${limit}`
  );
  return response.data;
}

// Get transaction status
getTransactionStatus: async (transactionReference: string) => {
  const response = await api.get(
    `/api/v1/payment/transaction/${transactionReference}`
  );
  return response.data;
}

// Get inline checkout config
getInlineCheckoutConfig: async (amount: number, userEmail: string) => {
  const response = await api.get(
    `/api/v1/payment/inline-config?amount=${amount}&user_email=${userEmail}`
  );
  return response.data;
}
```

---

### 3. ChatInput Component (`src/components/ChatInput.tsx`)

**Changes**:

#### Updated Analysis Call
```typescript
// BEFORE
const analysisReport = await senalignAPI.analyzeDataset(
  uploadResponse.dataset_id
);

// AFTER
const analysisReport = await senalignAPI.analyzeDataset(
  uploadResponse.dataset_id,
  "user@senalign.com"  // Pass user email for token check
);
```

#### Enhanced Error Handling
```typescript
// BEFORE
catch (err: any) {
  setError(
    err.response?.data?.detail || 
    err.message || 
    "Failed to analyze dataset. Please try again."
  );
}

// AFTER
catch (err: any) {
  // Check for insufficient tokens error (HTTP 402)
  if (err.response?.status === 402) {
    const errorDetail = err.response?.data?.detail;
    if (typeof errorDetail === "object" && 
        errorDetail.error === "Insufficient token balance") {
      setError(
        `⚠️ Insufficient tokens: You need ${errorDetail.required_tokens} tokens ` +
        `but only have ${errorDetail.current_balance}. ` +
        `Click the token balance in the header to purchase more tokens.`
      );
    } else {
      setError(
        "Insufficient tokens to run analysis. Please purchase tokens to continue."
      );
    }
  } else {
    setError(
      err.response?.data?.detail || 
      err.message || 
      "Failed to analyze dataset. Please try again."
    );
  }
}
```

**User Experience**:
- **Before**: Generic error message
- **After**: 
  - Detects HTTP 402 (Payment Required)
  - Shows exact token counts
  - Provides clear action: "Click token balance to purchase"
  - User-friendly emoji indicator

---

### 4. New Components Created

#### TokenBalance.tsx (118 lines)
**Already existed** - Imported and integrated into Header

**Features**:
- Real-time balance display
- Visual indicators
- Refresh functionality
- Low balance warnings
- Error handling

#### TokenPurchase.tsx (422 lines)
**Already existed** - Imported and integrated into Header

**Features**:
- Beautiful modal UI
- Pricing information
- Quick select options (₦500, ₦1,000, ₦5,000)
- Custom amount input
- Live calculations
- Interswitch payment integration
- Auto-verification polling
- Success/error feedback

---

## User Flow

### Purchase Flow
1. User sees token balance in header (e.g., "5 tokens" in amber)
2. Clicks the token badge
3. Modal opens showing pricing options
4. Selects ₦1,000 (shows "2,000 tokens = ~200 analyses")
5. Clicks "Proceed to Payment"
6. Interswitch payment window opens
7. User completes payment
8. Window closes
9. System verifies automatically
10. Success message appears
11. Modal closes
12. Balance updates to 2,005 tokens (green)

### Analysis Flow with Tokens
1. User uploads dataset
2. Describes ML problem
3. Clicks "Analyze"
4. **System checks token balance** (needs 10 tokens)
5. If sufficient:
   - Deducts 10 tokens
   - Runs analysis
   - Shows results with "Tokens consumed: 10, Remaining: 1,995"
6. If insufficient:
   - Shows error: "Need 10 tokens, have 5"
   - User clicks token badge → Purchases → Tries again

---

## Visual Changes

### Header (Desktop)
```
┌────────────────────────────────────────────────────────────────┐
│  🛡️ Senalign          [💰 1,995 tokens]  [Log In]             │
└────────────────────────────────────────────────────────────────┘
```

### Header (Mobile)
```
┌──────────────────────────────────┐
│  🛡️ Senalign  [💰 1,995] [Login] │
└──────────────────────────────────┘
```

### Token Balance States

**Good Balance**:
```
┌──────────────────────┐
│ 💰 1,995 tokens     │  ← Green background
└──────────────────────┘
```

**Low Balance**:
```
┌──────────────────────┐
│ ⚠️ 15 tokens        │  ← Amber background
└──────────────────────┘
```

**Loading**:
```
┌──────────────────────┐
│ 💰 ...              │  ← Gray background
└──────────────────────┘
```

---

## Configuration

### Default User Email
```typescript
// src/components/Header.tsx
const DEFAULT_USER_EMAIL = "user@senalign.com";
```

**Note**: For production, replace with:
```typescript
import { useAuth } from './context/AuthContext';

const { user } = useAuth();
const userEmail = user?.email || "guest@senalign.com";
```

### API Base URL
```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

**Environment Variable** (`.env`):
```bash
VITE_API_URL=http://localhost:8000  # Development
```

---

## Testing

### Manual Testing Steps

1. **Start services**:
   ```bash
   # Backend
   docker compose up -d mongodb
   make run
   
   # Frontend
   cd frontend
   npm run dev
   ```

2. **Test token display**:
   - ✅ Open http://localhost:3000
   - ✅ See token balance in header
   - ✅ Check color (green or amber)

3. **Test purchase flow**:
   - ✅ Click token balance
   - ✅ Modal opens with pricing
   - ✅ Select ₦1,000
   - ✅ Click "Proceed to Payment"
   - ✅ Interswitch window opens
   - ✅ Enter test card: 5060990580000217499
   - ✅ Complete payment
   - ✅ Verify tokens credited

4. **Test analysis**:
   - ✅ Upload CSV file
   - ✅ Enter problem description
   - ✅ Click "Analyze"
   - ✅ Analysis runs
   - ✅ Balance decrements by 10

5. **Test insufficient tokens**:
   - ✅ Use email with 0 tokens
   - ✅ Try to analyze
   - ✅ See helpful error message
   - ✅ Click token balance
   - ✅ Purchase tokens
   - ✅ Retry analysis successfully

---

## Files Modified

### Modified Files
1. `src/components/Header.tsx` - Added token balance and purchase modal
2. `src/services/api.ts` - Added payment methods, updated analyze method
3. `src/components/ChatInput.tsx` - Enhanced error handling for insufficient tokens

### New Files
1. `frontend/PAYMENT_UI_GUIDE.md` - Comprehensive UI integration guide

### Files Used (Already Existed)
1. `src/components/TokenBalance.tsx` - Reusable balance component
2. `src/components/TokenPurchase.tsx` - Purchase modal component

---

## Dependencies

**No new dependencies required!**

All payment components use existing packages:
- `react` - Core framework
- `lucide-react` - Icons (Coins, AlertCircle, etc.)
- `axios` - API calls

---

## Breaking Changes

### None!

The integration is **backward compatible**:
- `user-email` header is optional in analyze endpoint
- Works without authentication (uses default email)
- Gracefully handles missing token service
- Shows helpful errors instead of breaking

---

## Next Steps

### For Production

1. **Add Authentication**:
   ```typescript
   // Replace hardcoded email with:
   const { user } = useAuth();
   const userEmail = user?.email;
   ```

2. **Update Environment**:
   ```bash
   # .env.production
   VITE_API_URL=https://api.yourdomain.com
   ```

3. **Test with Live Credentials**:
   - Update backend Interswitch credentials
   - Test full payment flow
   - Verify SSL/HTTPS

4. **Build for Production**:
   ```bash
   npm run build
   # Deploy dist/ folder
   ```

---

## Summary

✅ **What Changed**:
- Token balance in header (1 component update)
- Purchase modal integration (1 component update)
- Payment API methods (7 new methods)
- Enhanced error handling (1 component update)

✅ **User Benefits**:
- See balance at a glance
- One-click purchase access
- Clear error messages
- Smooth payment experience
- Auto-refresh after purchase

✅ **Developer Benefits**:
- Clean integration
- Reusable components
- Type-safe API methods
- Comprehensive error handling
- Easy to test

---

**The frontend is now fully integrated with the payment system! 🎉**

Users can purchase tokens and run analyses seamlessly.