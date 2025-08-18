#!/usr/bin/env python3
"""
Tests for Coverage Reporting Functionality
Tests the enhanced coverage reporting system for patient-trial matching
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.coverage_report import CoverageReportGenerator, CoverageReport
from ayusynapse.matcher.predicates import Predicate, PredicateType, PredicateOperator
from ayusynapse.matcher.engine import TrialMatchResult, MatchResult

class TestCoverageReporting:
    """Test coverage reporting functionality"""
    
    def __init__(self):
        self.generator = CoverageReportGenerator()
    
    def test_biomarker_mappings(self):
        """Test biomarker mappings are loaded correctly"""
        assert "her2" in self.generator.biomarker_mappings
        assert "egfr" in self.generator.biomarker_mappings
        assert "kras" in self.generator.biomarker_mappings
        
        her2_info = self.generator.biomarker_mappings["her2"]
        assert her2_info["test_name"] == "HER2 IHC/ISH"
        assert her2_info["urgency"] == "high"
        assert "days" in her2_info["time_to_result"]
    
    def test_lab_test_mappings(self):
        """Test lab test mappings are loaded correctly"""
        assert "hemoglobin" in self.generator.lab_test_mappings
        assert "creatinine" in self.generator.lab_test_mappings
        assert "ecog" in self.generator.lab_test_mappings
        
        hgb_info = self.generator.lab_test_mappings["hemoglobin"]
        assert hgb_info["test_name"] == "Complete Blood Count (CBC)"
        assert hgb_info["urgency"] == "low"
        assert "hours" in hgb_info["time_to_result"]
    
    def test_condition_mappings(self):
        """Test condition mappings are loaded correctly"""
        assert "diabetes" in self.generator.condition_mappings
        assert "hypertension" in self.generator.condition_mappings
        
        diabetes_info = self.generator.condition_mappings["diabetes"]
        assert "Diabetes mellitus" in diabetes_info["documentation"]
        assert diabetes_info["urgency"] == "medium"
    
    def test_categorize_missing_criteria(self):
        """Test categorization of missing criteria"""
        # Test biomarker categorization
        her2_predicate = Predicate(
            type="Observation",
            field="her2",
            op=PredicateOperator.EQUALS,
            value="positive",
            inclusion=True,
            weight=1.0
        )
        assert self.generator._categorize_missing_criteria(her2_predicate) == "biomarker"
        
        # Test lab test categorization
        hgb_predicate = Predicate(
            type="Observation", 
            field="hemoglobin",
            op=PredicateOperator.GREATER_THAN,
            value=10.0,
            inclusion=True,
            weight=1.0
        )
        assert self.generator._categorize_missing_criteria(hgb_predicate) == "lab_test"
        
        # Test condition categorization
        condition_predicate = Predicate(
            type="Condition",
            field="diabetes",
            op=PredicateOperator.EQUALS,
            value="active",
            inclusion=True,
            weight=1.0
        )
        assert self.generator._categorize_missing_criteria(condition_predicate) == "condition"
        
        # Test demographic categorization
        age_predicate = Predicate(
            type="Patient",
            field="age",
            op=PredicateOperator.GREATER_THAN,
            value=18,
            inclusion=True,
            weight=1.0
        )
        assert self.generator._categorize_missing_criteria(age_predicate) == "demographic"
    
    def test_generate_recommendations(self):
        """Test generation of actionable recommendations"""
        recommendations = self.generator._generate_recommendations(
            missing_biomarkers=["her2", "kras"],
            missing_lab_tests=["hemoglobin"],
            missing_conditions=["diabetes"],
            missing_demographics=["age"],
            missing_medications=[]
        )
        
        # Should have recommendations for each missing item
        assert len(recommendations) >= 4
        
        # Check for biomarker recommendations
        her2_rec = next((r for r in recommendations if "HER2 IHC/ISH" in r), None)
        assert her2_rec is not None
        assert "3-5 days" in her2_rec
        assert "$$" in her2_rec
        
        # Check for lab test recommendations
        hgb_rec = next((r for r in recommendations if "Complete Blood Count" in r), None)
        assert hgb_rec is not None
        assert "1-2 hours" in hgb_rec
        
        # Check for condition recommendations
        diabetes_rec = next((r for r in recommendations if "Diabetes mellitus" in r), None)
        assert diabetes_rec is not None
        
        # Check for demographic recommendations
        age_rec = next((r for r in recommendations if "age" in r.lower()), None)
        assert age_rec is not None
    
    def test_generate_priority_actions(self):
        """Test generation of prioritized actions"""
        priority_actions = self.generator._generate_priority_actions(
            missing_biomarkers=["her2", "kras"],
            missing_lab_tests=["hemoglobin"],
            missing_conditions=["heart_disease"],
            missing_demographics=["age"],
            missing_medications=[]
        )
        
        # Should have priority actions
        assert len(priority_actions) >= 4
        
        # Check for urgent biomarker actions
        her2_urgent = next((a for a in priority_actions if "URGENT" in a and "HER2" in a), None)
        assert her2_urgent is not None
        
        # Check for priority condition actions
        heart_priority = next((a for a in priority_actions if "PRIORITY" in a and "Cardiac" in a), None)
        assert heart_priority is not None
        
        # Check for scheduled lab actions
        hgb_scheduled = next((a for a in priority_actions if "Schedule" in a and "CBC" in a), None)
        assert hgb_scheduled is not None
    
    def test_estimate_completion_time(self):
        """Test completion time estimation"""
        # Test with only quick lab tests
        time_quick = self.generator._estimate_completion_time(
            missing_biomarkers=[],
            missing_lab_tests=["hemoglobin", "creatinine"],
            missing_conditions=[],
            missing_demographics=[],
            missing_medications=[]
        )
        assert time_quick == "Same day"
        
        # Test with biomarker tests
        time_biomarker = self.generator._estimate_completion_time(
            missing_biomarkers=["her2"],
            missing_lab_tests=[],
            missing_conditions=[],
            missing_demographics=[],
            missing_medications=[]
        )
        assert "days" in time_biomarker or "weeks" in time_biomarker
        
        # Test with multiple long-lead items
        time_complex = self.generator._estimate_completion_time(
            missing_biomarkers=["tmb"],
            missing_lab_tests=["hemoglobin"],
            missing_conditions=["heart_disease"],
            missing_demographics=[],
            missing_medications=[]
        )
        assert "weeks" in time_complex
    
    def test_determine_confidence_level(self):
        """Test confidence level determination"""
        # Very high confidence
        assert self.generator._determine_confidence_level(95.0, 0, 0) == "Very High"
        
        # High confidence
        assert self.generator._determine_confidence_level(85.0, 1, 0) == "High"
        
        # Medium confidence
        assert self.generator._determine_confidence_level(75.0, 2, 0) == "Medium"
        
        # Low confidence
        assert self.generator._determine_confidence_level(65.0, 3, 0) == "Low"
        
        # Very low confidence
        assert self.generator._determine_confidence_level(50.0, 5, 2) == "Very Low"
    
    def test_format_coverage_summary(self):
        """Test coverage summary formatting"""
        # Test with no criteria
        summary_empty = self.generator.format_coverage_summary(
            CoverageReport(
                coverage_percentage=0.0,
                total_criteria=0,
                matched_criteria=0,
                missing_criteria=0,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=[],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert summary_empty == "No criteria to evaluate"
        
        # Test with partial coverage
        summary_partial = self.generator.format_coverage_summary(
            CoverageReport(
                coverage_percentage=80.0,
                total_criteria=5,
                matched_criteria=4,
                missing_criteria=1,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=[],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert "80.0% coverage" in summary_partial
        assert "(4/5 criteria matched)" in summary_partial
        assert "1 missing" in summary_partial
    
    def test_get_missing_biomarkers_summary(self):
        """Test missing biomarkers summary"""
        # Test with no missing biomarkers
        summary_none = self.generator.get_missing_biomarkers_summary(
            CoverageReport(
                coverage_percentage=100.0,
                total_criteria=5,
                matched_criteria=5,
                missing_criteria=0,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=[],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert summary_none == "All required biomarkers present"
        
        # Test with missing biomarkers
        summary_missing = self.generator.get_missing_biomarkers_summary(
            CoverageReport(
                coverage_percentage=80.0,
                total_criteria=5,
                matched_criteria=4,
                missing_criteria=1,
                failed_criteria=0,
                missing_biomarkers=["her2", "kras"],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=[],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert "Missing biomarkers: her2, kras" in summary_missing
    
    def test_get_next_steps_summary(self):
        """Test next steps summary"""
        # Test with no actions needed
        summary_none = self.generator.get_next_steps_summary(
            CoverageReport(
                coverage_percentage=100.0,
                total_criteria=5,
                matched_criteria=5,
                missing_criteria=0,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=[],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert summary_none == "No additional data needed"
        
        # Test with single action
        summary_single = self.generator.get_next_steps_summary(
            CoverageReport(
                coverage_percentage=80.0,
                total_criteria=5,
                matched_criteria=4,
                missing_criteria=1,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=["Order HER2 test"],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert "Next step: Order HER2 test" in summary_single
        
        # Test with multiple actions
        summary_multiple = self.generator.get_next_steps_summary(
            CoverageReport(
                coverage_percentage=60.0,
                total_criteria=5,
                matched_criteria=3,
                missing_criteria=2,
                failed_criteria=0,
                missing_biomarkers=[],
                missing_lab_tests=[],
                missing_conditions=[],
                missing_demographics=[],
                missing_medications=[],
                recommended_actions=[],
                priority_actions=["Order HER2 test", "Order KRAS test", "Get age"],
                estimated_completion_time="",
                confidence_level=""
            )
        )
        assert "Next steps: Order HER2 test and 2 more" in summary_multiple
    
    def test_generate_coverage_report_integration(self):
        """Test full coverage report generation"""
        # Create mock patient features
        patient_features = {
            "age": 55,
            "gender": "female",
            "conditions": ["breast_cancer"],
            "observations": {"hemoglobin": 12.5}
        }
        
        # Create mock trial result
        mock_result = TrialMatchResult(
            eligible=True,
            score=80.0,
            matched_inclusions=[Mock()],
            unmatched_inclusions=[],
            missing_inclusions=[
                Predicate(type="Observation", field="her2", op=PredicateOperator.EQUALS, value="positive", inclusion=True, weight=1.0),
                Predicate(type="Observation", field="kras", op=PredicateOperator.EQUALS, value="wild_type", inclusion=True, weight=1.0)
            ],
            exclusions_triggered=[],
            total_inclusions=3,
            matched_count=1,
            coverage_percentage=33.3,
            reasons=["Matched 1 inclusion criteria"],
            suggested_data=["Need HER2 test", "Need KRAS test"]
        )
        
        # Generate coverage report
        report = self.generator.generate_coverage_report(patient_features, mock_result, "TEST-001")
        
        # Verify report structure
        assert report.coverage_percentage == 33.3
        assert report.total_criteria == 3
        assert report.matched_criteria == 1
        assert report.missing_criteria == 2
        assert report.failed_criteria == 0
        
        # Verify missing biomarkers
        assert "her2" in report.missing_biomarkers
        assert "kras" in report.missing_biomarkers
        
        # Verify recommendations
        assert len(report.recommended_actions) >= 2
        assert any("HER2 IHC/ISH" in action for action in report.recommended_actions)
        assert any("KRAS Mutation Testing" in action for action in report.recommended_actions)
        
        # Verify priority actions
        assert len(report.priority_actions) >= 2
        assert any("URGENT" in action for action in report.priority_actions)
        
        # Verify completion time
        assert "days" in report.estimated_completion_time
        
        # Verify confidence level
        assert report.confidence_level in ["Very High", "High", "Medium", "Low", "Very Low"]

def main():
    """Run all tests"""
    print("🧪 Running Coverage Reporting Tests...")
    
    test_instance = TestCoverageReporting()
    
    # Run all test methods
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            method = getattr(test_instance, method_name)
            method()
            print(f"✅ {method_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name}: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

