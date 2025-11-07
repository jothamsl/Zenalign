import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import datasets, analysis
from app.config import get_settings, validate_required_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("Starting Senalign Dataset Quality Validator API")
    
    # Validate required environment variables
    try:
        settings = get_settings()
        logger.info("✓ Configuration loaded successfully")
        
        if not settings.openai_api_key:
            logger.warning(
                "⚠️  OPENAI_API_KEY not set. LLM analysis will fail. "
                "Set it with: export OPENAI_API_KEY=your_key_here"
            )
        else:
            logger.info("✓ OPENAI_API_KEY is set")
            
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    yield
    
    logger.info("Shutting down Senalign API")


app = FastAPI(
    title="Senalign Dataset Quality Validator",
    description="API for dataset quality validation with LLM-powered analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(datasets.router)
app.include_router(analysis.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Senalign Dataset Quality Validator",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        settings = get_settings()
        return {
            "status": "healthy",
            "openai_configured": bool(settings.openai_api_key),
            "exa_configured": bool(settings.exa_api_key),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
