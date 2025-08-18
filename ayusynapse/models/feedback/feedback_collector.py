"""
Feedback Collector - Captures and stores user feedback on trial matching results
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FeedbackEntry:
    """Represents a single feedback entry"""
    feedback_id: str
    prediction_id: str
    trial_id: str
    patient_id: str
    feedback_type: str  # 'correct', 'incorrect', 'partial', 'missing_entity'
    confidence_score: float
    user_id: str
    timestamp: str
    comments: Optional[str] = None
    suggested_corrections: Optional[Dict] = None
    metadata: Optional[Dict] = None

class FeedbackCollector:
    """Collects and manages user feedback on trial matching results"""
    
    def __init__(self, feedback_file: str = "feedback_data.json"):
        self.feedback_file = Path(feedback_file)
        self.logger = logging.getLogger(__name__)
        self._ensure_feedback_file()
    
    def _ensure_feedback_file(self):
        """Ensure feedback file exists"""
        if not self.feedback_file.exists():
            self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_feedback([])
    
    def collect_feedback(self, 
                        prediction_id: str,
                        trial_id: str,
                        patient_id: str,
                        confidence_score: float,
                        user_id: str,
                        feedback_type: str,
                        comments: Optional[str] = None,
                        suggested_corrections: Optional[Dict] = None,
                        metadata: Optional[Dict] = None) -> str:
        """
        Collect feedback from user after displaying trial matches
        
        Args:
            prediction_id: Unique identifier for the prediction
            trial_id: Clinical trial identifier
            patient_id: Patient identifier
            confidence_score: Model confidence score
            user_id: User providing feedback
            feedback_type: Type of feedback ('correct', 'incorrect', 'partial', 'missing_entity')
            comments: Optional user comments
            suggested_corrections: Optional suggested corrections
            metadata: Optional additional metadata
        
        Returns:
            feedback_id: Unique identifier for the feedback entry
        """
        try:
            feedback_id = str(uuid.uuid4())
            
            feedback_entry = FeedbackEntry(
                feedback_id=feedback_id,
                prediction_id=prediction_id,
                trial_id=trial_id,
                patient_id=patient_id,
                feedback_type=feedback_type,
                confidence_score=confidence_score,
                user_id=user_id,
                timestamp=datetime.now().isoformat(),
                comments=comments,
                suggested_corrections=suggested_corrections,
                metadata=metadata
            )
            
            # Load existing feedback
            feedback_data = self._load_feedback()
            
            # Add new feedback
            feedback_data.append(asdict(feedback_entry))
            
            # Save updated feedback
            self._save_feedback(feedback_data)
            
            self.logger.info(f"Feedback collected: {feedback_id} for prediction {prediction_id}")
            return feedback_id
            
        except Exception as e:
            self.logger.error(f"Error collecting feedback: {e}")
            raise
    
    def get_feedback_by_prediction(self, prediction_id: str) -> Optional[FeedbackEntry]:
        """Get feedback for a specific prediction"""
        try:
            feedback_data = self._load_feedback()
            
            for entry in feedback_data:
                if entry['prediction_id'] == prediction_id:
                    return FeedbackEntry(**entry)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting feedback by prediction: {e}")
            return None
    
    def get_feedback_by_trial(self, trial_id: str) -> List[FeedbackEntry]:
        """Get all feedback for a specific trial"""
        try:
            feedback_data = self._load_feedback()
            
            trial_feedback = []
            for entry in feedback_data:
                if entry['trial_id'] == trial_id:
                    trial_feedback.append(FeedbackEntry(**entry))
            
            return trial_feedback
            
        except Exception as e:
            self.logger.error(f"Error getting feedback by trial: {e}")
            return []
    
    def get_feedback_by_user(self, user_id: str) -> List[FeedbackEntry]:
        """Get all feedback from a specific user"""
        try:
            feedback_data = self._load_feedback()
            
            user_feedback = []
            for entry in feedback_data:
                if entry['user_id'] == user_id:
                    user_feedback.append(FeedbackEntry(**entry))
            
            return user_feedback
            
        except Exception as e:
            self.logger.error(f"Error getting feedback by user: {e}")
            return []
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics about collected feedback"""
        try:
            feedback_data = self._load_feedback()
            
            if not feedback_data:
                return {
                    'total_feedback': 0,
                    'feedback_types': {},
                    'average_confidence': 0.0,
                    'recent_feedback': 0
                }
            
            # Count feedback types
            feedback_types = {}
            confidence_scores = []
            recent_count = 0
            
            for entry in feedback_data:
                # Count feedback types
                feedback_type = entry['feedback_type']
                feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
                
                # Collect confidence scores
                confidence_scores.append(entry['confidence_score'])
                
                # Count recent feedback (last 7 days)
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if (datetime.now() - timestamp).days <= 7:
                    recent_count += 1
            
            return {
                'total_feedback': len(feedback_data),
                'feedback_types': feedback_types,
                'average_confidence': sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
                'recent_feedback': recent_count
            }
            
        except Exception as e:
            self.logger.error(f"Error getting feedback statistics: {e}")
            return {}
    
    def _load_feedback(self) -> List[Dict]:
        """Load feedback data from file"""
        try:
            if not self.feedback_file.exists():
                return []
            
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading feedback: {e}")
            return []
    
    def _save_feedback(self, feedback_data: List[Dict]):
        """Save feedback data to file"""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving feedback: {e}")
            raise
