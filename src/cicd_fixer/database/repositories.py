"""Database repository layer for the CI/CD Fixer Agent."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from .connection import get_db_connection
from .models import (
    WorkflowRun, FailureAnalysis, FixHistory, MLPredictions,
    RepositoryLearning, AnalyticsMetrics
)
from ..core.logging import get_logger

logger = get_logger(__name__)


class WorkflowRunRepository:
    """Repository for workflow run operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create_workflow_run(self, owner: str, repo: str, run_id: int, **kwargs) -> Optional[int]:
        """Create a new workflow run record.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: GitHub Actions run ID
            **kwargs: Additional workflow run data
            
        Returns:
            Created workflow run ID or None if failed
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = """
                    INSERT INTO workflow_runs (owner, repo_name, run_id, workflow_name, status, conclusion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                cursor.execute(query, (
                    owner, repo, run_id,
                    kwargs.get('workflow_name'),
                    kwargs.get('status'),
                    kwargs.get('conclusion')
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    logger.info(f"Created workflow run {result['id']} for {owner}/{repo}")
                    return result['id']
                    
        except Exception as e:
            logger.error(f"Failed to create workflow run: {e}")
            return None
    
    def get_workflow_run(self, run_id: int) -> Optional[Dict[str, Any]]:
        """Get workflow run by GitHub run ID.
        
        Args:
            run_id: GitHub Actions run ID
            
        Returns:
            Workflow run data or None if not found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = "SELECT * FROM workflow_runs WHERE run_id = %s"
                cursor.execute(query, (run_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Failed to get workflow run {run_id}: {e}")
            return None
    
    def update_workflow_run(self, run_id: int, **kwargs) -> bool:
        """Update workflow run data.
        
        Args:
            run_id: GitHub Actions run ID
            **kwargs: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    if hasattr(WorkflowRun, key):
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                set_clauses.append("updated_at = %s")
                values.append(datetime.utcnow())
                values.append(run_id)
                
                query = f"""
                    UPDATE workflow_runs 
                    SET {', '.join(set_clauses)}
                    WHERE run_id = %s
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"Updated workflow run {run_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update workflow run {run_id}: {e}")
            return False


class FailureAnalysisRepository:
    """Repository for failure analysis operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create_failure_analysis(self, workflow_run_id: int, **kwargs) -> Optional[str]:
        """Create a new failure analysis record.
        
        Args:
            workflow_run_id: Associated workflow run ID
            **kwargs: Failure analysis data
            
        Returns:
            Failure ID or None if failed
        """
        try:
            failure_id = str(uuid.uuid4())
            
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = """
                    INSERT INTO failure_analyses (
                        failure_id, workflow_run_id, error_pattern, error_type,
                        error_severity, suggested_fix, fix_confidence
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    failure_id, workflow_run_id,
                    kwargs.get('error_pattern'),
                    kwargs.get('error_type'),
                    kwargs.get('error_severity'),
                    kwargs.get('suggested_fix'),
                    kwargs.get('fix_confidence', 0.0)
                ))
                
                conn.commit()
                logger.info(f"Created failure analysis {failure_id}")
                return failure_id
                
        except Exception as e:
            logger.error(f"Failed to create failure analysis: {e}")
            return None
    
    def get_failure_analysis(self, failure_id: str) -> Optional[Dict[str, Any]]:
        """Get failure analysis by ID.
        
        Args:
            failure_id: Failure analysis ID
            
        Returns:
            Failure analysis data or None if not found
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = "SELECT * FROM failure_analyses WHERE failure_id = %s"
                cursor.execute(query, (failure_id,))
                
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Failed to get failure analysis {failure_id}: {e}")
            return None
    
    def update_fix_status(self, failure_id: str, status: str, **kwargs) -> bool:
        """Update fix status for a failure analysis.
        
        Args:
            failure_id: Failure analysis ID
            status: New fix status
            **kwargs: Additional fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                # Map status to boolean fields
                status_updates = {
                    'approved': {'fix_approved': True, 'fix_rejected': False},
                    'rejected': {'fix_approved': False, 'fix_rejected': True},
                    'implemented': {'fix_implemented': True}
                }
                
                updates = status_updates.get(status, {})
                updates.update(kwargs)
                
                if not updates:
                    return False
                
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
                
                values.append(failure_id)
                
                query = f"""
                    UPDATE failure_analyses 
                    SET {', '.join(set_clauses)}
                    WHERE failure_id = %s
                """
                
                cursor.execute(query, values)
                conn.commit()
                
                logger.info(f"Updated fix status for {failure_id} to {status}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update fix status for {failure_id}: {e}")
            return False


class MLPredictionsRepository:
    """Repository for ML prediction operations."""
    
    def __init__(self):
        self.db = get_db_connection()
    
    def create_prediction(self, error_log_hash: str, **kwargs) -> Optional[int]:
        """Create a new ML prediction record.
        
        Args:
            error_log_hash: Hash of the error log
            **kwargs: Prediction data
            
        Returns:
            Prediction ID or None if failed
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = """
                    INSERT INTO ml_predictions (
                        error_log_hash, error_pattern, predicted_success,
                        confidence_score, factors
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """
                
                cursor.execute(query, (
                    error_log_hash,
                    kwargs.get('error_pattern'),
                    kwargs.get('predicted_success', 0.0),
                    kwargs.get('confidence_score', 0.0),
                    kwargs.get('factors', {})
                ))
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    logger.info(f"Created ML prediction {result['id']}")
                    return result['id']
                    
        except Exception as e:
            logger.error(f"Failed to create ML prediction: {e}")
            return None
    
    def update_prediction_outcome(self, prediction_id: int, outcome: str, feedback_score: float = None) -> bool:
        """Update ML prediction with actual outcome.
        
        Args:
            prediction_id: Prediction ID
            outcome: Actual outcome
            feedback_score: Optional feedback score
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = self.db.get_cursor(conn)
                
                query = """
                    UPDATE ml_predictions 
                    SET actual_outcome = %s, feedback_score = %s
                    WHERE id = %s
                """
                
                cursor.execute(query, (outcome, feedback_score, prediction_id))
                conn.commit()
                
                logger.info(f"Updated prediction {prediction_id} outcome to {outcome}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update prediction {prediction_id}: {e}")
            return False


# Repository instances
workflow_run_repo = WorkflowRunRepository()
failure_analysis_repo = FailureAnalysisRepository()
ml_predictions_repo = MLPredictionsRepository()
