"""
Upload router for dataset ingestion with problem context.
Modular tool following Ch. 4 principles (clear interfaces).
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from datetime import datetime, UTC
from bson import ObjectId
import pandas as pd
import json
import os
from typing import Optional
import logging

from app.models.schemas import UploadRequest, UploadResponse, ProblemType
from app.services.db import get_database, init_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["upload"])

# Global MongoDB client (will be initialized in main.py lifespan)
_db_client = None


def get_db():
    """Dependency to get database instance."""
    global _db_client
    if _db_client is None:
        _db_client = init_db()
    return get_database(_db_client)


async def validate_and_read_file(file: UploadFile) -> tuple[pd.DataFrame, int, int]:
    """
    Validate and read uploaded file into a DataFrame.

    Args:
        file: Uploaded file

    Returns:
        Tuple of (dataframe, rows, columns)

    Raises:
        HTTPException: If file is invalid
    """
    # Validate file type
    allowed_extensions = [".csv", ".json"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
        )

    # Read file content
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Parse based on file type
    try:
        if file_ext == ".csv":
            df = pd.read_csv(pd.io.common.BytesIO(content))
        else:  # .json
            data = json.loads(content.decode("utf-8"))
            df = pd.DataFrame(data)

        if df.empty:
            raise HTTPException(status_code=400, detail="Dataset is empty")

        rows, columns = df.shape
        return df, rows, columns

    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")


def save_dataset_to_temp(
    df: pd.DataFrame, dataset_id: str, original_filename: str
) -> str:
    """
    Save dataset to temp directory for later processing.

    Args:
        df: DataFrame to save
        dataset_id: Unique dataset ID
        original_filename: Original filename

    Returns:
        Path to saved file
    """
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Save as CSV for consistency
    file_ext = os.path.splitext(original_filename)[1]
    filename = f"{dataset_id}{file_ext}"
    filepath = os.path.join(temp_dir, filename)

    df.to_csv(filepath, index=False)
    logger.info(f"Dataset saved to {filepath}")

    return filepath


def detect_problem_type(problem_description: str) -> str:
    """
    Auto-detect problem type from description.
    Simple keyword-based detection (can be enhanced with LLM later).

    Args:
        problem_description: User's problem description

    Returns:
        Detected problem type
    """
    description_lower = problem_description.lower()

    # Keyword mapping
    keywords = {
        ProblemType.ANOMALY_DETECTION: [
            "fraud",
            "anomaly",
            "outlier",
            "detect",
            "unusual",
        ],
        ProblemType.CLASSIFICATION: [
            "classify",
            "classification",
            "predict",
            "category",
            "label",
        ],
        ProblemType.REGRESSION: [
            "predict",
            "regression",
            "forecast",
            "estimate",
            "price",
        ],
        ProblemType.TIME_SERIES: ["time series", "temporal", "forecast", "trend"],
        ProblemType.CLUSTERING: ["cluster", "segment", "group", "similar"],
        ProblemType.NLP: ["text", "sentiment", "language", "nlp", "document"],
    }

    # Count keyword matches
    scores = {}
    for problem_type, kw_list in keywords.items():
        score = sum(1 for kw in kw_list if kw in description_lower)
        if score > 0:
            scores[problem_type] = score

    # Return best match or OTHER
    if scores:
        return max(scores, key=scores.get).value
    return ProblemType.OTHER.value


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    problem_description: str = Form(..., min_length=10, max_length=1000),
    problem_type: Optional[str] = Form(default=None),
    dataset_description: Optional[str] = Form(default=None, max_length=500),
    db=Depends(get_db),
):
    """
    Upload a dataset with problem context.

    This endpoint accepts CSV or JSON files along with a description of the ML problem.
    The problem description guides all downstream analysis (profiling, LLM recommendations, etc.).

    Example problem description:
    "I'm working with transaction data from the last 2 years and need to detect
    fraudulent credit card transactions using purchase history and behavioral signals"

    Args:
        file: CSV or JSON file
        problem_description: Description of the ML problem (min 10 chars)
        problem_type: Optional explicit problem type (auto-detected if not provided)
        dataset_description: Optional additional context about the dataset

    Returns:
        UploadResponse with dataset_id and metadata
    """
    logger.info(f"Uploading dataset: {file.filename}")

    # Validate and read file
    df, rows, columns = await validate_and_read_file(file)

    # Auto-detect problem type if not provided
    if problem_type is None:
        problem_type = detect_problem_type(problem_description)
    else:
        # Validate provided problem type
        try:
            problem_type = ProblemType(problem_type).value
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid problem_type. Must be one of: {[pt.value for pt in ProblemType]}",
            )

    # Generate unique dataset ID
    upload_time = datetime.now(UTC).replace(tzinfo=None)  # Store as naive UTC

    # Save to MongoDB
    dataset_doc = {
        "filename": file.filename,
        "upload_time": upload_time,
        "shape": {"rows": rows, "columns": columns},
        "problem_description": problem_description,
        "problem_type": problem_type,
        "dataset_description": dataset_description,
        "column_names": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }

    result = db["datasets"].insert_one(dataset_doc)
    dataset_id = str(result.inserted_id)

    # Save dataset to temp directory
    filepath = save_dataset_to_temp(df, dataset_id, file.filename)

    # Update document with file path
    db["datasets"].update_one(
        {"_id": result.inserted_id}, {"$set": {"file_path": filepath}}
    )

    logger.info(f"Dataset uploaded successfully: {dataset_id}")

    return UploadResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        rows=rows,
        columns=columns,
        problem_description=problem_description,
        problem_type=problem_type,
        upload_time=upload_time,
        message="Dataset uploaded successfully",
    )


@router.get("/datasets", response_model=list)
async def list_datasets(db=Depends(get_db)):
    """
    List all uploaded datasets with metadata.

    Returns:
        List of dataset metadata (without file content)
    """
    try:
        datasets = list(
            db["datasets"]
            .find(
                {},
                {
                    "_id": 1,
                    "filename": 1,
                    "upload_time": 1,
                    "shape": 1,
                    "problem_description": 1,
                    "problem_type": 1,
                    "dataset_description": 1,
                    "column_names": 1,
                },
            )
            .sort("upload_time", -1)
        )

        # Convert ObjectId to string for JSON serialization
        for dataset in datasets:
            dataset["dataset_id"] = str(dataset["_id"])
            del dataset["_id"]

        return datasets

    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list datasets: {str(e)}"
        )


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, db=Depends(get_db)):
    """
    Get detailed information about a specific dataset.

    Args:
        dataset_id: ID of the dataset

    Returns:
        Dataset metadata and information
    """
    try:
        # Try to find by ObjectId first, then by string
        try:
            dataset = db["datasets"].find_one({"_id": ObjectId(dataset_id)})
        except:
            dataset = db["datasets"].find_one({"_id": dataset_id})

        if not dataset:
            raise HTTPException(
                status_code=404, detail=f"Dataset not found: {dataset_id}"
            )

        # Convert ObjectId to string
        dataset["dataset_id"] = str(dataset["_id"])
        del dataset["_id"]

        return dataset

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve dataset: {str(e)}"
        )


@router.get("/reports")
async def list_reports(db=Depends(get_db)):
    """
    List all analysis reports.

    Returns:
        List of analysis reports with metadata
    """
    try:
        reports = list(
            db["reports"]
            .find(
                {},
                {
                    "_id": 1,
                    "dataset_id": 1,
                    "problem_type": 1,
                    "problem_description": 1,
                    "quality_scores": 1,
                    "created_at": 1,
                    "overall_assessment": 1,
                },
            )
            .sort("created_at", -1)
        )

        # Convert ObjectId to string
        for report in reports:
            report["report_id"] = str(report["_id"])
            del report["_id"]

        return reports

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.get("/reports/{report_id}")
async def get_report(report_id: str, db=Depends(get_db)):
    """
    Get detailed analysis report.

    Args:
        report_id: ID of the analysis report

    Returns:
        Complete analysis report
    """
    try:
        # Try to find by ObjectId first, then by string
        try:
            report = db["reports"].find_one({"_id": ObjectId(report_id)})
        except:
            report = db["reports"].find_one({"_id": report_id})

        if not report:
            raise HTTPException(
                status_code=404, detail=f"Report not found: {report_id}"
            )

        # Convert ObjectId to string
        report["report_id"] = str(report["_id"])
        del report["_id"]

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve report: {str(e)}"
        )
