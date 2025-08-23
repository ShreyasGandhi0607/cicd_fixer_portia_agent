"""Health check endpoints for the CI/CD Fixer Agent."""

from datetime import datetime
from fastapi import APIRouter, Depends
from ...models.responses import HealthResponse
from ...core.config import get_settings
from ...core.logging import get_logger
from ...database.connection import get_db_connection
from ...services.github_service import GitHubService
from ...services.gemini_agent import GeminiFixerAgent

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Check the overall health of the application and its services."""
    logger.info("Health check requested")
    
    settings = get_settings()
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Check database connection
    db_connection = get_db_connection()
    db_status = "healthy" if db_connection.test_connection() else "unhealthy"
    
    # Check GitHub service
    github_service = GitHubService()
    github_status = "healthy" if github_service.test_connection() else "unhealthy"
    
    # Check Gemini AI service
    gemini_agent = GeminiFixerAgent()
    gemini_status = "healthy" if gemini_agent.test_connection() else "unhealthy"
    
    # Check Portia agent service
    try:
        from ..services.portia_agent import portia_agent
        portia_status = "healthy" if portia_agent.test_portia_connection() else "unhealthy"
    except Exception as e:
        logger.warning(f"Portia agent health check failed: {e}")
        portia_status = "unhealthy"
    
    services = {
        "database": db_status,
        "github": github_status,
        "gemini_ai": gemini_status,
        "portia_agent": portia_status
    }
    
    # Determine overall status
    overall_status = "healthy"
    if any(status == "unhealthy" for status in services.values()):
        overall_status = "degraded"
    
    logger.info(f"Health check completed - Status: {overall_status}")
    
    return HealthResponse(
        status=overall_status,
        timestamp=timestamp,
        services=services
    )


@router.get("/ready")
async def readiness_check():
    """Check if the application is ready to serve requests."""
    logger.info("Readiness check requested")
    
    # Check critical services
    db_connection = get_db_connection()
    if not db_connection.test_connection():
        logger.error("Database not ready")
        return {"status": "not_ready", "reason": "Database connection failed"}
    
    github_service = GitHubService()
    if not github_service.test_connection():
        logger.warning("GitHub service not ready")
        return {"status": "not_ready", "reason": "GitHub service unavailable"}
    
    logger.info("Application is ready")
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Check if the application is alive and responding."""
    logger.debug("Liveness check requested")
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
