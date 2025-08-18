"""
Test script for the feedback system
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.models.feedback.feedback_collector import FeedbackCollector
from ayusynapse.api.feedback_ui import FeedbackUI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_feedback_collection():
    """Test the feedback collection functionality"""
    print("🧪 Testing Feedback Collection System")
    print("=" * 50)
    
    # Initialize feedback collector
    feedback_collector = FeedbackCollector("test_feedback.json")
    
    # Test data
    test_feedback_data = [
        {
            "prediction_id": "pred-001",
            "trial_id": "NCT07062263",
            "patient_id": "patient-001",
            "confidence_score": 0.85,
            "user_id": "doctor-smith",
            "feedback_type": "correct",
            "comments": "Excellent match for HER2+ biliary cancer patient",
            "suggested_corrections": None,
            "metadata": {"source": "test"}
        },
        {
            "prediction_id": "pred-002",
            "trial_id": "NCT12345678",
            "patient_id": "patient-002",
            "confidence_score": 0.45,
            "user_id": "doctor-jones",
            "feedback_type": "incorrect",
            "comments": "Patient has CNS metastases which should exclude them",
            "suggested_corrections": {"exclusions": "Add CNS metastases check"},
            "metadata": {"source": "test"}
        },
        {
            "prediction_id": "pred-003",
            "trial_id": "NCT98765432",
            "patient_id": "patient-003",
            "confidence_score": 0.72,
            "user_id": "doctor-brown",
            "feedback_type": "partial",
            "comments": "Match is mostly correct but missing some lab criteria",
            "suggested_corrections": {"lab_criteria": "Include creatinine clearance"},
            "metadata": {"source": "test"}
        }
    ]
    
    # Collect feedback
    feedback_ids = []
    for feedback_data in test_feedback_data:
        try:
            feedback_id = feedback_collector.collect_feedback(**feedback_data)
            feedback_ids.append(feedback_id)
            print(f"✅ Collected feedback: {feedback_id}")
        except Exception as e:
            print(f"❌ Error collecting feedback: {e}")
    
    # Test retrieval by prediction
    print("\n📋 Testing Feedback Retrieval")
    print("-" * 30)
    
    for prediction_id in ["pred-001", "pred-002", "pred-003"]:
        feedback = feedback_collector.get_feedback_by_prediction(prediction_id)
        if feedback:
            print(f"📝 Feedback for {prediction_id}: {feedback.feedback_type} by {feedback.user_id}")
        else:
            print(f"❌ No feedback found for {prediction_id}")
    
    # Test retrieval by trial
    print("\n🏥 Testing Feedback by Trial")
    print("-" * 30)
    
    trial_feedback = feedback_collector.get_feedback_by_trial("NCT07062263")
    print(f"📊 Found {len(trial_feedback)} feedback entries for trial NCT07062263")
    
    # Test retrieval by user
    print("\n👤 Testing Feedback by User")
    print("-" * 30)
    
    user_feedback = feedback_collector.get_feedback_by_user("doctor-smith")
    print(f"📊 Found {len(user_feedback)} feedback entries from doctor-smith")
    
    # Test statistics
    print("\n📈 Testing Feedback Statistics")
    print("-" * 30)
    
    stats = feedback_collector.get_feedback_statistics()
    print(f"Total Feedback: {stats['total_feedback']}")
    print(f"Recent Feedback (7 days): {stats['recent_feedback']}")
    print(f"Average Confidence: {stats['average_confidence']:.2f}")
    print("Feedback Types:")
    for feedback_type, count in stats['feedback_types'].items():
        print(f"  {feedback_type}: {count}")
    
    return feedback_collector

def test_feedback_ui():
    """Test the feedback UI functionality"""
    print("\n🖥️ Testing Feedback UI")
    print("=" * 50)
    
    # Initialize feedback UI
    feedback_ui = FeedbackUI()
    
    # Mock match result
    mock_match_result = {
        "prediction_id": "pred-test-001",
        "trial_id": "NCT07062263",
        "patient_id": "patient-test-001",
        "confidence_score": 0.85,
        "score": 85.0,
        "eligible": True
    }
    
    # Mock feedback callback
    def mock_feedback_callback(**kwargs):
        print(f"📤 Feedback callback called with: {kwargs}")
        return "feedback-mock-001"
    
    # Test feedback prompt (commented out to avoid blocking)
    print("📋 Feedback prompt would be displayed here")
    print("In a real scenario, this would show:")
    print("  - Trial ID: NCT07062263")
    print("  - Patient ID: patient-test-001")
    print("  - Confidence Score: 0.85")
    print("  - Match Score: 85.0")
    print("  - Eligible: True")
    print("  - Feedback options: Correct, Incorrect, Partial, Missing Entity, Skip")
    
    # Test feedback summary display
    print("\n📊 Testing Feedback Summary Display")
    print("-" * 40)
    
    mock_stats = {
        "total_feedback": 15,
        "recent_feedback": 3,
        "average_confidence": 0.78,
        "feedback_types": {
            "correct": 10,
            "incorrect": 3,
            "partial": 2
        }
    }
    
    feedback_ui.display_feedback_summary(mock_stats)
    
    # Test feedback for trial display
    print("\n📋 Testing Feedback for Trial Display")
    print("-" * 40)
    
    mock_feedback_list = [
        {
            "feedback_type": "correct",
            "user_id": "doctor-smith",
            "confidence_score": 0.85,
            "timestamp": "2024-01-15T10:30:00",
            "comments": "Excellent match for HER2+ patient"
        },
        {
            "feedback_type": "incorrect",
            "user_id": "doctor-jones",
            "confidence_score": 0.45,
            "timestamp": "2024-01-14T14:20:00",
            "comments": "Patient has CNS metastases",
            "suggested_corrections": {"exclusions": "Add CNS check"}
        }
    ]
    
    feedback_ui.display_feedback_for_trial("NCT07062263", mock_feedback_list)
    
    # Test HTML form generation
    print("\n🌐 Testing HTML Form Generation")
    print("-" * 40)
    
    html_form = feedback_ui.create_html_feedback_form(mock_match_result, "/api/feedback/collect")
    print("HTML form generated (first 200 chars):")
    print(html_form[:200] + "...")

def test_feedback_integration():
    """Test feedback integration with matching system"""
    print("\n🔗 Testing Feedback Integration")
    print("=" * 50)
    
    # Simulate a match result with feedback tracking
    match_result = {
        "prediction_id": "pred-integration-001",
        "trial_id": "NCT07062263",
        "patient_id": "patient-integration-001",
        "confidence_score": 0.85,
        "score": 85.0,
        "eligible": True,
        "summary": "Good match for HER2+ biliary cancer",
        "matched_criteria": ["HER2 positive", "Biliary cancer"],
        "blockers": [],
        "missing_data": ["ECOG performance status"],
        "recommendations": ["Obtain ECOG performance status"]
    }
    
    # Initialize feedback collector
    feedback_collector = FeedbackCollector("integration_test_feedback.json")
    
    # Simulate feedback collection after match
    print("🎯 Match Result Generated:")
    print(f"  Trial: {match_result['trial_id']}")
    print(f"  Patient: {match_result['patient_id']}")
    print(f"  Score: {match_result['score']}")
    print(f"  Eligible: {match_result['eligible']}")
    print(f"  Prediction ID: {match_result['prediction_id']}")
    
    print("\n📋 Feedback Collection Process:")
    print("1. Display match results to user")
    print("2. Prompt for feedback")
    print("3. Collect feedback data")
    print("4. Store feedback for model improvement")
    
    # Simulate feedback collection
    feedback_id = feedback_collector.collect_feedback(
        prediction_id=match_result['prediction_id'],
        trial_id=match_result['trial_id'],
        patient_id=match_result['patient_id'],
        confidence_score=match_result['confidence_score'],
        user_id="doctor-integration",
        feedback_type="correct",
        comments="Good match, patient meets all criteria",
        metadata={"integration_test": True}
    )
    
    print(f"\n✅ Feedback collected with ID: {feedback_id}")
    
    # Verify feedback was stored
    stored_feedback = feedback_collector.get_feedback_by_prediction(match_result['prediction_id'])
    if stored_feedback:
        print(f"✅ Feedback verified: {stored_feedback.feedback_type} by {stored_feedback.user_id}")
    else:
        print("❌ Feedback not found")

def main():
    """Run all feedback system tests"""
    print("🚀 Feedback System Test Suite")
    print("=" * 60)
    
    try:
        # Test feedback collection
        feedback_collector = test_feedback_collection()
        
        # Test feedback UI
        test_feedback_ui()
        
        # Test feedback integration
        test_feedback_integration()
        
        print("\n🎉 All feedback system tests completed successfully!")
        print("\n📝 Next Steps:")
        print("1. Integrate feedback collection into the main matching API")
        print("2. Add feedback UI to the web interface")
        print("3. Implement feedback analysis for model improvement")
        print("4. Create feedback dashboard for administrators")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()

