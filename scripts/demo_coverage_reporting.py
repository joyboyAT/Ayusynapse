#!/usr/bin/env python3
"""
Demo: Enhanced Coverage Reporting for Patient-Trial Matching
Showcases the new coverage reporting functionality with realistic examples
"""

import sys
import os
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from matcher.coverage_report import CoverageReportGenerator, CoverageReport
from matcher.predicates import Predicate, PredicateType, PredicateOperator
from matcher.engine import TrialMatchResult, MatchResult

def create_sample_patient_features() -> Dict[str, Any]:
    """Create sample patient features for demonstration"""
    return {
        "age": 58,
        "gender": "female",
        "conditions": ["breast_cancer", "hypertension"],
        "observations": {
            "hemoglobin": 11.8,
            "creatinine": 1.2,
            "ecog": 1
        },
        "medications": ["metformin", "lisinopril"]
    }

def create_sample_trial_predicates() -> List[Predicate]:
    """Create sample trial predicates for demonstration"""
    return [
        # Demographics
        Predicate(type="Patient", field="age", op=PredicateOperator.GREATER_THAN, value=18, inclusion=True, weight=1.0),
        Predicate(type="Patient", field="gender", op=PredicateOperator.EQUALS, value="female", inclusion=True, weight=1.0),
        
        # Lab tests
        Predicate(type="Observation", field="hemoglobin", op=PredicateOperator.GREATER_THAN, value=10.0, inclusion=True, weight=1.0),
        Predicate(type="Observation", field="creatinine", op=PredicateOperator.LESS_THAN, value=2.0, inclusion=True, weight=1.0),
        Predicate(type="Observation", field="ecog", op=PredicateOperator.LESS_THAN_EQUAL, value=2, inclusion=True, weight=1.0),
        
        # Biomarkers (missing)
        Predicate(type="Observation", field="her2", op=PredicateOperator.EQUALS, value="positive", inclusion=True, weight=2.0),
        Predicate(type="Observation", field="egfr", op=PredicateOperator.EQUALS, value="wild_type", inclusion=True, weight=2.0),
        Predicate(type="Observation", field="kras", op=PredicateOperator.EQUALS, value="wild_type", inclusion=True, weight=1.5),
        
        # Conditions
        Predicate(type="Condition", field="breast_cancer", op=PredicateOperator.EQUALS, value="active", inclusion=True, weight=1.0),
        
        # Exclusions
        Predicate(type="Condition", field="heart_disease", op=PredicateOperator.EQUALS, value="active", inclusion=False, weight=1.0),
        Predicate(type="Medication", field="warfarin", op=PredicateOperator.EQUALS, value="active", inclusion=False, weight=1.0)
    ]

def create_sample_trial_result(patient_features: Dict[str, Any], predicates: List[Predicate]) -> TrialMatchResult:
    """Create a sample trial result for demonstration"""
    # Simulate matching results
    matched_inclusions = [
        MatchResult(
            predicate=predicates[0],  # Age
            matched=True,
            evidence="Patient age 58 > 18"
        ),
        MatchResult(
            predicate=predicates[1],  # Gender
            matched=True,
            evidence="Patient gender female matches requirement"
        ),
        MatchResult(
            predicate=predicates[2],  # Hemoglobin
            matched=True,
            evidence="Hemoglobin 11.8 > 10.0"
        ),
        MatchResult(
            predicate=predicates[3],  # Creatinine
            matched=True,
            evidence="Creatinine 1.2 < 2.0"
        ),
        MatchResult(
            predicate=predicates[4],  # ECOG
            matched=True,
            evidence="ECOG 1 <= 2"
        ),
        MatchResult(
            predicate=predicates[7],  # Breast cancer
            matched=True,
            evidence="Breast cancer condition active"
        )
    ]
    
    unmatched_inclusions = [
        MatchResult(
            predicate=predicates[8],  # Heart disease exclusion
            matched=False,
            evidence="No heart disease documented"
        )
    ]
    
    missing_inclusions = [
        predicates[5],  # HER2
        predicates[6],  # EGFR
        predicates[7]   # KRAS
    ]
    
    total_inclusions = 8  # Only inclusion criteria
    matched_count = 6
    coverage_percentage = (matched_count / total_inclusions) * 100
    
    return TrialMatchResult(
        eligible=True,
        score=75.0,  # Good score but missing some biomarkers
        matched_inclusions=matched_inclusions,
        unmatched_inclusions=unmatched_inclusions,
        missing_inclusions=missing_inclusions,
        exclusions_triggered=[],
        total_inclusions=total_inclusions,
        matched_count=matched_count,
        coverage_percentage=coverage_percentage,
        reasons=[
            "✅ Matched 6 inclusion criteria:",
            "   • Patient.age: Patient age 58 > 18",
            "   • Patient.gender: Patient gender female matches requirement",
            "   • Observation.hemoglobin: Hemoglobin 11.8 > 10.0",
            "   • Observation.creatinine: Creatinine 1.2 < 2.0",
            "   • Observation.ecog: ECOG 1 <= 2",
            "   • Condition.breast_cancer: Breast cancer condition active",
            "⚠️  Missing data for 3 criteria:",
            "   • Observation.her2",
            "   • Observation.egfr",
            "   • Observation.kras"
        ],
        suggested_data=[
            "🔬 Need HER2 IHC/ISH testing",
            "🔬 Need EGFR mutation testing",
            "🔬 Need KRAS mutation testing"
        ]
    )

