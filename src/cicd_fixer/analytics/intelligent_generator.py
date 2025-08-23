"""Intelligent fix generation using ML and pattern analysis."""

import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import re

from ..core.logging import get_logger
from ..services.gemini_agent import GeminiFixerAgent
from .pattern_analyzer import CICDPatternAnalyzer
from .ml_predictor import MLPatternRecognizer

logger = get_logger(__name__)


@dataclass
class FixSuggestion:
    """Intelligent fix suggestion."""
    fix_id: str
    description: str
    steps: List[str]
    commands: List[str]
    confidence: float
    reasoning: str
    estimated_time: str
    risk_level: str
    alternatives: List[str]
    created_at: datetime


class IntelligentFixGenerator:
    """Generates intelligent fixes using ML, pattern analysis, and AI."""
    
    def __init__(self):
        """Initialize the intelligent fix generator."""
        self.gemini_agent = GeminiFixerAgent()
        self.pattern_analyzer = CICDPatternAnalyzer()
        self.ml_predictor = MLPatternRecognizer()
        self.fix_cache = {}
        self.cache_ttl = timedelta(hours=2)
    
    def generate_fix(self, error_log: str, repo_context: Dict[str, Any], 
                    use_ml: bool = True, use_patterns: bool = True) -> FixSuggestion:
        """Generate an intelligent fix for a CI/CD failure.
        
        Args:
            error_log: Error log text
            repo_context: Repository context information
            use_ml: Whether to use ML predictions
            use_patterns: Whether to use pattern analysis
            
        Returns:
            Intelligent fix suggestion
        """
        try:
            logger.info("Generating intelligent fix for CI/CD failure")
            
            # Check cache first
            cache_key = self._generate_cache_key(error_log, repo_context)
            if cache_key in self.fix_cache:
                cached_fix = self.fix_cache[cache_key]
                if datetime.utcnow() - cached_fix.created_at < self.cache_ttl:
                    logger.info("Returning cached fix suggestion")
                    return cached_fix
            
            # Generate base fix using Gemini AI
            base_fix = self.gemini_agent.analyze_failure_and_suggest_fix(error_log, repo_context)
            
            # Enhance with pattern analysis if enabled
            if use_patterns:
                base_fix = self._enhance_with_patterns(base_fix, error_log, repo_context)
            
            # Enhance with ML predictions if enabled
            if use_ml:
                base_fix = self._enhance_with_ml(base_fix, error_log, repo_context)
            
            # Generate alternatives
            alternatives = self._generate_alternative_fixes(error_log, repo_context, base_fix)
            
            # Create fix suggestion
            fix_suggestion = FixSuggestion(
                fix_id=self._generate_fix_id(),
                description=base_fix.get('fix_suggestion', {}).get('description', 'No fix available'),
                steps=base_fix.get('fix_suggestion', {}).get('steps', []),
                commands=base_fix.get('fix_suggestion', {}).get('commands', []),
                confidence=base_fix.get('fix_suggestion', {}).get('confidence', 0.0),
                reasoning=base_fix.get('error_analysis', {}).get('root_cause', 'Analysis not available'),
                estimated_time=base_fix.get('fix_suggestion', {}).get('estimated_time', 'Unknown'),
                risk_level=self._assess_risk_level(base_fix),
                alternatives=alternatives,
                created_at=datetime.utcnow()
            )
            
            # Cache the result
            self.fix_cache[cache_key] = fix_suggestion
            
            logger.info(f"Generated intelligent fix with confidence {fix_suggestion.confidence:.2f}")
            return fix_suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate intelligent fix: {e}")
            return self._generate_fallback_fix(error_log, repo_context)
    
    def _enhance_with_patterns(self, base_fix: Dict[str, Any], error_log: str, 
                              repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance fix with pattern analysis insights.
        
        Args:
            base_fix: Base fix from AI
            error_log: Error log text
            repo_context: Repository context
            
        Returns:
            Enhanced fix dictionary
        """
        try:
            # Get pattern analysis
            patterns = self.pattern_analyzer.analyze_failure_patterns(days_back=30)
            
            # Extract relevant patterns
            error_type = base_fix.get('error_analysis', {}).get('error_type', 'unknown')
            error_types = patterns.get('patterns', {}).get('error_types', {})
            
            # Adjust confidence based on pattern frequency
            if error_type in error_types:
                frequency = error_types[error_type]
                if frequency > 10:
                    # High frequency error - increase confidence
                    base_fix['fix_suggestion']['confidence'] = min(
                        base_fix['fix_suggestion'].get('confidence', 0.0) * 1.2, 1.0
                    )
                    base_fix['fix_suggestion']['steps'].append(
                        f"Note: This is a common error (occurred {frequency} times). "
                        "Consider implementing preventive measures."
                    )
            
            # Add pattern-based recommendations
            recommendations = patterns.get('recommendations', [])
            if recommendations:
                base_fix['pattern_recommendations'] = recommendations[:3]  # Top 3
            
            return base_fix
            
        except Exception as e:
            logger.warning(f"Pattern enhancement failed: {e}")
            return base_fix
    
    def _enhance_with_ml(self, base_fix: Dict[str, Any], error_log: str, 
                         repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance fix with ML predictions.
        
        Args:
            base_fix: Base fix from AI
            error_log: Error log text
            repo_context: Repository context
            
        Returns:
            Enhanced fix dictionary
        """
        try:
            # Get ML prediction
            suggested_fix = base_fix.get('fix_suggestion', {}).get('description', '')
            prediction = self.ml_predictor.predict_success(error_log, suggested_fix, repo_context)
            
            # Adjust confidence based on ML prediction
            if prediction.prediction == "likely_success":
                base_fix['fix_suggestion']['confidence'] = min(
                    base_fix['fix_suggestion'].get('confidence', 0.0) * 1.1, 1.0
                )
                base_fix['ml_insights'] = {
                    'prediction': prediction.prediction,
                    'confidence': prediction.confidence,
                    'factors': prediction.factors
                }
            elif prediction.prediction == "likely_failure":
                base_fix['fix_suggestion']['confidence'] = max(
                    base_fix['fix_suggestion'].get('confidence', 0.0) * 0.8, 0.1
                )
                base_fix['ml_insights'] = {
                    'prediction': prediction.prediction,
                    'confidence': prediction.confidence,
                    'factors': prediction.factors,
                    'warning': 'ML model predicts low success likelihood'
                }
            
            return base_fix
            
        except Exception as e:
            logger.warning(f"ML enhancement failed: {e}")
            return base_fix
    
    def _generate_alternative_fixes(self, error_log: str, repo_context: Dict[str, Any], 
                                  base_fix: Dict[str, Any]) -> List[str]:
        """Generate alternative fix approaches.
        
        Args:
            error_log: Error log text
            repo_context: Repository context
            base_fix: Base fix suggestion
            
        Returns:
            List of alternative fix descriptions
        """
        alternatives = []
        
        try:
            # Generate alternative using different approach
            alt_context = repo_context.copy()
            alt_context['approach'] = 'alternative'
            
            alt_fix = self.gemini_agent.analyze_failure_and_suggest_fix(error_log, alt_context)
            alt_description = alt_fix.get('fix_suggestion', {}).get('description', '')
            
            if alt_description and alt_description != base_fix.get('fix_suggestion', {}).get('description', ''):
                alternatives.append(alt_description)
            
            # Add common alternative approaches based on error type
            error_type = base_fix.get('error_analysis', {}).get('error_type', 'unknown')
            
            if error_type == 'dependency_error':
                alternatives.extend([
                    "Try using a different package manager (yarn instead of npm)",
                    "Clear package manager cache and retry",
                    "Check for version conflicts in package-lock.json"
                ])
            elif error_type == 'test_failure':
                alternatives.extend([
                    "Run tests in isolation to identify specific failures",
                    "Check test environment configuration",
                    "Review recent code changes that might affect tests"
                ])
            elif error_type == 'build_error':
                alternatives.extend([
                    "Try building with verbose logging for more details",
                    "Check build tool version compatibility",
                    "Verify all required dependencies are installed"
                ])
            
            # Remove duplicates and limit to top alternatives
            unique_alternatives = list(dict.fromkeys(alternatives))
            return unique_alternatives[:5]  # Top 5 alternatives
            
        except Exception as e:
            logger.warning(f"Alternative fix generation failed: {e}")
            return alternatives
    
    def _assess_risk_level(self, base_fix: Dict[str, Any]) -> str:
        """Assess the risk level of applying the fix.
        
        Args:
            base_fix: Fix suggestion dictionary
            
        Returns:
            Risk level string (low, medium, high)
        """
        try:
            confidence = base_fix.get('fix_suggestion', {}).get('confidence', 0.0)
            error_severity = base_fix.get('error_analysis', {}).get('error_severity', 'medium')
            
            # High confidence + low severity = low risk
            if confidence > 0.8 and error_severity == 'low':
                return 'low'
            # Low confidence + high severity = high risk
            elif confidence < 0.5 and error_severity == 'high':
                return 'high'
            else:
                return 'medium'
                
        except Exception:
            return 'medium'
    
    def _generate_cache_key(self, error_log: str, repo_context: Dict[str, Any]) -> str:
        """Generate cache key for fix suggestions.
        
        Args:
            error_log: Error log text
            repo_context: Repository context
            
        Returns:
            Cache key string
        """
        # Create hash of error log and key context elements
        context_str = f"{repo_context.get('language', '')}{repo_context.get('framework', '')}"
        combined = f"{error_log[:200]}{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _generate_fix_id(self) -> str:
        """Generate unique fix ID.
        
        Returns:
            Unique fix ID string
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(timestamp).encode()).hexdigest()[:8]
        return f"fix_{timestamp}_{random_suffix}"
    
    def _generate_fallback_fix(self, error_log: str, repo_context: Dict[str, Any]) -> FixSuggestion:
        """Generate a basic fallback fix when intelligent generation fails.
        
        Args:
            error_log: Error log text
            repo_context: Repository context
            
        Returns:
            Basic fix suggestion
        """
        logger.info("Generating fallback fix")
        
        return FixSuggestion(
            fix_id=self._generate_fix_id(),
            description="Manual investigation required - AI analysis failed",
            steps=[
                "Review the error logs carefully",
                "Identify the specific failure point",
                "Check recent changes that might have caused the issue",
                "Consult team members or documentation",
                "Implement fix and test thoroughly"
            ],
            commands=[],
            confidence=0.1,
            reasoning="Fallback fix due to analysis failure",
            estimated_time="30-60 minutes",
            risk_level="high",
            alternatives=[
                "Use traditional debugging methods",
                "Check similar issues in project history",
                "Review CI/CD pipeline configuration"
            ],
            created_at=datetime.utcnow()
        )
    
    def get_fix_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated fixes.
        
        Returns:
            Fix generation statistics
        """
        try:
            total_fixes = len(self.fix_cache)
            high_confidence_fixes = sum(
                1 for fix in self.fix_cache.values() 
                if fix.confidence > 0.8
            )
            
            return {
                "total_fixes_generated": total_fixes,
                "high_confidence_fixes": high_confidence_fixes,
                "average_confidence": sum(fix.confidence for fix in self.fix_cache.values()) / max(total_fixes, 1),
                "cache_size": len(self.fix_cache),
                "last_generated": max(fix.created_at for fix in self.fix_cache.values()).isoformat() if self.fix_cache else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get fix statistics: {e}")
            return {"error": str(e)}
    
    def clear_cache(self) -> None:
        """Clear the fix suggestion cache."""
        self.fix_cache.clear()
        logger.info("Fix suggestion cache cleared")
