import pandas as pd
import numpy as np
from typing import Dict, List, Any
from app.models.schemas import ColumnProfile, DatasetProfile
from app.utils.pii_detector import PIIDetector


def profile_column(df: pd.DataFrame, col_name: str) -> ColumnProfile:
    """Profile a single column."""
    series = df[col_name]
    
    # Basic stats
    missing_count = int(series.isna().sum())
    missing_percent = float(missing_count / len(series) * 100)
    unique_count = int(series.nunique())
    dtype = str(series.dtype)
    
    # Top categories for categorical/object columns
    top_categories = None
    if dtype == 'object' or unique_count < 50:
        value_counts = series.value_counts().head(10)
        top_categories = [
            {"value": str(val), "count": int(count)}
            for val, count in value_counts.items()
        ]
    
    # Numeric stats
    numeric_stats = None
    if pd.api.types.is_numeric_dtype(series):
        numeric_stats = {
            "mean": float(series.mean()) if not series.isna().all() else None,
            "std": float(series.std()) if not series.isna().all() else None,
            "min": float(series.min()) if not series.isna().all() else None,
            "max": float(series.max()) if not series.isna().all() else None,
            "median": float(series.median()) if not series.isna().all() else None,
        }
    
    # PII detection
    sample_values = series.dropna().astype(str).head(100).tolist()
    has_pii, pii_types = PIIDetector.detect(col_name, sample_values)
    
    return ColumnProfile(
        name=col_name,
        dtype=dtype,
        missing_count=missing_count,
        missing_percent=missing_percent,
        unique_count=unique_count,
        top_categories=top_categories,
        numeric_stats=numeric_stats,
        pii_detected=has_pii,
        pii_types=pii_types,
    )


def calculate_quality_score(df: pd.DataFrame, column_profiles: List[ColumnProfile]) -> float:
    """
    Calculate simple quality score (0-100) based on:
    - Completeness (missing data)
    - Uniqueness
    - PII presence (slight penalty)
    """
    if len(df) == 0:
        return 0.0
    
    # Completeness score (0-50 points)
    total_cells = len(df) * len(df.columns)
    missing_cells = df.isna().sum().sum()
    completeness = (1 - missing_cells / total_cells) * 50
    
    # Uniqueness score (0-30 points)
    avg_unique_ratio = np.mean([
        prof.unique_count / len(df) for prof in column_profiles
    ])
    uniqueness = min(avg_unique_ratio * 30, 30)
    
    # PII penalty (0-20 points, full points if no PII)
    pii_columns = sum(1 for prof in column_profiles if prof.pii_detected)
    pii_score = max(20 - (pii_columns * 2), 0)
    
    return round(completeness + uniqueness + pii_score, 2)


def profile_dataset(df: pd.DataFrame, dataset_id: str) -> DatasetProfile:
    """Generate complete dataset profile."""
    column_profiles = [profile_column(df, col) for col in df.columns]
    
    quality_score = calculate_quality_score(df, column_profiles)
    
    pii_columns = [prof.name for prof in column_profiles if prof.pii_detected]
    pii_summary = {
        "pii_detected": len(pii_columns) > 0,
        "pii_columns": pii_columns,
        "pii_column_count": len(pii_columns),
    }
    
    return DatasetProfile(
        dataset_id=dataset_id,
        total_rows=len(df),
        total_columns=len(df.columns),
        quality_score=quality_score,
        columns=column_profiles,
        pii_summary=pii_summary,
    )