def demonstrate_coverage_reporting():
    """Demonstrate the enhanced coverage reporting functionality"""
    print("🏥 Enhanced Coverage Reporting Demo")
    print("=" * 50)
    
    # Initialize the coverage report generator
    generator = CoverageReportGenerator()
    
    # Create sample data
    patient_features = create_sample_patient_features()
    trial_predicates = create_sample_trial_predicates()
    trial_result = create_sample_trial_result(patient_features, trial_predicates)
    
    print(f"📋 Patient Profile:")
    print(f"   Age: {patient_features['age']}")
    print(f"   Gender: {patient_features['gender']}")
    print(f"   Conditions: {', '.join(patient_features['conditions'])}")
    print(f"   Lab Tests: {', '.join([f'{k}={v}' for k, v in patient_features['observations'].items()])}")
    print()
    
    print(f"🎯 Trial Requirements:")
    print(f"   Total Criteria: {trial_result.total_inclusions}")
    print(f"   Matched: {trial_result.matched_count}")
    print(f"   Missing: {len(trial_result.missing_inclusions)}")
    print(f"   Score: {trial_result.score:.1f}/100")
    print(f"   Eligible: {'✅ Yes' if trial_result.eligible else '❌ No'}")
    print()
    
    # Generate enhanced coverage report
    print("📊 Enhanced Coverage Report")
    print("-" * 30)
    
    coverage_report = generator.generate_coverage_report(
        patient_features, trial_result, "DEMO-TRIAL-001"
    )
    
    # Display coverage summary
    print(f"📈 Coverage Summary:")
    print(f"   {generator.format_coverage_summary(coverage_report)}")
    print(f"   Confidence Level: {coverage_report.confidence_level}")
    print(f"   Estimated Completion Time: {coverage_report.estimated_completion_time}")
    print()
    
    # Display missing data breakdown
    print(f"🔍 Missing Data Analysis:")
    if coverage_report.missing_biomarkers:
        print(f"   🧬 Biomarkers: {', '.join(coverage_report.missing_biomarkers)}")
    if coverage_report.missing_lab_tests:
        print(f"   🩸 Lab Tests: {', '.join(coverage_report.missing_lab_tests)}")
    if coverage_report.missing_conditions:
        print(f"   🏥 Conditions: {', '.join(coverage_report.missing_conditions)}")
    if coverage_report.missing_demographics:
        print(f"   👤 Demographics: {', '.join(coverage_report.missing_demographics)}")
    if coverage_report.missing_medications:
        print(f"   💊 Medications: {', '.join(coverage_report.missing_medications)}")
    print()
    
    # Display recommendations
    print(f"💡 Recommended Actions:")
    for i, action in enumerate(coverage_report.recommended_actions, 1):
        print(f"   {i}. {action}")
    print()
    
    # Display priority actions
    print(f"🚨 Priority Actions:")
    for i, action in enumerate(coverage_report.priority_actions, 1):
        print(f"   {i}. {action}")
    print()
    
    # Display summary methods
    print(f"📋 Summary Methods:")
    print(f"   Biomarkers: {generator.get_missing_biomarkers_summary(coverage_report)}")
    print(f"   Next Steps: {generator.get_next_steps_summary(coverage_report)}")
    print()

