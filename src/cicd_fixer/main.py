"""Main FastAPI application for the CI/CD Fixer Agent."""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.logging import get_logger
from .api.routes import health, analysis, webhook
# from .api.routes import portia  # Temporarily disabled for debugging
from .database.connection import get_db_connection

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting CI/CD Fixer Agent...")
    
    # Test database connection
    try:
        db_connection = get_db_connection()
        if db_connection.test_connection():
            logger.info("Database connection established")
        else:
            logger.warning("Database connection failed - some features may be limited")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    # Test external services
    try:
        from .services.github_service import GitHubService
        github_service = GitHubService()
        if github_service.test_connection():
            logger.info("GitHub service connection established")
        else:
            logger.warning("GitHub service connection failed")
    except Exception as e:
        logger.error(f"GitHub service initialization error: {e}")
    
    try:
        from .services.gemini_agent import GeminiFixerAgent
        gemini_agent = GeminiFixerAgent()
        if gemini_agent.test_connection():
            logger.info("Gemini AI service connection established")
        else:
            logger.warning("Gemini AI service connection failed")
    except Exception as e:
        logger.error(f"Gemini AI service initialization error: {e}")
    
    # Temporarily disable Portia service for debugging
    # try:
    #     from .services.portia_agent import portia_agent
    #     if portia_agent.test_portia_connection():
    #         logger.info("Portia service connection established")
    #     else:
    #         logger.warning("Portia service connection failed")
    # except Exception as e:
    #     logger.error(f"Portia service initialization error: {e}")
    
    logger.info("CI/CD Fixer Agent startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CI/CD Fixer Agent...")


# Create FastAPI application
app = FastAPI(
    title="CI/CD Fixer Agent",
    description="AI-powered CI/CD failure analysis and fix generation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(webhook.router, prefix="/api/v1")
# app.include_router(portia.router, prefix="/api/v1")  # Temporarily disabled for debugging

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "CI/CD Fixer Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": "2025-08-23T10:00:00.000Z"
        }
    )

# Health check endpoint for basic monitoring
@app.get("/health")
async def basic_health():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "cicd-fixer-agent"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "cicd_fixer.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
