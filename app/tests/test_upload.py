"""
Test dataset upload endpoint with problem context.
Following TDD: Write failing tests first.
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import json
import mongomock
from app.main import app
from app.routers import upload


@pytest.fixture
def client():
    """FastAPI test client with mocked database."""
    # Mock the database
    mock_client = mongomock.MongoClient()
    upload._db_client = mock_client
    
    return TestClient(app)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    csv_content = """transaction_id,amount,merchant,timestamp,is_fraud
1,45.50,Amazon,2024-01-01 10:00:00,0
2,1200.00,Electronics Store,2024-01-01 11:00:00,1
3,23.99,Coffee Shop,2024-01-01 12:00:00,0
4,5000.00,Luxury Store,2024-01-01 13:00:00,1
5,15.00,Gas Station,2024-01-01 14:00:00,0"""
    return BytesIO(csv_content.encode())


@pytest.fixture
def sample_json_file():
    """Create a sample JSON file for testing."""
    json_content = [
        {"transaction_id": 1, "amount": 45.50, "merchant": "Amazon", "is_fraud": 0},
        {"transaction_id": 2, "amount": 1200.00, "merchant": "Electronics Store", "is_fraud": 1},
    ]
    return BytesIO(json.dumps(json_content).encode())


@pytest.fixture
def problem_description():
    """Sample problem description."""
    return "I'm working with transaction data from the last 2 years and need to detect fraudulent credit card transactions using purchase history and behavioral signals"


class TestUploadEndpoint:
    """Test the dataset upload endpoint with problem context."""
    
    def test_upload_csv_with_problem_context(self, client, sample_csv_file, problem_description):
        """Test uploading a CSV file with problem description."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("transactions.csv", sample_csv_file, "text/csv")},
            data={"problem_description": problem_description}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "dataset_id" in data
        assert data["filename"] == "transactions.csv"
        assert data["rows"] == 5
        assert data["columns"] == 5
        assert data["problem_description"] == problem_description
        assert "problem_type" in data
        assert "upload_time" in data
        assert data["message"] == "Dataset uploaded successfully"
    
    def test_upload_json_with_problem_context(self, client, sample_json_file, problem_description):
        """Test uploading a JSON file with problem description."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("transactions.json", sample_json_file, "application/json")},
            data={"problem_description": problem_description}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "transactions.json"
        assert data["rows"] == 2
    
    def test_upload_without_problem_description(self, client, sample_csv_file):
        """Test that upload fails without problem description."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", sample_csv_file, "text/csv")}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_upload_with_short_problem_description(self, client, sample_csv_file):
        """Test that short problem descriptions are rejected."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", sample_csv_file, "text/csv")},
            data={"problem_description": "short"}
        )
        
        assert response.status_code == 422
    
    def test_upload_with_optional_problem_type(self, client, sample_csv_file, problem_description):
        """Test upload with explicit problem type."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", sample_csv_file, "text/csv")},
            data={
                "problem_description": problem_description,
                "problem_type": "anomaly_detection"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["problem_type"] == "anomaly_detection"
    
    def test_upload_invalid_file_type(self, client, problem_description):
        """Test that invalid file types are rejected."""
        file_content = BytesIO(b"Not a valid CSV or JSON")
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", file_content, "text/plain")},
            data={"problem_description": problem_description}
        )
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    def test_upload_empty_file(self, client, problem_description):
        """Test that empty files are rejected."""
        empty_file = BytesIO(b"")
        response = client.post(
            "/api/v1/upload",
            files={"file": ("empty.csv", empty_file, "text/csv")},
            data={"problem_description": problem_description}
        )
        
        assert response.status_code == 400
    
    def test_dataset_metadata_stored_in_db(self, client, sample_csv_file, problem_description):
        """Test that dataset metadata is stored in MongoDB."""
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.csv", sample_csv_file, "text/csv")},
            data={"problem_description": problem_description}
        )
        
        assert response.status_code == 200
        dataset_id = response.json()["dataset_id"]
        
        # Verify we can retrieve it (will test this with a GET endpoint later)
        assert dataset_id is not None
        assert len(dataset_id) > 0
