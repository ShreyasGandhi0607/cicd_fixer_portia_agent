"""Analysis endpoints for the CI/CD Fixer Agent."""

import hashlib
from typing import Dict, Any
from cicd_fixer.api.routes.analytics import generate_fix_suggestions
from fastapi import APIRouter, HTTPException, Depends
from ...models.requests import AnalysisRequest, MLPredictionRequest, MLFixGenerationRequest
from ...models.responses import AnalysisResponse, MLPredictionResponse, FixResponse
from ...services.github_service import GitHubService
from ...services.gemini_agent import GeminiFixerAgent
from ...database.repositories import workflow_run_repo, failure_analysis_repo, ml_predictions_repo
from ...core.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)
router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/workflow", response_model=AnalysisResponse)
async def analyze_workflow_failure(request: AnalysisRequest):
    """Analyze a GitHub Actions workflow failure and suggest fixes."""
    logger.info(f"Workflow analysis requested for {request.owner}/{request.repo} run {request.run_id}")
    
    try:
        # Initialize services
        github_service = GitHubService()
        gemini_agent = GeminiFixerAgent()
        
        # Get workflow run information
        workflow_run = github_service.get_workflow_run(request.owner, request.repo, request.run_id)
        if not workflow_run:
            raise HTTPException(status_code=404, detail="Workflow run not found")
        
        # Get workflow logs
        logs = github_service.get_workflow_run_logs(request.owner, request.repo, request.run_id)
        if not logs:
            raise HTTPException(status_code=500, detail="Failed to retrieve workflow logs")
        
        # Create workflow run record in database
        workflow_run_id = workflow_run_repo.create_workflow_run(
            owner=request.owner,
            repo=request.repo,
            run_id=request.run_id,
            workflow_name=workflow_run.get('name'),
            status=workflow_run.get('status'),
            conclusion=workflow_run.get('conclusion')
        )
        
        if not workflow_run_id:
            raise HTTPException(status_code=500, detail="Failed to create workflow run record")
        
        # Analyze failure using Gemini AI
        repo_context = {
            "language": _detect_language(logs),
            "framework": _detect_framework(logs),
            "build_system": _detect_build_system(logs)
        }
        
        analysis_result = gemini_agent.analyze_failure_and_suggest_fix(logs, repo_context)
        
        # Create failure analysis record
        failure_id = failure_analysis_repo.create_failure_analysis(
            workflow_run_id=workflow_run_id,
            error_pattern=analysis_result.get('error_analysis', {}).get('error_type'),
            error_type=analysis_result.get('error_analysis', {}).get('error_type'),
            error_severity=analysis_result.get('error_analysis', {}).get('error_severity'),
            suggested_fix=analysis_result.get('fix_suggestion', {}).get('description'),
            fix_confidence=analysis_result.get('fix_suggestion', {}).get('confidence', 0.0)
        )
        
        if not failure_id:
            raise HTTPException(status_code=500, detail="Failed to create failure analysis record")
        
        # Update workflow run with analysis results
        workflow_run_repo.update_workflow_run(
            request.run_id,
            failure_logs=logs,
            fix_suggestions=analysis_result,
            confidence_score=analysis_result.get('fix_suggestion', {}).get('confidence', 0.0),
            repository_context=repo_context
        )
        
        logger.info(f"Workflow analysis completed successfully. Failure ID: {failure_id}")
        
        return AnalysisResponse(
            message="Analysis completed successfully",
            failure_id=failure_id,
            owner=request.owner,
            repo=request.repo,
            run_id=request.run_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")


@router.post("/ml-prediction", response_model=MLPredictionResponse)
async def predict_fix_success(request: MLPredictionRequest):
    """Predict the success likelihood of a suggested fix using ML."""
    logger.info("ML prediction requested for fix success")
    
    try:
        # Create hash of error log for ML prediction
        error_log_hash = hashlib.sha256(request.error_log.encode()).hexdigest()
        
        # Get existing prediction if available
        existing_prediction = ml_predictions_repo.get_prediction_by_hash(error_log_hash)
        
        if existing_prediction:
            # Use existing prediction
            prediction_data = existing_prediction
        else:
            # Generate new prediction using Gemini AI
            gemini_agent = GeminiFixerAgent()
            
            # Create context for prediction
            context = {
                "error_log": request.error_log,
                "suggested_fix": request.suggested_fix,
                "repo_context": request.repo_context,
                "error_type": request.error_type,
                "language": request.language
            }
            
            # Generate prediction prompt
            prediction_prompt = f"""
            Analyze the following CI/CD failure and suggested fix to predict the likelihood of success:
            
            Error Log: {request.error_log}
            Suggested Fix: {request.suggested_fix}
            Repository Context: {request.repo_context or 'Not provided'}
            Error Type: {request.error_type or 'Unknown'}
            Language: {request.language or 'Unknown'}
            
            Provide your prediction in JSON format:
            {{
                "prediction": "likely_success|likely_failure|uncertain",
                "confidence": 0.85,
                "factors": ["factor1", "factor2"],
                "recommendation": "specific recommendation"
            }}
            """
            
            # Get AI prediction
            ai_response = gemini_agent._analyze_with_gemini(prediction_prompt, {})
            
            prediction_data = {
                "error_log_hash": error_log_hash,
                "error_pattern": request.error_type,
                "predicted_success": 0.8 if "success" in ai_response.get("prediction", "").lower() else 0.2,
                "confidence_score": ai_response.get("confidence", 0.5),
                "factors": ai_response.get("factors", []),
                "recommendation": ai_response.get("recommendation", "Manual review recommended")
            }
            
            # Store prediction in database
            prediction_id = ml_predictions_repo.create_prediction(error_log_hash, **prediction_data)
            if prediction_id:
                prediction_data["id"] = prediction_id
        
        # Convert prediction to response format
        prediction_status = "likely_success" if prediction_data["predicted_success"] > 0.6 else "likely_failure"
        
        return MLPredictionResponse(
            prediction=prediction_status,
            confidence=prediction_data["confidence_score"],
            factors=prediction_data.get("factors", []),
            recommendation=prediction_data.get("recommendation", "Manual review recommended")
        )
        
    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate ML prediction")


@router.post("/generate-fix", response_model=FixResponse)
async def generate_intelligent_fix(request: MLFixGenerationRequest):
    """Generate an intelligent fix using ML and AI analysis."""
    logger.info("Intelligent fix generation requested")
    
    try:
        # Use Gemini AI to generate enhanced fix
        gemini_agent = GeminiFixerAgent()
        
        # Create enhanced context for fix generation
        enhanced_context = {
            "error_log": request.error_log,
            "repo_context": request.repo_context,
            "error_type": request.error_type,
            "language": request.language,
            "previous_successes": _get_previous_successes(request.error_type, request.language)
        }
        
        # Generate fix using AI
        analysis_result = gemini_agent.analyze_failure_and_suggest_fix(
            request.error_log, 
            enhanced_context
        )
        
        # Extract fix information
        fix_suggestion = analysis_result.get('fix_suggestion', {})
        
        # Generate unique fix ID
        import uuid
        fix_id = str(uuid.uuid4())
        
        return FixResponse(
            fix_id=fix_id,
            suggested_fix=fix_suggestion.get('description', 'No fix suggestion available'),
            confidence=fix_suggestion.get('confidence', 0.0),
            reasoning=analysis_result.get('error_analysis', {}).get('root_cause', 'Analysis not available'),
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Intelligent fix generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate intelligent fix")


def _detect_language(logs: str) -> str:
    """Detect the primary language from workflow logs."""
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


def _detect_framework(logs: str) -> str:
    """Detect the framework from workflow logs."""
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


def _detect_build_system(logs: str) -> str:
    """Detect the build system from workflow logs."""
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


def _get_previous_successes(error_type: str, language: str) -> list:
    """Get previous successful fixes for similar errors."""
    # TODO: Implement database query for previous successful fixes
    return []
