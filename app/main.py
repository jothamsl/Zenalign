"""
FastAPI main application.
Single-agent backend for dataset quality auditing.
Integrated with Interswitch payment gateway for token-based monetization.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analyze, payment, upload
from app.services.db import close_db, init_db
from app.services.interswitch_client import InterswitchClient
from app.services.token_service import TokenService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database client
db_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global db_client
    logger.info("Senalign backend starting up...")

    # Initialize MongoDB connection
    try:
        db_client = init_db()
        upload._db_client = db_client  # Share with upload router
        analyze._db_client = db_client  # Share with analyze router
        logger.info("Database connected")

        # Initialize payment services
        try:
            # Initialize Interswitch client
            interswitch_client = InterswitchClient()
            payment._interswitch_client = interswitch_client
            logger.info("Interswitch payment gateway initialized")

            # Initialize token service
            token_service = TokenService(db_client)
            payment._token_service = token_service
            analyze._token_service = token_service
            logger.info("Token service initialized")

        except Exception as e:
            logger.warning(f"Payment services initialization failed: {e}")

    except Exception as e:
        logger.warning(f"Database connection failed (will use mocks for testing): {e}")

    yield

    # Cleanup
    if db_client:
        close_db(db_client)
        logger.info("Database connection closed")
    logger.info("Senalign backend shutting down...")


app = FastAPI(
    title="Senalign",
    description="Backend co-pilot for dataset quality auditing",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(payment.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "senalign"}
