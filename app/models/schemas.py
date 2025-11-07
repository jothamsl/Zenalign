from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    size_bytes: int
    uploaded_at: str


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_percent: float
    unique_count: int
    top_categories: Optional[List[Dict[str, Any]]] = None
    numeric_stats: Optional[Dict[str, float]] = None
    pii_detected: bool = False
    pii_types: List[str] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    dataset_id: str
    total_rows: int
    total_columns: int
    quality_score: float
    columns: List[ColumnProfile]
    pii_summary: Dict[str, Any]


class AnalysisRequest(BaseModel):
    dataset_id: str
    problem_description: str = Field(
        ..., 
        description="Natural language description of the ML problem you're trying to solve"
    )
    target_column: Optional[str] = None
    protected_columns: List[str] = Field(default_factory=list)


class LLMAnalysisReport(BaseModel):
    job_id: str
    dataset_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    profile: Optional[DatasetProfile] = None
    llm_recommendations: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AnalysisStartResponse(BaseModel):
    job_id: str
    status: str
    message: str
