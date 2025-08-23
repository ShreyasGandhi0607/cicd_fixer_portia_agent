"""API request models for the CI/CD Fixer Agent."""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request model for workflow analysis."""
    owner: str = Field(..., description="GitHub repository owner/organization", example="microsoft")
    repo: str = Field(..., description="Repository name", example="vscode") 
    run_id: int = Field(..., description="GitHub Actions workflow run ID", example=17152193292)


class PortiaAnalysisRequest(BaseModel):
    """Request model for Portia-powered analysis."""
    owner: str = Field(..., description="GitHub repository owner/organization", example="microsoft")
    repo: str = Field(..., description="Repository name", example="vscode")
    run_id: int = Field(..., description="GitHub Actions workflow run ID", example=17152193292)


class FixApprovalRequest(BaseModel):
    """Request model for fix approval/rejection."""
    action: Literal["approve", "reject"] = Field(..., description="Action to perform", example="approve")
    comment: Optional[str] = Field(None, description="Optional comment for the action", example="Fix looks good, proceed")


class ClarificationResponse(BaseModel):
    """Request model for clarification responses."""
    response: str = Field(..., description="Response to the clarification", example="yes")


class MLPredictionRequest(BaseModel):
    """Request model for ML-based success prediction."""
    error_log: str = Field(..., description="Error log content", example="npm install failed with ENOENT error")
    suggested_fix: str = Field(..., description="Proposed fix solution", example="Run npm install --legacy-peer-deps")
    repo_context: Optional[str] = Field(None, description="Repository context", example="Node.js application with package.json")
    error_type: Optional[str] = Field(None, description="Error classification", example="dependency_error")
    language: Optional[str] = Field(None, description="Primary language", example="javascript")


class MLFixGenerationRequest(BaseModel):
    """Request model for enhanced fix generation."""
    error_log: str = Field(..., description="Error log content", example="TypeError: Cannot read property of undefined")
    repo_context: Optional[str] = Field(None, description="Repository context", example="React TypeScript application")
    error_type: Optional[str] = Field(None, description="Error classification", example="test_failure")
    language: Optional[str] = Field(None, description="Primary language", example="typescript")


class MLFeedbackRequest(BaseModel):
    """Request model for ML feedback learning."""
    error_log: str = Field(..., description="Original error log", example="npm install failed")
    suggested_fix: str = Field(..., description="Fix that was applied", example="Clear npm cache and reinstall")
    fix_status: Literal["approved", "rejected", "pending"] = Field(..., description="Fix outcome", example="approved")
    repo_context: Optional[str] = Field(None, description="Repository context", example="Node.js project")
    user_feedback: Optional[str] = Field(None, description="User feedback", example="Fix worked perfectly")
    fix_effectiveness: Optional[float] = Field(None, description="Effectiveness rating (0-1)", example=0.9)


class FixSuggestionsRequest(BaseModel):
    """Request model for fix suggestions."""
    error_logs: List[str] = Field(..., description="Array of error log lines")
    repo_context: Optional[str] = Field(None, description="Optional repo context")
    owner: Optional[str] = Field(None, description="GitHub owner (optional)")
    repo: Optional[str] = Field(None, description="GitHub repo (optional)")


class WebhookPayload(BaseModel):
    """GitHub webhook payload model."""
    action: Optional[str] = Field(None, description="Webhook action")
    workflow_run: Optional[dict] = Field(None, description="Workflow run data")
    repository: Optional[dict] = Field(None, description="Repository information")
    sender: Optional[dict] = Field(None, description="Sender information")
