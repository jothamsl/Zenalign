"""
Database connection service for MongoDB.
Follows single-agent architecture with episodic memory storage.
"""

import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


def init_db() -> MongoClient:
    """
    Initialize MongoDB connection.
    Returns MongoDB client instance.
    """
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/senalign")

    try:
        logger.info(f"Attempting to connect to MongoDB at {mongodb_uri}")
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        # Verify connection
        client.admin.command("ping")
        logger.info(f"Successfully connected to MongoDB at {mongodb_uri}")

        # Test database access
        db = client.get_database("senalign")
        logger.info(
            f"Database 'senalign' accessible, collections: {db.list_collection_names()}"
        )

        return client
    except ImportError as e:
        logger.error(f"pymongo not installed: {e}")
        logger.error("Please install pymongo with: pip install pymongo")
        raise
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB at {mongodb_uri}: {e}")
        logger.error("Check if MongoDB is running and MONGODB_URI is correct")
        logger.error("For local setup, try: docker run -d -p 27017:27017 mongo:latest")
        raise


def get_database(client: MongoClient, db_name: str = "senalign") -> Database:
    """
    Get database instance from client.

    Args:
        client: MongoDB client
        db_name: Database name (default: senalign)

    Returns:
        Database instance
    """
    try:
        db = client[db_name]
        logger.debug(f"Accessing database: {db_name}")
        return db
    except Exception as e:
        logger.error(f"Failed to access database '{db_name}': {e}")
        raise


def close_db(client: MongoClient) -> None:
    """
    Close MongoDB connection.

    Args:
        client: MongoDB client to close
    """
    try:
        if client:
            client.close()
            logger.info("MongoDB connection closed")
    except Exception as e:
        logger.warning(f"Error closing MongoDB connection: {e}")


def test_database_operations(client: MongoClient, db_name: str = "senalign") -> bool:
    """
    Test basic database operations (insert, find, delete).

    Args:
        client: MongoDB client
        db_name: Database name to test

    Returns:
        True if all operations succeed, False otherwise
    """
    try:
        db = get_database(client, db_name)
        test_collection = db["test_connection"]

        # Test insert
        test_doc = {"test": "data", "timestamp": logger.info.__name__}
        result = test_collection.insert_one(test_doc)
        logger.info(f"Test insert successful, ID: {result.inserted_id}")

        # Test find
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if not found_doc:
            raise Exception("Test document not found after insert")
        logger.info("Test find successful")

        # Test delete (cleanup)
        delete_result = test_collection.delete_one({"_id": result.inserted_id})
        if delete_result.deleted_count != 1:
            logger.warning("Test cleanup: document not deleted properly")
        else:
            logger.info("Test cleanup successful")

        logger.info("All database operations test passed")
        return True

    except Exception as e:
        logger.error(f"Database operations test failed: {e}")
        return False
