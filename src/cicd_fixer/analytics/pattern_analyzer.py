"""Pattern analyzer for CI/CD failures and fixes."""

import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
import math
from dataclasses import dataclass

from ..database.repositories import workflow_run_repo, failure_analysis_repo
from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PatternResult:
    """Result of pattern analysis."""
    pattern_type: str
    confidence: float
    frequency: int
    examples: List[str]
    metadata: Dict[str, Any]


class CICDPatternAnalyzer:
    """Analyzes patterns in CI/CD failures and fixes to improve future suggestions."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        self.pattern_cache = {}
        self.cache_ttl = timedelta(hours=1)
        self.last_cache_update = None
    
    def analyze_failure_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze patterns in workflow failures over the specified time period.
        
        Args:
            days_back: Number of days to look back for analysis
            
        Returns:
            Dictionary containing pattern analysis results
        """
        try:
            logger.info(f"Analyzing failure patterns for the last {days_back} days")
            
            # Check cache first
            cache_key = f"patterns_{days_back}"
            if self._is_cache_valid(cache_key):
                logger.info("Returning cached pattern analysis")
                return self.pattern_cache[cache_key]
            
            # Get workflow runs from database
            # Note: This would need to be implemented in the repository layer
            # For now, we'll use a placeholder approach
            
            # Analyze patterns
            patterns = self._extract_patterns([])  # Empty list for now
            
            result = {
                "analysis_period": f"Last {days_back} days",
                "total_runs": 0,  # Would come from database
                "patterns": patterns,
                "recommendations": self._generate_recommendations(patterns),
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            self._cache_result(cache_key, result)
            
            logger.info("Pattern analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing failure patterns: {e}")
            return {
                "error": str(e),
                "patterns": {},
                "recommendations": []
            }
    
    def _extract_patterns(self, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract patterns from workflow run data.
        
        Args:
            runs: List of workflow run data
            
        Returns:
            Dictionary of extracted patterns
        """
        if not runs:
            return {}
        
        # Initialize pattern counters
        repo_failures = Counter()
        error_types = Counter()
        time_patterns = defaultdict(int)
        fix_success_rates = defaultdict(lambda: {"total": 0, "approved": 0})
        
        for run in runs:
            # Count repository failures
            repo_key = f"{run.get('owner', 'unknown')}/{run.get('repo_name', 'unknown')}"
            repo_failures[repo_key] += 1
            
            # Count error types
            if run.get('conclusion') == 'failure':
                error_log = run.get('failure_logs', '')
                error_type = self._classify_error(error_log)
                error_types[error_type] += 1
            
            # Time-based patterns
            created_at = run.get('created_at')
            if created_at:
                hour = created_at.hour
                time_patterns[hour] += 1
            
            # Fix success rates
            fix_status = run.get('fix_status', 'pending')
            if fix_status in ['approved', 'rejected']:
                fix_success_rates[fix_status]["total"] += 1
                if fix_status == 'approved':
                    fix_success_rates['approved']['approved'] += 1
        
        return {
            "repository_failures": dict(repo_failures.most_common(10)),
            "error_types": dict(error_types.most_common(10)),
            "time_patterns": dict(time_patterns),
            "fix_success_rates": dict(fix_success_rates),
            "total_analyzed": len(runs)
        }
    
    def _classify_error(self, error_log: str) -> str:
        """Classify error type based on error log content.
        
        Args:
            error_log: Error log text
            
        Returns:
            Error classification string
        """
        error_log_lower = error_log.lower()
        
        # Common CI/CD error patterns
        if any(pattern in error_log_lower for pattern in ['npm install', 'package.json', 'dependency']):
            return 'dependency_error'
        elif any(pattern in error_log_lower for pattern in ['test', 'spec', 'jest', 'mocha']):
            return 'test_failure'
        elif any(pattern in error_log_lower for pattern in ['build', 'compile', 'make']):
            return 'build_error'
        elif any(pattern in error_log_lower for pattern in ['permission', 'access', '403', '401']):
            return 'permission_error'
        elif any(pattern in error_log_lower for pattern in ['timeout', 'timed out']):
            return 'timeout_error'
        elif any(pattern in error_log_lower for pattern in ['memory', 'out of memory']):
            return 'resource_error'
        else:
            return 'unknown_error'
    
    def _generate_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on pattern analysis.
        
        Args:
            patterns: Extracted patterns
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Repository-specific recommendations
        repo_failures = patterns.get('repository_failures', {})
        if repo_failures:
            top_failing_repo = max(repo_failures.items(), key=lambda x: x[1])
            recommendations.append(
                f"Repository {top_failing_repo[0]} has {top_failing_repo[1]} failures. "
                "Consider implementing automated testing and dependency management."
            )
        
        # Error type recommendations
        error_types = patterns.get('error_types', {})
        if 'dependency_error' in error_types and error_types['dependency_error'] > 5:
            recommendations.append(
                "High number of dependency errors detected. "
                "Consider implementing dependency scanning and automated updates."
            )
        
        if 'test_failure' in error_types and error_types['test_failure'] > 10:
            recommendations.append(
                "Frequent test failures detected. "
                "Review test stability and implement flaky test detection."
            )
        
        # Time-based recommendations
        time_patterns = patterns.get('time_patterns', {})
        if time_patterns:
            peak_hour = max(time_patterns.items(), key=lambda x: x[1])
            recommendations.append(
                f"Peak failure time detected at {peak_hour[0]}:00. "
                "Consider scheduling maintenance during off-peak hours."
            )
        
        # Fix success rate recommendations
        fix_rates = patterns.get('fix_success_rates', {})
        if 'approved' in fix_rates and 'rejected' in fix_rates:
            approved_rate = fix_rates['approved']['approved'] / max(fix_rates['approved']['total'], 1)
            if approved_rate < 0.7:
                recommendations.append(
                    f"Low fix approval rate ({approved_rate:.1%}). "
                    "Review fix generation quality and user feedback."
                )
        
        return recommendations
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid.
        
        Args:
            cache_key: Cache key to check
            
        Returns:
            True if cache is valid, False otherwise
        """
        if cache_key not in self.pattern_cache:
            return False
        
        if not self.last_cache_update:
            return False
        
        return datetime.utcnow() - self.last_cache_update < self.cache_ttl
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache analysis result.
        
        Args:
            cache_key: Cache key
            result: Result to cache
        """
        self.pattern_cache[cache_key] = result
        self.last_cache_update = datetime.utcnow()
        logger.debug(f"Cached pattern analysis result for key: {cache_key}")
    
    def clear_cache(self) -> None:
        """Clear the pattern cache."""
        self.pattern_cache.clear()
        self.last_cache_update = None
        logger.info("Pattern analysis cache cleared")
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get a summary of recent patterns.
        
        Returns:
            Pattern summary dictionary
        """
        try:
            # Analyze last 7 days for summary
            patterns = self.analyze_failure_patterns(days_back=7)
            
            return {
                "summary": "Recent pattern analysis",
                "total_patterns": len(patterns.get('patterns', {})),
                "top_error_type": self._get_top_error_type(patterns),
                "recommendation_count": len(patterns.get('recommendations', [])),
                "last_updated": patterns.get('analyzed_at')
            }
            
        except Exception as e:
            logger.error(f"Error generating pattern summary: {e}")
            return {"error": str(e)}
    
    def _get_top_error_type(self, patterns: Dict[str, Any]) -> str:
        """Get the most common error type from patterns.
        
        Args:
            patterns: Pattern analysis results
            
        Returns:
            Top error type string
        """
        error_types = patterns.get('error_types', {})
        if not error_types:
            return "unknown"
        
        return max(error_types.items(), key=lambda x: x[1])[0]
