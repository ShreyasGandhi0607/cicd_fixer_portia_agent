"""Database models and schemas for the CI/CD Fixer Agent."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class WorkflowRun(Base):
    """Model for GitHub Actions workflow runs."""
    
    __tablename__ = "workflow_runs"
    
    id = Column(Integer, primary_key=True)
    repo_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    run_id = Column(BigInteger, nullable=False, unique=True)
    workflow_name = Column(String(255))
    status = Column(String(50))
    conclusion = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    failure_logs = Column(Text)
    fix_suggestions = Column(JSON)
    fix_status = Column(String(50), default="pending")
    confidence_score = Column(Float)
    ml_prediction = Column(String(100))
    repository_context = Column(JSON)


class FailureAnalysis(Base):
    """Model for failure analysis records."""
    
    __tablename__ = "failure_analyses"
    
    id = Column(Integer, primary_key=True)
    failure_id = Column(String(100), unique=True, nullable=False)
    workflow_run_id = Column(Integer, nullable=False)
    error_pattern = Column(String(500))
    error_type = Column(String(100))
    error_severity = Column(String(50))
    suggested_fix = Column(Text)
    fix_confidence = Column(Float)
    fix_approved = Column(Boolean, default=False)
    fix_rejected = Column(Boolean, default=False)
    fix_implemented = Column(Boolean, default=False)
    analysis_timestamp = Column(DateTime, default=func.now())
    ml_insights = Column(JSON)
    user_feedback = Column(Text)


class FixHistory(Base):
    """Model for fix implementation history."""
    
    __tablename__ = "fix_history"
    
    id = Column(Integer, primary_key=True)
    failure_analysis_id = Column(Integer, nullable=False)
    fix_description = Column(Text, nullable=False)
    fix_implementation = Column(Text)
    fix_effectiveness = Column(Float)
    implementation_timestamp = Column(DateTime, default=func.now())
    implemented_by = Column(String(255))
    notes = Column(Text)


class MLPredictions(Base):
    """Model for ML prediction records."""
    
    __tablename__ = "ml_predictions"
    
    id = Column(Integer, primary_key=True)
    error_log_hash = Column(String(64), unique=True, nullable=False)
    error_pattern = Column(String(500))
    predicted_success = Column(Float)
    confidence_score = Column(Float)
    factors = Column(JSON)
    prediction_timestamp = Column(DateTime, default=func.now())
    actual_outcome = Column(String(50))
    feedback_score = Column(Float)


class RepositoryLearning(Base):
    """Model for repository-specific learning data."""
    
    __tablename__ = "repository_learning"
    
    id = Column(Integer, primary_key=True)
    owner = Column(String(255), nullable=False)
    repo_name = Column(String(255), nullable=False)
    language = Column(String(100))
    framework = Column(String(100))
    common_patterns = Column(JSON)
    successful_fixes = Column(JSON)
    failure_patterns = Column(JSON)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    learning_score = Column(Float, default=0.0)


class AnalyticsMetrics(Base):
    """Model for analytics and metrics."""
    
    __tablename__ = "analytics_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    timestamp = Column(DateTime, default=func.now())
    context = Column(JSON)
    tags = Column(JSON)


# Pydantic models for API responses
class WorkflowRunResponse:
    """Response model for workflow run data."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.repo_name = data.get('repo_name')
        self.owner = data.get('owner')
        self.run_id = data.get('run_id')
        self.workflow_name = data.get('workflow_name')
        self.status = data.get('status')
        self.conclusion = data.get('conclusion')
        self.created_at = data.get('created_at')
        self.failure_logs = data.get('failure_logs')
        self.fix_suggestions = data.get('fix_suggestions')
        self.fix_status = data.get('fix_status')
        self.confidence_score = data.get('confidence_score')
        self.ml_prediction = data.get('ml_prediction')


class FailureAnalysisResponse:
    """Response model for failure analysis data."""
    
    def __init__(self, data: Dict[str, Any]):
        self.failure_id = data.get('failure_id')
        self.workflow_run_id = data.get('workflow_run_id')
        self.error_pattern = data.get('error_pattern')
        self.error_type = data.get('error_type')
        self.error_severity = data.get('error_severity')
        self.suggested_fix = data.get('suggested_fix')
        self.fix_confidence = data.get('fix_confidence')
        self.fix_approved = data.get('fix_approved')
        self.fix_rejected = data.get('fix_rejected')
        self.fix_implemented = data.get('fix_implemented')
        self.analysis_timestamp = data.get('analysis_timestamp')
        self.ml_insights = data.get('ml_insights')
        self.user_feedback = data.get('user_feedback')
