"""
Resume-Job Matching System - FastAPI Application
Production-ready with PostgreSQL, BERT embeddings, and async processing.
"""

import sys
import os
from contextlib import asynccontextmanager
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from core.database import init_db, close_db
from api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting Resume-Job Matching System...")
    logger.info(f"Database: {'SQLite' if settings.USE_SQLITE else 'PostgreSQL'}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    
    # Import models to register them with Base.metadata
    from models.job import Job
    from models.resume import Resume
    from models.task import BackgroundTask
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.warning("Continuing without database - some features may not work")

    
    # Pre-load embedding model (optional, but speeds up first request)
    try:
        from services.embedding_service import get_embedding_service
        embedding_service = get_embedding_service()
        logger.info("Embedding model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not pre-load embedding model: {e}")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Goodbye!")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Resume-Job Matching System
    
    A production-ready Information Retrieval system that matches resumes to job descriptions
    using semantic understanding (BERT) and skill-based matching.
    
    ### Features:
    - **Semantic Search**: BERT embeddings understand context, not just keywords
    - **Skill Gap Analysis**: Identifies missing skills with fuzzy matching
    - **Instant Search**: PostgreSQL + pgvector for millisecond vector search
    - **Background Tasks**: Async processing for heavy operations
    - **LLM Integration**: AI-powered explanations and email generation
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root - returns basic info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


# Static files (for frontend if needed)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(project_root, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  Resume-Job Matching System v2.0")
    print("  Production-Ready with BERT + PostgreSQL")
    print("=" * 60)
    print(f"\n  Server: http://{settings.HOST}:{settings.PORT}")
    print(f"  API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  Database: {'SQLite' if settings.USE_SQLITE else 'PostgreSQL'}")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
