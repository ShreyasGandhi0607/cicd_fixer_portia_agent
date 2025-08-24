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
    sender: Optional[str] = Field(None, description="Sender information")


# Additional request models for the new routes

class FixHistoryRequest(BaseModel):
    """Request model for fix history."""
    owner: str = Field(..., description="GitHub repository owner/organization")
    repo: str = Field(..., description="Repository name")
    limit: Optional[int] = Field(100, description="Maximum number of fixes to return")
    status: Optional[str] = Field(None, description="Filter by fix status")


class FailureListRequest(BaseModel):
    """Request model for failure listing."""
    owner: Optional[str] = Field(None, description="Filter by repository owner")
    repo: Optional[str] = Field(None, description="Filter by repository name")
    status: Optional[str] = Field(None, description="Filter by failure status")
    limit: Optional[int] = Field(100, description="Maximum number of failures to return")
    offset: Optional[int] = Field(0, description="Number of failures to skip")


class AnalyticsPatternRequest(BaseModel):
    """Request model for pattern analysis."""
    owner: Optional[str] = Field(None, description="Repository owner for specific analysis")
    repo: Optional[str] = Field(None, description="Repository name for specific analysis")
    time_range: Optional[str] = Field("30d", description="Time range for analysis (e.g., 7d, 30d, 90d)")
    error_type: Optional[str] = Field(None, description="Filter by error type")


class AnalyticsEffectivenessRequest(BaseModel):
    """Request model for effectiveness analysis."""
    owner: Optional[str] = Field(None, description="Repository owner")
    repo: Optional[str] = Field(None, description="Repository name")
    time_range: Optional[str] = Field("30d", description="Time range for analysis")
    fix_type: Optional[str] = Field(None, description="Filter by fix type")


class RepositoryProfileRequest(BaseModel):
    """Request model for repository profile analysis."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    include_ml: Optional[bool] = Field(True, description="Include ML-based insights")


class DashboardRequest(BaseModel):
    """Request model for dashboard data."""
    time_range: Optional[str] = Field("30d", description="Time range for dashboard data")
    owner: Optional[str] = Field(None, description="Filter by repository owner")
    repo: Optional[str] = Field(None, description="Filter by repository name")


class MLSimilarFixesRequest(BaseModel):
    """Request model for ML similar fixes search."""
    error_log: str = Field(..., description="Error log to find similar fixes for")
    owner: Optional[str] = Field(None, description="Repository owner")
    repo: Optional[str] = Field(None, description="Repository name")
    limit: Optional[int] = Field(10, description="Maximum number of similar fixes to return")


class MLPredictSuccessRequest(BaseModel):
    """Request model for ML success prediction."""
    error_log: str = Field(..., description="Error log content")
    suggested_fix: str = Field(..., description="Proposed fix solution")
    repo_context: Optional[str] = Field(None, description="Repository context")
    error_type: Optional[str] = Field(None, description="Error classification")


class MLGenerateFixRequest(BaseModel):
    """Request model for ML-enhanced fix generation."""
    error_log: str = Field(..., description="Error log content")
    repo_context: Optional[str] = Field(None, description="Repository context")
    error_type: Optional[str] = Field(None, description="Error classification")
    language: Optional[str] = Field(None, description="Primary language")


class MLFeedbackLearningRequest(BaseModel):
    """Request model for ML feedback learning."""
    error_log: str = Field(..., description="Original error log")
    suggested_fix: str = Field(..., description="Fix that was applied")
    fix_status: Literal["approved", "rejected", "pending"] = Field(..., description="Fix outcome")
    repo_context: Optional[str] = Field(None, description="Repository context")
    user_feedback: Optional[str] = Field(None, description="User feedback")
    fix_effectiveness: Optional[float] = Field(None, description="Effectiveness rating (0-1)")


class MLPatternInsightsRequest(BaseModel):
    """Request model for ML pattern insights."""
    owner: Optional[str] = Field(None, description="Repository owner")
    repo: Optional[str] = Field(None, description="Repository name")
    time_range: Optional[str] = Field("90d", description="Time range for analysis")
    include_predictions: Optional[bool] = Field(True, description="Include ML predictions")


class MLModelPerformanceRequest(BaseModel):
    """Request model for ML model performance metrics."""
    model_type: Optional[str] = Field(None, description="Specific model type to analyze")
    time_range: Optional[str] = Field("30d", description="Time range for performance analysis")
    include_comparison: Optional[bool] = Field(True, description="Include comparison with previous periods")


class MLFixSuggestionsRequest(BaseModel):
    """Request model for ML fix suggestions."""
    error_logs: List[str] = Field(..., description="Array of error log lines")
    repo_context: Optional[str] = Field(None, description="Repository context")
    owner: Optional[str] = Field(None, description="GitHub owner")
    repo: Optional[str] = Field(None, description="GitHub repo")
    include_confidence: Optional[bool] = Field(True, description="Include confidence scores")


class PortiaClarificationRequest(BaseModel):
    """Request model for Portia clarification responses."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
    clarification_id: str = Field(..., description="Clarification ID")
    response: str = Field(..., description="Response to the clarification")


class PortiaFixApprovalRequest(BaseModel):
    """Request model for Portia fix approval/rejection."""
    fix_id: str = Field(..., description="Fix ID to approve/reject")
    action: Literal["approve", "reject"] = Field(..., description="Action to perform")
    comment: Optional[str] = Field(None, description="Optional comment for the action")


class PortiaPlanStatusRequest(BaseModel):
    """Request model for Portia plan status."""
    plan_run_id: str = Field(..., description="Portia plan run ID")


class PortiaPendingClarificationsRequest(BaseModel):
    """Request model for Portia pending clarifications."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
