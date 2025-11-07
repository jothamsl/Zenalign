import logging
from pathlib import Path
import pandas as pd
from app.utils.fileutils import save_uploaded_file, load_dataframe

logger = logging.getLogger(__name__)


def ingest_file(file_content: bytes, filename: str, data_dir: str) -> tuple[str, pd.DataFrame, int]:
    """
    Ingest uploaded file.
    Returns (dataset_id, dataframe, file_size)
    """
    logger.info(f"Ingesting file: {filename}")
    
    dataset_id, file_path = save_uploaded_file(file_content, filename, data_dir)
    
    try:
        df = load_dataframe(file_path)
        logger.info(f"Loaded dataset {dataset_id}: {len(df)} rows, {len(df.columns)} columns")
        
        file_size = file_path.stat().st_size
        
        return dataset_id, df, file_size
    except Exception as e:
        logger.error(f"Failed to load dataset {dataset_id}: {e}")
        # Clean up on failure
        file_path.unlink(missing_ok=True)
        raise
