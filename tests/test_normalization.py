#!/usr/bin/env python3
"""
Test Normalization Helper Function
Tests the normalize_enum function for handling variant string formats
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.features import normalize_enum
from ayusynapse.matcher.predicates import PredicateEvaluator, Predicate

class TestNormalization:
    """Test normalization functionality"""
    
    def test_normalize_enum_basic(self):
        """Test basic normalization cases"""
        print("\n🧪 Testing Basic Normalization")
        print("=" * 50)
        
        # Test positive variations
        assert normalize_enum("Positive") == "positive"
        assert normalize_enum("POS") == "positive"
        assert normalize_enum("+") == "positive"
        print("✅ Positive variations normalized correctly")
        
        # Test negative variations
        assert normalize_enum("negative") == "negative"
        assert normalize_enum("NEG") == "negative"
        assert normalize_enum("-") == "negative"
        print("✅ Negative variations normalized correctly")
        
        # Test boolean variations
        assert normalize_enum("Yes") == "true"
        assert normalize_enum("TRUE") == "true"
        assert normalize_enum("Present") == "true"
        assert normalize_enum("No") == "false"
        assert normalize_enum("FALSE") == "false"
        assert normalize_enum("Absent") == "false"
        print("✅ Boolean variations normalized correctly")
        
        # Test edge cases
        assert normalize_enum("") is None
        assert normalize_enum(None) is None
        assert normalize_enum("   ") is None
        print("✅ Edge cases handled correctly")
        
        # Test unknown values (should return cleaned lowercase)
        assert normalize_enum("Unknown") == "unknown"
        assert normalize_enum("ECOG 1") == "ecog 1"
        assert normalize_enum("Stage II") == "stage ii"
        print("✅ Unknown values return cleaned lowercase")
        
        print("✅ All basic normalization tests passed!")
    
    def test_normalize_enum_case_insensitive(self):
        """Test case insensitivity"""
        print("\n🧪 Testing Case Insensitivity")
        print("=" * 50)
        
        # Test various case combinations
        assert normalize_enum("POSITIVE") == "positive"
        assert normalize_enum("Positive") == "positive"
        assert normalize_enum("positive") == "positive"
        assert normalize_enum("PosItIvE") == "positive"
        
        assert normalize_enum("NEGATIVE") == "negative"
        assert normalize_enum("Negative") == "negative"
        assert normalize_enum("negative") == "negative"
        assert normalize_enum("NeGaTiVe") == "negative"
        
        print("✅ Case insensitivity working correctly!")
    
    def test_normalize_enum_whitespace(self):
        """Test whitespace handling"""
        print("\n🧪 Testing Whitespace Handling")
        print("=" * 50)
        
        # Test with various whitespace
        assert normalize_enum("  positive  ") == "positive"
        assert normalize_enum("\tnegative\n") == "negative"
        assert normalize_enum("  POS  ") == "positive"
        assert normalize_enum("  +  ") == "positive"
        
        print("✅ Whitespace handling working correctly!")
    
    def test_predicate_evaluation_with_normalization(self):
        """Test predicate evaluation with normalized values"""
        print("\n🧪 Testing Predicate Evaluation with Normalization")
        print("=" * 50)
        
        evaluator = PredicateEvaluator()
        
        # Test with various HER2 value formats
        test_cases = [
            ("POS", "positive", True),
            ("Positive", "positive", True),
            ("pos", "positive", True),
            ("+", "positive", True),
            ("NEG", "negative", False),
            ("Negative", "negative", False),
            ("neg", "negative", False),
            ("-", "negative", False),
        ]
        
        for obs_value, expected_normalized, should_match_positive in test_cases:
            # Create patient features with the test value
            patient_features = {
                "age": 55,
                "gender": "female",
                "conditions": [],
                "observations": [
                    {
                        "text": "HER2",
                        "value": obs_value,
                        "unit": None,
                        "normalized_unit": None,
                        "category": None,
                        "status": "final"
                    }
                ],
                "medications": [],
                "lab_results": [],
                "vital_signs": {}
            }
            
            # Test against positive predicate
            positive_predicate = Predicate(
                type="Observation",
                field="HER2",
                op="==",
                value="positive",
                inclusion=True
            )
            
            result = evaluator.evaluate_predicate(patient_features, positive_predicate)
            
            print(f"   Testing '{obs_value}' vs 'positive': {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
            
            if should_match_positive:
                assert result['match'] == True, f"'{obs_value}' should match 'positive'"
            else:
                assert result['match'] == False, f"'{obs_value}' should not match 'positive'"
        
        print("✅ All predicate evaluation tests with normalization passed!")
    
    def test_end_to_end_normalization(self):
        """Test end-to-end normalization with FHIR data"""
        print("\n🧪 Testing End-to-End Normalization")
        print("=" * 50)
        
        evaluator = PredicateEvaluator()
        
        # Create patient with HER2 observation using "POS" value
        patient_features = {
            "age": 55,
            "gender": "female",
            "conditions": [],
            "observations": [
                {
                    "text": "HER2",
                    "codes": [
                        {"system": "http://loinc.org", "code": "85319-0", "display": "HER2"}
                    ],
                    "value": "POS",  # This should be normalized to "positive"
                    "unit": None,
                    "normalized_unit": None,
                    "category": None,
                    "status": "final"
                }
            ],
            "medications": [],
            "lab_results": [],
            "vital_signs": {}
        }
        
        # Create trial predicate expecting "positive"
        trial_predicate = Predicate(
            type="Observation",
            field="HER2",
            op="==",
            value="positive",  # This should match the normalized "POS"
            inclusion=True
        )
        
        # Evaluate the predicate
        result = evaluator.evaluate_predicate(patient_features, trial_predicate)
        
        print(f"Patient HER2 value: 'POS'")
        print(f"Trial predicate value: 'positive'")
        print(f"Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"Evidence: {result['evidence']}")
        
        # This should match because "POS" normalizes to "positive"
        assert result['match'] == True, f"HER2 'POS' should match predicate 'positive'"
        print("✅ End-to-end normalization test passed!")
    
    def test_various_boolean_formats(self):
        """Test various boolean value formats"""
        print("\n🧪 Testing Various Boolean Formats")
        print("=" * 50)
        
        # Test true variations
        true_variations = ["yes", "Yes", "YES", "true", "True", "TRUE", "present", "Present", "PRESENT"]
        for val in true_variations:
            normalized = normalize_enum(val)
            assert normalized == "true", f"'{val}' should normalize to 'true', got '{normalized}'"
        
        # Test false variations
        false_variations = ["no", "No", "NO", "false", "False", "FALSE", "absent", "Absent", "ABSENT"]
        for val in false_variations:
            normalized = normalize_enum(val)
            assert normalized == "false", f"'{val}' should normalize to 'false', got '{normalized}'"
        
        print("✅ All boolean format variations normalized correctly!")

def test_normalization_integration():
    """Test normalization integration with the full pipeline"""
    print("\n🧪 Testing Normalization Integration")
    print("=" * 50)
    
    from tests.test_end_to_end import TestEndToEndPipeline
    
    # Create the test instance
    test_instance = TestEndToEndPipeline()
    
    # Get the sample patient bundle
    patient_bundle = test_instance.create_sample_patient_bundle()
    
    # Extract features
    from ayusynapse.matcher.features import FeatureExtractor
    feature_extractor = FeatureExtractor()
    patient_features = feature_extractor.extract_patient_features(patient_bundle)
    
    print(f"✅ Extracted patient features: age={patient_features.age}, gender={patient_features.gender}")
    print(f"   Conditions: {len(patient_features.conditions)}")
    print(f"   Observations: {len(patient_features.observations)}")
    
    # Test HER2 predicate with normalization
    evaluator = PredicateEvaluator()
    her2_predicate = Predicate(
        type="Observation",
        field="HER2",
        op="==",
        value="positive",
        inclusion=True
    )
    
    result = evaluator.evaluate_predicate(patient_features, her2_predicate)
    
    print(f"\n🔍 HER2 Predicate Test (with normalization):")
    print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
    print(f"   Evidence: {result['evidence']}")
    
    # The HER2 should match because normalization handles the value format
    assert result['match'] == True, f"HER2 should match with normalization: {result}"
    print("   ✅ HER2 normalization integration successful!")
    
    print("\n✅ Normalization integration test passed!")

if __name__ == "__main__":
    # Run all tests
    test_instance = TestNormalization()
    test_instance.test_normalize_enum_basic()
    test_instance.test_normalize_enum_case_insensitive()
    test_instance.test_normalize_enum_whitespace()
    test_instance.test_predicate_evaluation_with_normalization()
    test_instance.test_end_to_end_normalization()
    test_instance.test_various_boolean_formats()
    test_normalization_integration()
    
    print("\n🎉 All normalization tests completed successfully!")
