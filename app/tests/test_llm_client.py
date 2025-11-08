"""
Test LLM recommendations service.
Following TDD: Write failing tests first.
Context-aware AI recommendations (Ch. 5: orchestration with problem context).
Privacy-first: Only aggregated data sent to OpenAI (Ch. 12).
"""
import pytest
from unittest.mock import Mock, patch
from app.services.llm_client import LLMClient


@pytest.fixture
def sample_profile():
    """Sample profiling results."""
    return {
        'shape': {'rows': 100, 'columns': 5},
        'quality_scores': {
            'completeness': 0.80,
            'consistency': 0.90,
            'validity': 0.85,
            'overall': 0.85
        },
        'missing_values': {
            'amount': {'count': 20, 'percentage': 20.0}
        },
        'class_imbalance': {
            'is_fraud': {
                'imbalance_ratio': 30.0,
                'minority_percentage': 3.0
            }
        }
    }


@pytest.fixture
def sample_pii_report():
    """Sample PII detection results."""
    return {
        'summary': {
            'columns_with_pii': 2,
            'total_pii_values': 15
        },
        'emails': {'email': {'count': 10}},
        'ssn': {'ssn_col': {'count': 5}}
    }


@pytest.fixture
def problem_context():
    """Sample problem context."""
    return {
        'description': 'Detect fraudulent credit card transactions using purchase history',
        'type': 'anomaly_detection'
    }


class TestLLMClient:
    """Test the LLM recommendations service."""
    
    def test_client_initialization(self):
        """Test that client initializes with API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('app.services.llm_client.OpenAI'):
                client = LLMClient()
                assert client.api_key == 'test-key'
                assert client.model == 'gpt-4o'
    
    def test_build_prompt_includes_problem_context(self, problem_context, sample_profile):
        """Test that prompt includes problem description."""
        with patch('app.services.llm_client.OpenAI'):
            client = LLMClient(api_key='test')
            prompt = client._build_prompt(problem_context, sample_profile, {})
            
            assert 'fraudulent credit card transactions' in prompt.lower()
            assert 'anomaly_detection' in prompt.lower()
    
    def test_build_prompt_includes_quality_metrics(self, problem_context, sample_profile):
        """Test that prompt includes quality scores."""
        with patch('app.services.llm_client.OpenAI'):
            client = LLMClient(api_key='test')
            prompt = client._build_prompt(problem_context, sample_profile, {})
            
            assert '0.80' in prompt or '80%' in prompt  # Completeness
            assert 'missing' in prompt.lower()
    
    def test_build_prompt_includes_pii_warning(self, problem_context, sample_profile, sample_pii_report):
        """Test that prompt warns about PII when present."""
        with patch('app.services.llm_client.OpenAI'):
            client = LLMClient(api_key='test')
            prompt = client._build_prompt(problem_context, sample_profile, sample_pii_report)
            
            assert 'pii' in prompt.lower() or 'sensitive' in prompt.lower()
            assert '2' in prompt  # Number of PII columns
    
    def test_build_prompt_no_raw_data(self, problem_context, sample_profile):
        """Test that NO raw data values are in prompt (privacy check)."""
        with patch('app.services.llm_client.OpenAI'):
            client = LLMClient(api_key='test')
            prompt = client._build_prompt(problem_context, sample_profile, {})
            
            # Should only have aggregated stats, no raw values
            assert 'row 1' not in prompt.lower()
            assert 'john@email.com' not in prompt.lower()
            # Should have aggregated info
            assert 'percentage' in prompt.lower() or '%' in prompt
    
    @patch('app.services.llm_client.OpenAI')
    def test_generate_recommendations_calls_openai(self, mock_openai_class, problem_context, sample_profile):
        """Test that generate_recommendations calls OpenAI API."""
        # Mock the API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"recommendations": []}'))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = LLMClient(api_key='test')
        result = client.generate_recommendations(problem_context, sample_profile, {})
        
        # Verify API was called
        assert mock_client.chat.completions.create.called
    
    @patch('app.services.llm_client.OpenAI')
    def test_generate_recommendations_returns_structured_data(self, mock_openai_class, problem_context, sample_profile):
        """Test that recommendations are returned in structured format."""
        # Mock structured response
        mock_client = Mock()
        mock_response = Mock()
        recommendations_json = '''
        {
            "recommendations": [
                {
                    "category": "data_quality",
                    "issue": "missing_values",
                    "severity": "high",
                    "suggestion": "Impute missing values in amount column",
                    "code_example": "df['amount'].fillna(df['amount'].median(), inplace=True)"
                }
            ],
            "priority_actions": ["Handle class imbalance", "Impute missing values"],
            "overall_assessment": "Dataset needs significant preparation"
        }
        '''
        mock_response.choices = [Mock(message=Mock(content=recommendations_json))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = LLMClient(api_key='test')
        result = client.generate_recommendations(problem_context, sample_profile, {})
        
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)
        assert len(result['recommendations']) > 0
        assert 'category' in result['recommendations'][0]
        assert 'suggestion' in result['recommendations'][0]
    
    @patch('app.services.llm_client.OpenAI')
    def test_generate_recommendations_problem_aware(self, mock_openai_class, problem_context, sample_profile):
        """Test that recommendations are tailored to problem type."""
        # Mock response specific to anomaly detection
        mock_client = Mock()
        mock_response = Mock()
        recommendations_json = '''
        {
            "recommendations": [
                {
                    "category": "class_imbalance",
                    "issue": "severe_imbalance",
                    "severity": "critical",
                    "suggestion": "For anomaly detection, use SMOTE to oversample minority class",
                    "code_example": "from imblearn.over_sampling import SMOTE"
                }
            ]
        }
        '''
        mock_response.choices = [Mock(message=Mock(content=recommendations_json))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = LLMClient(api_key='test')
        result = client.generate_recommendations(problem_context, sample_profile, {})
        
        # Check that response mentions anomaly detection context
        first_rec = result['recommendations'][0]
        assert 'anomaly' in first_rec['suggestion'].lower() or 'imbalance' in first_rec['suggestion'].lower()
    
    def test_error_handling_invalid_api_key(self):
        """Test handling of invalid API key."""
        # Don't even try to create LLMClient - just test the validation logic
        with pytest.raises(ValueError, match='API key'):
            # This will fail before OpenAI client is created
            with patch('app.services.llm_client.OpenAI'):
                LLMClient(api_key=None)
    
    @patch('app.services.llm_client.OpenAI')
    def test_error_handling_api_failure(self, mock_openai_class, problem_context, sample_profile):
        """Test graceful handling of API failures."""
        # Mock API error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        client = LLMClient(api_key='test')
        result = client.generate_recommendations(problem_context, sample_profile, {})
        
        # Should return error structure instead of crashing
        assert 'error' in result or 'recommendations' in result
