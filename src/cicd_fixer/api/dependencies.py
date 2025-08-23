"""
FastAPI dependencies for dependency injection.
Manages service instances and database connections.
"""

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status

from ..core.config import get_settings, get_database_settings, get_github_settings, get_ai_settings
from ..database.connection import DatabaseManager
from ..database.repositories import WorkflowRunRepository, AnalyticsRepository
from ..services.github_service import GitHubService
from ..services.gemini_agent import GeminiFixerAgent
from ..services.portia_agent import CICDFixerPortiaAgent
from ..analytics.pattern_analyzer import CICDPatternAnalyzer
from ..analytics.repository_learning import RepositoryLearningSystem
from ..analytics.ml_predictor import MLPatternRecognizer, SuccessPredictor
from ..analytics.intelligent_generator import IntelligentFixGenerator

logger = logging.getLogger(__name__)


# Configuration dependencies
@lru_cache()
def get_app_settings():
    """Get application settings (cached)."""
    return get_settings()


# Database dependencies
@lru_cache()
def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    try:
        settings = get_database_settings()
        return DatabaseManager(
            host=settings.host,
            port=settings.port,
            database=settings.name,
            user=settings.user,
            password=settings.password
        )
    except Exception as e:
        logger.error(f"Failed to initialize database manager: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )


def get_database_connection():
    """Get database connection (per-request)."""
    db_manager = get_database_manager()
    try:
        with db_manager.get_connection() as conn:
            yield conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


def get_workflow_repository(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> WorkflowRunRepository:
    """Get workflow run repository."""
    return WorkflowRunRepository(db_manager)


def get_analytics_repository(
    db_manager: DatabaseManager = Depends(get_database_manager)
) -> AnalyticsRepository:
    """Get analytics repository."""
    return AnalyticsRepository(db_manager)


# Service dependencies
@lru_cache()
def get_github_service() -> GitHubService:
    """Get GitHub service instance."""
    try:
        settings = get_github_settings()
        return GitHubService(token=settings.token)
    except Exception as e:
        logger.error(f"Failed to initialize GitHub service: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub service unavailable"
        )


@lru_cache()
def get_gemini_agent() -> GeminiFixerAgent:
    """Get Gemini AI agent instance."""
    try:
        settings = get_ai_settings()
        if not settings.google_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google API key not configured"
            )
        return GeminiFixerAgent(api_key=settings.google_api_key)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initialize Gemini agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini AI service unavailable"
        )


@lru_cache()
def get_portia_agent() -> CICDFixerPortiaAgent:
    """Get Portia agent instance."""
    try:
        settings = get_ai_settings()
        if not settings.google_api_key and settings.enable_portia:
            logger.warning("Portia agent initialized without Google API key")
        return CICDFixerPortiaAgent()
    except Exception as e:
        logger.error(f"Failed to initialize Portia agent: {e}")
        # Return None instead of raising for optional service
        return None


# Analytics dependencies
@lru_cache()
def get_pattern_analyzer() -> CICDPatternAnalyzer:
    """Get pattern analyzer instance."""
    try:
        db_manager = get_database_manager()
        return CICDPatternAnalyzer(db_manager)
    except Exception as e:
        logger.error(f"Failed to initialize pattern analyzer: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pattern analyzer unavailable"
        )


@lru_cache()
def get_repository_learning_system() -> RepositoryLearningSystem:
    """Get repository learning system instance."""
    try:
        db_manager = get_database_manager()
        return RepositoryLearningSystem(db_manager)
    except Exception as e:
        logger.error(f"Failed to initialize repository learning system: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Repository learning system unavailable"
        )


@lru_cache()
def get_ml_pattern_recognizer() -> MLPatternRecognizer:
    """Get ML pattern recognizer instance."""
    try:
        db_manager = get_database_manager()
        return MLPatternRecognizer(db_manager)
    except Exception as e:
        logger.error(f"Failed to initialize ML pattern recognizer: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML pattern recognizer unavailable"
        )


@lru_cache()
def get_success_predictor() -> SuccessPredictor:
    """Get success predictor instance."""
    try:
        db_manager = get_database_manager()
        return SuccessPredictor(db_manager)
    except Exception as e:
        logger.error(f"Failed to initialize success predictor: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Success predictor unavailable"
        )


@lru_cache()
def get_intelligent_fix_generator() -> IntelligentFixGenerator:
    """Get intelligent fix generator instance."""
    try:
        db_manager = get_database_manager()
        return IntelligentFixGenerator(db_manager)
    except Exception as e:
        logger.error(f"Failed to initialize intelligent fix generator: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Intelligent fix generator unavailable"
        )


# Type aliases for dependency injection
DatabaseManagerDep = Annotated[DatabaseManager, Depends(get_database_manager)]
WorkflowRepositoryDep = Annotated[WorkflowRunRepository, Depends(get_workflow_repository)]
AnalyticsRepositoryDep = Annotated[AnalyticsRepository, Depends(get_analytics_repository)]

GitHubServiceDep = Annotated[GitHubService, Depends(get_github_service)]
GeminiAgentDep = Annotated[GeminiFixerAgent, Depends(get_gemini_agent)]
PortiaAgentDep = Annotated[CICDFixerPortiaAgent, Depends(get_portia_agent)]

PatternAnalyzerDep = Annotated[CICDPatternAnalyzer, Depends(get_pattern_analyzer)]
RepoLearningDep = Annotated[RepositoryLearningSystem, Depends(get_repository_learning_system)]
MLPatternRecognizerDep = Annotated[MLPatternRecognizer, Depends(get_ml_pattern_recognizer)]
SuccessPredictorDep = Annotated[SuccessPredictor, Depends(get_success_predictor)]
IntelligentFixGeneratorDep = Annotated[IntelligentFixGenerator, Depends(get_intelligent_fix_generator)]


# Health check dependency
def check_service_health() -> dict:
    """Check health of all services."""
    health_status = {
        "database": "unknown",
        "github": "unknown",
        "gemini": "unknown",
        "portia": "unknown"
    }
    
    # Check database
    try:
        db_manager = get_database_manager()
        with db_manager.get_connection():
            health_status["database"] = "healthy"
    except Exception:
        health_status["database"] = "unhealthy"
    
    # Check GitHub service
    try:
        github_service = get_github_service()
        if github_service.token:
            health_status["github"] = "healthy"
        else:
            health_status["github"] = "limited"  # No token
    except Exception:
        health_status["github"] = "unhealthy"
    
    # Check Gemini service
    try:
        gemini_agent = get_gemini_agent()
        health_status["gemini"] = "healthy"
    except HTTPException as e:
        if "not configured" in str(e.detail):
            health_status["gemini"] = "not_configured"
        else:
            health_status["gemini"] = "unhealthy"
    except Exception:
        health_status["gemini"] = "unhealthy"
    
    # Check Portia service
    try:
        portia_agent = get_portia_agent()
        if portia_agent:
            health_status["portia"] = "healthy"
        else:
            health_status["portia"] = "limited"
    except Exception:
        health_status["portia"] = "unhealthy"
    
    return health_status


# Optional dependencies (don't raise if unavailable)
def get_optional_portia_agent() -> CICDFixerPortiaAgent | None:
    """Get Portia agent if available, None otherwise."""
    try:
        return get_portia_agent()
    except Exception:
        return None


def get_optional_gemini_agent() -> GeminiFixerAgent | None:
    """Get Gemini agent if available, None otherwise."""
    try:
        return get_gemini_agent()
    except Exception:
        return None