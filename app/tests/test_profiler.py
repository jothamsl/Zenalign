"""
Test dataset profiling service.
Following TDD: Write failing tests first.
Profiler is problem-context-aware (uses problem_type to prioritize issues).
"""
import pytest
import pandas as pd
import numpy as np
from app.services.profiler import DatasetProfiler


@pytest.fixture
def sample_df_with_issues():
    """Create a sample DataFrame with various quality issues."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'amount': [100, 200, np.nan, 400, 500, 600, 10000, 800, 900, np.nan],  # Missing + outlier
        'category': ['A', 'B', 'A', 'A', 'A', 'A', 'A', 'B', 'C', 'A'],  # Imbalanced
        'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                      '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
        'is_fraud': [0, 1, 0, 0, 0, 0, 0, 1, 1, 0]  # Target for classification
    })


@pytest.fixture
def clean_df():
    """Create a clean DataFrame with no issues."""
    return pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0, 1, 0, 1, 0]
    })


class TestDatasetProfiler:
    """Test the DatasetProfiler service."""
    
    def test_profiler_initialization(self, sample_df_with_issues):
        """Test that profiler initializes with DataFrame and problem type."""
        profiler = DatasetProfiler(
            df=sample_df_with_issues,
            problem_type="classification"
        )
        
        assert profiler.df is not None
        assert profiler.problem_type == "classification"
        assert profiler.n_rows == 10
        assert profiler.n_cols == 5
    
    def test_detect_missing_values(self, sample_df_with_issues):
        """Test detection of missing values."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        missing_info = profiler.detect_missing_values()
        
        assert 'amount' in missing_info
        assert missing_info['amount']['count'] == 2
        assert missing_info['amount']['percentage'] == 20.0
    
    def test_detect_outliers(self, sample_df_with_issues):
        """Test outlier detection using IQR method."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        outliers = profiler.detect_outliers()
        
        assert 'amount' in outliers
        assert 10000 in outliers['amount']['values']  # Outlier value
        assert outliers['amount']['count'] > 0
    
    def test_detect_class_imbalance(self, sample_df_with_issues):
        """Test class imbalance detection for classification problems."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        imbalance = profiler.detect_class_imbalance()
        
        assert 'category' in imbalance
        assert imbalance['category']['imbalance_ratio'] > 1.0  # More A's than others
        assert 'A' in imbalance['category']['distribution']
    
    def test_analyze_data_types(self, sample_df_with_issues):
        """Test data type analysis."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        dtypes_info = profiler.analyze_data_types()
        
        assert 'numeric' in dtypes_info
        assert 'categorical' in dtypes_info
        assert 'datetime' in dtypes_info or 'object' in dtypes_info
        assert len(dtypes_info['numeric']) >= 2  # amount, id, is_fraud
    
    def test_calculate_quality_scores(self, sample_df_with_issues):
        """Test overall quality score calculation."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        scores = profiler.calculate_quality_scores()
        
        assert 'completeness' in scores
        assert 'consistency' in scores
        assert 'validity' in scores
        assert 'overall' in scores
        
        assert 0 <= scores['completeness'] <= 1
        assert 0 <= scores['overall'] <= 1
    
    def test_generate_profile(self, sample_df_with_issues):
        """Test complete profile generation."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        profile = profiler.generate_profile()
        
        assert 'shape' in profile
        assert 'dtypes' in profile
        assert 'missing_values' in profile
        assert 'outliers' in profile
        assert 'class_imbalance' in profile
        assert 'quality_scores' in profile
        
        assert profile['shape']['rows'] == 10
        assert profile['shape']['columns'] == 5
    
    def test_problem_context_awareness_classification(self, sample_df_with_issues):
        """Test that profiler prioritizes class imbalance for classification."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        profile = profiler.generate_profile()
        
        # Class imbalance should be detected
        assert len(profile['class_imbalance']) > 0
    
    def test_problem_context_awareness_regression(self, sample_df_with_issues):
        """Test that profiler handles regression differently."""
        profiler = DatasetProfiler(sample_df_with_issues, "regression")
        profile = profiler.generate_profile()
        
        # For regression, class imbalance is less critical
        # But outliers are very important
        assert 'outliers' in profile
    
    def test_clean_dataset_high_scores(self, clean_df):
        """Test that clean dataset gets high quality scores."""
        profiler = DatasetProfiler(clean_df, "classification")
        scores = profiler.calculate_quality_scores()
        
        assert scores['completeness'] >= 0.95
        assert scores['overall'] >= 0.85
    
    def test_issue_summary(self, sample_df_with_issues):
        """Test generation of issue summary with severity levels."""
        profiler = DatasetProfiler(sample_df_with_issues, "classification")
        issues = profiler.get_issue_summary()
        
        assert isinstance(issues, list)
        assert len(issues) > 0
        
        # Check first issue has required fields
        first_issue = issues[0]
        assert 'type' in first_issue
        assert 'severity' in first_issue  # critical, high, medium, low
        assert 'column' in first_issue or first_issue['type'] == 'overall'
        assert 'description' in first_issue
