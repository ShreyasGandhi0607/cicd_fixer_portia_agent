"""API response models for the CI/CD Fixer Agent."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall health status", example="healthy")
    timestamp: str = Field(..., description="Check timestamp", example="2025-08-23T10:00:00.000Z")
    services: Dict[str, str] = Field(..., description="Individual service statuses")


class AnalysisResponse(BaseModel):
    """Analysis response model."""
    message: str = Field(..., description="Response message", example="Analysis triggered successfully")
    failure_id: str = Field(..., description="Unique failure ID", example="7")
    owner: str = Field(..., description="Repository owner", example="microsoft")
    repo: str = Field(..., description="Repository name", example="vscode")
    run_id: int = Field(..., description="Workflow run ID", example=17152193292)


class FixResponse(BaseModel):
    """Fix generation response model."""
    fix_id: str = Field(..., description="Unique fix ID")
    suggested_fix: str = Field(..., description="Generated fix suggestion")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation for the fix")
    created_at: datetime = Field(..., description="Fix creation timestamp")


class MLPredictionResponse(BaseModel):
    """ML prediction response model."""
    prediction: str = Field(..., description="Predicted outcome", example="likely_success")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    factors: List[str] = Field(..., description="Factors influencing prediction")
    recommendation: str = Field(..., description="Recommended action")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response model."""
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebhookResponse(BaseModel):
    """Webhook processing response model."""
    processed: bool = Field(..., description="Whether webhook was processed successfully")
    message: str = Field(..., description="Processing result message")
    workflow_run_id: Optional[int] = Field(None, description="Processed workflow run ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Additional response models for the new routes

class FixDetailResponse(BaseModel):
    """Detailed fix response model."""
    fix_id: str = Field(..., description="Unique fix ID")
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    run_id: int = Field(..., description="Workflow run ID")
    suggested_fix: str = Field(..., description="Generated fix suggestion")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation for the fix")
    status: str = Field(..., description="Fix status (pending, approved, rejected)")
    created_at: datetime = Field(..., description="Fix creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    approved_by: Optional[str] = Field(None, description="User who approved/rejected the fix")
    approval_comment: Optional[str] = Field(None, description="Approval/rejection comment")


class FixListResponse(BaseModel):
    """List of fixes response model."""
    fixes: List[FixDetailResponse] = Field(..., description="List of fixes")
    total: int = Field(..., description="Total number of fixes")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of fixes per page")


class FixHistoryResponse(BaseModel):
    """Fix history response model."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    fixes: List[FixDetailResponse] = Field(..., description="List of historical fixes")
    total: int = Field(..., description="Total number of fixes")
    success_rate: float = Field(..., description="Overall fix success rate")


class FixApprovalResponse(BaseModel):
    """Fix approval/rejection response model."""
    fix_id: str = Field(..., description="Fix ID")
    action: str = Field(..., description="Action performed (approve/reject)")
    status: str = Field(..., description="New fix status")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(..., description="Action timestamp")


class FailureDetailResponse(BaseModel):
    """Detailed failure response model."""
    failure_id: str = Field(..., description="Unique failure ID")
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    run_id: int = Field(..., description="Workflow run ID")
    error_log: str = Field(..., description="Error log content")
    error_type: str = Field(..., description="Error classification")
    status: str = Field(..., description="Failure status")
    created_at: datetime = Field(..., description="Failure creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    fix_id: Optional[str] = Field(None, description="Associated fix ID")


class FailureListResponse(BaseModel):
    """List of failures response model."""
    failures: List[FailureDetailResponse] = Field(..., description="List of failures")
    total: int = Field(..., description="Total number of failures")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of failures per page")


class FailureStatisticsResponse(BaseModel):
    """Failure statistics response model."""
    total_failures: int = Field(..., description="Total number of failures")
    resolved_failures: int = Field(..., description="Number of resolved failures")
    pending_failures: int = Field(..., description="Number of pending failures")
    success_rate: float = Field(..., description="Overall resolution success rate")
    average_resolution_time: Optional[float] = Field(None, description="Average time to resolve (hours)")
    top_error_types: List[Dict[str, Any]] = Field(..., description="Most common error types")
    repository_stats: List[Dict[str, Any]] = Field(..., description="Statistics by repository")


class AnalyticsPatternResponse(BaseModel):
    """Pattern analysis response model."""
    patterns: List[Dict[str, Any]] = Field(..., description="Identified failure patterns")
    total_patterns: int = Field(..., description="Total number of patterns")
    time_range: str = Field(..., description="Analysis time range")
    insights: List[str] = Field(..., description="Key insights from pattern analysis")


class AnalyticsEffectivenessResponse(BaseModel):
    """Effectiveness analysis response model."""
    overall_effectiveness: float = Field(..., description="Overall fix effectiveness score")
    fix_type_effectiveness: List[Dict[str, Any]] = Field(..., description="Effectiveness by fix type")
    repository_effectiveness: List[Dict[str, Any]] = Field(..., description="Effectiveness by repository")
    time_trends: List[Dict[str, Any]] = Field(..., description="Effectiveness trends over time")


class RepositoryProfileResponse(BaseModel):
    """Repository profile response model."""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    total_failures: int = Field(..., description="Total number of failures")
    total_fixes: int = Field(..., description="Total number of fixes")
    success_rate: float = Field(..., description="Fix success rate")
    common_error_types: List[Dict[str, Any]] = Field(..., description="Most common error types")
    fix_effectiveness: Dict[str, Any] = Field(..., description="Fix effectiveness metrics")
    ml_insights: Optional[Dict[str, Any]] = Field(None, description="ML-based insights")


class DashboardResponse(BaseModel):
    """Dashboard data response model."""
    summary: Dict[str, Any] = Field(..., description="Overall summary statistics")
    recent_failures: List[FailureDetailResponse] = Field(..., description="Recent failures")
    recent_fixes: List[FixDetailResponse] = Field(..., description="Recent fixes")
    top_repositories: List[Dict[str, Any]] = Field(..., description="Top repositories by activity")
    trends: Dict[str, Any] = Field(..., description="Trend data over time")


class MLSimilarFixesResponse(BaseModel):
    """ML similar fixes response model."""
    similar_fixes: List[Dict[str, Any]] = Field(..., description="List of similar fixes")
    total_found: int = Field(..., description="Total number of similar fixes found")
    similarity_scores: List[float] = Field(..., description="Similarity scores for each fix")
    recommendations: List[str] = Field(..., description="Recommended actions based on similar fixes")


class MLPatternInsightsResponse(BaseModel):
    """ML pattern insights response model."""
    insights: List[Dict[str, Any]] = Field(..., description="ML-generated pattern insights")
    predictions: List[Dict[str, Any]] = Field(..., description="ML predictions for future failures")
    confidence_scores: List[float] = Field(..., description="Confidence scores for predictions")
    recommendations: List[str] = Field(..., description="Recommended preventive actions")


class MLModelPerformanceResponse(BaseModel):
    """ML model performance response model."""
    model_type: str = Field(..., description="Model type analyzed")
    accuracy: float = Field(..., description="Model accuracy score")
    precision: float = Field(..., description="Model precision score")
    recall: float = Field(..., description="Model recall score")
    f1_score: float = Field(..., description="Model F1 score")
    performance_trends: List[Dict[str, Any]] = Field(..., description="Performance trends over time")
    comparison_data: Optional[Dict[str, Any]] = Field(None, description="Comparison with previous periods")


class PortiaAnalysisResponse(BaseModel):
    """Portia analysis response model."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
    status: str = Field(..., description="Analysis status")
    message: str = Field(..., description="Response message")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
    clarifications_needed: Optional[List[Dict[str, Any]]] = Field(None, description="List of clarifications needed")


class PortiaClarificationResponse(BaseModel):
    """Portia clarification response model."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
    clarification_id: str = Field(..., description="Clarification ID")
    status: str = Field(..., description="Clarification status")
    message: str = Field(..., description="Response message")


class PortiaPlanStatusResponse(BaseModel):
    """Portia plan status response model."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
    status: str = Field(..., description="Plan status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    current_step: Optional[str] = Field(None, description="Current step being executed")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results if completed")


class PortiaPendingClarificationsResponse(BaseModel):
    """Portia pending clarifications response model."""
    plan_run_id: str = Field(..., description="Portia plan run ID")
    clarifications: List[Dict[str, Any]] = Field(..., description="List of pending clarifications")
    total_pending: int = Field(..., description="Total number of pending clarifications")


class PortiaToolsResponse(BaseModel):
    """Portia tools response model."""
    available_tools: List[Dict[str, Any]] = Field(..., description="List of available Portia tools")
    total_tools: int = Field(..., description="Total number of available tools")
    tool_categories: List[str] = Field(..., description="Available tool categories")


class PortiaHealthResponse(BaseModel):
    """Portia health response model."""
    status: str = Field(..., description="Portia service status")
    connection: str = Field(..., description="Connection status to Portia")
    available_tools: int = Field(..., description="Number of available tools")
    last_check: datetime = Field(..., description="Last health check timestamp")
