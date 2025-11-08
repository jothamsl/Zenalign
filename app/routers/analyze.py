"""
Analysis orchestration router.
Sequential chain (Ch. 5): Profile → PII → LLM → Report.
Ties all services together for complete dataset analysis.
Integrated with token-based payment system.
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict, Optional

import pandas as pd
from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from app.models.payment_schemas import ServiceType, TokenConsumptionRequest
from app.services.db import get_database, init_db
from app.services.exa_client import ExaClient
from app.services.llm_client import LLMClient
from app.services.pii_detector import PIIDetector
from app.services.profiler import DatasetProfiler
from app.services.token_service import TokenService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analyze"])

# Global MongoDB client and token service
_db_client = None
_token_service: Optional[TokenService] = None


def get_db():
    """Dependency to get database instance."""
    global _db_client
    if _db_client is None:
        _db_client = init_db()
    return get_database(_db_client)


@router.post("/analyze/{dataset_id}")
async def analyze_dataset(
    dataset_id: str,
    user_email: Optional[str] = Header(
        None, description="User email for token validation"
    ),
    db=Depends(get_db),
):
    """
    Run complete analysis pipeline on uploaded dataset.

    **Requires tokens**: Consumes 10 tokens per analysis.

    Orchestration sequence (Ch. 5 sequential chain):
    0. Check user token balance and consume tokens
    1. Load dataset + metadata from MongoDB
    2. Profile dataset (quality scores, issues)
    3. Detect PII (privacy scan)
    4. Generate LLM recommendations (context-aware)
    5. Search for domain resources (Exa)
    6. Create complete report
    7. Store report in MongoDB

    Args:
        dataset_id: ID of uploaded dataset
        user_email: User email address (from header for token validation)

    Returns:
        Complete analysis report

    Raises:
        HTTPException 402: Insufficient token balance
        HTTPException 404: Dataset not found
        HTTPException 500: Analysis failed
    """
    logger.info(f"Starting analysis for dataset: {dataset_id} (user: {user_email})")

    try:
        # Step 0: Check and consume tokens
        if _token_service and user_email:
            logger.info(f"Checking token balance for {user_email}")

            # Get token cost for analysis
            analysis_cost = _token_service.get_service_cost(ServiceType.ANALYSIS)

            # Check if user has sufficient balance
            if not _token_service.has_sufficient_balance(user_email, analysis_cost):
                user_balance = _token_service.get_or_create_user_balance(user_email)
                raise HTTPException(
                    status_code=402,
                    detail={
                        "error": "Insufficient token balance",
                        "required_tokens": analysis_cost,
                        "current_balance": user_balance.token_balance,
                        "message": f"You need {analysis_cost} tokens to run analysis but only have {user_balance.token_balance}. Please purchase more tokens.",
                    },
                )

            # Consume tokens
            try:
                consumption_request = TokenConsumptionRequest(
                    user_email=user_email,
                    tokens_to_consume=analysis_cost,
                    service_type=ServiceType.ANALYSIS,
                    dataset_id=dataset_id,
                    description="Dataset analysis with profiling, PII detection, and AI recommendations",
                )
                consumption_response = _token_service.consume_tokens(
                    consumption_request
                )
                logger.info(
                    f"Consumed {analysis_cost} tokens from {user_email}. "
                    f"Remaining balance: {consumption_response.remaining_balance}"
                )
            except Exception as e:
                logger.error(f"Failed to consume tokens: {e}")
                raise HTTPException(
                    status_code=400, detail=f"Failed to process token payment: {str(e)}"
                )
        elif not user_email:
            logger.warning(
                "No user_email provided - running analysis without token check (for testing/backward compatibility)"
            )
        else:
            logger.warning(
                "Token service not initialized - running analysis without token check"
            )

        # Step 1: Load dataset metadata
        try:
            dataset_doc = db["datasets"].find_one({"_id": ObjectId(dataset_id)})
        except:
            # If ObjectId conversion fails, try as string
            dataset_doc = db["datasets"].find_one({"_id": dataset_id})

        if not dataset_doc:
            raise HTTPException(
                status_code=404, detail=f"Dataset not found: {dataset_id}"
            )

        # Extract problem context
        problem_context = {
            "description": dataset_doc.get("problem_description", ""),
            "type": dataset_doc.get("problem_type", "unknown"),
        }

        # Load dataset file
        file_path = dataset_doc.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404, detail="Dataset file not found on disk"
            )

        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")

        # Step 2: Profile dataset
        logger.info("Step 1/3: Profiling dataset...")
        profiler = DatasetProfiler(df, problem_context["type"])
        profile = profiler.generate_profile()

        # Step 3: Detect PII
        logger.info("Step 2/3: Detecting PII...")
        pii_detector = PIIDetector(df)
        pii_report = pii_detector.detect_all_pii()

        # Step 4: Generate LLM recommendations
        logger.info("Step 3/4: Generating AI recommendations...")
        try:
            llm_client = LLMClient()
            llm_response = llm_client.generate_recommendations(
                problem_context, profile, pii_report
            )
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}. Using fallback.")
            llm_response = {
                "recommendations": [],
                "priority_actions": ["LLM unavailable - check API key"],
                "overall_assessment": "Analysis complete but AI recommendations unavailable",
                "error": str(e),
            }

        # Step 5: Create initial report WITHOUT domain resources
        # Resources will be fetched asynchronously
        logger.info("Creating initial report (resources will be fetched separately)...")

        # Step 6: Create initial report
        report = {
            "dataset_id": dataset_id,
            "problem_type": problem_context["type"],
            "problem_description": problem_context["description"],
            "quality_scores": profile["quality_scores"],
            "shape": profile["shape"],
            "dtypes": profile["dtypes"],
            "missing_values": profile["missing_values"],
            "outliers": profile["outliers"],
            "class_imbalance": profile["class_imbalance"],
            "pii_report": pii_report,
            "recommendations": llm_response.get("recommendations", []),
            "priority_actions": llm_response.get("priority_actions", []),
            "overall_assessment": llm_response.get("overall_assessment", ""),
            "domain_resources": [],  # Empty initially, will be populated by background task
            "resources_status": "pending",  # Status: pending, loading, complete, error
            "created_at": datetime.now(UTC).replace(tzinfo=None),
        }

        # Step 7: Store initial report in MongoDB
        result = db["reports"].insert_one(report.copy())
        report["report_id"] = str(result.inserted_id)

        # Add token consumption info to response
        if _token_service and user_email:
            user_balance = _token_service.get_or_create_user_balance(user_email)
            report["token_info"] = {
                "tokens_consumed": _token_service.get_service_cost(
                    ServiceType.ANALYSIS
                ),
                "remaining_balance": user_balance.token_balance,
            }

        logger.info(f"Initial analysis complete. Report ID: {report['report_id']}")
        logger.info(
            f"Domain resources will be fetched asynchronously for report: {report['report_id']}"
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/{dataset_id}/resources")
async def fetch_resources(dataset_id: str, db=Depends(get_db)):
    """
    Fetch domain resources for an analyzed dataset.
    This endpoint is called separately to avoid blocking the main analysis.

    Args:
        dataset_id: ID of the dataset

    Returns:
        Domain resources list
    """
    logger.info(f"Fetching domain resources for dataset: {dataset_id}")

    try:
        # Load dataset metadata
        try:
            dataset_doc = db["datasets"].find_one({"_id": ObjectId(dataset_id)})
        except:
            dataset_doc = db["datasets"].find_one({"_id": dataset_id})

        if not dataset_doc:
            raise HTTPException(
                status_code=404, detail=f"Dataset not found: {dataset_id}"
            )

        # Get the report for this dataset
        try:
            report = db["reports"].find_one(
                {"dataset_id": dataset_id},
                sort=[("created_at", -1)],  # Get most recent report
            )
        except Exception:
            report = None

        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis report found for dataset: {dataset_id}",
            )

        # Extract problem context
        problem_context = {
            "description": dataset_doc.get("problem_description", ""),
            "type": dataset_doc.get("problem_type", "unknown"),
        }

        # Update status to loading
        db["reports"].update_one(
            {"_id": report["_id"]}, {"$set": {"resources_status": "loading"}}
        )

        # Search for domain resources with Exa
        logger.info("Searching for domain resources...")
        try:
            # Convert recommendations to issues format for Exa
            issues_for_search = []
            for rec in report.get("recommendations", [])[:5]:  # Limit to top 5
                issues_for_search.append(
                    {
                        "category": rec.get("category", "unknown"),
                        "severity": rec.get("severity", "medium"),
                        "description": rec.get("suggestion", ""),
                    }
                )

            exa_client = ExaClient()
            domain_resources = exa_client.search_resources(
                problem_context, issues_for_search, max_results=12
            )

            # Update report with resources
            db["reports"].update_one(
                {"_id": report["_id"]},
                {
                    "$set": {
                        "domain_resources": domain_resources,
                        "resources_status": "complete",
                        "resources_updated_at": datetime.now(UTC).replace(tzinfo=None),
                    }
                },
            )

            logger.info(
                f"Successfully fetched {len(domain_resources)} domain resources"
            )

            return {
                "dataset_id": dataset_id,
                "resources": domain_resources,
                "status": "complete",
                "count": len(domain_resources),
            }

        except Exception as e:
            logger.warning(f"Exa search failed: {e}. Returning empty resources.")

            # Update status to error
            db["reports"].update_one(
                {"_id": report["_id"]},
                {
                    "$set": {
                        "domain_resources": [],
                        "resources_status": "error",
                        "resources_error": str(e),
                    }
                },
            )

            return {
                "dataset_id": dataset_id,
                "resources": [],
                "status": "error",
                "error": str(e),
                "count": 0,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching resources: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch resources: {str(e)}"
        )


@router.get("/reports/{report_id}/resources")
async def get_report_resources(report_id: str, db=Depends(get_db)):
    """
    Get the current status and resources for a report.
    Used for polling the resources status.

    Args:
        report_id: ID of the report

    Returns:
        Resources status and data
    """
    try:
        # Get the report
        try:
            report = db["reports"].find_one({"_id": ObjectId(report_id)})
        except:
            report = db["reports"].find_one({"_id": report_id})

        if not report:
            raise HTTPException(
                status_code=404, detail=f"Report not found: {report_id}"
            )

        return {
            "report_id": report_id,
            "resources": report.get("domain_resources", []),
            "status": report.get("resources_status", "pending"),
            "count": len(report.get("domain_resources", [])),
            "updated_at": report.get("resources_updated_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report resources: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get report resources: {str(e)}"
        )
