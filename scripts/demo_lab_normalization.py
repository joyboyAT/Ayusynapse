#!/usr/bin/env python3
"""
Lab Unit Normalization Demo
Demonstrates the lab unit normalization functionality
"""

import sys
import os

# Add the matcher directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'matcher'))

from matcher.unit_normalizer import LabUnitNormalizer, normalize_unit

def main():
    """Demonstrate lab unit normalization"""
    print("🔬 Lab Unit Normalization Demo")
    print("=" * 50)
    
    # Create normalizer instance
    normalizer = LabUnitNormalizer()
    
    print("\n📋 Example 1: Hemoglobin Conversion")
    print("-" * 30)
    print("Input: 13 g/dL")
    value, unit = normalize_unit(13, "g/dL", "hemoglobin")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 130 g/L")
    
    print("\n📋 Example 2: Glucose Conversion")
    print("-" * 30)
    print("Input: 90 mg/dL")
    value, unit = normalize_unit(90, "mg/dL", "glucose")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 5.0 mmol/L")
    
    print("\n📋 Example 3: Creatinine Conversion")
    print("-" * 30)
    print("Input: 1.0 mg/dL")
    value, unit = normalize_unit(1.0, "mg/dL", "creatinine")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 88.4 μmol/L")
    
    print("\n📋 Example 4: Cholesterol Conversion")
    print("-" * 30)
    print("Input: 200 mg/dL")
    value, unit = normalize_unit(200, "mg/dL", "cholesterol")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 5.18 mmol/L")
    
    print("\n📋 Example 5: Bilirubin Conversion")
    print("-" * 30)
    print("Input: 1.0 mg/dL")
    value, unit = normalize_unit(1.0, "mg/dL", "bilirubin")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 17.1 μmol/L")
    
    print("\n📋 Example 6: Albumin Conversion")
    print("-" * 30)
    print("Input: 4.0 g/dL")
    value, unit = normalize_unit(4.0, "g/dL", "albumin")
    print(f"Output: {value} {unit}")
    print("✅ Expected: 40.0 g/L")
    
    print("\n🔧 Supported Test Types:")
    print("-" * 30)
    supported_tests = normalizer.get_supported_tests()
    for test in supported_tests:
        standard_unit = normalizer.get_standard_unit(test)
        print(f"• {test.capitalize()}: {standard_unit}")
    
    print("\n🔄 Bidirectional Conversions:")
    print("-" * 30)
    
    # Test bidirectional conversion for hemoglobin
    print("Hemoglobin conversions:")
    value1, unit1 = normalize_unit(13, "g/dL", "hemoglobin")
    value2, unit2 = normalize_unit(value1, unit1, "hemoglobin")
    print(f"  13 g/dL → {value1} {unit1} → {value2} {unit2}")
    
    # Test bidirectional conversion for glucose
    print("Glucose conversions:")
    value1, unit1 = normalize_unit(90, "mg/dL", "glucose")
    value2, unit2 = normalize_unit(value1, unit1, "glucose")
    print(f"  90 mg/dL → {value1} {unit1} → {value2} {unit2}")
    
    print("\n🎯 Integration with EMR Pipeline:")
    print("-" * 30)
    print("The lab unit normalization is now integrated into:")
    print("• Feature extraction pipeline")
    print("• Predicate evaluation system")
    print("• Patient-trial matching algorithm")
    print("• All lab value comparisons")
    
    print("\n✅ Lab unit normalization is ready for use!")
    print("=" * 50)

if __name__ == "__main__":
    main()
