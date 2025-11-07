import pytest
import pandas as pd
from app.services.profiler import profile_column, profile_dataset, calculate_quality_score
from app.models.schemas import ColumnProfile


@pytest.fixture
def sample_df():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "age": [25, 30, 35, None, 40],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "email": ["alice@example.com", "bob@test.org", None, "david@mail.com", "eve@example.com"],
        "score": [85.5, 90.0, 78.5, 88.0, 92.5],
    })


def test_profile_numeric_column(sample_df):
    profile = profile_column(sample_df, "age")
    
    assert profile.name == "age"
    assert profile.missing_count == 1
    assert profile.missing_percent == 20.0
    assert profile.numeric_stats is not None
    assert profile.numeric_stats["mean"] == pytest.approx(32.5, 0.1)


def test_profile_categorical_column(sample_df):
    profile = profile_column(sample_df, "name")
    
    assert profile.name == "name"
    assert profile.dtype == "object"
    assert profile.unique_count == 5
    assert profile.top_categories is not None
    assert len(profile.top_categories) == 5


def test_profile_pii_column(sample_df):
    profile = profile_column(sample_df, "email")
    
    assert profile.name == "email"
    assert profile.pii_detected is True
    assert "email" in profile.pii_types


def test_calculate_quality_score(sample_df):
    profiles = [profile_column(sample_df, col) for col in sample_df.columns]
    score = calculate_quality_score(sample_df, profiles)
    
    assert 0 <= score <= 100
    assert isinstance(score, float)


def test_profile_dataset(sample_df):
    profile = profile_dataset(sample_df, "test_ds_123")
    
    assert profile.dataset_id == "test_ds_123"
    assert profile.total_rows == 5
    assert profile.total_columns == 4
    assert len(profile.columns) == 4
    assert profile.pii_summary["pii_detected"] is True
    assert "email" in profile.pii_summary["pii_columns"]
    assert 0 <= profile.quality_score <= 100


def test_empty_dataframe():
    df = pd.DataFrame()
    profiles = []
    score = calculate_quality_score(df, profiles)
    assert score == 0.0
