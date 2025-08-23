"""Portia tools registry for CI/CD operations."""

from typing import Dict, Any, List, Optional
from portia import Tool, ToolRegistry
from ..core.logging import get_logger

logger = get_logger(__name__)


class CustomTool(Tool):
    """Custom Tool implementation that satisfies Portia's requirements."""
    
    def __init__(self, name: str, description: str, function, parameters: Dict[str, Any]):
        super().__init__(name=name, description=description, function=function, parameters=parameters)
    
    def run(self, **kwargs):
        """Run the tool with the given parameters."""
        return self.function(**kwargs)


def create_ci_cd_tool_registry() -> ToolRegistry:
    """Create and register all CI/CD tools for Portia.
    
    Returns:
        ToolRegistry with all CI/CD tools
    """
    registry = ToolRegistry()
    
    # Create a list of tools
    tools = [
        analyze_workflow_failure_tool(),
        fetch_workflow_logs_tool(),
        generate_fix_suggestion_tool(),
        create_github_issue_tool(),
        update_database_tool(),
        classify_error_type_tool(),
        assess_fix_confidence_tool(),
        validate_fix_suggestion_tool()
    ]
    
    # Try different registration methods based on Portia SDK version
    try:
        # Method 1: Try register_tool
        for tool in tools:
            registry.register_tool(tool)
        logger.info(f"Registered {len(tools)} CI/CD tools with Portia using register_tool")
    except AttributeError:
        try:
            # Method 2: Try add_tool
            for tool in tools:
                registry.add_tool(tool)
            logger.info(f"Registered {len(tools)} CI/CD tools with Portia using add_tool")
        except AttributeError:
            try:
                # Method 3: Try tools property assignment
                registry.tools = tools
                logger.info(f"Registered {len(tools)} CI/CD tools with Portia using direct assignment")
            except AttributeError:
                # Method 4: Create a simple mock registry
                logger.warning("Could not register tools with Portia SDK, using mock registry")
                registry.tools = tools
                registry.get_tool = lambda name: next((t for t in tools if t.name == name), None)
    
    return registry


def analyze_workflow_failure_tool() -> Tool:
    """Tool for analyzing CI/CD workflow failures."""
    
    def analyze_failure(workflow_data: Dict[str, Any], error_logs: str) -> Dict[str, Any]:
        """Analyze a CI/CD workflow failure.
        
        Args:
            workflow_data: Workflow run information
            error_logs: Error logs from the failed run
            
        Returns:
            Analysis result with error classification and fix suggestions
        """
        try:
            # Basic error pattern analysis
            error_logs_lower = error_logs.lower()
            
            # Common CI/CD failure patterns
            if "npm install" in error_logs_lower or "package.json" in error_logs_lower:
                error_type = "dependency_error"
                severity = "medium"
                common_fixes = [
                    "Check package.json for syntax errors",
                    "Clear npm cache and reinstall",
                    "Update Node.js version if outdated"
                ]
            elif "test" in error_logs_lower and "fail" in error_logs_lower:
                error_type = "test_failure"
                severity = "high"
                common_fixes = [
                    "Review test failures in detail",
                    "Check test environment configuration",
                    "Verify test dependencies are installed"
                ]
            elif "build" in error_logs_lower and "fail" in error_logs_lower:
                error_type = "build_error"
                severity = "high"
                common_fixes = [
                    "Check build configuration",
                    "Verify all dependencies are available",
                    "Review build tool version compatibility"
                ]
            elif "permission" in error_logs_lower or "access" in error_logs_lower:
                error_type = "permission_error"
                severity = "critical"
                common_fixes = [
                    "Check GitHub token permissions",
                    "Verify repository access rights",
                    "Review workflow file permissions"
                ]
            else:
                error_type = "unknown_error"
                severity = "medium"
                common_fixes = [
                    "Review error logs manually",
                    "Check recent code changes",
                    "Consult team members or documentation"
                ]
            
            return {
                "error_type": error_type,
                "severity": severity,
                "common_fixes": common_fixes,
                "workflow_name": workflow_data.get("name", "Unknown"),
                "repository": f"{workflow_data.get('repository', {}).get('full_name', 'Unknown')}",
                "run_id": workflow_data.get("id", "Unknown"),
                "analysis_timestamp": "2025-08-23T10:00:00.000Z"
            }
            
        except Exception as e:
            logger.error(f"Error in workflow failure analysis: {e}")
            return {
                "error_type": "analysis_error",
                "severity": "unknown",
                "common_fixes": ["Manual investigation required"],
                "error": str(e)
            }
    
    return CustomTool(
        name="analyze_workflow_failure",
        description="Analyze CI/CD workflow failures and classify error types",
        function=analyze_failure,
        parameters={
            "workflow_data": {
                "type": "object",
                "description": "Workflow run information from GitHub API"
            },
            "error_logs": {
                "type": "string",
                "description": "Error logs from the failed workflow run"
            }
        }
    )


