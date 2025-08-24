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

# Import and include additional routes
from .api.routes import fixes, failures, analytics, portia

app.include_router(fixes.router, prefix="/api/v1")
app.include_router(failures.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(portia.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with comprehensive API information."""
    return {
        "message": "CI/CD Fixer Agent API",
        "version": "1.0.0",
        "description": "AI-powered CI/CD failure analysis and fix generation system",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "webhook": "/api/v1/webhook/github", 
            "analysis": {
                "workflow": "/api/v1/analysis/workflow",
                "ml_prediction": "/api/v1/analysis/ml-prediction",
                "generate_fix": "/api/v1/analysis/generate-fix"
            },
            "fixes": {
                "list": "/api/v1/fixes",
                "detail": "/api/v1/fixes/{fix_id}",
                "approve": "/api/v1/fixes/{fix_id}/approve",
                "reject": "/api/v1/fixes/{fix_id}/reject",
                "history": "/api/v1/fixes/history/{owner}/{repo}"
            },
            "failures": {
                "list": "/api/v1/failures",
                "detail": "/api/v1/failures/{failure_id}",
                "repository": "/api/v1/failures/repository/{owner}/{repo}",
                "statistics": "/api/v1/failures/statistics/summary"
            },
            "analytics": {
                "patterns": "/api/v1/analytics/patterns",
                "effectiveness": "/api/v1/analytics/effectiveness",
                "repository_profile": "/api/v1/analytics/repository/{owner}/{repo}",
                "dashboard": "/api/v1/analytics/dashboard",
                "ml_similar_fixes": "/api/v1/analytics/ml/similar-fixes",
                "ml_predict_success": "/api/v1/analytics/ml/predict-success",
                "ml_generate_fix": "/api/v1/analytics/ml/generate-enhanced-fix",
                "ml_learn_feedback": "/api/v1/analytics/ml/learn-from-feedback",
                "ml_pattern_insights": "/api/v1/analytics/ml/pattern-insights",
                "ml_model_performance": "/api/v1/analytics/ml/model-performance",
                "ml_fix_suggestions": "/api/v1/analytics/ml/fix-suggestions"
            },
            "portia": {
                "analyze": "/api/v1/portia/analyze",
                "clarifications": "/api/v1/portia/clarifications/{plan_run_id}/{clarification_id}",
                "approve_fix": "/api/v1/portia/fixes/{fix_id}/approve",
                "reject_fix": "/api/v1/portia/fixes/{fix_id}/reject",
                "plan_status": "/api/v1/portia/plans/{plan_run_id}/status",
                "pending_clarifications": "/api/v1/portia/plans/{plan_run_id}/clarifications",
                "tools": "/api/v1/portia/tools",
                "health": "/api/v1/portia/health"
            }
        },
        "features": {
            "pattern_recognition": "✅ Implemented - Analyzes failure patterns across repositories",
            "success_prediction": "✅ Implemented - ML-based fix success prediction", 
            "intelligent_fix_generation": "✅ Implemented - Enhanced AI fix generation",
            "repository_learning": "✅ Implemented - Repository-specific intelligence",
            "historical_analysis": "✅ Implemented - Time-based pattern analysis",
            "portia_ai": "✅ Implemented - Plan-based AI analysis workflows",
            "fix_management": "✅ Implemented - Complete fix approval/rejection workflow",
            "failure_tracking": "✅ Implemented - Comprehensive failure analytics"
        }
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
