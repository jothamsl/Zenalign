import os
import uuid
import shutil
from pathlib import Path
from typing import Tuple
import pandas as pd


def generate_dataset_id() -> str:
    """Generate unique dataset ID."""
    return f"ds_{uuid.uuid4().hex[:12]}"


def generate_job_id() -> str:
    """Generate unique job ID."""
    return f"job_{uuid.uuid4().hex[:12]}"


def save_uploaded_file(file_content: bytes, filename: str, data_dir: str) -> Tuple[str, Path]:
    """
    Save uploaded file to data directory.
    Returns (dataset_id, file_path)
    """
    dataset_id = generate_dataset_id()
    os.makedirs(data_dir, exist_ok=True)
    
    # Preserve extension
    ext = Path(filename).suffix
    file_path = Path(data_dir) / f"{dataset_id}{ext}"
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return dataset_id, file_path


def load_dataframe(file_path: Path) -> pd.DataFrame:
    """Load DataFrame from various formats."""
    ext = file_path.suffix.lower()
    
    try:
        if ext == ".csv":
            # Try different encodings and separators
            try:
                return pd.read_csv(file_path)
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding='latin-1')
            except pd.errors.ParserError:
                # Try semicolon separator (common in Europe)
                return pd.read_csv(file_path, sep=';')
        
        elif ext == ".tsv":
            return pd.read_csv(file_path, sep='\t')
        
        elif ext == ".txt":
            # Try to detect delimiter
            with open(file_path, 'r') as f:
                first_line = f.readline()
                if '\t' in first_line:
                    return pd.read_csv(file_path, sep='\t')
                elif ';' in first_line:
                    return pd.read_csv(file_path, sep=';')
                elif '|' in first_line:
                    return pd.read_csv(file_path, sep='|')
                else:
                    return pd.read_csv(file_path)
        
        elif ext == ".json":
            # Try different JSON orientations
            try:
                return pd.read_json(file_path)
            except ValueError:
                return pd.read_json(file_path, lines=True)  # JSON Lines format
        
        elif ext == ".jsonl":
            return pd.read_json(file_path, lines=True)
        
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        
        elif ext == ".xlsb":
            return pd.read_excel(file_path, engine='pyxlsb')
        
        elif ext == ".parquet":
            return pd.read_parquet(file_path)
        
        elif ext == ".feather":
            return pd.read_feather(file_path)
        
        elif ext == ".pkl" or ext == ".pickle":
            return pd.read_pickle(file_path)
        
        elif ext == ".hdf" or ext == ".h5":
            return pd.read_hdf(file_path)
        
        elif ext == ".dta":
            return pd.read_stata(file_path)
        
        elif ext == ".sav":
            return pd.read_spss(file_path)
        
        elif ext == ".xml":
            return pd.read_xml(file_path)
        
        elif ext == ".html":
            # Read first table from HTML
            tables = pd.read_html(file_path)
            if tables:
                return tables[0]
            else:
                raise ValueError("No tables found in HTML file")
        
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    except Exception as e:
        raise ValueError(f"Failed to load {ext} file: {str(e)}")


def get_dataset_path(dataset_id: str, data_dir: str) -> Path:
    """Get path to dataset file."""
    extensions = [
        ".csv", ".tsv", ".txt",
        ".json", ".jsonl",
        ".xlsx", ".xls", ".xlsb",
        ".parquet", ".feather",
        ".pkl", ".pickle",
        ".hdf", ".h5",
        ".dta", ".sav",
        ".xml", ".html"
    ]
    
    for ext in extensions:
        path = Path(data_dir) / f"{dataset_id}{ext}"
        if path.exists():
            return path
    raise FileNotFoundError(f"Dataset {dataset_id} not found")
