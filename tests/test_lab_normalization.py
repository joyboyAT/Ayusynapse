#!/usr/bin/env python3
"""
Test Lab Unit Normalization
Tests the normalize_unit function for various lab value conversions
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.features import normalize_unit

class TestLabNormalization:
    """Test lab unit normalization functionality"""
    
    def test_hemoglobin_conversions(self):
        """Test hemoglobin unit conversions"""
        print("\n🧪 Testing Hemoglobin Conversions")
        print("=" * 50)
        
        # Test g/dL → g/L conversion
        assert normalize_unit(13.0, "g/dL") == 130.0, "13 g/dL should convert to 130 g/L"
        assert normalize_unit(15.5, "g/dL") == 155.0, "15.5 g/dL should convert to 155 g/L"
        print("✅ g/dL → g/L conversions working correctly")
        
        # Test g/L (already standard unit)
        assert normalize_unit(130.0, "g/L") == 130.0, "130 g/L should remain 130 g/L"
        assert normalize_unit(155.0, "g/L") == 155.0, "155 g/L should remain 155 g/L"
        print("✅ g/L (standard unit) preserved correctly")
        
        # Test case insensitivity
        assert normalize_unit(13.0, "G/DL") == 130.0, "Case insensitive conversion should work"
        assert normalize_unit(13.0, "g/dl") == 130.0, "Case insensitive conversion should work"
        print("✅ Case insensitivity working correctly")
        
        print("✅ All hemoglobin conversions passed!")
    
    def test_glucose_conversions(self):
        """Test glucose unit conversions"""
        print("\n🧪 Testing Glucose Conversions")
        print("=" * 50)
        
        # Test mg/dL → mmol/L conversion
        assert normalize_unit(90.0, "mg/dL", "glucose") == pytest.approx(4.995, rel=1e-3), "90 mg/dL glucose should convert to ~5 mmol/L"
        assert normalize_unit(126.0, "mg/dL", "glucose") == pytest.approx(6.993, rel=1e-3), "126 mg/dL glucose should convert to ~7 mmol/L"
        print("✅ mg/dL → mmol/L glucose conversions working correctly")
        
        # Test mmol/L (already standard unit)
        assert normalize_unit(5.0, "mmol/L", "glucose") == 5.0, "5 mmol/L should remain 5 mmol/L"
        assert normalize_unit(7.0, "mmol/L", "glucose") == 7.0, "7 mmol/L should remain 7 mmol/L"
        print("✅ mmol/L (standard unit) preserved correctly")
        
        print("✅ All glucose conversions passed!")
    
    def test_creatinine_conversions(self):
        """Test creatinine unit conversions"""
        print("\n🧪 Testing Creatinine Conversions")
        print("=" * 50)
        
        # Test mg/dL → μmol/L conversion
        assert normalize_unit(1.0, "mg/dL", "creatinine") == 88.4, "1 mg/dL creatinine should convert to 88.4 μmol/L"
        assert normalize_unit(1.5, "mg/dL", "creatinine") == 132.6, "1.5 mg/dL creatinine should convert to 132.6 μmol/L"
        print("✅ mg/dL → μmol/L creatinine conversions working correctly")
        
        # Test μmol/L (already standard unit)
        assert normalize_unit(88.4, "μmol/L", "creatinine") == 88.4, "88.4 μmol/L should remain 88.4 μmol/L"
        assert normalize_unit(132.6, "umol/L", "creatinine") == 132.6, "132.6 umol/L should remain 132.6 umol/L"
        print("✅ μmol/L (standard unit) preserved correctly")
        
        print("✅ All creatinine conversions passed!")
    
    def test_calcium_conversions(self):
        """Test calcium unit conversions"""
        print("\n🧪 Testing Calcium Conversions")
        print("=" * 50)
        
        # Test mg/dL → mmol/L conversion
        assert normalize_unit(10.0, "mg/dL", "calcium") == 2.5, "10 mg/dL calcium should convert to 2.5 mmol/L"
        assert normalize_unit(12.0, "mg/dL", "calcium") == 3.0, "12 mg/dL calcium should convert to 3.0 mmol/L"
        print("✅ mg/dL → mmol/L calcium conversions working correctly")
        
        # Test mmol/L (already standard unit)
        assert normalize_unit(2.5, "mmol/L", "calcium") == 2.5, "2.5 mmol/L should remain 2.5 mmol/L"
        assert normalize_unit(3.0, "mmol/L", "calcium") == 3.0, "3.0 mmol/L should remain 3.0 mmol/L"
        print("✅ mmol/L (standard unit) preserved correctly")
        
        print("✅ All calcium conversions passed!")
    
    def test_bilirubin_conversions(self):
        """Test bilirubin unit conversions"""
        print("\n🧪 Testing Bilirubin Conversions")
        print("=" * 50)
        
        # Test mg/dL → μmol/L conversion
        assert normalize_unit(1.0, "mg/dL", "bilirubin") == 17.1, "1 mg/dL bilirubin should convert to 17.1 μmol/L"
        assert normalize_unit(2.0, "mg/dL", "bilirubin") == 34.2, "2 mg/dL bilirubin should convert to 34.2 μmol/L"
        print("✅ mg/dL → μmol/L bilirubin conversions working correctly")
        
        # Test μmol/L (already standard unit)
        assert normalize_unit(17.1, "μmol/L", "bilirubin") == 17.1, "17.1 μmol/L should remain 17.1 μmol/L"
        assert normalize_unit(34.2, "umol/L", "bilirubin") == 34.2, "34.2 umol/L should remain 34.2 umol/L"
        print("✅ μmol/L (standard unit) preserved correctly")
        
        print("✅ All bilirubin conversions passed!")
    
    def test_albumin_conversions(self):
        """Test albumin unit conversions"""
        print("\n🧪 Testing Albumin Conversions")
        print("=" * 50)
        
        # Test g/dL → g/L conversion
        assert normalize_unit(4.0, "g/dL", "albumin") == 40.0, "4 g/dL albumin should convert to 40 g/L"
        assert normalize_unit(3.5, "g/dL", "albumin") == 35.0, "3.5 g/dL albumin should convert to 35 g/L"
        print("✅ g/dL → g/L albumin conversions working correctly")
        
        # Test g/L (already standard unit)
        assert normalize_unit(40.0, "g/L", "albumin") == 40.0, "40 g/L should remain 40 g/L"
        assert normalize_unit(35.0, "g/L", "albumin") == 35.0, "35 g/L should remain 35 g/L"
        print("✅ g/L (standard unit) preserved correctly")
        
        print("✅ All albumin conversions passed!")
    
    def test_cholesterol_conversions(self):
        """Test cholesterol unit conversions"""
        print("\n🧪 Testing Cholesterol Conversions")
        print("=" * 50)
        
        # Test mg/dL → mmol/L conversion
        assert normalize_unit(200.0, "mg/dL", "cholesterol") == pytest.approx(5.18, rel=1e-3), "200 mg/dL cholesterol should convert to ~5.18 mmol/L"
        assert normalize_unit(240.0, "mg/dL", "cholesterol") == pytest.approx(6.216, rel=1e-3), "240 mg/dL cholesterol should convert to ~6.216 mmol/L"
        print("✅ mg/dL → mmol/L cholesterol conversions working correctly")
        
        # Test mmol/L (already standard unit)
        assert normalize_unit(5.18, "mmol/L", "cholesterol") == 5.18, "5.18 mmol/L should remain 5.18 mmol/L"
        assert normalize_unit(6.216, "mmol/L", "cholesterol") == 6.216, "6.216 mmol/L should remain 6.216 mmol/L"
        print("✅ mmol/L (standard unit) preserved correctly")
        
        print("✅ All cholesterol conversions passed!")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases")
        print("=" * 50)
        
        # Test None values
        assert normalize_unit(None, "g/dL") is None, "None value should return None"
        assert normalize_unit(13.0, None) == 13.0, "None unit should return original value"
        print("✅ None values handled correctly")
        
        # Test empty strings
        assert normalize_unit(13.0, "") == 13.0, "Empty unit should return original value"
        assert normalize_unit(13.0, "   ") == 13.0, "Whitespace-only unit should return original value"
        print("✅ Empty/whitespace units handled correctly")
        
        # Test non-numeric values
        assert normalize_unit("13", "g/dL") == "13", "Non-numeric value should return original value"
        assert normalize_unit(13.0, "g/dL") == 130.0, "Numeric value should be converted"
        print("✅ Non-numeric values handled correctly")
        
        # Test unknown units
        assert normalize_unit(13.0, "unknown_unit") == 13.0, "Unknown unit should return original value"
        assert normalize_unit(13.0, "xyz") == 13.0, "Unknown unit should return original value"
        print("✅ Unknown units handled correctly")
        
        print("✅ All edge cases handled correctly!")
    
    def test_context_specific_conversions(self):
        """Test context-specific conversions for ambiguous units"""
        print("\n🧪 Testing Context-Specific Conversions")
        print("=" * 50)
        
        # Test mg/dL with different contexts
        glucose_mgdl = normalize_unit(90.0, "mg/dL", "glucose")
        creatinine_mgdl = normalize_unit(1.0, "mg/dL", "creatinine")
        calcium_mgdl = normalize_unit(10.0, "mg/dL", "calcium")
        
        print(f"   Glucose 90 mg/dL → {glucose_mgdl:.3f} mmol/L")
        print(f"   Creatinine 1 mg/dL → {creatinine_mgdl:.1f} μmol/L")
        print(f"   Calcium 10 mg/dL → {calcium_mgdl:.1f} mmol/L")
        
        assert glucose_mgdl == pytest.approx(4.995, rel=1e-3), "Glucose conversion should be to mmol/L"
        assert creatinine_mgdl == 88.4, "Creatinine conversion should be to μmol/L"
        assert calcium_mgdl == 2.5, "Calcium conversion should be to mmol/L"
        
        print("✅ Context-specific conversions working correctly!")
    
    def test_real_world_scenarios(self):
        """Test real-world lab value scenarios"""
        print("\n🧪 Testing Real-World Scenarios")
        print("=" * 50)
        
        # Scenario 1: Patient with multiple lab values in different units
        patient_labs = {
            "hemoglobin": normalize_unit(14.2, "g/dL"),
            "glucose": normalize_unit(95, "mg/dL", "glucose"),
            "creatinine": normalize_unit(0.9, "mg/dL", "creatinine"),
            "calcium": normalize_unit(9.8, "mg/dL", "calcium"),
            "albumin": normalize_unit(4.1, "g/dL", "albumin")
        }
        
        print("   Patient Lab Values (normalized):")
        print(f"   • Hemoglobin: 14.2 g/dL → {patient_labs['hemoglobin']} g/L")
        print(f"   • Glucose: 95 mg/dL → {patient_labs['glucose']:.3f} mmol/L")
        print(f"   • Creatinine: 0.9 mg/dL → {patient_labs['creatinine']:.1f} μmol/L")
        print(f"   • Calcium: 9.8 mg/dL → {patient_labs['calcium']:.2f} mmol/L")
        print(f"   • Albumin: 4.1 g/dL → {patient_labs['albumin']} g/L")
        
        # Verify conversions
        assert patient_labs['hemoglobin'] == 142.0, "Hemoglobin should be 142 g/L"
        assert patient_labs['glucose'] == pytest.approx(5.2725, rel=1e-3), "Glucose should be ~5.27 mmol/L"
        assert patient_labs['creatinine'] == pytest.approx(79.56, rel=1e-3), "Creatinine should be ~79.6 μmol/L"
        assert patient_labs['calcium'] == 2.45, "Calcium should be 2.45 mmol/L"
        assert patient_labs['albumin'] == 41.0, "Albumin should be 41 g/L"
        
        print("✅ Real-world scenario conversions working correctly!")
    
    def test_comparison_scenarios(self):
        """Test scenarios where normalized values can be compared"""
        print("\n🧪 Testing Comparison Scenarios")
        print("=" * 50)
        
        # Scenario: Compare lab values from different sources with different units
        lab_source_1 = {
            "hemoglobin": 14.2,  # g/dL
            "glucose": 95,       # mg/dL
            "creatinine": 0.9    # mg/dL
        }
        
        lab_source_2 = {
            "hemoglobin": 142,   # g/L (already normalized)
            "glucose": 5.27,     # mmol/L (already normalized)
            "creatinine": 79.6   # μmol/L (already normalized)
        }
        
        # Normalize source 1 values
        normalized_source_1 = {
            "hemoglobin": normalize_unit(lab_source_1["hemoglobin"], "g/dL"),
            "glucose": normalize_unit(lab_source_1["glucose"], "mg/dL", "glucose"),
            "creatinine": normalize_unit(lab_source_1["creatinine"], "mg/dL", "creatinine")
        }
        
        print("   Lab Source 1 (normalized):")
        print(f"   • Hemoglobin: {lab_source_1['hemoglobin']} g/dL → {normalized_source_1['hemoglobin']} g/L")
        print(f"   • Glucose: {lab_source_1['glucose']} mg/dL → {normalized_source_1['glucose']:.3f} mmol/L")
        print(f"   • Creatinine: {lab_source_1['creatinine']} mg/dL → {normalized_source_1['creatinine']:.1f} μmol/L")
        
        print("   Lab Source 2 (already normalized):")
        print(f"   • Hemoglobin: {lab_source_2['hemoglobin']} g/L")
        print(f"   • Glucose: {lab_source_2['glucose']} mmol/L")
        print(f"   • Creatinine: {lab_source_2['creatinine']} μmol/L")
        
        # Now we can compare the normalized values
        assert abs(normalized_source_1['hemoglobin'] - lab_source_2['hemoglobin']) < 0.1, "Hemoglobin values should be comparable"
        assert abs(normalized_source_1['glucose'] - lab_source_2['glucose']) < 0.01, "Glucose values should be comparable"
        assert abs(normalized_source_1['creatinine'] - lab_source_2['creatinine']) < 0.1, "Creatinine values should be comparable"
        
        print("✅ Comparison scenarios working correctly!")

def test_integration_with_predicates():
    """Test integration with predicate evaluation"""
    print("\n🧪 Testing Integration with Predicates")
    print("=" * 50)
    
    from ayusynapse.matcher.predicates import PredicateEvaluator, Predicate
    
    evaluator = PredicateEvaluator()
    
    # Create patient features with lab values in different units
    patient_features = {
        "age": 55,
        "gender": "female",
        "conditions": [],
        "observations": [
            {
                "text": "Hemoglobin",
                "value": 14.2,  # g/dL
                "unit": "g/dL",
                "normalized_unit": "g/L",
                "category": "laboratory",
                "status": "final"
            },
            {
                "text": "Glucose",
                "value": 95,  # mg/dL
                "unit": "mg/dL",
                "normalized_unit": "mmol/L",
                "category": "laboratory",
                "status": "final"
            }
        ],
        "medications": [],
        "lab_results": [],
        "vital_signs": {}
    }
    
    # Create predicates expecting normalized values
    hb_predicate = Predicate(
        type="Observation",
        field="Hemoglobin",
        op=">=",
        value=140,  # g/L (normalized)
        inclusion=True
    )
    
    glucose_predicate = Predicate(
        type="Observation",
        field="Glucose",
        op="<=",
        value=5.5,  # mmol/L (normalized)
        inclusion=True
    )
    
    # Test hemoglobin predicate
    hb_result = evaluator.evaluate_predicate(patient_features, hb_predicate)
    print(f"   Hemoglobin: 14.2 g/dL vs >= 140 g/L: {'✅ MATCH' if hb_result['match'] else '❌ NO MATCH'}")
    
    # Test glucose predicate
    glucose_result = evaluator.evaluate_predicate(patient_features, glucose_predicate)
    print(f"   Glucose: 95 mg/dL vs <= 5.5 mmol/L: {'✅ MATCH' if glucose_result['match'] else '❌ NO MATCH'}")
    
    # The predicates should work because the feature extractor normalizes values
    assert hb_result['match'] == True, "Hemoglobin should match (14.2 g/dL = 142 g/L >= 140 g/L)"
    assert glucose_result['match'] == True, "Glucose should match (95 mg/dL = 5.27 mmol/L <= 5.5 mmol/L)"
    
    print("✅ Integration with predicates working correctly!")

if __name__ == "__main__":
    # Run all tests
    test_instance = TestLabNormalization()
    test_instance.test_hemoglobin_conversions()
    test_instance.test_glucose_conversions()
    test_instance.test_creatinine_conversions()
    test_instance.test_calcium_conversions()
    test_instance.test_bilirubin_conversions()
    test_instance.test_albumin_conversions()
    test_instance.test_cholesterol_conversions()
    test_instance.test_edge_cases()
    test_instance.test_context_specific_conversions()
    test_instance.test_real_world_scenarios()
    test_instance.test_comparison_scenarios()
    test_integration_with_predicates()
    
    print("\n🎉 All lab normalization tests completed successfully!")
