"""GitHub webhook handling for the CI/CD Fixer Agent."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from datetime import datetime

from ...models.requests import WebhookPayload
from ...models.responses import WebhookResponse
from ...core.config import get_settings
from ...core.logging import get_logger
from ...services.github_service import GitHubService
from ...services.gemini_agent import GeminiFixerAgent
from ...database.repositories import workflow_run_repo, failure_analysis_repo

logger = get_logger(__name__)
router = APIRouter(prefix="/webhook", tags=["webhook"])


async def verify_webhook_signature(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_hub_signature: Optional[str] = Header(None)
) -> bool:
    """Verify GitHub webhook signature.
    
    Args:
        request: FastAPI request object
        x_hub_signature_256: GitHub webhook signature (SHA256)
        x_hub_signature: GitHub webhook signature (SHA1, deprecated)
        
    Returns:
        True if signature is valid, False otherwise
    """
    settings = get_settings()
    webhook_secret = settings.github_webhook_secret
    
    if not webhook_secret:
        logger.warning("No webhook secret configured, skipping signature verification")
        return True
    
    # Get the raw body
    body = await request.body()
    
    # Try SHA256 signature first (recommended)
    if x_hub_signature_256:
        expected_signature = f"sha256={hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()}"
        if hmac.compare_digest(x_hub_signature_256, expected_signature):
            return True
    
    # Fallback to SHA1 signature (deprecated but still supported)
    if x_hub_signature:
        expected_signature = f"sha1={hmac.new(webhook_secret.encode(), body, hashlib.sha256).hexdigest()}"
        if hmac.compare_digest(x_hub_signature, expected_signature):
            return True
    
    logger.warning("Webhook signature verification failed")
    return False


@router.post("/github", response_model=WebhookResponse)
async def github_webhook(
    request: Request,
    payload: WebhookPayload,
    signature_valid: bool = Depends(verify_webhook_signature)
):
    """Handle GitHub webhook events.
    
    Args:
        request: FastAPI request object
        payload: Webhook payload data
        signature_valid: Whether the webhook signature is valid
        
    Returns:
        Webhook processing response
    """
    try:
        if not signature_valid:
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        logger.info(f"Received GitHub webhook: {payload.action}")
        
        # Process different webhook events
        if payload.action == "completed" and payload.workflow_run:
            return await _process_workflow_completion(payload)
        elif payload.action == "requested" and payload.workflow_run:
            return await _process_workflow_request(payload)
        else:
            logger.info(f"Unhandled webhook action: {payload.action}")
            return WebhookResponse(
                processed=False,
                message=f"Unhandled webhook action: {payload.action}",
                timestamp=datetime.utcnow()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _process_workflow_completion(payload: WebhookPayload) -> WebhookResponse:
    """Process workflow completion webhook.
    
    Args:
        payload: Webhook payload with workflow run data
        
    Returns:
        Processing response
    """
    try:
        workflow_run = payload.workflow_run
        repository = payload.repository
        
        if not workflow_run or not repository:
            return WebhookResponse(
                processed=False,
                message="Missing workflow run or repository data",
                timestamp=datetime.utcnow()
            )
        
        owner = repository.get('owner', {}).get('login')
        repo_name = repository.get('name')
        run_id = workflow_run.get('id')
        conclusion = workflow_run.get('conclusion')
        
        if not all([owner, repo_name, run_id]):
            return WebhookResponse(
                processed=False,
                message="Missing required workflow run information",
                timestamp=datetime.utcnow()
            )
        
        logger.info(f"Processing workflow completion: {owner}/{repo_name} run {run_id}")
        
        # Check if workflow failed
        if conclusion == "failure":
            return await _analyze_workflow_failure(owner, repo_name, run_id, workflow_run)
        else:
            logger.info(f"Workflow {run_id} completed with status: {conclusion}")
            return WebhookResponse(
                processed=True,
                message=f"Workflow completed with status: {conclusion}",
                workflow_run_id=run_id,
                timestamp=datetime.utcnow()
            )
            
    except Exception as e:
        logger.error(f"Workflow completion processing failed: {e}")
        return WebhookResponse(
            processed=False,
            message=f"Failed to process workflow completion: {str(e)}",
            timestamp=datetime.utcnow()
        )


async def _process_workflow_request(payload: WebhookPayload) -> WebhookResponse:
    """Process workflow request webhook.
    
    Args:
        payload: Webhook payload with workflow run data
        
    Returns:
        Processing response
    """
    try:
        workflow_run = payload.workflow_run
        repository = payload.repository
        
        if not workflow_run or not repository:
            return WebhookResponse(
                processed=False,
                message="Missing workflow run or repository data",
                timestamp=datetime.utcnow()
            )
        
        owner = repository.get('owner', {}).get('login')
        repo_name = repository.get('name')
        run_id = workflow_run.get('id')
        
        logger.info(f"Workflow requested: {owner}/{repo_name} run {run_id}")
        
        # Create workflow run record in database
        workflow_run_id = workflow_run_repo.create_workflow_run(
            owner=owner,
            repo=repo_name,
            run_id=run_id,
            workflow_name=workflow_run.get('name'),
            status=workflow_run.get('status'),
            conclusion=workflow_run.get('conclusion')
        )
        
        if workflow_run_id:
            logger.info(f"Created workflow run record: {workflow_run_id}")
            return WebhookResponse(
                processed=True,
                message="Workflow run record created",
                workflow_run_id=run_id,
                timestamp=datetime.utcnow()
            )
        else:
            logger.warning(f"Failed to create workflow run record for run {run_id}")
            return WebhookResponse(
                processed=False,
                message="Failed to create workflow run record",
                workflow_run_id=run_id,
                timestamp=datetime.utcnow()
            )
            
    except Exception as e:
        logger.error(f"Workflow request processing failed: {e}")
        return WebhookResponse(
            processed=False,
            message=f"Failed to process workflow request: {str(e)}",
            timestamp=datetime.utcnow()
        )


async def _analyze_workflow_failure(owner: str, repo_name: str, run_id: int, 
                                   workflow_run: Dict[str, Any]) -> WebhookResponse:
    """Analyze a failed workflow and generate fix suggestions.
    
    Args:
        owner: Repository owner
        repo_name: Repository name
        run_id: Workflow run ID
        workflow_run: Workflow run data
        
    Returns:
        Analysis response
    """
    try:
        logger.info(f"Analyzing failed workflow: {owner}/{repo_name} run {run_id}")
        
        # Get workflow logs
        github_service = GitHubService()
        logs = github_service.get_workflow_run_logs(owner, repo_name, run_id)
        
        if not logs:
            logger.warning(f"Failed to retrieve logs for workflow run {run_id}")
            return WebhookResponse(
                processed=False,
                message="Failed to retrieve workflow logs",
                workflow_run_id=run_id,
                timestamp=datetime.utcnow()
            )
        
        # Analyze failure using Gemini AI
        gemini_agent = GeminiFixerAgent()
        repo_context = {
            "language": _detect_language_from_logs(logs),
            "framework": _detect_framework_from_logs(logs),
            "build_system": _detect_build_system_from_logs(logs)
        }
        
        analysis_result = gemini_agent.analyze_failure_and_suggest_fix(logs, repo_context)
        
        # Update workflow run with analysis results
        workflow_run_repo.update_workflow_run(
            run_id,
            failure_logs=logs,
            fix_suggestions=analysis_result,
            confidence_score=analysis_result.get('fix_suggestion', {}).get('confidence', 0.0),
            repository_context=repo_context
        )
        
        # Create failure analysis record
        failure_id = failure_analysis_repo.create_failure_analysis(
            workflow_run_id=run_id,
            error_pattern=analysis_result.get('error_analysis', {}).get('error_type'),
            error_type=analysis_result.get('error_analysis', {}).get('error_type'),
            error_severity=analysis_result.get('error_analysis', {}).get('error_severity'),
            suggested_fix=analysis_result.get('fix_suggestion', {}).get('description'),
            fix_confidence=analysis_result.get('fix_suggestion', {}).get('confidence', 0.0)
        )
        
        if failure_id:
            logger.info(f"Created failure analysis record: {failure_id}")
        
        return WebhookResponse(
            processed=True,
            message=f"Workflow failure analyzed successfully. Failure ID: {failure_id}",
            workflow_run_id=run_id,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Workflow failure analysis failed: {e}")
        return WebhookResponse(
            processed=False,
            message=f"Failed to analyze workflow failure: {str(e)}",
            workflow_run_id=run_id,
            timestamp=datetime.utcnow()
        )


def _detect_language_from_logs(logs: str) -> str:
    """Detect programming language from workflow logs.
    
    Args:
        logs: Workflow log text
        
    Returns:
        Detected language string
    """
    logs_lower = logs.lower()
    
    if "npm" in logs_lower or "node" in logs_lower:
        return "javascript"
    elif "python" in logs_lower or "pip" in logs_lower:
        return "python"
    elif "maven" in logs_lower or "gradle" in logs_lower:
        return "java"
    elif "dotnet" in logs_lower or "msbuild" in logs_lower:
        return "csharp"
    else:
        return "unknown"


def _detect_framework_from_logs(logs: str) -> str:
    """Detect framework from workflow logs.
    
    Args:
        logs: Workflow log text
        
    Returns:
        Detected framework string
    """
    logs_lower = logs.lower()
    
    if "react" in logs_lower:
        return "react"
    elif "vue" in logs_lower:
        return "vue"
    elif "angular" in logs_lower:
        return "angular"
    elif "django" in logs_lower:
        return "django"
    elif "flask" in logs_lower:
        return "flask"
    else:
        return "unknown"


def _detect_build_system_from_logs(logs: str) -> str:
    """Detect build system from workflow logs.
    
    Args:
        logs: Workflow log text
        
    Returns:
        Detected build system string
    """
    logs_lower = logs.lower()
    
    if "npm" in logs_lower:
        return "npm"
    elif "yarn" in logs_lower:
        return "yarn"
    elif "maven" in logs_lower:
        return "maven"
    elif "gradle" in logs_lower:
        return "gradle"
    elif "dotnet" in logs_lower:
        return "dotnet"
    else:
        return "unknown"
