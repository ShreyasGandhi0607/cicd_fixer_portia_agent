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