def fetch_workflow_logs_tool() -> Tool:
    """Tool for fetching workflow logs."""
    
    def fetch_logs(owner: str, repo: str, run_id: int) -> str:
        """Fetch workflow logs from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            run_id: Workflow run ID
            
        Returns:
            Workflow logs as string
        """
        try:
            # This would integrate with GitHubService
            # For now, return a placeholder
            return f"Workflow logs for {owner}/{repo} run {run_id} would be fetched here"
            
        except Exception as e:
            logger.error(f"Error fetching workflow logs: {e}")
            return f"Error fetching logs: {str(e)}"
    
    return CustomTool(
        name="fetch_workflow_logs",
        description="Fetch workflow logs from GitHub Actions",
        function=fetch_logs,
        parameters={
            "owner": {
                "type": "string",
                "description": "Repository owner"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "run_id": {
                "type": "integer",
                "description": "Workflow run ID"
            }
        }
    )


def generate_fix_suggestion_tool() -> Tool:
    """Tool for generating fix suggestions."""
    
    def generate_fix(error_type: str, error_logs: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fix suggestions based on error type and context.
        
        Args:
            error_type: Type of error that occurred
            error_logs: Error logs for context
            context: Additional context information
            
        Returns:
            Fix suggestion with steps and confidence
        """
        try:
            # Generate fix based on error type
            if error_type == "dependency_error":
                fix = {
                    "description": "Fix dependency installation issues",
                    "steps": [
                        "Clear package manager cache",
                        "Delete node_modules and package-lock.json",
                        "Run npm install with --legacy-peer-deps flag",
                        "Verify package.json syntax"
                    ],
                    "commands": [
                        "npm cache clean --force",
                        "rm -rf node_modules package-lock.json",
                        "npm install --legacy-peer-deps"
                    ],
                    "confidence": 0.85,
                    "estimated_time": "5-10 minutes"
                }
            elif error_type == "test_failure":
                fix = {
                    "description": "Resolve test failures",
                    "steps": [
                        "Review test output for specific failures",
                        "Check test environment configuration",
                        "Verify test dependencies are installed",
                        "Run tests in isolation to identify issues"
                    ],
                    "commands": [
                        "npm test -- --verbose",
                        "npm test -- --testNamePattern='specific_test_name'"
                    ],
                    "confidence": 0.75,
                    "estimated_time": "15-30 minutes"
                }
            elif error_type == "build_error":
                fix = {
                    "description": "Fix build configuration issues",
                    "steps": [
                        "Check build tool version compatibility",
                        "Verify all required dependencies",
                        "Review build configuration files",
                        "Check for syntax errors in source code"
                    ],
                    "commands": [
                        "node --version",
                        "npm --version",
                        "npm run build --verbose"
                    ],
                    "confidence": 0.80,
                    "estimated_time": "10-20 minutes"
                }
            else:
                fix = {
                    "description": "General troubleshooting required",
                    "steps": [
                        "Review error logs carefully",
                        "Check recent code changes",
                        "Verify environment configuration",
                        "Consult team documentation"
                    ],
                    "commands": [],
                    "confidence": 0.50,
                    "estimated_time": "30-60 minutes"
                }
            
            # Add context-specific information
            fix["context"] = context
            fix["generated_at"] = "2025-08-23T10:00:00.000Z"
            
            return fix
            
        except Exception as e:
            logger.error(f"Error generating fix suggestion: {e}")
            return {
                "description": "Error occurred while generating fix",
                "steps": ["Manual investigation required"],
                "commands": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    return CustomTool(
        name="generate_fix_suggestion",
        description="Generate fix suggestions for CI/CD failures",
        function=generate_fix,
        parameters={
            "error_type": {
                "type": "string",
                "description": "Type of error that occurred"
            },
            "error_logs": {
                "type": "string",
                "description": "Error logs for context"
            },
            "context": {
                "type": "object",
                "description": "Additional context information"
            }
        }
    )


def create_github_issue_tool() -> Tool:
    """Tool for creating GitHub issues."""
    
    def create_issue(owner: str, repo: str, title: str, body: str, labels: List[str]) -> Dict[str, Any]:
        """Create a GitHub issue with fix details.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            labels: Issue labels
            
        Returns:
            Created issue information
        """
        try:
            # This would integrate with GitHubService
            # For now, return a placeholder
            return {
                "success": True,
                "issue_number": 123,
                "html_url": f"https://github.com/{owner}/{repo}/issues/123",
                "title": title,
                "labels": labels,
                "created_at": "2025-08-23T10:00:00.000Z"
            }
            
        except Exception as e:
            logger.error(f"Error creating GitHub issue: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return CustomTool(
        name="create_github_issue",
        description="Create GitHub issues for CI/CD fixes",
        function=create_issue,
        parameters={
            "owner": {
                "type": "string",
                "description": "Repository owner"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "title": {
                "type": "string",
                "description": "Issue title"
            },
            "body": {
                "type": "string",
                "description": "Issue body"
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Issue labels"
            }
        }
    )


def update_database_tool() -> Tool:
    """Tool for updating database records."""
    
    def update_record(table: str, record_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a database record.
        
        Args:
            table: Table name
            record_id: Record ID to update
            updates: Fields to update
            
        Returns:
            Update result
        """
        try:
            # This would integrate with database repositories
            # For now, return a placeholder
            return {
                "success": True,
                "table": table,
                "record_id": record_id,
                "updated_fields": list(updates.keys()),
                "updated_at": "2025-08-23T10:00:00.000Z"
            }
            
        except Exception as e:
            logger.error(f"Error updating database record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return CustomTool(
        name="update_database",
        description="Update database records with analysis results",
        function=update_record,
        parameters={
            "table": {
                "type": "string",
                "description": "Table name"
            },
            "record_id": {
                "type": "integer",
                "description": "Record ID to update"
            },
            "updates": {
                "type": "object",
                "description": "Fields to update"
            }
        }
    )


def classify_error_type_tool() -> Tool:
    """Tool for classifying error types."""
    
    def classify_error(error_logs: str) -> str:
        """Classify error type based on log content.
        
        Args:
            error_logs: Error log content
            
        Returns:
            Error classification
        """
        try:
            error_logs_lower = error_logs.lower()
            
            if any(pattern in error_logs_lower for pattern in ["npm install", "package.json", "dependency"]):
                return "dependency_error"
            elif any(pattern in error_logs_lower for pattern in ["test", "spec", "jest", "mocha"]):
                return "test_failure"
            elif any(pattern in error_logs_lower for pattern in ["build", "compile", "make"]):
                return "build_error"
            elif any(pattern in error_logs_lower for pattern in ["permission", "access", "403", "401"]):
                return "permission_error"
            elif any(pattern in error_logs_lower for pattern in ["timeout", "timed out"]):
                return "timeout_error"
            else:
                return "unknown_error"
                
        except Exception as e:
            logger.error(f"Error classifying error type: {e}")
            return "classification_error"
    
    return CustomTool(
        name="classify_error_type",
        description="Classify CI/CD error types based on log content",
        function=classify_error,
        parameters={
            "error_logs": {
                "type": "string",
                "description": "Error log content to classify"
            }
        }
    )


def assess_fix_confidence_tool() -> Tool:
    """Tool for assessing fix confidence."""
    
    def assess_confidence(error_type: str, fix_steps: List[str], context: Dict[str, Any]) -> float:
        """Assess confidence level of a fix suggestion.
        
        Args:
            error_type: Type of error
            fix_steps: Proposed fix steps
            context: Additional context
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            base_confidence = 0.5
            
            # Adjust based on error type
            if error_type == "dependency_error":
                base_confidence += 0.2
            elif error_type == "test_failure":
                base_confidence += 0.1
            elif error_type == "build_error":
                base_confidence += 0.15
            
            # Adjust based on fix steps
            if len(fix_steps) >= 3:
                base_confidence += 0.1
            if any("clear" in step.lower() for step in fix_steps):
                base_confidence += 0.05
            
            # Adjust based on context
            if context.get("has_similar_fixes", False):
                base_confidence += 0.1
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error assessing fix confidence: {e}")
            return 0.5
    
    return CustomTool(
        name="assess_fix_confidence",
        description="Assess confidence level of fix suggestions",
        function=assess_confidence,
        parameters={
            "error_type": {
                "type": "string",
                "description": "Type of error"
            },
            "fix_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Proposed fix steps"
            },
            "context": {
                "type": "object",
                "description": "Additional context"
            }
        }
    )


def validate_fix_suggestion_tool() -> Tool:
    """Tool for validating fix suggestions."""
    
    def validate_fix(fix_suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a fix suggestion for completeness and safety.
        
        Args:
            fix_suggestion: Fix suggestion to validate
            
        Returns:
            Validation result
        """
        try:
            validation_result = {
                "is_valid": True,
                "warnings": [],
                "errors": [],
                "safety_score": 0.8
            }
            
            # Check required fields
            required_fields = ["description", "steps", "confidence"]
            for field in required_fields:
                if field not in fix_suggestion:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")
            
            # Check confidence level
            confidence = fix_suggestion.get("confidence", 0)
            if confidence < 0.3:
                validation_result["warnings"].append("Low confidence fix - manual review recommended")
                validation_result["safety_score"] -= 0.2
            
            # Check for dangerous commands
            dangerous_patterns = ["rm -rf", "sudo", "chmod 777"]
            commands = fix_suggestion.get("commands", [])
            for command in commands:
                for pattern in dangerous_patterns:
                    if pattern in command.lower():
                        validation_result["warnings"].append(f"Potentially dangerous command: {command}")
                        validation_result["safety_score"] -= 0.3
            
            # Ensure safety score is within bounds
            validation_result["safety_score"] = max(0.0, min(1.0, validation_result["safety_score"]))
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating fix suggestion: {e}")
            return {
                "is_valid": False,
                "warnings": [],
                "errors": [f"Validation error: {str(e)}"],
                "safety_score": 0.0
            }
    
    return CustomTool(
        name="validate_fix_suggestion",
        description="Validate fix suggestions for completeness and safety",
        function=validate_fix,
        parameters={
            "fix_suggestion": {
                "type": "string",
                "description": "Fix suggestion to validate"
            }
        }
    )
