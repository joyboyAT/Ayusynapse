#!/usr/bin/env python3
"""
Predicate Model for Patient-Trial Matching
Represents clinical trial criteria as machine-checkable rules
"""

import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Import the normalization helper
try:
    from .features import normalize_enum
except ImportError:
    from matcher.features import normalize_enum

logger = logging.getLogger(__name__)

class PredicateType(Enum):
    """Types of predicates"""
    PATIENT = "Patient"
    CONDITION = "Condition"
    OBSERVATION = "Observation"
    MEDICATION = "Medication"

class PredicateOperator(Enum):
    """Operators for predicate evaluation"""
    # Presence operators
    PRESENT = "present"
    ABSENT = "absent"
    
    # Equality operators
    EQUALS = "=="
    NOT_EQUALS = "!="
    
    # Comparison operators
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    GREATER = ">"
    LESS = "<"
    
    # Set operators
    IN = "in"
    NOT_IN = "not_in"
    
    # Range operators
    RANGE = "range"

@dataclass
class Predicate:
    """Represents a single clinical trial criterion"""
    type: str  # Patient, Condition, Observation, Medication
    field: Optional[str] = None  # age, gender, HER2, Hemoglobin, etc.
    code: Optional[str] = None  # SNOMED/LOINC/RxNorm code
    op: str = "present"  # present, absent, ==, !=, >=, <=, in, not_in, range
    value: Optional[Union[str, int, float, List]] = None
    unit: Optional[str] = None  # For lab values
    weight: int = 1  # Importance weight for scoring
    inclusion: bool = True  # True for inclusion, False for exclusion
    reason: Optional[str] = None  # Human-readable reason
    
    def __post_init__(self):
        """Validate predicate after initialization"""
        if not self.field and not self.code:
            raise ValueError("Predicate must have either field or code specified")
        
        if self.op in ["==", "!=", ">=", "<=", ">", "<", "in", "not_in", "range"] and self.value is None:
            raise ValueError(f"Operator {self.op} requires a value")

