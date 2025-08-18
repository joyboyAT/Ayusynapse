"""
Feedback API - REST endpoints for collecting and retrieving feedback
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from ..models.feedback.feedback_collector import FeedbackCollector, FeedbackEntry

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class FeedbackRequest(BaseModel):
    prediction_id: str = Field(..., description="Unique identifier for the prediction")
    trial_id: str = Field(..., description="Clinical trial identifier")
    patient_id: str = Field(..., description="Patient identifier")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    user_id: str = Field(..., description="User providing feedback")
    feedback_type: str = Field(..., description="Type of feedback: correct, incorrect, partial, missing_entity")
    comments: Optional[str] = Field(None, description="Optional user comments")
    suggested_corrections: Optional[Dict] = Field(None, description="Optional suggested corrections")
    metadata: Optional[Dict] = Field(None, description="Optional additional metadata")

class FeedbackResponse(BaseModel):
    feedback_id: str
    prediction_id: str
    trial_id: str
    patient_id: str
    feedback_type: str
    confidence_score: float
    user_id: str
    timestamp: str
    comments: Optional[str] = None
    suggested_corrections: Optional[Dict] = None
    metadata: Optional[Dict] = None

class FeedbackStatistics(BaseModel):
    total_feedback: int
    feedback_types: Dict[str, int]
    average_confidence: float
    recent_feedback: int

# Create router
router = APIRouter(prefix="/feedback", tags=["feedback"])

# Dependency to get feedback collector
def get_feedback_collector() -> FeedbackCollector:
    return FeedbackCollector()

@router.post("/collect", response_model=Dict[str, str])
async def collect_feedback(
    feedback_request: FeedbackRequest,
    feedback_collector: FeedbackCollector = Depends(get_feedback_collector)
):
    """
    Collect feedback from user after displaying trial matches
    """
    try:
        feedback_id = feedback_collector.collect_feedback(
            prediction_id=feedback_request.prediction_id,
            trial_id=feedback_request.trial_id,
            patient_id=feedback_request.patient_id,
            confidence_score=feedback_request.confidence_score,
            user_id=feedback_request.user_id,
            feedback_type=feedback_request.feedback_type,
            comments=feedback_request.comments,
            suggested_corrections=feedback_request.suggested_corrections,
            metadata=feedback_request.metadata
        )
        
        return {"feedback_id": feedback_id, "status": "success"}
        
    except Exception as e:
        logger.error(f"Error collecting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect feedback: {str(e)}")

@router.get("/prediction/{prediction_id}", response_model=Optional[FeedbackResponse])
async def get_feedback_by_prediction(
    prediction_id: str,
    feedback_collector: FeedbackCollector = Depends(get_feedback_collector)
):
    """
    Get feedback for a specific prediction
    """
    try:
        feedback = feedback_collector.get_feedback_by_prediction(prediction_id)
        
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        return FeedbackResponse(**feedback.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback by prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")

@router.get("/trial/{trial_id}", response_model=List[FeedbackResponse])
async def get_feedback_by_trial(
    trial_id: str,
    feedback_collector: FeedbackCollector = Depends(get_feedback_collector)
):
    """
    Get all feedback for a specific trial
    """
    try:
        feedback_list = feedback_collector.get_feedback_by_trial(trial_id)
        
        return [FeedbackResponse(**feedback.__dict__) for feedback in feedback_list]
        
    except Exception as e:
        logger.error(f"Error getting feedback by trial: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")

@router.get("/user/{user_id}", response_model=List[FeedbackResponse])
async def get_feedback_by_user(
    user_id: str,
    feedback_collector: FeedbackCollector = Depends(get_feedback_collector)
):
    """
    Get all feedback from a specific user
    """
    try:
        feedback_list = feedback_collector.get_feedback_by_user(user_id)
        
        return [FeedbackResponse(**feedback.__dict__) for feedback in feedback_list]
        
    except Exception as e:
        logger.error(f"Error getting feedback by user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve feedback: {str(e)}")

@router.get("/statistics", response_model=FeedbackStatistics)
async def get_feedback_statistics(
    feedback_collector: FeedbackCollector = Depends(get_feedback_collector)
):
    """
    Get statistics about collected feedback
    """
    try:
        stats = feedback_collector.get_feedback_statistics()
        
        return FeedbackStatistics(**stats)
        
    except Exception as e:
        logger.error(f"Error getting feedback statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}")

@router.get("/health")
async def feedback_health_check():
    """
    Health check endpoint for feedback service
    """
    return {"status": "healthy", "service": "feedback"}
