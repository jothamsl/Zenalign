"""
Analysis orchestration router.
Sequential chain (Ch. 5): Profile → PII → LLM → Report.
Ties all services together for complete dataset analysis.
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, UTC
from bson import ObjectId
import pandas as pd
import os
import logging
from typing import Dict, Any

from app.services.db import get_database, init_db
from app.services.profiler import DatasetProfiler
from app.services.pii_detector import PIIDetector
from app.services.llm_client import LLMClient
from app.services.exa_client import ExaClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analyze"])

# Global MongoDB client
_db_client = None


def get_db():
    """Dependency to get database instance."""
    global _db_client
    if _db_client is None:
        _db_client = init_db()
    return get_database(_db_client)


@router.post("/analyze/{dataset_id}")
async def analyze_dataset(dataset_id: str, db=Depends(get_db)):
    """
    Run complete analysis pipeline on uploaded dataset.
    
    Orchestration sequence (Ch. 5 sequential chain):
    1. Load dataset + metadata from MongoDB
    2. Profile dataset (quality scores, issues)
    3. Detect PII (privacy scan)
    4. Generate LLM recommendations (context-aware)
    5. Search for domain resources (Exa)
    6. Create complete report
    7. Store report in MongoDB
    
    Args:
        dataset_id: ID of uploaded dataset
        
    Returns:
        Complete analysis report
    """
    logger.info(f"Starting analysis for dataset: {dataset_id}")
    
    try:
        # Step 1: Load dataset metadata
        try:
            dataset_doc = db["datasets"].find_one({"_id": ObjectId(dataset_id)})
        except:
            # If ObjectId conversion fails, try as string
            dataset_doc = db["datasets"].find_one({"_id": dataset_id})
        
        if not dataset_doc:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset not found: {dataset_id}"
            )
        
        # Extract problem context
        problem_context = {
            'description': dataset_doc.get('problem_description', ''),
            'type': dataset_doc.get('problem_type', 'unknown')
        }
        
        # Load dataset file
        file_path = dataset_doc.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Dataset file not found on disk"
            )
        
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataset: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Step 2: Profile dataset
        logger.info("Step 1/3: Profiling dataset...")
        profiler = DatasetProfiler(df, problem_context['type'])
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
                problem_context,
                profile,
                pii_report
            )
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}. Using fallback.")
            llm_response = {
                'recommendations': [],
                'priority_actions': ['LLM unavailable - check API key'],
                'overall_assessment': 'Analysis complete but AI recommendations unavailable',
                'error': str(e)
            }
        
        # Step 5: Search for domain resources with Exa
        logger.info("Step 4/4: Searching for domain resources...")
        try:
            # Convert issues to format Exa expects
            issues_for_search = []
            for issue in profile.get('issues', []):
                issues_for_search.append({
                    'category': issue.get('issue', 'unknown'),
                    'severity': issue.get('severity', 'medium'),
                    'description': issue.get('why_matters', '')
                })
            
            exa_client = ExaClient()
            domain_resources = exa_client.search_resources(
                problem_context,
                issues_for_search,
                max_results=8
            )
        except Exception as e:
            logger.warning(f"Exa search failed: {e}. Continuing without resources.")
            domain_resources = []
        
        # Step 6: Create complete report
        report = {
            'dataset_id': dataset_id,
            'problem_type': problem_context['type'],
            'problem_description': problem_context['description'],
            'quality_scores': profile['quality_scores'],
            'shape': profile['shape'],
            'dtypes': profile['dtypes'],
            'missing_values': profile['missing_values'],
            'outliers': profile['outliers'],
            'class_imbalance': profile['class_imbalance'],
            'pii_report': pii_report,
            'recommendations': llm_response.get('recommendations', []),
            'priority_actions': llm_response.get('priority_actions', []),
            'overall_assessment': llm_response.get('overall_assessment', ''),
            'domain_resources': domain_resources,
            'created_at': datetime.now(UTC).replace(tzinfo=None)
        }
        
        # Step 7: Store report in MongoDB
        # Step 6: Store report in MongoDB
        result = db["reports"].insert_one(report.copy())
        report['report_id'] = str(result.inserted_id)
        
        logger.info(f"Analysis complete. Report ID: {report['report_id']}")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
