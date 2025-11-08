import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Include API routers
app.include_router(datasets.router)
app.include_router(analysis.router)


# Serve frontend static files if they exist (for production)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    logger.info(f"Serving frontend from {frontend_dist}")
    
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend."""
        return FileResponse(frontend_dist / "index.html")
    
    @app.get("/{full_path:path}")
    async def serve_frontend_routes(full_path: str):
        """Serve React frontend for all other routes (SPA routing)."""
        # Don't intercept API routes
        if full_path.startswith(("datasets/", "analysis/", "health", "docs", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(frontend_dist / "index.html")
else:
    logger.warning("Frontend dist folder not found. Serving API only.")
    
    @app.get("/")
    async def root():
        """Health check endpoint."""
        return {
            "service": "Senalign Dataset Quality Validator",
            "status": "running",
            "version": "1.0.0",
            "note": "Frontend not built. Run 'npm run build' in frontend directory."
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
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
