# Lab Unit Normalization Implementation

## Overview

This document describes the implementation of lab unit normalization for the EMR project. The system provides standardized unit conversions for laboratory values to ensure consistent comparison and matching across different units.

## Implementation Summary

### 1. Core Components

#### `matcher/unit_normalizer.py`
- **LabUnitNormalizer Class**: Main class for handling unit conversions
- **normalize_unit() Function**: Convenience function for easy access
- **Supported Conversions**: Comprehensive dictionary of unit conversions

#### Key Features:
- **Test-specific conversions**: Each lab test type has its own conversion rules
- **Bidirectional conversions**: Convert between any supported units for a test
- **Error handling**: Graceful handling of unsupported units and test types
- **Extensible**: Easy to add new test types and units

### 2. Supported Test Types and Conversions

| Test Type | Supported Units | Standard Unit |
|-----------|----------------|---------------|
| Hemoglobin | g/dL, g/L, mmol/L | g/L |
| Glucose | mg/dL, mmol/L, g/L | mmol/L |
| Creatinine | mg/dL, μmol/L, umol/L, mmol/L | μmol/L |
| Cholesterol | mg/dL, mmol/L, g/L | mmol/L |
| Triglycerides | mg/dL, mmol/L, g/L | mmol/L |
| Bilirubin | mg/dL, μmol/L, umol/L, mmol/L | μmol/L |
| Albumin | g/dL, g/L, mmol/L | g/L |

### 3. Example Conversions

#### Hemoglobin
- **Input**: 13 g/dL → **Output**: 130 g/L
- **Input**: 130 g/L → **Output**: 13 g/dL

#### Glucose
- **Input**: 90 mg/dL → **Output**: 5.0 mmol/L
- **Input**: 5.0 mmol/L → **Output**: 90 mg/dL

#### Creatinine
- **Input**: 1.0 mg/dL → **Output**: 88.4 μmol/L
- **Input**: 88.4 μmol/L → **Output**: 1.0 mg/dL

### 4. Integration Points

#### Feature Extraction Pipeline
- Updated `matcher/features.py` to use the new normalizer
- Enhanced `normalize_lab_value()` method
- Automatic normalization during feature extraction

#### Predicate Evaluation System
- Updated `matcher/predicates.py` to handle unit mismatches
- Automatic unit conversion during predicate evaluation
- Improved matching accuracy for lab values

#### Patient-Trial Matching
- Seamless integration with existing matching algorithms
- Consistent unit handling across all comparisons
- Better accuracy for lab-based inclusion/exclusion criteria

### 5. Usage Examples

#### Basic Usage
```python
from matcher.unit_normalizer import normalize_unit

# Convert hemoglobin from g/dL to g/L
value, unit = normalize_unit(13, "g/dL", "hemoglobin")
print(f"{value} {unit}")  # Output: 130.0 g/L

# Convert glucose from mg/dL to mmol/L
value, unit = normalize_unit(90, "mg/dL", "glucose")
print(f"{value} {unit}")  # Output: 5.0 mmol/L
```

#### Advanced Usage
```python
from matcher.unit_normalizer import LabUnitNormalizer

normalizer = LabUnitNormalizer()

# Get standard unit for a test type
standard_unit = normalizer.get_standard_unit("hemoglobin")  # Returns "g/L"

# Convert between specific units
converted_value = normalizer.convert_between_units(
    13, "g/dL", "mmol/L", "hemoglobin"
)

# Get list of supported tests
supported_tests = normalizer.get_supported_tests()
```

### 6. Testing

#### Test Coverage
- **Unit Tests**: `tests/test_lab_unit_normalization.py`
- **Integration Tests**: Tests with predicate evaluation
- **Edge Cases**: Zero values, negative values, invalid inputs
- **Bidirectional Conversions**: Verify round-trip conversions

#### Test Results
All tests pass successfully, including:
- ✅ Hemoglobin conversions
- ✅ Glucose conversions  
- ✅ Creatinine conversions
- ✅ Cholesterol conversions
- ✅ Bilirubin conversions
- ✅ Albumin conversions
- ✅ Integration with predicates
- ✅ Edge case handling

### 7. Benefits

#### For EMR Pipeline
1. **Consistent Comparisons**: All lab values are normalized to standard units
2. **Improved Matching**: Better accuracy in patient-trial matching
3. **Reduced Errors**: Eliminates unit mismatch issues
4. **Extensible**: Easy to add new lab tests and units

#### For Clinical Trials
1. **Standardized Criteria**: Trial criteria can use standard units
2. **Better Matching**: More accurate patient eligibility assessment
3. **Reduced Manual Work**: Automatic unit conversion
4. **Compliance**: Follows clinical standards for lab values

### 8. Future Enhancements

#### Planned Additions
- **More Test Types**: Additional lab tests (electrolytes, enzymes, etc.)
- **Temperature Conversions**: Celsius/Fahrenheit conversions
- **Pressure Conversions**: Blood pressure unit conversions
- **Weight/Height**: BMI and anthropometric conversions

#### Extensibility
- **Configuration Files**: External configuration for conversions
- **API Integration**: Integration with external lab systems
- **Validation**: Enhanced validation of conversion factors
- **Logging**: Detailed logging of conversion operations

### 9. Maintenance

#### Adding New Test Types
1. Add conversion dictionary to `_load_conversions()`
2. Update supported tests list
3. Add corresponding tests
4. Update documentation

#### Adding New Units
1. Add conversion factors to existing test types
2. Ensure bidirectional conversions work
3. Update tests
4. Verify integration

### 10. Conclusion

The lab unit normalization system provides a robust, extensible solution for handling unit conversions in the EMR project. It ensures consistent, accurate comparisons across different lab value units and improves the overall quality of patient-trial matching.

The implementation follows best practices for:
- **Modularity**: Clean separation of concerns
- **Testability**: Comprehensive test coverage
- **Extensibility**: Easy to add new features
- **Integration**: Seamless integration with existing systems
- **Documentation**: Clear documentation and examples

This system is now ready for production use and will significantly improve the accuracy and reliability of lab value comparisons in the EMR pipeline.
