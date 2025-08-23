"""ML-based predictor for CI/CD fix success and failure patterns."""

import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

from ..core.logging import get_logger
from ..database.repositories import ml_predictions_repo

logger = get_logger(__name__)


@dataclass
class PredictionResult:
    """Result of ML prediction."""
    prediction: str
    confidence: float
    factors: List[str]
    model_version: str
    timestamp: datetime


class MLPatternRecognizer:
    """Machine learning-based pattern recognition for CI/CD failures."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the ML pattern recognizer.
        
        Args:
            model_path: Path to saved ML model
        """
        self.model_path = model_path or "models/cicd_predictor.pkl"
        self.model = None
        self.vectorizer = None
        self.feature_names = []
        self.model_version = "1.0.0"
        self.last_training = None
        
        # Load existing model if available
        self._load_model()
    
    def _load_model(self) -> None:
        """Load pre-trained ML model from disk."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.vectorizer = model_data['vectorizer']
                    self.feature_names = model_data['feature_names']
                    self.model_version = model_data.get('version', '1.0.0')
                    self.last_training = model_data.get('last_training')
                
                logger.info(f"Loaded ML model version {self.model_version}")
            else:
                logger.info("No pre-trained model found, will train new model")
                
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None
    
    def _save_model(self) -> None:
        """Save trained ML model to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'feature_names': self.feature_names,
                'version': self.model_version,
                'last_training': datetime.utcnow()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"ML model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")
    
    def extract_features(self, error_log: str, repo_context: Dict[str, Any]) -> np.ndarray:
        """Extract features from error log and repository context.
        
        Args:
            error_log: Error log text
            repo_context: Repository context information
            
        Returns:
            Feature vector as numpy array
        """
        if self.vectorizer is None:
            # Initialize vectorizer if not available
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 3)
            )
        
        # Combine error log with context
        combined_text = f"{error_log} {repo_context.get('language', '')} {repo_context.get('framework', '')}"
        
        # Transform text to features
        features = self.vectorizer.fit_transform([combined_text])
        return features.toarray()
    
    def predict_success(self, error_log: str, suggested_fix: str, repo_context: Dict[str, Any]) -> PredictionResult:
        """Predict the success likelihood of a suggested fix.
        
        Args:
            error_log: Error log text
            suggested_fix: Suggested fix description
            repo_context: Repository context
            
        Returns:
            Prediction result
        """
        try:
            if self.model is None:
                logger.warning("No trained model available, using fallback prediction")
                return self._fallback_prediction(error_log, suggested_fix, repo_context)
            
            # Extract features
            features = self.extract_features(error_log, repo_context)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(features)[0]
            prediction_class = self.model.predict(features)[0]
            
            # Determine confidence and factors
            confidence = max(prediction_proba)
            factors = self._extract_prediction_factors(features, repo_context)
            
            # Map prediction class to human-readable format
            prediction_map = {
                0: "likely_failure",
                1: "likely_success",
                2: "uncertain"
            }
            prediction = prediction_map.get(prediction_class, "uncertain")
            
            return PredictionResult(
                prediction=prediction,
                confidence=confidence,
                factors=factors,
                model_version=self.model_version,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return self._fallback_prediction(error_log, suggested_fix, repo_context)
    
    def _fallback_prediction(self, error_log: str, suggested_fix: str, repo_context: Dict[str, Any]) -> PredictionResult:
        """Fallback prediction when ML model is not available.
        
        Args:
            error_log: Error log text
            suggested_fix: Suggested fix description
            repo_context: Repository context
            
        Returns:
            Basic prediction result
        """
        # Simple rule-based prediction
        error_log_lower = error_log.lower()
        fix_lower = suggested_fix.lower()
        
        # Check for common success indicators
        success_indicators = ['clear cache', 'update dependencies', 'fix version', 'correct path']
        failure_indicators = ['restart service', 'check logs', 'manual intervention']
        
        success_score = sum(1 for indicator in success_indicators if indicator in fix_lower)
        failure_score = sum(1 for indicator in failure_indicators if indicator in fix_lower)
        
        if success_score > failure_score:
            prediction = "likely_success"
            confidence = 0.6
        elif failure_score > success_score:
            prediction = "likely_failure"
            confidence = 0.6
        else:
            prediction = "uncertain"
            confidence = 0.4
        
        factors = [
            f"Rule-based analysis (success: {success_score}, failure: {failure_score})",
            f"Repository language: {repo_context.get('language', 'unknown')}",
            f"Framework: {repo_context.get('framework', 'unknown')}"
        ]
        
        return PredictionResult(
            prediction=prediction,
            confidence=confidence,
            factors=factors,
            model_version="fallback",
            timestamp=datetime.utcnow()
        )
    
    def _extract_prediction_factors(self, features: np.ndarray, repo_context: Dict[str, Any]) -> List[str]:
        """Extract factors that influenced the prediction.
        
        Args:
            features: Feature vector
            repo_context: Repository context
            
        Returns:
            List of influencing factors
        """
        factors = []
        
        # Add repository context factors
        if repo_context.get('language'):
            factors.append(f"Language: {repo_context['language']}")
        
        if repo_context.get('framework'):
            factors.append(f"Framework: {repo_context['framework']}")
        
        # Add feature importance factors if available
        if hasattr(self.model, 'feature_importances_') and len(self.feature_names) > 0:
            # Get top features
            top_indices = np.argsort(self.model.feature_importances_)[-5:]
            top_features = [self.feature_names[i] for i in top_indices if i < len(self.feature_names)]
            if top_features:
                factors.append(f"Key features: {', '.join(top_features[:3])}")
        
        return factors
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the ML model with new data.
        
        Args:
            training_data: List of training examples
            
        Returns:
            Training results
        """
        try:
            if not training_data:
                logger.warning("No training data provided")
                return {"error": "No training data provided"}
            
            logger.info(f"Training ML model with {len(training_data)} examples")
            
            # Prepare training data
            X = []
            y = []
            
            for example in training_data:
                error_log = example.get('error_log', '')
                repo_context = example.get('repo_context', {})
                outcome = example.get('outcome', 'unknown')
                
                # Extract features
                features = self.extract_features(error_log, repo_context)
                X.append(features.flatten())
                
                # Map outcome to numeric label
                outcome_map = {
                    'success': 1,
                    'failure': 0,
                    'uncertain': 2
                }
                y.append(outcome_map.get(outcome, 2))
            
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Update model version
            self.model_version = f"1.{int(datetime.utcnow().timestamp())}"
            self.last_training = datetime.utcnow()
            
            # Save model
            self._save_model()
            
            logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
            
            return {
                "accuracy": accuracy,
                "model_version": self.model_version,
                "training_samples": len(training_data),
                "test_samples": len(X_test),
                "last_training": self.last_training.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current ML model.
        
        Returns:
            Model information dictionary
        """
        return {
            "model_version": self.model_version,
            "last_training": self.last_training.isoformat() if self.last_training else None,
            "model_path": self.model_path,
            "is_trained": self.model is not None,
            "feature_count": len(self.feature_names) if self.feature_names else 0
        }
