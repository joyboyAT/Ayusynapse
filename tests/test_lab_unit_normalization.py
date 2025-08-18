#!/usr/bin/env python3
"""
Test Lab Unit Normalization
Tests the normalize_unit helper function and lab unit conversions
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ayusynapse.matcher.unit_normalizer import LabUnitNormalizer, normalize_unit

class TestLabUnitNormalization:
    """Test lab unit normalization functionality"""
    
    def __init__(self):
        """Initialize test fixtures"""
        self.normalizer = LabUnitNormalizer()
    
    def test_hemoglobin_conversions(self):
        """Test hemoglobin unit conversions"""
        print("\n🧪 Testing Hemoglobin Unit Conversions")
        print("=" * 50)
        
        # Test g/dL to g/L conversion
        value, unit = self.normalizer.normalize_unit(13, "g/dL", "hemoglobin")
        print(f"13 g/dL -> {value} {unit}")
        assert value == 130.0, f"Expected 130.0, got {value}"
        assert unit == "g/L", f"Expected 'g/L', got {unit}"
        print("   ✅ g/dL to g/L conversion successful")
        
        # Test g/L to g/dL conversion
        value, unit = self.normalizer.normalize_unit(130, "g/L", "hemoglobin")
        print(f"130 g/L -> {value} {unit}")
        assert value == 13.0, f"Expected 13.0, got {value}"
        assert unit == "g/dL", f"Expected 'g/dL', got {unit}"
        print("   ✅ g/L to g/dL conversion successful")
        
        # Test g/dL to mmol/L conversion
        value, unit = self.normalizer.normalize_unit(13, "g/dL", "hemoglobin")
        # Note: This will convert to g/L first, but we can test direct conversion
        converted_value = self.normalizer.convert_between_units(13, "g/dL", "mmol/L", "hemoglobin")
        print(f"13 g/dL -> {converted_value} mmol/L")
        assert abs(converted_value - 8.07) < 0.1, f"Expected ~8.07, got {converted_value}"
        print("   ✅ g/dL to mmol/L conversion successful")
        
        print("✅ All hemoglobin conversions passed!")
    
    def test_glucose_conversions(self):
        """Test glucose unit conversions"""
        print("\n🧪 Testing Glucose Unit Conversions")
        print("=" * 50)
        
        # Test mg/dL to mmol/L conversion
        value, unit = self.normalizer.normalize_unit(90, "mg/dL", "glucose")
        print(f"90 mg/dL -> {value} {unit}")
        assert abs(value - 5.0) < 0.1, f"Expected ~5.0, got {value}"
        assert unit == "mmol/L", f"Expected 'mmol/L', got {unit}"
        print("   ✅ mg/dL to mmol/L conversion successful")
        
        # Test mmol/L to mg/dL conversion
        value, unit = self.normalizer.normalize_unit(5.0, "mmol/L", "glucose")
        print(f"5.0 mmol/L -> {value} {unit}")
        assert abs(value - 90.0) < 1.0, f"Expected ~90.0, got {value}"
        assert unit == "mg/dL", f"Expected 'mg/dL', got {unit}"
        print("   ✅ mmol/L to mg/dL conversion successful")
        
        # Test g/L to mg/dL conversion
        converted_value = self.normalizer.convert_between_units(1.0, "g/L", "mg/dL", "glucose")
        print(f"1.0 g/L -> {converted_value} mg/dL")
        assert abs(converted_value - 100.0) < 1.0, f"Expected ~100.0, got {converted_value}"
        print("   ✅ g/L to mg/dL conversion successful")
        
        print("✅ All glucose conversions passed!")
    
    def test_creatinine_conversions(self):
        """Test creatinine unit conversions"""
        print("\n🧪 Testing Creatinine Unit Conversions")
        print("=" * 50)
        
        # Test mg/dL to μmol/L conversion
        value, unit = self.normalizer.normalize_unit(1.0, "mg/dL", "creatinine")
        print(f"1.0 mg/dL -> {value} {unit}")
        assert abs(value - 88.4) < 1.0, f"Expected ~88.4, got {value}"
        assert unit == "μmol/L", f"Expected 'μmol/L', got {unit}"
        print("   ✅ mg/dL to μmol/L conversion successful")
        
        # Test μmol/L to mg/dL conversion
        value, unit = self.normalizer.normalize_unit(88.4, "μmol/L", "creatinine")
        print(f"88.4 μmol/L -> {value} {unit}")
        assert abs(value - 1.0) < 0.1, f"Expected ~1.0, got {value}"
        assert unit == "mg/dL", f"Expected 'mg/dL', got {unit}"
        print("   ✅ μmol/L to mg/dL conversion successful")
        
        # Test alternative spelling (umol/L)
        value, unit = self.normalizer.normalize_unit(88.4, "umol/L", "creatinine")
        print(f"88.4 umol/L -> {value} {unit}")
        assert abs(value - 1.0) < 0.1, f"Expected ~1.0, got {value}"
        assert unit == "mg/dL", f"Expected 'mg/dL', got {unit}"
        print("   ✅ umol/L to mg/dL conversion successful")
        
        print("✅ All creatinine conversions passed!")
    
    def test_cholesterol_conversions(self):
        """Test cholesterol unit conversions"""
        print("\n🧪 Testing Cholesterol Unit Conversions")
        print("=" * 50)
        
        # Test mg/dL to mmol/L conversion
        value, unit = self.normalizer.normalize_unit(200, "mg/dL", "cholesterol")
        print(f"200 mg/dL -> {value} {unit}")
        assert abs(value - 5.18) < 0.1, f"Expected ~5.18, got {value}"
        assert unit == "mmol/L", f"Expected 'mmol/L', got {unit}"
        print("   ✅ mg/dL to mmol/L conversion successful")
        
        # Test mmol/L to mg/dL conversion
        value, unit = self.normalizer.normalize_unit(5.18, "mmol/L", "cholesterol")
        print(f"5.18 mmol/L -> {value} {unit}")
        assert abs(value - 200.0) < 5.0, f"Expected ~200.0, got {value}"
        assert unit == "mg/dL", f"Expected 'mg/dL', got {unit}"
        print("   ✅ mmol/L to mg/dL conversion successful")
        
        print("✅ All cholesterol conversions passed!")
    
    def test_bilirubin_conversions(self):
        """Test bilirubin unit conversions"""
        print("\n🧪 Testing Bilirubin Unit Conversions")
        print("=" * 50)
        
        # Test mg/dL to μmol/L conversion
        value, unit = self.normalizer.normalize_unit(1.0, "mg/dL", "bilirubin")
        print(f"1.0 mg/dL -> {value} {unit}")
        assert abs(value - 17.1) < 1.0, f"Expected ~17.1, got {value}"
        assert unit == "μmol/L", f"Expected 'μmol/L', got {unit}"
        print("   ✅ mg/dL to μmol/L conversion successful")
        
        # Test μmol/L to mg/dL conversion
        value, unit = self.normalizer.normalize_unit(17.1, "μmol/L", "bilirubin")
        print(f"17.1 μmol/L -> {value} {unit}")
        assert abs(value - 1.0) < 0.1, f"Expected ~1.0, got {value}"
        assert unit == "mg/dL", f"Expected 'mg/dL', got {unit}"
        print("   ✅ μmol/L to mg/dL conversion successful")
        
        print("✅ All bilirubin conversions passed!")
    
    def test_albumin_conversions(self):
        """Test albumin unit conversions"""
        print("\n🧪 Testing Albumin Unit Conversions")
        print("=" * 50)
        
        # Test g/dL to g/L conversion
        value, unit = self.normalizer.normalize_unit(4.0, "g/dL", "albumin")
        print(f"4.0 g/dL -> {value} {unit}")
        assert value == 40.0, f"Expected 40.0, got {value}"
        assert unit == "g/L", f"Expected 'g/L', got {unit}"
        print("   ✅ g/dL to g/L conversion successful")
        
        # Test g/L to g/dL conversion
        value, unit = self.normalizer.normalize_unit(40.0, "g/L", "albumin")
        print(f"40.0 g/L -> {value} {unit}")
        assert value == 4.0, f"Expected 4.0, got {value}"
        assert unit == "g/dL", f"Expected 'g/dL', got {unit}"
        print("   ✅ g/L to g/dL conversion successful")
        
        print("✅ All albumin conversions passed!")
    
    def test_convenience_function(self):
        """Test the convenience normalize_unit function"""
        print("\n🧪 Testing Convenience Function")
        print("=" * 50)
        
        # Test the convenience function
        value, unit = normalize_unit(13, "g/dL", "hemoglobin")
        print(f"normalize_unit(13, 'g/dL', 'hemoglobin') -> {value} {unit}")
        assert value == 130.0, f"Expected 130.0, got {value}"
        assert unit == "g/L", f"Expected 'g/L', got {unit}"
        print("   ✅ Convenience function works correctly")
        
        print("✅ Convenience function test passed!")
    
    def test_unsupported_conversions(self):
        """Test handling of unsupported conversions"""
        print("\n🧪 Testing Unsupported Conversions")
        print("=" * 50)
        
        # Test unsupported test type
        value, unit = self.normalizer.normalize_unit(10, "mg/dL", "unknown_test")
        print(f"Unknown test type: {value} {unit}")
        assert value == 10, f"Expected original value 10, got {value}"
        assert unit == "mg/dL", f"Expected original unit 'mg/dL', got {unit}"
        print("   ✅ Unsupported test type handled gracefully")
        
        # Test unsupported unit
        value, unit = self.normalizer.normalize_unit(10, "unknown_unit", "glucose")
        print(f"Unknown unit: {value} {unit}")
        assert value == 10, f"Expected original value 10, got {value}"
        assert unit == "unknown_unit", f"Expected original unit 'unknown_unit', got {unit}"
        print("   ✅ Unsupported unit handled gracefully")
        
        # Test None values
        value, unit = self.normalizer.normalize_unit(10, None, "glucose")
        print(f"None unit: {value} {unit}")
        assert value == 10, f"Expected original value 10, got {value}"
        assert unit is None, f"Expected None unit, got {unit}"
        print("   ✅ None unit handled gracefully")
        
        print("✅ All unsupported conversion tests passed!")
    
    def test_get_standard_units(self):
        """Test getting standard units for test types"""
        print("\n🧪 Testing Standard Unit Retrieval")
        print("=" * 50)
        
        # Test hemoglobin standard unit
        standard_unit = self.normalizer.get_standard_unit("hemoglobin")
        print(f"Hemoglobin standard unit: {standard_unit}")
        assert standard_unit == "g/L", f"Expected 'g/L', got {standard_unit}"
        print("   ✅ Hemoglobin standard unit correct")
        
        # Test glucose standard unit
        standard_unit = self.normalizer.get_standard_unit("glucose")
        print(f"Glucose standard unit: {standard_unit}")
        assert standard_unit == "mmol/L", f"Expected 'mmol/L', got {standard_unit}"
        print("   ✅ Glucose standard unit correct")
        
        # Test unknown test type
        standard_unit = self.normalizer.get_standard_unit("unknown_test")
        print(f"Unknown test standard unit: {standard_unit}")
        assert standard_unit is None, f"Expected None, got {standard_unit}"
        print("   ✅ Unknown test type handled correctly")
        
        print("✅ All standard unit tests passed!")
    
    def test_supported_tests_and_units(self):
        """Test getting lists of supported tests and units"""
        print("\n🧪 Testing Supported Tests and Units")
        print("=" * 50)
        
        # Test supported tests
        supported_tests = self.normalizer.get_supported_tests()
        print(f"Supported tests: {supported_tests}")
        expected_tests = ["hemoglobin", "glucose", "creatinine", "cholesterol", "triglycerides", "bilirubin", "albumin"]
        for test in expected_tests:
            assert test in supported_tests, f"Expected {test} to be in supported tests"
        print("   ✅ All expected tests are supported")
        
        # Test supported units for hemoglobin
        hemoglobin_units = self.normalizer.get_supported_units("hemoglobin")
        print(f"Hemoglobin supported units: {hemoglobin_units}")
        expected_units = ["g/dL", "g/L", "mmol/L"]
        for unit in expected_units:
            assert unit in hemoglobin_units, f"Expected {unit} to be in hemoglobin units"
        print("   ✅ All expected hemoglobin units are supported")
        
        # Test supported units for unknown test
        unknown_units = self.normalizer.get_supported_units("unknown_test")
        print(f"Unknown test supported units: {unknown_units}")
        assert unknown_units == [], f"Expected empty list, got {unknown_units}"
        print("   ✅ Unknown test returns empty unit list")
        
        print("✅ All supported tests and units tests passed!")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases")
        print("=" * 50)
        
        # Test zero values
        value, unit = self.normalizer.normalize_unit(0, "mg/dL", "glucose")
        print(f"Zero value: {value} {unit}")
        assert value == 0.0, f"Expected 0.0, got {value}"
        assert unit == "mmol/L", f"Expected 'mmol/L', got {unit}"
        print("   ✅ Zero value handled correctly")
        
        # Test negative values
        value, unit = self.normalizer.normalize_unit(-5, "mg/dL", "glucose")
        print(f"Negative value: {value} {unit}")
        assert value == -0.2775, f"Expected -0.2775, got {value}"
        assert unit == "mmol/L", f"Expected 'mmol/L', got {unit}"
        print("   ✅ Negative value handled correctly")
        
        # Test very large values
        value, unit = self.normalizer.normalize_unit(1000, "mg/dL", "glucose")
        print(f"Large value: {value} {unit}")
        assert abs(value - 55.5) < 1.0, f"Expected ~55.5, got {value}"
        assert unit == "mmol/L", f"Expected 'mmol/L', got {unit}"
        print("   ✅ Large value handled correctly")
        
        # Test invalid value types
        value, unit = self.normalizer.normalize_unit("invalid", "mg/dL", "glucose")
        print(f"Invalid value type: {value} {unit}")
        assert value == "invalid", f"Expected original value, got {value}"
        assert unit == "mg/dL", f"Expected original unit, got {unit}"
        print("   ✅ Invalid value type handled gracefully")
        
        print("✅ All edge case tests passed!")

def test_integration_with_predicates():
    """Test integration with predicate evaluation"""
    print("\n🧪 Testing Integration with Predicates")
    print("=" * 50)
    
    from ayusynapse.matcher.predicates import PredicateEvaluator, Predicate
    
    evaluator = PredicateEvaluator()
    
    # Create patient features with lab results
    patient_features = {
        "age": 55,
        "gender": "female",
        "conditions": [],
        "observations": [],
        "medications": [],
        "lab_results": [
            {
                "text": "Hemoglobin",
                "value": 13.0,
                "unit": "g/dL",
                "normalized_unit": None,
                "category": "laboratory",
                "status": "final"
            },
            {
                "text": "Glucose",
                "value": 90.0,
                "unit": "mg/dL",
                "normalized_unit": None,
                "category": "laboratory",
                "status": "final"
            }
        ],
        "vital_signs": {}
    }
    
    # Test hemoglobin predicate with different units
    hb_predicate = Predicate(
        type="Observation",
        field="Hemoglobin",
        op=">=",
        value=120,
        unit="g/L",  # Different unit than patient data
        inclusion=True
    )
    
    result = evaluator.evaluate_predicate(patient_features, hb_predicate)
    print(f"Hemoglobin predicate (13 g/dL >= 120 g/L): {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
    print(f"Evidence: {result['evidence']}")
    assert result['match'] == True, f"Hemoglobin should match after unit normalization: {result}"
    print("   ✅ Hemoglobin unit normalization in predicates works")
    
    # Test glucose predicate with different units
    glucose_predicate = Predicate(
        type="Observation",
        field="Glucose",
        op="<=",
        value=6.0,
        unit="mmol/L",  # Different unit than patient data
        inclusion=True
    )
    
    result = evaluator.evaluate_predicate(patient_features, glucose_predicate)
    print(f"Glucose predicate (90 mg/dL <= 6.0 mmol/L): {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
    print(f"Evidence: {result['evidence']}")
    assert result['match'] == True, f"Glucose should match after unit normalization: {result}"
    print("   ✅ Glucose unit normalization in predicates works")
    
    print("✅ All integration tests passed!")

if __name__ == "__main__":
    # Run all tests
    test_instance = TestLabUnitNormalization()
    test_instance.test_hemoglobin_conversions()
    test_instance.test_glucose_conversions()
    test_instance.test_creatinine_conversions()
    test_instance.test_cholesterol_conversions()
    test_instance.test_bilirubin_conversions()
    test_instance.test_albumin_conversions()
    test_instance.test_convenience_function()
    test_instance.test_unsupported_conversions()
    test_instance.test_get_standard_units()
    test_instance.test_supported_tests_and_units()
    test_instance.test_edge_cases()
    test_integration_with_predicates()
    
    print("\n🎉 All lab unit normalization tests completed successfully!")
