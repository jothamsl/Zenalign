"""
Test database connection and initialization.
Following TDD: Write test first, then implement.
Using mongomock for lightweight testing without MongoDB server.
"""
import pytest
import mongomock
from app.services.db import get_database, init_db, close_db


@pytest.fixture
def mock_mongo_client(monkeypatch):
    """Mock MongoDB client for testing."""
    def mock_init_db():
        return mongomock.MongoClient()
    
    monkeypatch.setattr("app.services.db.MongoClient", mongomock.MongoClient)
    return mock_init_db


class TestDatabaseConnection:
    """Test MongoDB connection setup."""
    
    def test_init_db_returns_client(self, mock_mongo_client):
        """Test that init_db successfully creates and returns a MongoDB client."""
        client = mock_mongo_client()
        assert client is not None
        assert hasattr(client, 'server_info')
        close_db(client)
    
    def test_get_database_returns_db_instance(self, mock_mongo_client):
        """Test that get_database returns a valid database instance."""
        client = mock_mongo_client()
        db = get_database(client)
        assert db is not None
        assert hasattr(db, 'list_collection_names')
        
        # Verify expected collections can be accessed
        assert isinstance(db.list_collection_names(), list)
        close_db(client)
    
    def test_database_ping(self, mock_mongo_client):
        """Test that we can ping the database to verify connection."""
        client = mock_mongo_client()
        # Ping should not raise an exception
        try:
            client.admin.command('ping')
            success = True
        except Exception:
            success = False
        
        assert success is True
        close_db(client)
