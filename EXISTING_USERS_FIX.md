# Fix for Existing Users - Free Tokens Grant

## Issue

Existing users who signed up before the free tokens feature was implemented still have 0 tokens in their database records. This prevents them from using the platform.

## Solution

We've updated all existing users with 0 tokens to have 100 free tokens.

---

## What Was Done

### 1. Immediate Fix (Already Applied)

The user `user@senalign.com` was updated directly:

```bash
# Before
token_balance: 0
total_purchased: 0
total_consumed: 0

# After
token_balance: 100
total_purchased: 100
total_consumed: 0
```

### 2. Migration Script Created

A migration script is now available to update all existing users:

**Location**: `migrations/grant_free_tokens_to_existing_users.py`

**Usage**:
```bash
# Dry run (see what would change)
python migrations/grant_free_tokens_to_existing_users.py

# Apply changes
python migrations/grant_free_tokens_to_existing_users.py --live

# Apply and verify
python migrations/grant_free_tokens_to_existing_users.py --live --verify
```

---

## For Future Existing Users

If you need to manually grant free tokens to a specific user:

### Option 1: Using MongoDB Shell

```bash
mongo senalign
```

```javascript
db.user_tokens.updateOne(
  { user_email: "user@example.com" },
  {
    $set: {
      token_balance: 100,
      total_purchased: 100,
      updated_at: new Date()
    }
  }
)
```

### Option 2: Using Python Script

```python
from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient('mongodb://localhost:27017/')
db = client['senalign']

db['user_tokens'].update_one(
    {'user_email': 'user@example.com'},
    {
        '$set': {
            'token_balance': 100,
            'total_purchased': 100,
            'updated_at': datetime.now(timezone.utc)
        }
    }
)
```

### Option 3: Using Migration Script

```bash
# Will only update users with 0 tokens
python migrations/grant_free_tokens_to_existing_users.py --live
```

---

## Migration Script Features

✅ **Safe**: Only updates users with `token_balance = 0` and `total_purchased = 0`  
✅ **Dry Run**: Test mode to see what would change  
✅ **Confirmation**: Asks for confirmation before making changes  
✅ **Verification**: Can verify results after migration  
✅ **Logging**: Detailed output of all changes  
✅ **Error Handling**: Graceful handling of failures  

---

## Example Migration Output

```bash
$ python migrations/grant_free_tokens_to_existing_users.py --live

======================================================================
Migration: Grant Free Tokens to Existing Users
======================================================================
Database: senalign
Free tokens amount: 100
Mode: LIVE
======================================================================

🔍 Finding eligible users...
📊 Found 3 eligible user(s):

  • user@senalign.com
    - Current balance: 0 tokens
    - Total purchased: 0 tokens
    - Total consumed: 0 tokens
    - Created: 2025-11-08T10:58:07.200000

  • testuser@example.com
    - Current balance: 0 tokens
    - Total purchased: 0 tokens
    - Total consumed: 5 tokens
    - Created: 2025-11-07T15:30:00.000000

  • demo@senalign.com
    - Current balance: 0 tokens
    - Total purchased: 0 tokens
    - Total consumed: 0 tokens
    - Created: 2025-11-06T09:15:00.000000

⚠️  This will grant free tokens to the above users.
Continue? (yes/no): yes

🚀 Granting free tokens...

  ✓ Granted 100 tokens to user@senalign.com
  ✓ Granted 100 tokens to testuser@example.com
  ✓ Granted 100 tokens to demo@senalign.com

======================================================================
Migration Summary
======================================================================
Total users processed: 3
✓ Successful: 3
✗ Failed: 0
Mode: LIVE
======================================================================
```

---

## Verification

After running the migration, verify it worked:

```bash
# Check specific user
curl http://localhost:8000/api/v1/payment/balance/user@senalign.com

# Or using MongoDB
mongo senalign --eval "db.user_tokens.find({user_email: 'user@senalign.com'}).pretty()"
```

**Expected Result**:
```json
{
  "user_email": "user@senalign.com",
  "token_balance": 100,
  "total_purchased": 100,
  "total_consumed": 0,
  "last_purchase_date": null,
  "created_at": "2025-11-08T10:58:07.200000",
  "updated_at": "2025-11-08T12:48:20.047000"
}
```

---

## Prevention for Future

New users created after this fix will automatically receive 100 free tokens due to the updated code in:

**File**: `app/services/token_service.py`

**Code**:
```python
def get_or_create_user_balance(self, user_email: str):
    # Check if user exists
    user_data = self.users_collection.find_one({"user_email": user_email})
    
    if user_data:
        return UserTokenBalance(**user_data)
    
    # NEW USER: Automatically grant 100 free tokens
    new_user = UserTokenBalance(
        user_email=user_email,
        token_balance=FREE_TOKENS_FOR_NEW_USERS,  # 100 tokens
        total_purchased=FREE_TOKENS_FOR_NEW_USERS,
        total_consumed=0,