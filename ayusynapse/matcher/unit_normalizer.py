#!/usr/bin/env python3
"""
Lab Unit Normalization Module
Provides standardized unit conversions for laboratory values
"""

from typing import Dict, Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)

class LabUnitNormalizer:
    """Normalizes laboratory values to standard units"""
    
    def __init__(self):
        """Initialize with supported unit conversions"""
        self.conversions = self._load_conversions()
    
    def _load_conversions(self) -> Dict[str, Dict[str, Dict[str, Union[float, callable]]]]:
        """
        Load supported unit conversions
        
        Returns:
            Dictionary mapping test types to unit conversions
        """
        return {
            # Hemoglobin conversions
            "hemoglobin": {
                "g/dL": {
                    "g/L": 10.0,  # g/dL to g/L
                    "mmol/L": 0.6206  # g/dL to mmol/L (molecular weight ~16114.5 g/mol)
                },
                "g/L": {
                    "g/dL": 0.1,  # g/L to g/dL
                    "mmol/L": 0.06206  # g/L to mmol/L
                },
                "mmol/L": {
                    "g/dL": 1.611,  # mmol/L to g/dL
                    "g/L": 16.11  # mmol/L to g/L
                }
            },
            
            # Glucose conversions
            "glucose": {
                "mg/dL": {
                    "mmol/L": 0.0555,  # mg/dL to mmol/L
                    "g/L": 0.01  # mg/dL to g/L
                },
                "mmol/L": {
                    "mg/dL": 18.0,  # mmol/L to mg/dL
                    "g/L": 0.18  # mmol/L to g/L
                },
                "g/L": {
                    "mg/dL": 100.0,  # g/L to mg/dL
                    "mmol/L": 5.55  # g/L to mmol/L
                }
            },
            
            # Creatinine conversions
            "creatinine": {
                "mg/dL": {
                    "μmol/L": 88.4,  # mg/dL to μmol/L
                    "umol/L": 88.4,  # mg/dL to umol/L (alternative spelling)
                    "mmol/L": 0.0884  # mg/dL to mmol/L
                },
                "μmol/L": {
                    "mg/dL": 0.0113,  # μmol/L to mg/dL
                    "umol/L": 1.0,  # μmol/L to umol/L
                    "mmol/L": 0.001  # μmol/L to mmol/L
                },
                "umol/L": {
                    "mg/dL": 0.0113,  # umol/L to mg/dL
                    "μmol/L": 1.0,  # umol/L to μmol/L
                    "mmol/L": 0.001  # umol/L to mmol/L
                },
                "mmol/L": {
                    "mg/dL": 11.3,  # mmol/L to mg/dL
                    "μmol/L": 1000.0,  # mmol/L to μmol/L
                    "umol/L": 1000.0  # mmol/L to umol/L
                }
            },
            
            # Cholesterol conversions
            "cholesterol": {
                "mg/dL": {
                    "mmol/L": 0.0259,  # mg/dL to mmol/L
                    "g/L": 0.01  # mg/dL to g/L
                },
                "mmol/L": {
                    "mg/dL": 38.67,  # mmol/L to mg/dL
                    "g/L": 0.3867  # mmol/L to g/L
                },
                "g/L": {
                    "mg/dL": 100.0,  # g/L to mg/dL
                    "mmol/L": 2.59  # g/L to mmol/L
                }
            },
            
            # Triglycerides conversions
            "triglycerides": {
                "mg/dL": {
                    "mmol/L": 0.0113,  # mg/dL to mmol/L
                    "g/L": 0.01  # mg/dL to g/L
                },
                "mmol/L": {
                    "mg/dL": 88.5,  # mmol/L to mg/dL
                    "g/L": 0.885  # mmol/L to g/L
                },
                "g/L": {
                    "mg/dL": 100.0,  # g/L to mg/dL
                    "mmol/L": 1.13  # g/L to mmol/L
                }
            },
            
            # Bilirubin conversions
            "bilirubin": {
                "mg/dL": {
                    "μmol/L": 17.1,  # mg/dL to μmol/L
                    "umol/L": 17.1,  # mg/dL to umol/L
                    "mmol/L": 0.0171  # mg/dL to mmol/L
                },
                "μmol/L": {
                    "mg/dL": 0.0585,  # μmol/L to mg/dL
                    "umol/L": 1.0,  # μmol/L to umol/L
                    "mmol/L": 0.001  # μmol/L to mmol/L
                },
                "umol/L": {
                    "mg/dL": 0.0585,  # umol/L to mg/dL
                    "μmol/L": 1.0,  # umol/L to μmol/L
                    "mmol/L": 0.001  # umol/L to mmol/L
                },
                "mmol/L": {
                    "mg/dL": 58.5,  # mmol/L to mg/dL
                    "μmol/L": 1000.0,  # mmol/L to μmol/L
                    "umol/L": 1000.0  # mmol/L to umol/L
                }
            },
            
            # Albumin conversions
            "albumin": {
                "g/dL": {
                    "g/L": 10.0,  # g/dL to g/L
                    "mmol/L": 0.145  # g/dL to mmol/L (molecular weight ~66438 g/mol)
                },
                "g/L": {
                    "g/dL": 0.1,  # g/L to g/dL
                    "mmol/L": 0.0145  # g/L to mmol/L
                },
                "mmol/L": {
                    "g/dL": 6.9,  # mmol/L to g/dL
                    "g/L": 69.0  # mmol/L to g/L
                }
            }
        }
    
    def normalize_unit(self, value: float, unit: str, test_type: Optional[str] = None) -> Tuple[float, str]:
        """
        Normalize a lab value to standard units
        
        Args:
            value: Numeric value to normalize
            unit: Current unit of the value
            test_type: Type of lab test (e.g., 'hemoglobin', 'glucose', 'creatinine')
            
        Returns:
            Tuple of (normalized_value, normalized_unit)
            
        Examples:
            >>> normalizer = LabUnitNormalizer()
            >>> normalizer.normalize_unit(13, "g/dL", "hemoglobin")
            (130, "g/L")
            >>> normalizer.normalize_unit(90, "mg/dL", "glucose")
            (5.0, "mmol/L")
        """
        if not isinstance(value, (int, float)):
            logger.warning(f"Invalid value type: {type(value)}. Expected numeric value.")
            return value, unit
        
        if not unit or not test_type:
            return value, unit
        
        # Clean and normalize unit and test type
        unit_clean = unit.strip()
        test_type_clean = test_type.lower().strip()
        
        # Find the test type in our conversions
        for test_key, test_conversions in self.conversions.items():
            if test_key in test_type_clean or test_type_clean in test_key:
                if unit_clean in test_conversions:
                    # Get the first target unit as the standard
                    target_unit = list(test_conversions[unit_clean].keys())[0]
                    conversion_factor = test_conversions[unit_clean][target_unit]
                    
                    # Apply conversion
                    if callable(conversion_factor):
                        normalized_value = conversion_factor(value)
                    else:
                        normalized_value = value * conversion_factor
                    
                    logger.debug(f"Converted {value} {unit_clean} to {normalized_value} {target_unit} for {test_type}")
                    return normalized_value, target_unit
        
        # If no conversion found, return original values
        logger.debug(f"No conversion found for {test_type} with unit {unit_clean}")
        return value, unit
    
    def get_standard_unit(self, test_type: str) -> Optional[str]:
        """
        Get the standard unit for a given test type
        
        Args:
            test_type: Type of lab test
            
        Returns:
            Standard unit for the test type, or None if not found
        """
        test_type_clean = test_type.lower().strip()
        
        for test_key, test_conversions in self.conversions.items():
            if test_key in test_type_clean or test_type_clean in test_key:
                # Return the first unit from the first conversion as standard
                first_unit_conversions = list(test_conversions.values())[0]
                return list(first_unit_conversions.keys())[0]
        
        return None
    
    def convert_between_units(self, value: float, from_unit: str, to_unit: str, test_type: str) -> Optional[float]:
        """
        Convert a value between two specific units for a given test type
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit
            to_unit: Target unit
            test_type: Type of lab test
            
        Returns:
            Converted value, or None if conversion not possible
        """
        if not isinstance(value, (int, float)):
            return None
        
        test_type_clean = test_type.lower().strip()
        from_unit_clean = from_unit.strip()
        to_unit_clean = to_unit.strip()
        
        # Find the test type
        for test_key, test_conversions in self.conversions.items():
            if test_key in test_type_clean or test_type_clean in test_key:
                if from_unit_clean in test_conversions and to_unit_clean in test_conversions[from_unit_clean]:
                    conversion_factor = test_conversions[from_unit_clean][to_unit_clean]
                    
                    if callable(conversion_factor):
                        return conversion_factor(value)
                    else:
                        return value * conversion_factor
        
        return None
    
    def get_supported_tests(self) -> list:
        """Get list of supported test types"""
        return list(self.conversions.keys())
    
    def get_supported_units(self, test_type: str) -> list:
        """Get list of supported units for a given test type"""
        test_type_clean = test_type.lower().strip()
        
        for test_key, test_conversions in self.conversions.items():
            if test_key in test_type_clean or test_type_clean in test_key:
                return list(test_conversions.keys())
        
        return []

# Global instance for easy access
lab_normalizer = LabUnitNormalizer()

def normalize_unit(value: float, unit: str, test_type: Optional[str] = None) -> Tuple[float, str]:
    """
    Convenience function to normalize lab units
    
    Args:
        value: Numeric value to normalize
        unit: Current unit of the value
        test_type: Type of lab test (optional)
        
    Returns:
        Tuple of (normalized_value, normalized_unit)
    """
    return lab_normalizer.normalize_unit(value, unit, test_type)
