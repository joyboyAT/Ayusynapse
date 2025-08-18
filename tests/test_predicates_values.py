#!/usr/bin/env python3
"""
Test Observation Value Parsing in Predicates
Tests the get_observation_value helper function and predicate evaluation
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.predicates import PredicateEvaluator, Predicate

class TestObservationValueParsing:
    """Test observation value parsing functionality"""
    
    def create_test_patient_bundle(self) -> Dict[str, Any]:
        """Create a test patient bundle with HER2 and ECOG observations"""
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-001",
                        "gender": "female",
                        "birthDate": "1968-01-01"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-her2",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "85319-0",
                                    "display": "HER2"
                                }
                            ],
                            "text": "HER2"
                        },
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "10828004",
                                    "display": "Positive"
                                }
                            ],
                            "text": "Positive"
                        },
                        "status": "final"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-ecog",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "89243-3",
                                    "display": "ECOG Performance Status"
                                }
                            ],
                            "text": "ECOG Performance Status"
                        },
                        "valueInteger": 1,
                        "status": "final"
                    }
                }
            ]
        }
    
    def test_get_observation_value_helper(self):
        """Test the get_observation_value helper function"""
        print("\n🧪 Testing get_observation_value Helper Function")
        print("=" * 60)
        
        evaluator = PredicateEvaluator()
        
        # Test HER2 observation with valueCodeableConcept
        her2_obs = {
            "text": "HER2",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "10828004",
                        "display": "Positive"
                    }
                ],
                "text": "Positive"
            }
        }
        
        value, unit = evaluator.get_observation_value(her2_obs)
        print(f"HER2 Observation:")
        print(f"   Input: {her2_obs}")
        print(f"   Extracted value: {value}")
        print(f"   Extracted unit: {unit}")
        
        assert value == "positive", f"Expected 'positive' (normalized), got {value}"
        assert unit is None, f"Expected None unit, got {unit}"
        print("   ✅ HER2 value extraction successful")
        
        # Test ECOG observation with valueInteger
        ecog_obs = {
            "text": "ECOG Performance Status",
            "valueInteger": 1
        }
        
        value, unit = evaluator.get_observation_value(ecog_obs)
        print(f"\nECOG Observation:")
        print(f"   Input: {ecog_obs}")
        print(f"   Extracted value: {value}")
        print(f"   Extracted unit: {unit}")
        
        assert value == 1, f"Expected 1, got {value}"
        assert unit is None, f"Expected None unit, got {unit}"
        print("   ✅ ECOG value extraction successful")
        
        # Test Hemoglobin observation with valueQuantity
        hb_obs = {
            "text": "Hemoglobin",
            "valueQuantity": {
                "value": 13.0,
                "unit": "g/dL"
            }
        }
        
        value, unit = evaluator.get_observation_value(hb_obs)
        print(f"\nHemoglobin Observation:")
        print(f"   Input: {hb_obs}")
        print(f"   Extracted value: {value}")
        print(f"   Extracted unit: {unit}")
        
        assert value == 13.0, f"Expected 13.0, got {value}"
        assert unit == "g/dL", f"Expected 'g/dL', got {unit}"
        print("   ✅ Hemoglobin value extraction successful")
        
        print("\n✅ All observation value extraction tests passed!")
    
    def test_predicate_evaluation_with_fhir_values(self):
        """Test predicate evaluation with proper FHIR value formats"""
        print("\n🧪 Testing Predicate Evaluation with FHIR Values")
        print("=" * 60)
        
        evaluator = PredicateEvaluator()
        
        # Create patient features with flattened structure (as produced by feature extractor)
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
                    "value": "Positive",
                    "unit": None,
                    "normalized_unit": None,
                    "category": None,
                    "status": "final"
                },
                {
                    "text": "ECOG Performance Status",
                    "codes": [
                        {"system": "http://loinc.org", "code": "89243-3", "display": "ECOG Performance Status"}
                    ],
                    "value": 1,
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
        
        # Test HER2 predicate
        her2_predicate = Predicate(
            type="Observation",
            field="HER2",
            op="==",
            value="positive",
            inclusion=True
        )
        
        print(f"\n🔍 Testing HER2 Predicate:")
        print(f"   Field: {her2_predicate.field}")
        print(f"   Operator: {her2_predicate.op}")
        print(f"   Expected Value: {her2_predicate.value}")
        

        
        result = evaluator.evaluate_predicate(patient_features, her2_predicate)
        
        print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"   Evidence: {result['evidence']}")
        
        assert result['match'] == True, f"HER2 should match, but got: {result}"
        print("   ✅ HER2 predicate evaluation successful")
        
        # Test ECOG predicate
        ecog_predicate = Predicate(
            type="Observation",
            field="ECOG Performance Status",
            op="<=",
            value=2,
            inclusion=True
        )
        
        print(f"\n🔍 Testing ECOG Predicate:")
        print(f"   Field: {ecog_predicate.field}")
        print(f"   Operator: {ecog_predicate.op}")
        print(f"   Expected Value: {ecog_predicate.value}")
        
        result = evaluator.evaluate_predicate(patient_features, ecog_predicate)
        
        print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"   Evidence: {result['evidence']}")
        
        assert result['match'] == True, f"ECOG should match, but got: {result}"
        print("   ✅ ECOG predicate evaluation successful")
        
        print("\n✅ All predicate evaluation tests passed!")
    
    def test_case_insensitive_string_comparison(self):
        """Test that string comparisons are case-insensitive"""
        print("\n🧪 Testing Case-Insensitive String Comparison")
        print("=" * 60)
        
        evaluator = PredicateEvaluator()
        
        # Test with different case variations (flattened structure)
        patient_features = {
            "age": 55,
            "gender": "female",
            "conditions": [],
            "observations": [
                {
                    "text": "HER2",
                    "value": "POSITIVE",  # Uppercase
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
        
        # Predicate expects lowercase "positive"
        her2_predicate = Predicate(
            type="Observation",
            field="HER2",
            op="==",
            value="positive",  # Lowercase
            inclusion=True
        )
        
        result = evaluator.evaluate_predicate(patient_features, her2_predicate)
        
        print(f"HER2 Observation: 'POSITIVE' (uppercase)")
        print(f"Predicate expects: 'positive' (lowercase)")
        print(f"Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"Evidence: {result['evidence']}")
        
        assert result['match'] == True, f"Case-insensitive comparison should match, but got: {result}"
        print("   ✅ Case-insensitive string comparison successful")
        
        print("\n✅ Case-insensitive comparison test passed!")

def test_integration_with_end_to_end():
    """Test that the fixes resolve the blockers in the end-to-end test"""
    print("\n🧪 Testing Integration with End-to-End Pipeline")
    print("=" * 60)
    
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
    
    # Test HER2 predicate specifically
    evaluator = PredicateEvaluator()
    her2_predicate = Predicate(
        type="Observation",
        field="HER2",
        op="==",
        value="positive",
        inclusion=True
    )
    

    
    result = evaluator.evaluate_predicate(patient_features, her2_predicate)
    
    print(f"\n🔍 HER2 Predicate Test:")
    print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
    print(f"   Evidence: {result['evidence']}")
    
    # The HER2 should now match because we can parse the valueCodeableConcept.text
    assert result['match'] == True, f"HER2 should now match with proper value parsing: {result}"
    print("   ✅ HER2 blocker resolved!")
    
    # Test ECOG predicate
    ecog_predicate = Predicate(
        type="Observation",
        field="ECOG",
        op="<=",
        value=2,
        inclusion=True
    )
    
    result = evaluator.evaluate_predicate(patient_features, ecog_predicate)
    
    print(f"\n🔍 ECOG Predicate Test:")
    print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
    print(f"   Evidence: {result['evidence']}")
    
    # The ECOG should now match because we can parse the valueInteger
    assert result['match'] == True, f"ECOG should now match with proper value parsing: {result}"
    print("   ✅ ECOG blocker resolved!")
    
    print("\n✅ Integration test passed - blockers should be resolved!")

if __name__ == "__main__":
    # Run all tests
    test_instance = TestObservationValueParsing()
    test_instance.test_get_observation_value_helper()
    test_instance.test_predicate_evaluation_with_fhir_values()
    test_instance.test_case_insensitive_string_comparison()
    test_integration_with_end_to_end()
    
    print("\n🎉 All observation value parsing tests completed successfully!")
