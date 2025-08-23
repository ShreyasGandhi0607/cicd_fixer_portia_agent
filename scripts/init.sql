-- Database initialization script for CI/CD Fixer Agent
-- This script runs when the PostgreSQL container starts

-- Create the database if it doesn't exist
SELECT 'CREATE DATABASE cicd_fixer_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cicd_fixer_db')\gexec

-- Connect to the database
\c cicd_fixer_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
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
);

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
);

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
);

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
);

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
);

CREATE TABLE IF NOT EXISTS analytics_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context JSONB,
    tags JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_workflow_runs_run_id ON workflow_runs(run_id);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_owner_repo ON workflow_runs(owner, repo_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_created_at ON workflow_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_failure_analyses_failure_id ON failure_analyses(failure_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_error_hash ON ml_predictions(error_log_hash);
CREATE INDEX IF NOT EXISTS idx_repository_learning_owner_repo ON repository_learning(owner, repo_name);

-- Insert some sample data for testing
INSERT INTO workflow_runs (repo_name, owner, run_id, workflow_name, status, conclusion) 
VALUES ('test-repo', 'test-owner', 12345, 'CI Pipeline', 'completed', 'success')
ON CONFLICT (run_id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log completion
SELECT 'Database initialization completed successfully' as status;
