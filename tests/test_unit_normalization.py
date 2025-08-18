#!/usr/bin/env python3
"""
Test Lab Unit Normalization
Tests the normalize_unit function for converting lab values to standard units
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.features import normalize_unit, FeatureExtractor
from ayusynapse.matcher.predicates import PredicateEvaluator, Predicate

class TestUnitNormalization:
    """Test unit normalization functionality"""
    
    def test_hemoglobin_normalization(self):
        """Test hemoglobin unit conversions"""
        print("\n🧪 Testing Hemoglobin Normalization")
        print("=" * 50)
        
        # Test g/dL → g/L conversion
        assert normalize_unit(13, "g/dL") == 130, "13 g/dL should convert to 130 g/L"
        assert normalize_unit(12.5, "g/dL") == 125, "12.5 g/dL should convert to 125 g/L"
        assert normalize_unit(15.2, "g/dL") == 152, "15.2 g/dL should convert to 152 g/L"
        print("✅ g/dL → g/L conversions working correctly")
        
        # Test g/L (already standard)
        assert normalize_unit(130, "g/L") == 130, "130 g/L should remain 130 g/L"
        assert normalize_unit(125, "g/L") == 125, "125 g/L should remain 125 g/L"
        print("✅ g/L values remain unchanged")
        
        # Test case insensitivity
        assert normalize_unit(13, "G/DL") == 130, "Case insensitive conversion should work"
        assert normalize_unit(13, "g/dl") == 130, "Lowercase conversion should work"
        print("✅ Case insensitivity working correctly")
        
        print("✅ All hemoglobin normalization tests passed!")
    
    def test_glucose_normalization(self):
        """Test glucose unit conversions"""
        print("\n🧪 Testing Glucose Normalization")
        print("=" * 50)
        
        # Test mg/dL → mmol/L conversion
        assert abs(normalize_unit(90, "mg/dL") - 5.0) < 0.01, "90 mg/dL should convert to ~5.0 mmol/L"
        assert abs(normalize_unit(126, "mg/dL") - 7.0) < 0.01, "126 mg/dL should convert to ~7.0 mmol/L"
        assert abs(normalize_unit(200, "mg/dL") - 11.1) < 0.01, "200 mg/dL should convert to ~11.1 mmol/L"
        print("✅ mg/dL → mmol/L conversions working correctly")
        
        # Test mmol/L (already standard)
        assert normalize_unit(5.0, "mmol/L") == 5.0, "5.0 mmol/L should remain 5.0 mmol/L"
        assert normalize_unit(7.0, "mmol/L") == 7.0, "7.0 mmol/L should remain 7.0 mmol/L"
        print("✅ mmol/L values remain unchanged")
        
        print("✅ All glucose normalization tests passed!")
    
    def test_creatinine_normalization(self):
        """Test creatinine unit conversions"""
        print("\n🧪 Testing Creatinine Normalization")
        print("=" * 50)
        
        # Test mg/dL → μmol/L conversion
        assert abs(normalize_unit(1.0, "mg/dL") - 88.4) < 0.1, "1.0 mg/dL should convert to ~88.4 μmol/L"
        assert abs(normalize_unit(1.5, "mg/dL") - 132.6) < 0.1, "1.5 mg/dL should convert to ~132.6 μmol/L"
        print("✅ mg/dL → μmol/L conversions working correctly")
        
        # Test μmol/L (already standard)
        assert normalize_unit(88.4, "μmol/L") == 88.4, "88.4 μmol/L should remain 88.4 μmol/L"
        assert normalize_unit(88.4, "umol/L") == 88.4, "Alternative spelling should work"
        print("✅ μmol/L values remain unchanged")
        
        print("✅ All creatinine normalization tests passed!")
    
    def test_sodium_normalization(self):
        """Test sodium unit conversions"""
        print("\n🧪 Testing Sodium Normalization")
        print("=" * 50)
        
        # Test mEq/L → mmol/L conversion (1:1 for monovalent ions)
        assert normalize_unit(140, "mEq/L") == 140, "140 mEq/L should convert to 140 mmol/L"
        assert normalize_unit(135, "mEq/L") == 135, "135 mEq/L should convert to 135 mmol/L"
        print("✅ mEq/L → mmol/L conversions working correctly")
        
        # Test mmol/L (already standard)
        assert normalize_unit(140, "mmol/L") == 140, "140 mmol/L should remain 140 mmol/L"
        print("✅ mmol/L values remain unchanged")
        
        print("✅ All sodium normalization tests passed!")
    
    def test_calcium_normalization(self):
        """Test calcium unit conversions"""
        print("\n🧪 Testing Calcium Normalization")
        print("=" * 50)
        
        # Test mg/dL → mmol/L conversion
        assert abs(normalize_unit(10.0, "mg/dL") - 2.5) < 0.01, "10.0 mg/dL should convert to ~2.5 mmol/L"
        assert abs(normalize_unit(8.0, "mg/dL") - 2.0) < 0.01, "8.0 mg/dL should convert to ~2.0 mmol/L"
        print("✅ mg/dL → mmol/L conversions working correctly")
        
        # Test mmol/L (already standard)
        assert normalize_unit(2.5, "mmol/L") == 2.5, "2.5 mmol/L should remain 2.5 mmol/L"
        print("✅ mmol/L values remain unchanged")
        
        print("✅ All calcium normalization tests passed!")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases")
        print("=" * 50)
        
        # Test invalid inputs
        assert normalize_unit(None, "g/dL") is None, "None value should return None"
        assert normalize_unit("invalid", "g/dL") == "invalid", "Non-numeric value should return unchanged"
        assert normalize_unit(13, None) == 13, "None unit should return original value"
        assert normalize_unit(13, "") == 13, "Empty unit should return original value"
        print("✅ Invalid inputs handled correctly")
        
        # Test unknown units
        assert normalize_unit(13, "unknown_unit") == 13, "Unknown unit should return original value"
        assert normalize_unit(13, "xyz") == 13, "Unknown unit should return original value"
        print("✅ Unknown units handled correctly")
        
        # Test whitespace handling
        assert normalize_unit(13, "  g/dL  ") == 130, "Whitespace should be stripped"
        assert normalize_unit(13, "\tg/dL\n") == 130, "Various whitespace should be handled"
        print("✅ Whitespace handling working correctly")
        
        print("✅ All edge case tests passed!")
    
    def test_integration_with_feature_extraction(self):
        """Test unit normalization integration with feature extraction"""
        print("\n🧪 Testing Integration with Feature Extraction")
        print("=" * 50)
        
        # Create a sample patient bundle with lab values
        patient_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-001",
                        "gender": "female",
                        "birthDate": "1985-03-15"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-hb",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "718-7",
                                    "display": "Hemoglobin"
                                }
                            ],
                            "text": "Hemoglobin"
                        },
                        "valueQuantity": {
                            "value": 13.5,
                            "unit": "g/dL"
                        },
                        "status": "final",
                        "category": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                        "code": "laboratory"
                                    }
                                ]
                            }
                        ]
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "observation-glucose",
                        "subject": {"reference": "Patient/patient-001"},
                        "code": {
                            "coding": [
                                {
                                    "system": "http://loinc.org",
                                    "code": "2339-0",
                                    "display": "Glucose"
                                }
                            ],
                            "text": "Glucose"
                        },
                        "valueQuantity": {
                            "value": 126,
                            "unit": "mg/dL"
                        },
                        "status": "final",
                        "category": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                        "code": "laboratory"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        # Extract features
        extractor = FeatureExtractor()
        patient_features = extractor.extract_patient_features(patient_bundle)
        
        print(f"✅ Extracted patient features: age={patient_features.age}, gender={patient_features.gender}")
        print(f"   Lab results: {len(patient_features.lab_results)}")
        
        # Check that lab values were normalized
        for lab in patient_features.lab_results:
            print(f"   Lab: {lab['text']}")
            print(f"     Original value: {lab.get('original_value', 'N/A')}")
            print(f"     Normalized value: {lab['value']}")
            print(f"     Unit: {lab['unit']}")
            
            if lab['text'] == 'Hemoglobin':
                assert lab['value'] == 135, f"Hemoglobin should be normalized to 135 g/L, got {lab['value']}"
                assert lab.get('original_value') == 13.5, f"Original value should be preserved"
            elif lab['text'] == 'Glucose':
                assert abs(lab['value'] - 7.0) < 0.01, f"Glucose should be normalized to ~7.0 mmol/L, got {lab['value']}"
                assert lab.get('original_value') == 126, f"Original value should be preserved"
        
        print("✅ Feature extraction with unit normalization working correctly!")
    
    def test_predicate_evaluation_with_normalized_values(self):
        """Test predicate evaluation with normalized lab values"""
        print("\n🧪 Testing Predicate Evaluation with Normalized Values")
        print("=" * 50)
        
        # Create patient features with normalized lab values
        patient_features = {
            "age": 55,
            "gender": "female",
            "conditions": [],
            "observations": [],
            "medications": [],
            "lab_results": [
                {
                    "text": "Hemoglobin",
                    "value": 135,  # Normalized from 13.5 g/dL
                    "unit": "g/dL",
                    "original_value": 13.5,
                    "status": "final"
                },
                {
                    "text": "Glucose",
                    "value": 7.0,  # Normalized from 126 mg/dL
                    "unit": "mg/dL",
                    "original_value": 126,
                    "status": "final"
                }
            ],
            "vital_signs": {}
        }
        
        # Test hemoglobin predicate with g/L units
        hb_predicate = Predicate(
            type="Observation",
            field="Hemoglobin",
            op=">=",
            value=120,  # 120 g/L
            unit="g/L",
            inclusion=True
        )
        
        evaluator = PredicateEvaluator()
        result = evaluator.evaluate_predicate(patient_features, hb_predicate)
        
        print(f"🔍 Hemoglobin Test:")
        print(f"   Patient value: 135 g/L (normalized from 13.5 g/dL)")
        print(f"   Predicate: >= 120 g/L")
        print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"   Evidence: {result['evidence']}")
        
        assert result['match'] == True, f"Hemoglobin should match: {result}"
        print("   ✅ Hemoglobin predicate evaluation successful!")
        
        # Test glucose predicate with mmol/L units
        glucose_predicate = Predicate(
            type="Observation",
            field="Glucose",
            op=">=",
            value=7.0,  # 7.0 mmol/L
            unit="mmol/L",
            inclusion=True
        )
        
        result = evaluator.evaluate_predicate(patient_features, glucose_predicate)
        
        print(f"\n🔍 Glucose Test:")
        print(f"   Patient value: 7.0 mmol/L (normalized from 126 mg/dL)")
        print(f"   Predicate: >= 7.0 mmol/L")
        print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"   Evidence: {result['evidence']}")
        
        assert result['match'] == True, f"Glucose should match: {result}"
        print("   ✅ Glucose predicate evaluation successful!")
        
        print("\n✅ All predicate evaluation tests with normalized values passed!")

def test_comprehensive_unit_conversions():
    """Test comprehensive unit conversions for various lab tests"""
    print("\n🧪 Testing Comprehensive Unit Conversions")
    print("=" * 60)
    
    # Test cases: (original_value, original_unit, expected_normalized_value, test_name)
    test_cases = [
        # Hemoglobin
        (13.5, "g/dL", 135, "Hemoglobin g/dL → g/L"),
        (130, "g/L", 130, "Hemoglobin g/L (already standard)"),
        
        # Glucose
        (90, "mg/dL", 5.0, "Glucose mg/dL → mmol/L"),
        (126, "mg/dL", 7.0, "Glucose mg/dL → mmol/L"),
        (5.0, "mmol/L", 5.0, "Glucose mmol/L (already standard)"),
        
        # Creatinine
        (1.0, "mg/dL", 88.4, "Creatinine mg/dL → μmol/L"),
        (1.5, "mg/dL", 132.6, "Creatinine mg/dL → μmol/L"),
        (88.4, "μmol/L", 88.4, "Creatinine μmol/L (already standard)"),
        
        # Sodium
        (140, "mEq/L", 140, "Sodium mEq/L → mmol/L"),
        (135, "mmol/L", 135, "Sodium mmol/L (already standard)"),
        
        # Calcium
        (10.0, "mg/dL", 2.5, "Calcium mg/dL → mmol/L"),
        (2.5, "mmol/L", 2.5, "Calcium mmol/L (already standard)"),
        
        # Bilirubin
        (1.0, "mg/dL", 17.1, "Bilirubin mg/dL → μmol/L"),
        (17.1, "μmol/L", 17.1, "Bilirubin μmol/L (already standard)"),
        
        # Albumin
        (4.0, "g/dL", 40, "Albumin g/dL → g/L"),
        (40, "g/L", 40, "Albumin g/L (already standard)"),
        
        # Cholesterol
        (200, "mg/dL", 5.18, "Cholesterol mg/dL → mmol/L"),
        (5.18, "mmol/L", 5.18, "Cholesterol mmol/L (already standard)"),
    ]
    
    for original_value, original_unit, expected_value, test_name in test_cases:
        normalized_value = normalize_unit(original_value, original_unit)
        
        # Use tolerance for floating point comparisons
        if isinstance(expected_value, float):
            assert abs(normalized_value - expected_value) < 0.01, f"{test_name}: Expected {expected_value}, got {normalized_value}"
        else:
            assert normalized_value == expected_value, f"{test_name}: Expected {expected_value}, got {normalized_value}"
        
        print(f"   ✅ {test_name}: {original_value} {original_unit} → {normalized_value}")
    
    print("✅ All comprehensive unit conversion tests passed!")

if __name__ == "__main__":
    # Run all tests
    test_instance = TestUnitNormalization()
    test_instance.test_hemoglobin_normalization()
    test_instance.test_glucose_normalization()
    test_instance.test_creatinine_normalization()
    test_instance.test_sodium_normalization()
    test_instance.test_calcium_normalization()
    test_instance.test_edge_cases()
    test_instance.test_integration_with_feature_extraction()
    test_instance.test_predicate_evaluation_with_normalized_values()
    test_comprehensive_unit_conversions()
    
    print("\n🎉 All unit normalization tests completed successfully!")
