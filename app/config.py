import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration. Loads from environment variables."""
    
    # Required keys
    openai_api_key: str
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Optional keys (for future features)
    exa_api_key: Optional[str] = None
    kaggle_username: Optional[str] = None
    kaggle_key: Optional[str] = None
    
    # App settings
    data_dir: str = "data"
    max_upload_size_mb: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get validated settings. Raises ValidationError if required keys missing."""
    return Settings()


def validate_required_keys(*keys: str) -> None:
    """
    Validate that specific environment variables are set.
    Raises RuntimeError with clear instructions if missing.
    """
    missing = []
    for key in keys:
        if not os.getenv(key):
            missing.append(key)
    
    if missing:
        raise RuntimeError(
            f"ERROR: Missing required environment variable(s): {', '.join(missing)}\n"
            f"ACTION: Set the missing keys and re-run:\n" +
            "\n".join(f"  export {k}=your_value_here" for k in missing) +
            "\nNo fallback will be used."
        )
