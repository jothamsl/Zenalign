import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import DatasetUploadResponse
from app.services.ingestion import ingest_file
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a dataset file (CSV, JSON, or Excel).
    Returns dataset_id and basic file info.
    """
    settings = get_settings()
    
    # Check file extension
    filename = file.filename or "unknown"
    supported_extensions = [
        '.csv', '.tsv', '.txt',
        '.json', '.jsonl',
        '.xlsx', '.xls', '.xlsb',
        '.parquet', '.feather',
        '.pkl', '.pickle',
        '.hdf', '.h5',
        '.dta', '.sav',
        '.xml', '.html'
    ]
    
    if not any(filename.lower().endswith(ext) for ext in supported_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {', '.join(supported_extensions)}"
        )
    
    # Read file
    content = await file.read()
    
    # Check size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
        )
    
    try:
        # Ingest in thread (pandas is sync)
        dataset_id, df, file_size = await asyncio.to_thread(
            ingest_file,
            content,
            filename,
            settings.data_dir
        )
        
        return DatasetUploadResponse(
            dataset_id=dataset_id,
            filename=filename,
            rows=len(df),
            columns=len(df.columns),
            size_bytes=file_size,
            uploaded_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