class PredicateEvaluator:
    """Evaluates predicates against patient features"""
    
    def __init__(self, feature_extractor=None):
        """Initialize with optional feature extractor for normalization"""
        self.feature_extractor = feature_extractor
    
    def evaluate_predicate(self, patient_features, predicate: Predicate) -> Dict[str, Any]:
        """
        Evaluate a single predicate against patient features
        
        Args:
            patient_features: Extracted patient features
            predicate: Predicate to evaluate
            
        Returns:
            Dictionary with match status and evidence
        """
        try:
            # Convert PatientFeatures dataclass to dict if needed
            if hasattr(patient_features, 'age'):
                # It's a PatientFeatures dataclass
                patient_dict = {
                    'age': patient_features.age,
                    'gender': patient_features.gender,
                    'conditions': patient_features.conditions,
                    'observations': patient_features.observations,
                    'medications': patient_features.medications,
                    'lab_results': patient_features.lab_results,
                    'vital_signs': patient_features.vital_signs
                }
            else:
                # It's already a dict
                patient_dict = patient_features
            
            if predicate.type == "Patient":
                return self._evaluate_patient_predicate(patient_dict, predicate)
            elif predicate.type == "Condition":
                return self._evaluate_condition_predicate(patient_dict, predicate)
            elif predicate.type == "Observation":
                return self._evaluate_observation_predicate(patient_dict, predicate)
            elif predicate.type == "Medication":
                return self._evaluate_medication_predicate(patient_dict, predicate)
            else:
                return {
                    "match": False,
                    "evidence": f"Unknown predicate type: {predicate.type}",
                    "error": True
                }
        except Exception as e:
            logger.error(f"Error evaluating predicate {predicate}: {e}")
            return {
                "match": False,
                "evidence": f"Evaluation error: {str(e)}",
                "error": True
            }
    
    def _evaluate_patient_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate patient-specific predicates"""
        if predicate.field == "age":
            return self._evaluate_age_predicate(patient_features, predicate)
        elif predicate.field == "gender":
            return self._evaluate_gender_predicate(patient_features, predicate)
        else:
            return {
                "match": False,
                "evidence": f"Unknown patient field: {predicate.field}",
                "error": True
            }
    
    def _evaluate_age_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate age-based predicates"""
        patient_age = patient_features.get('age')
        
        if patient_age is None:
            return {
                "match": False,
                "evidence": "Patient age not available",
                "error": True  # Mark as missing data
            }
        
        if predicate.op == "present":
            return {
                "match": True,
                "evidence": f"Patient age is present: {patient_age} years"
            }
        elif predicate.op == "absent":
            return {
                "match": False,
                "evidence": f"Patient age is present: {patient_age} years"
            }
        elif predicate.op in [">=", "<=", ">", "<", "==", "!="]:
            return self._evaluate_comparison(patient_age, predicate.op, predicate.value, "age")
        elif predicate.op == "range":
            if isinstance(predicate.value, (list, tuple)) and len(predicate.value) == 2:
                min_age, max_age = predicate.value
                if min_age <= patient_age <= max_age:
                    return {
                        "match": True,
                        "evidence": f"Patient age {patient_age} is within range [{min_age}, {max_age}]"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"Patient age {patient_age} is outside range [{min_age}, {max_age}]"
                    }
            else:
                return {
                    "match": False,
                    "evidence": f"Invalid range format: {predicate.value}",
                    "error": True
                }
        else:
            return {
                "match": False,
                "evidence": f"Unsupported operator for age: {predicate.op}",
                "error": True
            }
    
    def _evaluate_gender_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate gender-based predicates"""
        patient_gender = patient_features.get('gender')
        
        if patient_gender is None:
            return {
                "match": False,
                "evidence": "Patient gender not available",
                "error": True  # Mark as missing data
            }
        
        # Normalize gender if feature extractor is available
        if self.feature_extractor:
            normalized_gender = self.feature_extractor.normalize_enum(patient_gender)
            if normalized_gender:
                patient_gender = normalized_gender
        
        if predicate.op == "present":
            return {
                "match": True,
                "evidence": f"Patient gender is present: {patient_gender}"
            }
        elif predicate.op == "absent":
            return {
                "match": False,
                "evidence": f"Patient gender is present: {patient_gender}"
            }
        elif predicate.op == "==":
            if patient_gender.lower() == str(predicate.value).lower():
                return {
                    "match": True,
                    "evidence": f"Patient gender {patient_gender} matches required {predicate.value}"
                }
            else:
                return {
                    "match": False,
                    "evidence": f"Patient gender {patient_gender} does not match required {predicate.value}"
                }
        elif predicate.op == "!=":
            if patient_gender.lower() != str(predicate.value).lower():
                return {
                    "match": True,
                    "evidence": f"Patient gender {patient_gender} is not {predicate.value}"
                }
            else:
                return {
                    "match": False,
                    "evidence": f"Patient gender {patient_gender} matches excluded {predicate.value}"
                }
        elif predicate.op in ["in", "not_in"]:
            if isinstance(predicate.value, (list, tuple)):
                value_list = [str(v).lower() for v in predicate.value]
                if predicate.op == "in":
                    if patient_gender.lower() in value_list:
                        return {
                            "match": True,
                            "evidence": f"Patient gender {patient_gender} is in allowed list {predicate.value}"
                        }
                    else:
                        return {
                            "match": False,
                            "evidence": f"Patient gender {patient_gender} is not in allowed list {predicate.value}"
                        }
                else:  # not_in
                    if patient_gender.lower() not in value_list:
                        return {
                            "match": True,
                            "evidence": f"Patient gender {patient_gender} is not in excluded list {predicate.value}"
                        }
                    else:
                        return {
                            "match": False,
                            "evidence": f"Patient gender {patient_gender} is in excluded list {predicate.value}"
                        }
            else:
                return {
                    "match": False,
                    "evidence": f"Invalid value format for {predicate.op}: {predicate.value}",
                    "error": True
                }
        else:
            return {
                "match": False,
                "evidence": f"Unsupported operator for gender: {predicate.op}",
                "error": True
            }
    
    def _evaluate_condition_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate condition-based predicates"""
        patient_conditions = patient_features.get('conditions', [])
        
        if predicate.op in ["present", "absent"]:
            return self._evaluate_condition_presence(patient_conditions, predicate)
        else:
            return {
                "match": False,
                "evidence": f"Unsupported operator for conditions: {predicate.op}",
                "error": True
            }
    
    def _evaluate_condition_presence(self, patient_conditions: List[Dict], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate condition presence/absence"""
        if predicate.code:
            # Check by SNOMED code
            for condition in patient_conditions:
                for code_info in condition.get('codes', []):
                    if code_info.get('code') == predicate.code:
                        if predicate.op == "present":
                            return {
                                "match": True,
                                "evidence": f"Condition with code {predicate.code} is present: {condition.get('text', 'Unknown')}"
                            }
                        else:  # absent
                            return {
                                "match": False,
                                "evidence": f"Condition with code {predicate.code} is present: {condition.get('text', 'Unknown')}"
                            }
            
            # Condition not found
            if predicate.op == "present":
                return {
                    "match": False,
                    "evidence": f"Condition with code {predicate.code} is not present"
                }
            else:  # absent
                return {
                    "match": True,
                    "evidence": f"Condition with code {predicate.code} is absent"
                }
        
        elif predicate.field:
            # Check by field name (text matching)
            for condition in patient_conditions:
                condition_text = condition.get('text', '').lower()
                if predicate.field.lower() in condition_text:
                    if predicate.op == "present":
                        return {
                            "match": True,
                            "evidence": f"Condition '{predicate.field}' is present: {condition.get('text', 'Unknown')}"
                        }
                    else:  # absent
                        return {
                            "match": False,
                            "evidence": f"Condition '{predicate.field}' is present: {condition.get('text', 'Unknown')}"
                        }
            
            # Condition not found
            if predicate.op == "present":
                return {
                    "match": False,
                    "evidence": f"Condition '{predicate.field}' is not present"
                }
            else:  # absent
                return {
                    "match": True,
                    "evidence": f"Condition '{predicate.field}' is absent"
                }
        
        else:
            return {
                "match": False,
                "evidence": "Predicate must specify either code or field",
                "error": True
            }
    
    def _evaluate_observation_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate observation-based predicates"""
        # Check lab results first
        lab_results = patient_features.get('lab_results', [])
        for lab in lab_results:
            if self._matches_observation(lab, predicate):
                return self._evaluate_observation_value(lab, predicate)
        
        # Check general observations
        observations = patient_features.get('observations', [])
        for obs in observations:
            if self._matches_observation(obs, predicate):
                return self._evaluate_observation_value(obs, predicate)
        
        # Check vital signs
        vital_signs = patient_features.get('vital_signs', {})
        for vital_name, vital_data in vital_signs.items():
            if self._matches_observation(vital_data, predicate):
                return self._evaluate_observation_value(vital_data, predicate)
        
        # Observation not found
        if predicate.op == "present":
            return {
                "match": False,
                "evidence": f"Observation '{predicate.field or predicate.code}' is not present"
            }
        elif predicate.op == "absent":
            return {
                "match": True,
                "evidence": f"Observation '{predicate.field or predicate.code}' is absent"
            }
        else:
            # For other operators (==, !=, >=, <=, etc.), missing data should be treated as missing
            return {
                "match": False,
                "evidence": f"Observation '{predicate.field or predicate.code}' is not present",
                "error": True  # Mark as missing data
            }
    
    def _matches_observation(self, observation: Dict, predicate: Predicate) -> bool:
        """Check if observation matches predicate criteria"""
        if predicate.code:
            # Check by LOINC code
            for code_info in observation.get('codes', []):
                if code_info.get('code') == predicate.code:
                    return True
            return False
        
        elif predicate.field:
            # Check by field name (text matching)
            observation_text = observation.get('text', '').lower()
            return predicate.field.lower() in observation_text
        
        return False
    
    def get_observation_value(self, obs: Dict) -> tuple:
        """Extract value and unit from observation in various FHIR formats"""
        val = None
        unit = None
        
        if "valueQuantity" in obs:
            val = obs["valueQuantity"]["value"]
            unit = obs["valueQuantity"].get("unit")
        elif "valueCodeableConcept" in obs:
            # Prioritize text over coding for better readability
            text = obs["valueCodeableConcept"].get("text")
            if text:
                val = text
            else:
                coding = obs["valueCodeableConcept"].get("coding", [])
                if coding:
                    val = coding[0].get("display") or coding[0].get("code")
        elif "valueInteger" in obs:
            val = obs["valueInteger"]
        elif "valueString" in obs:
            val = obs["valueString"]
        
        # Apply normalization to string values
        if isinstance(val, str):
            val = normalize_enum(val)
        
        return val, unit

    def _evaluate_observation_value(self, observation: Dict, predicate: Predicate) -> Dict[str, Any]:
        """Evaluate observation value against predicate"""
        if predicate.op in ["present", "absent"]:
            if predicate.op == "present":
                return {
                    "match": True,
                    "evidence": f"Observation '{observation.get('text', 'Unknown')}' is present"
                }
            else:
                return {
                    "match": False,
                    "evidence": f"Observation '{observation.get('text', 'Unknown')}' is present"
                }
        
        # Handle value comparisons - use flattened structure from feature extractor
        obs_value = observation.get('value')
        obs_unit = observation.get('unit')
        
        if obs_value is None:
            return {
                "match": False,
                "evidence": f"Observation '{observation.get('text', 'Unknown')}' has no value"
            }
        
        # Handle string values (like "positive", "negative")
        if isinstance(obs_value, str) and isinstance(predicate.value, str):
            # Normalize both values for comparison
            normalized_obs = normalize_enum(obs_value)
            normalized_pred = normalize_enum(predicate.value)
            
            if predicate.op == "==":
                if normalized_obs == normalized_pred:
                    return {
                        "match": True,
                        "evidence": f"{observation.get('text', 'Unknown')}: {obs_value} equals {predicate.value}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{observation.get('text', 'Unknown')}: {obs_value} does not equal {predicate.value}"
                    }
            elif predicate.op == "!=":
                if normalized_obs != normalized_pred:
                    return {
                        "match": True,
                        "evidence": f"{observation.get('text', 'Unknown')}: {obs_value} is not equal to {predicate.value}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{observation.get('text', 'Unknown')}: {obs_value} equals {predicate.value}"
                    }
            else:
                return {
                    "match": False,
                    "evidence": f"String comparison only supports == and != operators, got {predicate.op}"
                }
        
        # Handle numeric values
        if isinstance(obs_value, (int, float)) and isinstance(predicate.value, (int, float)):
            # The observation value should already be normalized from feature extraction
            # But we need to normalize the predicate value for comparison
            if predicate.unit:
                # Import the normalize_unit function
                try:
                    from .features import normalize_unit
                except ImportError:
                    from matcher.features import normalize_unit
                
                # Normalize predicate value to standard units
                normalized_pred_value = normalize_unit(predicate.value, predicate.unit)
                predicate_value = normalized_pred_value
                logger.debug(f"Normalized predicate value: {predicate.value} {predicate.unit} -> {normalized_pred_value}")
            else:
                predicate_value = predicate.value
            
            return self._evaluate_comparison(obs_value, predicate.op, predicate_value, observation.get('text', 'Unknown'))
        
        # Handle mixed types
        return {
            "match": False,
            "evidence": f"Cannot compare {type(obs_value).__name__} with {type(predicate.value).__name__}"
        }
    
    def _evaluate_medication_predicate(self, patient_features: Dict[str, Any], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate medication-based predicates"""
        patient_medications = patient_features.get('medications', [])
        
        if predicate.op in ["present", "absent"]:
            return self._evaluate_medication_presence(patient_medications, predicate)
        else:
            return {
                "match": False,
                "evidence": f"Unsupported operator for medications: {predicate.op}",
                "error": True
            }
    
    def _evaluate_medication_presence(self, patient_medications: List[Dict], predicate: Predicate) -> Dict[str, Any]:
        """Evaluate medication presence/absence"""
        if predicate.code:
            # Check by RxNorm code
            for medication in patient_medications:
                for code_info in medication.get('codes', []):
                    if code_info.get('code') == predicate.code:
                        if predicate.op == "present":
                            return {
                                "match": True,
                                "evidence": f"Medication with code {predicate.code} is present: {medication.get('text', 'Unknown')}"
                            }
                        else:  # absent
                            return {
                                "match": False,
                                "evidence": f"Medication with code {predicate.code} is present: {medication.get('text', 'Unknown')}"
                            }
            
            # Medication not found
            if predicate.op == "present":
                return {
                    "match": False,
                    "evidence": f"Medication with code {predicate.code} is not present"
                }
            else:  # absent
                return {
                    "match": True,
                    "evidence": f"Medication with code {predicate.code} is absent"
                }
        
        elif predicate.field:
            # Check by field name (text matching)
            for medication in patient_medications:
                medication_text = medication.get('text', '').lower()
                if predicate.field.lower() in medication_text:
                    if predicate.op == "present":
                        return {
                            "match": True,
                            "evidence": f"Medication '{predicate.field}' is present: {medication.get('text', 'Unknown')}"
                        }
                    else:  # absent
                        return {
                            "match": False,
                            "evidence": f"Medication '{predicate.field}' is present: {medication.get('text', 'Unknown')}"
                        }
            
            # Medication not found
            if predicate.op == "present":
                return {
                    "match": False,
                    "evidence": f"Medication '{predicate.field}' is not present"
                }
            else:  # absent
                return {
                    "match": True,
                    "evidence": f"Medication '{predicate.field}' is absent"
                }
        
        else:
            return {
                "match": False,
                "evidence": "Predicate must specify either code or field",
                "error": True
            }
    
    def _evaluate_comparison(self, actual_value: Union[int, float], op: str, expected_value: Union[int, float], context: str) -> Dict[str, Any]:
        """Evaluate comparison operators"""
        try:
            actual = float(actual_value)
            expected = float(expected_value)
            
            if op == "==":
                if actual == expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} equals {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} does not equal {expected}"
                    }
            
            elif op == "!=":
                if actual != expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} is not equal to {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} equals {expected}"
                    }
            
            elif op == ">=":
                if actual >= expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} >= {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} < {expected}"
                    }
            
            elif op == "<=":
                if actual <= expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} <= {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} > {expected}"
                    }
            
            elif op == ">":
                if actual > expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} > {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} <= {expected}"
                    }
            
            elif op == "<":
                if actual < expected:
                    return {
                        "match": True,
                        "evidence": f"{context}: {actual} < {expected}"
                    }
                else:
                    return {
                        "match": False,
                        "evidence": f"{context}: {actual} >= {expected}"
                    }
            
            else:
                return {
                    "match": False,
                    "evidence": f"Unsupported comparison operator: {op}",
                    "error": True
                }
        
        except (ValueError, TypeError) as e:
            return {
                "match": False,
                "evidence": f"Error comparing values: {actual_value} {op} {expected_value}",
                "error": True
            }

def create_sample_predicates() -> List[Predicate]:
    """Create sample predicates for testing"""
    return [
        # HER2 positive biomarker
        Predicate(
            type="Observation",
            field="HER2",
            op="==",
            value="positive",
            weight=3,
            inclusion=True
        ),
        
        # Biliary tract cancer condition
        Predicate(
            type="Condition",
            code="363418001",  # SNOMED code for biliary tract cancer
            op="present",
            weight=5,
            inclusion=True
        ),
        
        # Age requirement
        Predicate(
            type="Patient",
            field="age",
            op=">=",
            value=18,
            weight=2,
            inclusion=True
        ),
        
        # Hemoglobin requirement
        Predicate(
            type="Observation",
            field="Hemoglobin",
            op=">=",
            value=10,
            unit="g/dL",
            weight=1,
            inclusion=True
        ),
        
        # CNS metastases exclusion
        Predicate(
            type="Condition",
            code="128462008",  # SNOMED code for CNS metastases
            op="absent",
            inclusion=False,
            reason="CNS metastases"
        )
    ]

def test_predicate_evaluation():
    """Test predicate evaluation with sample data"""
    print("🧪 Testing Predicate Evaluation")
    print("=" * 50)
    
    # Create evaluator
    evaluator = PredicateEvaluator()
    
    # Create sample predicates
    predicates = create_sample_predicates()
    
    # Create sample patient features
    patient_features = {
        "age": 45,
        "gender": "female",
        "conditions": [
            {
                "text": "Biliary tract cancer",
                "codes": [
                    {"system": "http://snomed.info/sct", "code": "363418001", "display": "Biliary tract cancer"}
                ],
                "status": "active"
            }
        ],
        "observations": [
            {
                "text": "HER2",
                "codes": [
                    {"system": "http://loinc.org", "code": "85319-0", "display": "HER2"}
                ],
                "value": "positive",
                "status": "final"
            },
            {
                "text": "Hemoglobin",
                "codes": [
                    {"system": "http://loinc.org", "code": "718-7", "display": "Hemoglobin"}
                ],
                "value": 12.5,
                "unit": "g/dL",
                "status": "final"
            }
        ],
        "medications": [],
        "lab_results": [],
        "vital_signs": {}
    }
    
    # Evaluate each predicate
    for i, predicate in enumerate(predicates, 1):
        print(f"\n🔍 Testing Predicate {i}:")
        print(f"   Type: {predicate.type}")
        print(f"   Field/Code: {predicate.field or predicate.code}")
        print(f"   Operator: {predicate.op}")
        print(f"   Value: {predicate.value}")
        if predicate.unit:
            print(f"   Unit: {predicate.unit}")
        print(f"   Weight: {predicate.weight}")
        print(f"   Inclusion: {predicate.inclusion}")
        
        result = evaluator.evaluate_predicate(patient_features, predicate)
        
        print(f"   Result: {'✅ MATCH' if result['match'] else '❌ NO MATCH'}")
        print(f"   Evidence: {result['evidence']}")
        if result.get('error'):
            print(f"   ⚠️  Error: {result['error']}")
    
    print(f"\n✅ Predicate evaluation test completed!")

if __name__ == "__main__":
    test_predicate_evaluation()
