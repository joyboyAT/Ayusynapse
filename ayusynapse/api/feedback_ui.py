"""
Feedback UI - User interface components for collecting feedback
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FeedbackPrompt:
    """Represents a feedback prompt for a trial match"""
    prediction_id: str
    trial_id: str
    patient_id: str
    confidence_score: float
    match_result: Dict[str, Any]
    feedback_callback: Callable

class FeedbackUI:
    """User interface for collecting feedback on trial matches"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def display_feedback_prompt(self, match_result: Dict[str, Any], feedback_callback: Callable) -> str:
        """
        Display feedback prompt after showing trial matches
        
        Args:
            match_result: The trial match result to get feedback on
            feedback_callback: Callback function to handle feedback submission
        
        Returns:
            feedback_id: The ID of the collected feedback
        """
        try:
            # Extract information from match result
            prediction_id = match_result.get('prediction_id', 'unknown')
            trial_id = match_result.get('trial_id', 'unknown')
            patient_id = match_result.get('patient_id', 'unknown')
            confidence_score = match_result.get('confidence_score', 0.0)
            
            # Create feedback prompt
            prompt = FeedbackPrompt(
                prediction_id=prediction_id,
                trial_id=trial_id,
                patient_id=patient_id,
                confidence_score=confidence_score,
                match_result=match_result,
                feedback_callback=feedback_callback
            )
            
            # Display the feedback interface
            return self._show_feedback_interface(prompt)
            
        except Exception as e:
            self.logger.error(f"Error displaying feedback prompt: {e}")
            raise
    
    def _show_feedback_interface(self, prompt: FeedbackPrompt) -> str:
        """
        Show the feedback interface and collect user input
        
        Args:
            prompt: The feedback prompt object
        
        Returns:
            feedback_id: The ID of the collected feedback
        """
        try:
            print("\n" + "="*60)
            print("📋 FEEDBACK REQUEST")
            print("="*60)
            
            # Display match summary
            print(f"Trial ID: {prompt.trial_id}")
            print(f"Patient ID: {prompt.patient_id}")
            print(f"Confidence Score: {prompt.confidence_score:.2f}")
            print(f"Match Score: {prompt.match_result.get('score', 'N/A')}")
            print(f"Eligible: {prompt.match_result.get('eligible', 'N/A')}")
            
            print("\nPlease provide feedback on this match:")
            print("1. Correct - The match is accurate")
            print("2. Incorrect - The match is wrong")
            print("3. Partial - The match is partially correct")
            print("4. Missing Entity - Important information was missed")
            print("5. Skip - No feedback")
            
            # Get user input
            while True:
                try:
                    choice = input("\nEnter your choice (1-5): ").strip()
                    
                    if choice == "1":
                        feedback_type = "correct"
                        break
                    elif choice == "2":
                        feedback_type = "incorrect"
                        break
                    elif choice == "3":
                        feedback_type = "partial"
                        break
                    elif choice == "4":
                        feedback_type = "missing_entity"
                        break
                    elif choice == "5":
                        print("Feedback skipped.")
                        return None
                    else:
                        print("Invalid choice. Please enter 1-5.")
                        
                except KeyboardInterrupt:
                    print("\nFeedback collection cancelled.")
                    return None
            
            # Get additional comments
            comments = input("\nAdditional comments (optional): ").strip()
            if not comments:
                comments = None
            
            # Get suggested corrections if feedback is not correct
            suggested_corrections = None
            if feedback_type != "correct":
                print("\nSuggested corrections (optional):")
                print("Format: 'field_name: corrected_value' (e.g., 'age: 65')")
                print("Press Enter to skip or type 'done' when finished")
                
                corrections = {}
                while True:
                    correction = input("Correction: ").strip()
                    if not correction or correction.lower() == 'done':
                        break
                    
                    if ':' in correction:
                        field, value = correction.split(':', 1)
                        corrections[field.strip()] = value.strip()
                
                if corrections:
                    suggested_corrections = corrections
            
            # Get user ID (in a real system, this would come from authentication)
            user_id = input("\nUser ID (optional, press Enter to use 'anonymous'): ").strip()
            if not user_id:
                user_id = "anonymous"
            
            # Submit feedback
            feedback_id = prompt.feedback_callback(
                prediction_id=prompt.prediction_id,
                trial_id=prompt.trial_id,
                patient_id=prompt.patient_id,
                confidence_score=prompt.confidence_score,
                user_id=user_id,
                feedback_type=feedback_type,
                comments=comments,
                suggested_corrections=suggested_corrections
            )
            
            print(f"\n✅ Feedback submitted successfully! Feedback ID: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            self.logger.error(f"Error showing feedback interface: {e}")
            raise
    
    def display_feedback_summary(self, feedback_stats: Dict[str, Any]):
        """
        Display a summary of collected feedback
        
        Args:
            feedback_stats: Statistics about collected feedback
        """
        try:
            print("\n" + "="*60)
            print("📊 FEEDBACK SUMMARY")
            print("="*60)
            
            print(f"Total Feedback: {feedback_stats.get('total_feedback', 0)}")
            print(f"Recent Feedback (7 days): {feedback_stats.get('recent_feedback', 0)}")
            print(f"Average Confidence: {feedback_stats.get('average_confidence', 0.0):.2f}")
            
            feedback_types = feedback_stats.get('feedback_types', {})
            if feedback_types:
                print("\nFeedback Types:")
                for feedback_type, count in feedback_types.items():
                    print(f"  {feedback_type}: {count}")
            
            print("="*60)
            
        except Exception as e:
            self.logger.error(f"Error displaying feedback summary: {e}")
    
    def display_feedback_for_trial(self, trial_id: str, feedback_list: List[Dict[str, Any]]):
        """
        Display feedback for a specific trial
        
        Args:
            trial_id: The trial ID
            feedback_list: List of feedback entries for the trial
        """
        try:
            print(f"\n📋 FEEDBACK FOR TRIAL: {trial_id}")
            print("="*60)
            
            if not feedback_list:
                print("No feedback available for this trial.")
                return
            
            for i, feedback in enumerate(feedback_list, 1):
                print(f"\nFeedback #{i}:")
                print(f"  Type: {feedback.get('feedback_type', 'N/A')}")
                print(f"  User: {feedback.get('user_id', 'N/A')}")
                print(f"  Confidence: {feedback.get('confidence_score', 'N/A')}")
                print(f"  Date: {feedback.get('timestamp', 'N/A')}")
                
                if feedback.get('comments'):
                    print(f"  Comments: {feedback['comments']}")
                
                if feedback.get('suggested_corrections'):
                    print(f"  Suggested Corrections: {feedback['suggested_corrections']}")
            
            print("="*60)
            
        except Exception as e:
            self.logger.error(f"Error displaying feedback for trial: {e}")
    
    def create_html_feedback_form(self, match_result: Dict[str, Any], api_endpoint: str) -> str:
        """
        Create HTML feedback form for web interface
        
        Args:
            match_result: The trial match result
            api_endpoint: The API endpoint for submitting feedback
        
        Returns:
            HTML string for the feedback form
        """
        try:
            prediction_id = match_result.get('prediction_id', 'unknown')
            trial_id = match_result.get('trial_id', 'unknown')
            patient_id = match_result.get('patient_id', 'unknown')
            confidence_score = match_result.get('confidence_score', 0.0)
            
            html = f"""
            <div class="feedback-form" id="feedback-{prediction_id}">
                <h3>📋 Provide Feedback</h3>
                <div class="match-summary">
                    <p><strong>Trial ID:</strong> {trial_id}</p>
                    <p><strong>Patient ID:</strong> {patient_id}</p>
                    <p><strong>Confidence:</strong> {confidence_score:.2f}</p>
                    <p><strong>Score:</strong> {match_result.get('score', 'N/A')}</p>
                    <p><strong>Eligible:</strong> {match_result.get('eligible', 'N/A')}</p>
                </div>
                
                <form id="feedbackForm-{prediction_id}" onsubmit="submitFeedback(event, '{prediction_id}')">
                    <input type="hidden" name="prediction_id" value="{prediction_id}">
                    <input type="hidden" name="trial_id" value="{trial_id}">
                    <input type="hidden" name="patient_id" value="{patient_id}">
                    <input type="hidden" name="confidence_score" value="{confidence_score}">
                    
                    <div class="form-group">
                        <label>Feedback Type:</label>
                        <select name="feedback_type" required>
                            <option value="">Select feedback type</option>
                            <option value="correct">Correct - Match is accurate</option>
                            <option value="incorrect">Incorrect - Match is wrong</option>
                            <option value="partial">Partial - Match is partially correct</option>
                            <option value="missing_entity">Missing Entity - Important info missed</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label>Comments (optional):</label>
                        <textarea name="comments" rows="3" placeholder="Additional comments..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>User ID:</label>
                        <input type="text" name="user_id" placeholder="Enter your user ID" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Submit Feedback</button>
                </form>
            </div>
            
            <script>
            async function submitFeedback(event, predictionId) {{
                event.preventDefault();
                
                const form = document.getElementById(`feedbackForm-${{predictionId}}`);
                const formData = new FormData(form);
                
                const feedbackData = {{
                    prediction_id: formData.get('prediction_id'),
                    trial_id: formData.get('trial_id'),
                    patient_id: formData.get('patient_id'),
                    confidence_score: parseFloat(formData.get('confidence_score')),
                    user_id: formData.get('user_id'),
                    feedback_type: formData.get('feedback_type'),
                    comments: formData.get('comments') || null
                }};
                
                try {{
                    const response = await fetch('{api_endpoint}', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(feedbackData)
                    }});
                    
                    if (response.ok) {{
                        const result = await response.json();
                        alert(`Feedback submitted successfully! ID: ${{result.feedback_id}}`);
                        form.reset();
                    }} else {{
                        alert('Error submitting feedback. Please try again.');
                    }}
                }} catch (error) {{
                    console.error('Error:', error);
                    alert('Error submitting feedback. Please try again.');
                }}
            }}
            </script>
            """
            
            return html
            
        except Exception as e:
            self.logger.error(f"Error creating HTML feedback form: {e}")
            return f"<p>Error creating feedback form: {str(e)}</p>"

