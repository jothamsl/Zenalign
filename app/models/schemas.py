"""
Pydantic schemas for request/response models.
Following single-agent architecture with problem-context-driven analysis.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class ProblemType(str, Enum):
    """Common ML problem types for context."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    OTHER = "other"


class UploadRequest(BaseModel):
    """Request model for dataset upload with problem context."""
    problem_description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Description of the ML problem (e.g., 'Detect fraudulent credit card transactions')",
        examples=["I'm working with transaction data from the last 2 years and need to detect fraudulent credit card transactions using purchase history and behavioral signals"]
    )
    problem_type: Optional[ProblemType] = Field(
        default=ProblemType.OTHER,
        description="Type of ML problem (auto-detected if not provided)"
    )
    dataset_description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional additional context about the dataset"
    )


class UploadResponse(BaseModel):
    """Response model for successful upload."""
    dataset_id: str = Field(..., description="Unique identifier for the uploaded dataset")
    filename: str = Field(..., description="Original filename")
    rows: int = Field(..., description="Number of rows in the dataset")
    columns: int = Field(..., description="Number of columns in the dataset")
    problem_description: str = Field(..., description="Problem context provided")
    problem_type: str = Field(..., description="Detected or provided problem type")
    upload_time: datetime = Field(..., description="Timestamp of upload")
    message: str = Field(default="Dataset uploaded successfully")


class AnalysisRequest(BaseModel):
    """Request model for dataset analysis."""
    ml_problem: Optional[str] = Field(
        default=None,
        description="Override problem description (uses upload context if not provided)"
    )


class Issue(BaseModel):
    """Data quality issue identified during analysis."""
    issue: str = Field(..., description="Name of the issue")
    severity: str = Field(..., description="Severity: critical, high, medium, low")
    why_matters: str = Field(..., description="Why this matters for the ML problem")
    fix_suggestion: str = Field(..., description="How to fix it")
    code_snippet: str = Field(..., description="Python code to apply the fix")


class Resource(BaseModel):
    """External resource (paper, blog, Kaggle notebook)."""
    title: str = Field(..., description="Resource title")
    url: str = Field(..., description="Resource URL")
    summary: str = Field(..., description="Brief summary")
    type: str = Field(..., description="Type: paper, blog, kaggle, documentation")


class Report(BaseModel):
    """Complete analysis report."""
    dataset_id: str
    problem_description: str = Field(..., description="Problem context guiding the analysis")
    problem_type: str
    quality_scores: Dict[str, float] = Field(
        ...,
        description="Quality metrics: completeness, consistency, validity, etc."
    )
    issues: List[Issue] = Field(default_factory=list)
    recommendations: List[Dict] = Field(
        default_factory=list,
        description="AI-generated recommendations from LLM"
    )
    domain_resources: List[Resource] = Field(
        default_factory=list,
        description="Relevant resources from Exa search"
    )
    created_at: datetime


class TransformRequest(BaseModel):
    """Request model for applying transformations."""
    fixes: List[str] = Field(
        ...,
        description="List of transformation codes to apply",
        examples=[["impute_mean", "remove_outliers", "balance_classes"]]
    )
    
    @field_validator('fixes')
    @classmethod
    def validate_fixes(cls, v):
        """Ensure fixes list is not empty."""
        if not v:
            raise ValueError("At least one fix must be specified")
        return v
