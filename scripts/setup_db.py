#!/usr/bin/env python3
"""Database setup script for the CI/CD Fixer Agent."""

import os
import sys
import psycopg2
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cicd_fixer.core.config import get_settings
from cicd_fixer.core.logging import get_logger

logger = get_logger(__name__)


def create_database():
    """Create the database and required tables."""
    try:
        settings = get_settings()
        
        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=settings.database_host,
            port=settings.database_port,
            user=settings.database_user,
            password=settings.database_password,
            database='postgres'  # Connect to default postgres database
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.database_name,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database: {settings.database_name}")
            cursor.execute(f"CREATE DATABASE {settings.database_name}")
            logger.info("Database created successfully")
        else:
            logger.info(f"Database {settings.database_name} already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to the specific database and create tables
        create_tables()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        sys.exit(1)


def create_tables():
    """Create the required database tables."""
    try:
        settings = get_settings()
        
        # Connect to the specific database
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        # Create workflow_runs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id SERIAL PRIMARY KEY,
                repo_name VARCHAR(255) NOT NULL,
                owner VARCHAR(255) NOT NULL,
                run_id BIGINT NOT NULL UNIQUE,
                workflow_name VARCHAR(255),
                status VARCHAR(50),
                conclusion VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                failure_logs TEXT,
                fix_suggestions JSONB,
                fix_status VARCHAR(50) DEFAULT 'pending',
                confidence_score FLOAT,
                ml_prediction VARCHAR(100),
                repository_context JSONB
            )
        """)
        
        # Create failure_analyses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_analyses (
                id SERIAL PRIMARY KEY,
                failure_id VARCHAR(100) UNIQUE NOT NULL,
                workflow_run_id INTEGER NOT NULL,
                error_pattern VARCHAR(500),
                error_type VARCHAR(100),
                error_severity VARCHAR(50),
                suggested_fix TEXT,
                fix_confidence FLOAT,
                fix_approved BOOLEAN DEFAULT FALSE,
                fix_rejected BOOLEAN DEFAULT FALSE,
                fix_implemented BOOLEAN DEFAULT FALSE,
                analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ml_insights JSONB,
                user_feedback TEXT,
                FOREIGN KEY (workflow_run_id) REFERENCES workflow_runs(id)
            )
        """)
        
        # Create fix_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fix_history (
                id SERIAL PRIMARY KEY,
                failure_analysis_id INTEGER NOT NULL,
                fix_description TEXT NOT NULL,
                fix_implementation TEXT,
                fix_effectiveness FLOAT,
                implementation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                implemented_by VARCHAR(255),
                notes TEXT,
                FOREIGN KEY (failure_analysis_id) REFERENCES failure_analyses(id)
            )
        """)
        
        # Create ml_predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id SERIAL PRIMARY KEY,
                error_log_hash VARCHAR(64) UNIQUE NOT NULL,
                error_pattern VARCHAR(500),
                predicted_success FLOAT,
                confidence_score FLOAT,
                factors JSONB,
                prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actual_outcome VARCHAR(50),
                feedback_score FLOAT
            )
        """)
        
        # Create repository_learning table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repository_learning (
                id SERIAL PRIMARY KEY,
                owner VARCHAR(255) NOT NULL,
                repo_name VARCHAR(255) NOT NULL,
                language VARCHAR(100),
                framework VARCHAR(100),
                common_patterns JSONB,
                successful_fixes JSONB,
                failure_patterns JSONB,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                learning_score FLOAT DEFAULT 0.0
            )
        """)
        
        # Create analytics_metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_metrics (
                id SERIAL PRIMARY KEY,
                metric_name VARCHAR(255) NOT NULL,
                metric_value FLOAT NOT NULL,
                metric_unit VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context JSONB,
                tags JSONB
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_runs_run_id ON workflow_runs(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_runs_owner_repo ON workflow_runs(owner, repo_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_runs_created_at ON workflow_runs(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_failure_analyses_failure_id ON failure_analyses(failure_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ml_predictions_error_hash ON ml_predictions(error_log_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repository_learning_owner_repo ON repository_learning(owner, repo_name)")
        
        conn.commit()
        logger.info("Database tables created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)


def main():
    """Main function to run database setup."""
    logger.info("Starting database setup...")
    
    try:
        create_database()
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
