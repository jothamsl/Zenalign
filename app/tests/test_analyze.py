"""
Test analysis orchestration endpoint.
Following TDD: Write failing tests first.
Sequential chain orchestration (Ch. 5): Profile → PII → LLM → Report.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import mongomock
import pandas as pd
import os
from io import BytesIO

from app.main import app
from app.routers import upload, analyze


@pytest.fixture
def client():
    """FastAPI test client with mocked database."""
    mock_client = mongomock.MongoClient()
    upload._db_client = mock_client
    analyze._db_client = mock_client
    
    return TestClient(app)


@pytest.fixture
def sample_dataset_id(client):
    """Upload a sample dataset and return its ID."""
    # Create test CSV
    csv_content = b"""transaction_id,amount,is_fraud
1,100,0
2,200,1
3,300,0
4,400,1
5,500,0"""
    
    file = BytesIO(csv_content)
    
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.csv", file, "text/csv")},
        data={
            "problem_description": "Detect fraudulent transactions using behavioral patterns"
        }
    )
    
    assert response.status_code == 200
    return response.json()["dataset_id"]


class TestAnalyzeEndpoint:
    """Test the analysis orchestration endpoint."""
    
    def test_analyze_endpoint_exists(self, client, sample_dataset_id):
        """Test that analyze endpoint is registered."""
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        # Should not be 404
        assert response.status_code != 404
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_returns_complete_report(self, mock_llm_class, client, sample_dataset_id):
        """Test that analyze returns a complete report."""
        # Mock LLM response
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {
            'recommendations': [
                {
                    'category': 'data_quality',
                    'issue': 'class_imbalance',
                    'severity': 'high',
                    'suggestion': 'Handle class imbalance',
                    'code_example': 'use SMOTE'
                }
            ],
            'priority_actions': ['Handle imbalance'],
            'overall_assessment': 'Dataset needs work'
        }
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Check report structure
        assert 'dataset_id' in report
        assert 'problem_type' in report
        assert 'quality_scores' in report
        assert 'pii_report' in report
        assert 'recommendations' in report
        assert 'created_at' in report
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_includes_profiling_results(self, mock_llm_class, client, sample_dataset_id):
        """Test that report includes profiling results."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {'recommendations': []}
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Should have quality scores from profiler
        assert 'quality_scores' in report
        assert 'completeness' in report['quality_scores']
        assert 'overall' in report['quality_scores']
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_includes_pii_detection(self, mock_llm_class, client, sample_dataset_id):
        """Test that report includes PII detection results."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {'recommendations': []}
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Should have PII report
        assert 'pii_report' in report
        assert 'summary' in report['pii_report']
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_includes_llm_recommendations(self, mock_llm_class, client, sample_dataset_id):
        """Test that report includes LLM recommendations."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {
            'recommendations': [
                {'category': 'data_quality', 'suggestion': 'Fix missing values'}
            ],
            'priority_actions': ['Action 1'],
            'overall_assessment': 'Good'
        }
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Should have LLM recommendations
        assert 'recommendations' in report
        assert len(report['recommendations']) > 0
        assert 'priority_actions' in report
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_stores_report_in_db(self, mock_llm_class, client, sample_dataset_id):
        """Test that report is stored in MongoDB."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {
            'recommendations': [],
            'priority_actions': [],
            'overall_assessment': 'OK'
        }
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Should have report_id
        assert 'report_id' in report or '_id' in report
    
    def test_analyze_invalid_dataset_id(self, client):
        """Test error handling for invalid dataset ID."""
        response = client.post("/api/v1/analyze/invalid_id_12345")
        
        assert response.status_code == 404
        assert 'detail' in response.json()
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_uses_problem_context(self, mock_llm_class, client, sample_dataset_id):
        """Test that analysis uses problem context from upload."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {'recommendations': []}
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        report = response.json()
        
        # Should include problem context
        assert 'problem_type' in report
        assert 'problem_description' in report
        assert 'fraud' in report['problem_description'].lower()
    
    @patch('app.routers.analyze.LLMClient')
    def test_analyze_sequential_orchestration(self, mock_llm_class, client, sample_dataset_id):
        """Test that services are called in correct order."""
        mock_llm = Mock()
        mock_llm.generate_recommendations.return_value = {'recommendations': []}
        mock_llm_class.return_value = mock_llm
        
        response = client.post(f"/api/v1/analyze/{sample_dataset_id}")
        
        assert response.status_code == 200
        
        # LLM should have been called with profile and PII data
        assert mock_llm.generate_recommendations.called
        call_args = mock_llm.generate_recommendations.call_args
        
        # Check that problem_context, profile, and pii_report were passed
        assert len(call_args[0]) >= 2  # At least problem_context and profile
