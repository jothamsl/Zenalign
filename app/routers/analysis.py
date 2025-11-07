import asyncio
import logging
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalysisRequest,
    AnalysisStartResponse,
    LLMAnalysisReport
)
from app.services.profiler import profile_dataset
from app.services.llm_client import get_llm_client
from app.utils.fileutils import get_dataset_path, load_dataframe, generate_job_id
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])

# In-memory job storage (for production use Redis/DB)
_jobs: Dict[str, LLMAnalysisReport] = {}


@router.post("/start", response_model=AnalysisStartResponse)
async def start_analysis(request: AnalysisRequest):
    """
    Start dataset analysis with profiling, PII detection, and LLM recommendations.
    Requires OPENAI_API_KEY to be set.
    """
    settings = get_settings()
    
    # Validate OpenAI key
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "ERROR: Missing required environment variable: OPENAI_API_KEY\n"
                "ACTION: export OPENAI_API_KEY=your_key_here and re-run. No fallback will be used."
            )
        )
    
    job_id = generate_job_id()
    
    # Initialize job
    job = LLMAnalysisReport(
        job_id=job_id,
        dataset_id=request.dataset_id,
        status="processing",
        created_at=datetime.utcnow().isoformat(),
    )
    _jobs[job_id] = job
    
    # Run analysis in background
    asyncio.create_task(_run_analysis(job_id, request, settings))
    
    return AnalysisStartResponse(
        job_id=job_id,
        status="processing",
        message="Analysis started. Poll /analysis/result/{job_id} for results."
    )


async def _run_analysis(job_id: str, request: AnalysisRequest, settings):
    """Background task to run the analysis."""
    job = _jobs[job_id]
    
    try:
        # Load dataset
        dataset_path = await asyncio.to_thread(
            get_dataset_path,
            request.dataset_id,
            settings.data_dir
        )
        df = await asyncio.to_thread(load_dataframe, dataset_path)
        
        # Profile dataset
        logger.info(f"Profiling dataset {request.dataset_id}")
        profile = await asyncio.to_thread(
            profile_dataset,
            df,
            request.dataset_id
        )
        
        # Get LLM recommendations
        logger.info(f"Getting LLM recommendations for {request.dataset_id}")
        llm_client = get_llm_client(settings.openai_api_key)
        recommendations = await asyncio.to_thread(
            llm_client.analyze_dataset,
            profile,
            request
        )
        
        # Update job
        job.status = "completed"
        job.completed_at = datetime.utcnow().isoformat()
        job.profile = profile
        job.llm_recommendations = recommendations
        
        logger.info(f"Analysis {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {job_id} failed: {e}")
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.utcnow().isoformat()


@router.get("/result/{job_id}", response_model=LLMAnalysisReport)
async def get_analysis_result(job_id: str):
    """
    Get analysis result by job_id.
    Poll this endpoint until status is 'completed' or 'failed'.
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return _jobs[job_id]