def demonstrate_different_scenarios():
    """Demonstrate different coverage scenarios"""
    print("🔄 Different Coverage Scenarios")
    print("=" * 40)
    
    generator = CoverageReportGenerator()
    
    # Scenario 1: Perfect match
    print("1️⃣ Perfect Match Scenario (100% coverage)")
    perfect_result = TrialMatchResult(
        eligible=True,
        score=100.0,
        matched_inclusions=[Mock() for _ in range(5)],
        unmatched_inclusions=[],
        missing_inclusions=[],
        exclusions_triggered=[],
        total_inclusions=5,
        matched_count=5,
        coverage_percentage=100.0,
        reasons=["All criteria matched"],
        suggested_data=[]
    )
    
    perfect_report = generator.generate_coverage_report({}, perfect_result, "PERFECT-TRIAL")
    print(f"   Coverage: {generator.format_coverage_summary(perfect_report)}")
    print(f"   Confidence: {perfect_report.confidence_level}")
    print(f"   Next Steps: {generator.get_next_steps_summary(perfect_report)}")
    print()
    
    # Scenario 2: Missing critical biomarkers
    print("2️⃣ Missing Critical Biomarkers (60% coverage)")
    biomarker_result = TrialMatchResult(
        eligible=False,
        score=60.0,
        matched_inclusions=[Mock() for _ in range(3)],
        unmatched_inclusions=[],
        missing_inclusions=[
            Predicate(type="Observation", field="her2", op=PredicateOperator.EQUALS, value="positive", inclusion=True, weight=2.0),
            Predicate(type="Observation", field="egfr", op=PredicateOperator.EQUALS, value="wild_type", inclusion=True, weight=2.0)
        ],
        exclusions_triggered=[],
        total_inclusions=5,
        matched_count=3,
        coverage_percentage=60.0,
        reasons=["Missing critical biomarkers"],
        suggested_data=["Need HER2 test", "Need EGFR test"]
    )
    
    biomarker_report = generator.generate_coverage_report({}, biomarker_result, "BIOMARKER-TRIAL")
    print(f"   Coverage: {generator.format_coverage_summary(biomarker_report)}")
    print(f"   Confidence: {biomarker_report.confidence_level}")
    print(f"   Missing: {generator.get_missing_biomarkers_summary(biomarker_report)}")
    print(f"   Next Steps: {generator.get_next_steps_summary(biomarker_report)}")
    print()
    
    # Scenario 3: Multiple missing items
    print("3️⃣ Multiple Missing Items (40% coverage)")
    complex_result = TrialMatchResult(
        eligible=False,
        score=40.0,
        matched_inclusions=[Mock() for _ in range(2)],
        unmatched_inclusions=[],
        missing_inclusions=[
            Predicate(type="Observation", field="her2", op=PredicateOperator.EQUALS, value="positive", inclusion=True, weight=2.0),
            Predicate(type="Observation", field="kras", op=PredicateOperator.EQUALS, value="wild_type", inclusion=True, weight=1.5),
            Predicate(type="Observation", field="hemoglobin", op=PredicateOperator.GREATER_THAN, value=10.0, inclusion=True, weight=1.0),
            Predicate(type="Condition", field="diabetes", op=PredicateOperator.EQUALS, value="active", inclusion=True, weight=1.0),
            Predicate(type="Patient", field="age", op=PredicateOperator.GREATER_THAN, value=18, inclusion=True, weight=1.0)
        ],
        exclusions_triggered=[],
        total_inclusions=7,
        matched_count=2,
        coverage_percentage=28.6,
        reasons=["Multiple missing criteria"],
        suggested_data=["Need multiple tests and documentation"]
    )
    
    complex_report = generator.generate_coverage_report({}, complex_result, "COMPLEX-TRIAL")
    print(f"   Coverage: {generator.format_coverage_summary(complex_report)}")
    print(f"   Confidence: {complex_report.confidence_level}")
    print(f"   Completion Time: {complex_report.estimated_completion_time}")
    print(f"   Next Steps: {generator.get_next_steps_summary(complex_report)}")
    print()

def demonstrate_biomarker_mappings():
    """Demonstrate the biomarker mappings"""
    print("🧬 Biomarker Mappings")
    print("=" * 25)
    
    generator = CoverageReportGenerator()
    
    print("Supported Biomarkers:")
    for biomarker, info in generator.biomarker_mappings.items():
        print(f"   • {biomarker.upper()}: {info['test_name']}")
        print(f"     - Urgency: {info['urgency']}")
        print(f"     - Time to Result: {info['time_to_result']}")
        print(f"     - Cost: {info['cost']}")
        print(f"     - Description: {info['description']}")
        print()
    
    print("Supported Lab Tests:")
    for test, info in list(generator.lab_test_mappings.items())[:3]:  # Show first 3
        print(f"   • {test.upper()}: {info['test_name']}")
        print(f"     - Urgency: {info['urgency']}")
        print(f"     - Time to Result: {info['time_to_result']}")
        print(f"     - Cost: {info['cost']}")
        print()

def main():
    """Main demonstration function"""
    print("🎯 Enhanced Coverage Reporting for Patient-Trial Matching")
    print("=" * 60)
    print()
    
    try:
        # Demonstrate main functionality
        demonstrate_coverage_reporting()
        
        # Demonstrate different scenarios
        demonstrate_different_scenarios()
        
        # Demonstrate biomarker mappings
        demonstrate_biomarker_mappings()
        
        print("✅ Demo completed successfully!")
        print()
        print("📝 Key Features Demonstrated:")
        print("   • Comprehensive coverage analysis")
        print("   • Missing data categorization")
        print("   • Actionable recommendations")
        print("   • Priority-based action planning")
        print("   • Time and cost estimates")
        print("   • Confidence level assessment")
        print("   • Multiple output formats")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

