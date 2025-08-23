"""Portia-specific API routes for the CI/CD Fixer Agent."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from ...models.requests import AnalysisRequest, FixApprovalRequest, ClarificationResponse
from ...models.responses import AnalysisResponse, SuccessResponse, ErrorResponse
from ...services.portia_agent import portia_agent
from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/portia", tags=["portia"])


@router.post("/analyze", response_model=AnalysisResponse)
async def portia_analyze_failure(request: AnalysisRequest):
    """Analyze a CI/CD failure using Portia's structured approach.
    
    This endpoint uses Portia's plan execution to analyze workflow failures
    and generate intelligent fix suggestions.
    """
    logger.info(f"Portia analysis requested for {request.owner}/{request.repo} run {request.run_id}")
    
    try:
        # Use Portia agent for analysis
        result = await portia_agent.analyze_ci_failure(
            owner=request.owner,
            repo=request.repo,
            run_id=request.run_id
        )
        
        if result.get("success"):
            return AnalysisResponse(
                message=result.get("message", "Analysis completed successfully"),
                failure_id=result.get("failure_id", "unknown"),
                owner=request.owner,
                repo=request.repo,
                run_id=request.run_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Portia analysis failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portia analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during Portia analysis")


@router.post("/clarification/respond")
async def handle_clarification(
    plan_run_id: str,
    clarification_id: str,
    response: ClarificationResponse
):
    """Handle human responses to Portia clarifications.
    
    This endpoint allows users to respond to Portia's clarification requests,
    such as approving or rejecting suggested fixes.
    """
    logger.info(f"Handling clarification {clarification_id} for plan run {plan_run_id}")
    
    try:
        result = await portia_agent.handle_clarification(
            plan_run_id=plan_run_id,
            clarification_id=clarification_id,
            response=response.response
        )
        
        if result.get("success"):
            return SuccessResponse(
                message=result.get("message", "Clarification handled successfully"),
                data={
                    "plan_run_id": plan_run_id,
                    "clarification_id": clarification_id,
                    "plan_state": result.get("plan_state"),
                    "final_output": result.get("final_output")
                }
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to handle clarification")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to handle clarification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fix/apply")
async def apply_approved_fix(workflow_run_id: int):
    """Apply an approved fix using Portia's plan execution.
    
    This endpoint creates a Portia plan to apply the approved fix,
    which may include creating GitHub issues or pull requests.
    """
    logger.info(f"Applying approved fix for workflow run {workflow_run_id}")
    
    try:
        result = await portia_agent.approve_and_apply_fix(workflow_run_id)
        
        if result.get("success"):
            return SuccessResponse(
                message=result.get("message", "Fix applied successfully"),
                data={
                    "plan_id": result.get("plan_id"),
                    "plan_run_id": result.get("plan_run_id"),
                    "state": result.get("state"),
                    "final_output": result.get("final_output")
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to apply fix")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply fix: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/plan/{plan_run_id}/status")
async def get_plan_status(plan_run_id: str):
    """Get the current status of a Portia plan run.
    
    This endpoint provides detailed information about the execution
    status of a Portia plan, including any pending clarifications.
    """
    logger.info(f"Getting status for plan run {plan_run_id}")
    
    try:
        result = await portia_agent.get_plan_run_status(plan_run_id)
        
        if result.get("success"):
            return SuccessResponse(
                message=result.get("message", "Plan status retrieved successfully"),
                data={
                    "plan_run_id": plan_run_id,
                    "state": result.get("state"),
                    "current_step": result.get("current_step"),
                    "clarifications": result.get("clarifications"),
                    "outputs": result.get("outputs"),
                    "final_output": result.get("final_output")
                }
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=result.get("error", "Plan run not found")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get plan status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clarifications/pending")
async def list_pending_clarifications():
    """List all pending clarifications that require human input.
    
    This endpoint shows all Portia clarifications that are waiting
    for human responses, such as fix approvals or rejections.
    """
    logger.info("Listing pending clarifications")
    
    try:
        result = await portia_agent.list_pending_clarifications()
        
        if result.get("success"):
            return SuccessResponse(
                message=result.get("message", "Pending clarifications retrieved successfully"),
                data={
                    "pending_clarifications": result.get("pending_clarifications"),
                    "count": result.get("count")
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to list clarifications")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list clarifications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/test")
async def test_portia_connection():
    """Test Portia agent connection and configuration.
    
    This endpoint verifies that the Portia agent is properly configured
    and can execute basic operations.
    """
    logger.info("Testing Portia connection")
    
    try:
        is_connected = portia_agent.test_portia_connection()
        
        if is_connected:
            return SuccessResponse(
                message="Portia connection test successful",
                data={
                    "status": "connected",
                    "agent_type": "CICDFixerPortiaAgent",
                    "tools_registered": len(portia_agent.tool_registry.tools) if hasattr(portia_agent, 'tool_registry') else 0
                }
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="Portia connection test failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portia connection test failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/tools")
async def list_available_tools():
    """List all available Portia tools for CI/CD operations.
    
    This endpoint shows all the tools that have been registered
    with the Portia agent for CI/CD failure analysis and fix generation.
    """
    logger.info("Listing available Portia tools")
    
    try:
        if hasattr(portia_agent, 'tool_registry') and hasattr(portia_agent.tool_registry, 'tools'):
            tools = []
            for tool in portia_agent.tool_registry.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
            
            return SuccessResponse(
                message=f"Found {len(tools)} available tools",
                data={
                    "tools": tools,
                    "total_count": len(tools)
                }
            )
        else:
            return SuccessResponse(
                message="No tools registry available",
                data={
                    "tools": [],
                    "total_count": 0
                }
            )
            
    except Exception as e:
        logger.error(f"Failed to list tools: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
