"""Gemini AI service for CI/CD failure analysis and fix generation."""

import os
from google import genai
from google.genai import types
from typing import Dict, Any, Optional
import json
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class GeminiFixerAgent:
    """AI agent for analyzing CI/CD failures and suggesting fixes using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini agent.
        
        Args:
            api_key: Google AI API key. If None, uses settings.
        """
        settings = get_settings()
        self.api_key = api_key or settings.google_api_key
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini AI service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("No Gemini API key provided. Using fallback analysis.")
    
    def analyze_failure_and_suggest_fix(self, error_logs: str, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CI/CD failure logs and suggest a fix using Gemini AI.
        
        Args:
            error_logs: The error logs from the failed CI/CD run
            repo_context: Additional context about the repository
            
        Returns:
            Dictionary containing analysis and suggested fix
        """
        if self.client:
            return self._analyze_with_gemini(error_logs, repo_context)
        else:
            return self._analyze_with_fallback(error_logs, repo_context)
    
    def _analyze_with_gemini(self, error_logs: str, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini AI to analyze the failure and suggest fixes."""
        prompt = self._build_analysis_prompt(error_logs, repo_context)
        
        try:
            logger.info("Sending analysis request to Gemini AI")
            
            # Try the new API format first
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[{"parts": [{"text": prompt}]}],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    candidate_count=1,
                    max_output_tokens=2048
                )
            )
            
            logger.info("Successfully received response from Gemini AI")
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            logger.error(f"Error calling Gemini API (new format): {e}")
            
            # Try alternative format
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        candidate_count=1,
                        max_output_tokens=2048
                    )
                )
                
                # Extract text from response properly
                response_text = ""
                if hasattr(response, 'text') and response.text:
                    response_text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text'):
                                    response_text += part.text
                
                if not response_text:
                    logger.warning("No response text found from Gemini API")
                    return self._analyze_with_fallback(error_logs, repo_context)
                
                logger.info("Successfully received response from Gemini AI (alternative format)")
                return self._parse_gemini_response(response_text)
                
            except Exception as e2:
                logger.error(f"Error calling Gemini API (alternative format): {e2}")
                return self._analyze_with_fallback(error_logs, repo_context)
    
    def _build_analysis_prompt(self, error_logs: str, repo_context: Dict[str, Any]) -> str:
        """Build the analysis prompt for Gemini AI.
        
        Args:
            error_logs: Error logs to analyze
            repo_context: Repository context information
            
        Returns:
            Formatted prompt string
        """
        context_info = ""
        if repo_context:
            context_info = f"""
Repository Context:
- Language: {repo_context.get('language', 'Unknown')}
- Framework: {repo_context.get('framework', 'Unknown')}
- Build System: {repo_context.get('build_system', 'Unknown')}
- Dependencies: {repo_context.get('dependencies', 'Unknown')}
"""
        
        prompt = f"""You are an expert CI/CD engineer and DevOps specialist. Analyze the following CI/CD failure logs and provide a comprehensive analysis and fix suggestion.

{context_info}

Error Logs:
{error_logs}

Please provide your analysis in the following JSON format:
{{
    "error_analysis": {{
        "error_type": "classification of the error (e.g., dependency_error, build_error, test_failure, etc.)",
        "error_severity": "high/medium/low",
        "root_cause": "detailed explanation of what caused the failure",
        "affected_components": ["list of components affected by this error"]
    }},
    "fix_suggestion": {{
        "description": "clear description of the fix",
        "steps": ["step1", "step2", "step3"],
        "commands": ["command1", "command2"],
        "confidence": 0.95,
        "estimated_time": "5-10 minutes"
    }},
    "prevention": {{
        "recommendations": ["suggestion1", "suggestion2"],
        "best_practices": ["practice1", "practice2"]
    }}
}}

Focus on providing actionable, specific fixes that can be implemented immediately. Consider the repository context when making suggestions."""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the Gemini AI response into structured data.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Parsed response dictionary
        """
        try:
            # Try to extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)
            
            # Try to find JSON anywhere in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            # If no JSON found, create a structured response from the text
            logger.warning("No JSON found in Gemini response, creating structured response")
            return self._create_structured_response(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return self._create_structured_response(response_text)
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._create_structured_response(response_text)
    
    def _create_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Create a structured response from unstructured text.
        
        Args:
            response_text: Unstructured response text
            
        Returns:
            Structured response dictionary
        """
        return {
            "error_analysis": {
                "error_type": "unknown",
                "error_severity": "medium",
                "root_cause": "Unable to parse AI response",
                "affected_components": ["unknown"]
            },
            "fix_suggestion": {
                "description": "Manual analysis required",
                "steps": ["Review the error logs manually", "Identify the root cause", "Implement appropriate fix"],
                "commands": [],
                "confidence": 0.0,
                "estimated_time": "unknown"
            },
            "prevention": {
                "recommendations": ["Enable better logging", "Implement automated testing"],
                "best_practices": ["Regular dependency updates", "CI/CD pipeline monitoring"]
            },
            "raw_response": response_text
        }
    
    def _analyze_with_fallback(self, error_logs: str, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when Gemini AI is not available.
        
        Args:
            error_logs: Error logs to analyze
            repo_context: Repository context information
            
        Returns:
            Basic analysis result
        """
        logger.info("Using fallback analysis (no AI available)")
        
        # Basic pattern matching for common CI/CD failures
        error_logs_lower = error_logs.lower()
        
        if "npm install" in error_logs_lower or "package.json" in error_logs_lower:
            error_type = "dependency_error"
            fix_description = "Check package.json and run npm install with appropriate flags"
        elif "test" in error_logs_lower and "fail" in error_logs_lower:
            error_type = "test_failure"
            fix_description = "Review test failures and fix underlying issues"
        elif "build" in error_logs_lower and "fail" in error_logs_lower:
            error_type = "build_error"
            fix_description = "Check build configuration and dependencies"
        else:
            error_type = "unknown_error"
            fix_description = "Manual investigation required"
        
        return {
            "error_analysis": {
                "error_type": error_type,
                "error_severity": "medium",
                "root_cause": "Basic pattern analysis (AI not available)",
                "affected_components": ["ci_cd_pipeline"]
            },
            "fix_suggestion": {
                "description": fix_description,
                "steps": ["Review error logs", "Identify specific failure point", "Apply appropriate fix"],
                "commands": [],
                "confidence": 0.3,
                "estimated_time": "15-30 minutes"
            },
            "prevention": {
                "recommendations": ["Enable AI-powered analysis", "Improve error logging"],
                "best_practices": ["Regular pipeline monitoring", "Automated testing"]
            }
        }
    
    def test_connection(self) -> bool:
        """Test Gemini AI service connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Simple test request
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents="Hello, this is a test message.",
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=10
                )
            )
            
            logger.info("Gemini AI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Gemini AI connection test failed: {e}")
            return False
