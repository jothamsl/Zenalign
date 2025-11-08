#!/usr/bin/env python3
"""
Migration Script: Grant Free Tokens to Existing Users

This script gives 100 free tokens to existing users who currently have 0 tokens.
This is a one-time migration to ensure all users have tokens to try the platform.

Usage:
    python migrations/grant_free_tokens_to_existing_users.py

Safety:
    - Only updates users with token_balance = 0
    - Does NOT affect users who already have tokens
    - Does NOT affect users who have made purchases
    - Provides detailed logging
    - Supports dry-run mode for testing
"""

import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.payment_config import FREE_TOKENS_FOR_NEW_USERS

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = "senalign"


class TokenMigration:
    """Migration class to grant free tokens to existing users."""

    def __init__(self, mongodb_uri: str, db_name: str, dry_run: bool = False):
        """
        Initialize migration.

        Args:
            mongodb_uri: MongoDB connection string
            db_name: Database name
            dry_run: If True, shows what would be done without making changes
        """
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]
        self.users_collection = self.db["user_tokens"]
        self.dry_run = dry_run

    def find_eligible_users(self):
        """
        Find users eligible for free tokens.

        Eligible users:
        - token_balance = 0
        - total_purchased = 0 (haven't purchased before)
        - total_consumed >= 0 (may have consumed tokens already)

        Returns:
            List of user documents
        """
        query = {
            "token_balance": 0,
            "total_purchased": 0,
        }

        users = list(self.users_collection.find(query))
        return users

    def grant_free_tokens(self, user_email: str) -> bool:
        """
        Grant free tokens to a specific user.

        Args:
            user_email: User email address

        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(
                f"  [DRY RUN] Would grant {FREE_TOKENS_FOR_NEW_USERS} tokens to {user_email}"
            )
            return True

        try:
            result = self.users_collection.update_one(
                {"user_email": user_email},
                {
                    "$set": {
                        "token_balance": FREE_TOKENS_FOR_NEW_USERS,
                        "total_purchased": FREE_TOKENS_FOR_NEW_USERS,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

            if result.modified_count > 0:
                print(f"  ✓ Granted {FREE_TOKENS_FOR_NEW_USERS} tokens to {user_email}")
                return True
            else:
                print(f"  ✗ Failed to update {user_email}")
                return False

        except Exception as e:
            print(f"  ✗ Error updating {user_email}: {e}")
            return False

    def run(self):
        """Execute the migration."""
        print("=" * 70)
        print("Migration: Grant Free Tokens to Existing Users")
        print("=" * 70)
        print(f"Database: {DB_NAME}")
        print(f"Free tokens amount: {FREE_TOKENS_FOR_NEW_USERS}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 70)
        print()

        # Find eligible users
        print("🔍 Finding eligible users...")
        eligible_users = self.find_eligible_users()

        if not eligible_users:
            print("✓ No eligible users found. All users already have tokens!")
            print()
            return

        print(f"📊 Found {len(eligible_users)} eligible user(s):\n")

        # Display user details
        for user in eligible_users:
            print(f"  • {user['user_email']}")
            print(f"    - Current balance: {user['token_balance']} tokens")
            print(f"    - Total purchased: {user['total_purchased']} tokens")
            print(f"    - Total consumed: {user['total_consumed']} tokens")
            print(f"    - Created: {user.get('created_at', 'N/A')}")
            print()

        # Confirm if not dry run
        if not self.dry_run:
            print("⚠️  This will grant free tokens to the above users.")
            confirm = input("Continue? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Migration cancelled.")
                return
            print()

        # Grant tokens to each user
        print("🚀 Granting free tokens...\n")
        success_count = 0
        fail_count = 0

        for user in eligible_users:
            if self.grant_free_tokens(user["user_email"]):
                success_count += 1
            else:
                fail_count += 1

        # Summary
        print()
        print("=" * 70)
        print("Migration Summary")
        print("=" * 70)
        print(f"Total users processed: {len(eligible_users)}")
        print(f"✓ Successful: {success_count}")
        print(f"✗ Failed: {fail_count}")
        print(f"Mode: {'DRY RUN (no changes made)' if self.dry_run else 'LIVE'}")
        print("=" * 70)

        if self.dry_run:
            print()
            print("💡 This was a dry run. No changes were made.")
            print(
                "   To apply changes, run: python migrations/grant_free_tokens_to_existing_users.py --live"
            )

    def verify(self):
        """Verify the migration results."""
        print("\n🔍 Verifying migration...\n")

        # Check for users with 0 tokens
        zero_balance_users = list(
            self.users_collection.find({"token_balance": 0, "total_purchased": 0})
        )

        if zero_balance_users:
            print(f"⚠️  Warning: {len(zero_balance_users)} user(s) still have 0 tokens:")
            for user in zero_balance_users:
                print(f"  • {user['user_email']}")
        else:
            print("✓ All eligible users now have free tokens!")

        # Count users with free tokens
        free_token_users = self.users_collection.count_documents(
            {
                "token_balance": FREE_TOKENS_FOR_NEW_USERS,
                "total_purchased": FREE_TOKENS_FOR_NEW_USERS,
                "total_consumed": 0,
            }
        )

        print(
            f"\n📊 Users with {FREE_TOKENS_FOR_NEW_USERS} free tokens (unused): {free_token_users}"
        )

    def close(self):
        """Close database connection."""
        self.client.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Grant free tokens to existing users with 0 balance"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute migration (default is dry-run mode)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify migration results after running",
    )

    args = parser.parse_args()

    # Create migration instance
    migration = TokenMigration(
        mongodb_uri=MONGODB_URI, db_name=DB_NAME, dry_run=not args.live
    )

    try:
        # Run migration
        migration.run()

        # Verify if requested
        if args.verify and args.live:
            migration.verify()

    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed with error: {e}")
        sys.exit(1)
    finally:
        migration.close()

    print()


if __name__ == "__main__":
    main()
