#!/usr/bin/env python3
"""
Feature Extraction for Patient-Trial Matching
Converts FHIR bundles into comparable features for matching algorithms
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def normalize_enum(text: str) -> str:
    """Normalize enum values to standard format"""
    if not text:
        return None
    t = text.strip().lower()
    if not t:  # Handle whitespace-only strings
        return None
    mapping = {
        "positive": "positive", "pos": "positive", "+": "positive",
        "negative": "negative", "neg": "negative", "-": "negative",
        "yes": "true", "true": "true", "present": "true",
        "no": "false", "false": "false", "absent": "false"
    }
    return mapping.get(t, t)   # default to cleaned lowercase if not mapped

def normalize_unit(value: float, unit: str, test_type: str = None) -> float:
    """
    Normalize lab values to standard units for comparison
    
    Args:
        value: Numeric value to normalize
        unit: Unit string (e.g., "g/dL", "mg/dL", "mmol/L")
        test_type: Optional test type for context-specific conversions
        
    Returns:
        Normalized value in standard unit
        
    Examples:
        normalize_unit(13, "g/dL") → 130 (g/L)
        normalize_unit(90, "mg/dL", "glucose") → 5 (mmol/L)
    """
    if not isinstance(value, (int, float)) or not unit:
        return value
    
    unit_clean = unit.strip().lower()
    
    # Lab value conversions to standard units
    # Note: Some units like mg/dL need context (test_type) for proper conversion
    conversions = {
        # Hemoglobin: g/dL → g/L
        "g/dl": lambda x: x * 10,
        "g/l": lambda x: x,  # Already in standard unit
        
        # Glucose: mg/dL → mmol/L
        "mg/dl": lambda x: x * 0.0555,  # mg/dL to mmol/L (for glucose)
        "mmol/l": lambda x: x,  # Already in standard unit
        
        # Creatinine: mg/dL → μmol/L
        "mg/dl": lambda x: x * 88.4,  # mg/dL to μmol/L (for creatinine)
        "μmol/l": lambda x: x,  # Already in standard unit
        "umol/l": lambda x: x,  # Alternative spelling
        
        # Sodium: mEq/L → mmol/L
        "meq/l": lambda x: x,  # mEq/L = mmol/L for monovalent ions
        "mmol/l": lambda x: x,  # Already in standard unit
        
        # Potassium: mEq/L → mmol/L
        "meq/l": lambda x: x,  # mEq/L = mmol/L for monovalent ions
        
        # Calcium: mg/dL → mmol/L
        "mg/dl": lambda x: x * 0.25,  # mg/dL to mmol/L (for calcium)
        
        # Bilirubin: mg/dL → μmol/L
        "mg/dl": lambda x: x * 17.1,  # mg/dL to μmol/L (for bilirubin)
        
        # Albumin: g/dL → g/L
        "g/dl": lambda x: x * 10,  # g/dL to g/L (for albumin)
        
        # Total Protein: g/dL → g/L
        "g/dl": lambda x: x * 10,  # g/dL to g/L (for total protein)
        
        # Cholesterol: mg/dL → mmol/L
        "mg/dl": lambda x: x * 0.0259,  # mg/dL to mmol/L (for cholesterol)
        
        # Triglycerides: mg/dL → mmol/L
        "mg/dl": lambda x: x * 0.0113,  # mg/dL to mmol/L (for triglycerides)
        
        # Urea Nitrogen (BUN): mg/dL → mmol/L
        "mg/dl": lambda x: x * 0.357,  # mg/dL to mmol/L (for BUN)
        
        # Uric Acid: mg/dL → μmol/L
        "mg/dl": lambda x: x * 59.5,  # mg/dL to μmol/L (for uric acid)
    }
    
    # Context-specific conversions for ambiguous units
    context_conversions = {
        "glucose": {
            "mg/dl": lambda x: x * 0.0555,  # mg/dL to mmol/L
            "mmol/l": lambda x: x,
        },
        "creatinine": {
            "mg/dl": lambda x: x * 88.4,  # mg/dL to μmol/L
            "μmol/l": lambda x: x,
            "umol/l": lambda x: x,
        },
        "calcium": {
            "mg/dl": lambda x: x * 0.25,  # mg/dL to mmol/L
            "mmol/l": lambda x: x,
        },
        "bilirubin": {
            "mg/dl": lambda x: x * 17.1,  # mg/dL to μmol/L
            "μmol/l": lambda x: x,
            "umol/l": lambda x: x,
        },
        "albumin": {
            "g/dl": lambda x: x * 10,  # g/dL to g/L
            "g/l": lambda x: x,
        },
        "total_protein": {
            "g/dl": lambda x: x * 10,  # g/dL to g/L
            "g/l": lambda x: x,
        },
        "cholesterol": {
            "mg/dl": lambda x: x * 0.0259,  # mg/dL to mmol/L
            "mmol/l": lambda x: x,
        },
        "triglycerides": {
            "mg/dl": lambda x: x * 0.0113,  # mg/dL to mmol/L
            "mmol/l": lambda x: x,
        },
        "bun": {
            "mg/dl": lambda x: x * 0.357,  # mg/dL to mmol/L
            "mmol/l": lambda x: x,
        },
        "uric_acid": {
            "mg/dl": lambda x: x * 59.5,  # mg/dL to μmol/L
            "μmol/l": lambda x: x,
            "umol/l": lambda x: x,
        },
    }
    
    # Try context-specific conversion first if test_type is provided
    if test_type and test_type.lower() in context_conversions:
        test_conversions = context_conversions[test_type.lower()]
        if unit_clean in test_conversions:
            return test_conversions[unit_clean](value)
    
    # Apply general conversion if available
    if unit_clean in conversions:
        return conversions[unit_clean](value)
    
    # Return original value if no conversion available
    logger.debug(f"No unit conversion available for '{unit}' (test_type: {test_type}), returning original value")
    return value

@dataclass
class PatientFeatures:
    """Extracted patient features for matching"""
    age: Optional[int] = None
    gender: Optional[str] = None
    conditions: List[Dict[str, Any]] = None
    observations: List[Dict[str, Any]] = None
    medications: List[Dict[str, Any]] = None
    lab_results: List[Dict[str, Any]] = None
    vital_signs: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.observations is None:
            self.observations = []
        if self.medications is None:
            self.medications = []
        if self.lab_results is None:
            self.lab_results = []
        if self.vital_signs is None:
            self.vital_signs = {}

@dataclass
class TrialPredicates:
    """Extracted trial inclusion/exclusion criteria"""
    inclusion: List[Dict[str, Any]] = None
    exclusion: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.inclusion is None:
            self.inclusion = []
        if self.exclusion is None:
            self.exclusion = []

class FeatureExtractor:
    """Extract features from FHIR bundles for patient-trial matching"""
    
    def __init__(self, emr_mappings_file: str = "data/processed/emr_mappings.json"):
        """Initialize with EMR mappings for normalization"""
        self.emr_mappings = self._load_emr_mappings(emr_mappings_file)
        self.ucum_units = self._load_ucum_units()
    
    def _load_emr_mappings(self, file_path: str) -> Dict[str, Any]:
        """Load EMR mappings for terminology normalization"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"EMR mappings file not found: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Error loading EMR mappings: {e}")
            return {}
    
    def _load_ucum_units(self) -> Dict[str, str]:
        """Load UCUM unit mappings for normalization"""
        return {
            # Age units
            "years": "a",
            "year": "a",
            "y": "a",
            "months": "mo",
            "month": "mo",
            "days": "d",
            "day": "d",
            
            # Weight units
            "kg": "kg",
            "kilograms": "kg",
            "lbs": "[lb_av]",
            "pounds": "[lb_av]",
            
            # Height units
            "cm": "cm",
            "centimeters": "cm",
            "m": "m",
            "meters": "m",
            "inches": "[in_i]",
            "in": "[in_i]",
            
            # Blood pressure
            "mmHg": "mm[Hg]",
            "mm Hg": "mm[Hg]",
            
            # Temperature
            "°C": "Cel",
            "Celsius": "Cel",
            "°F": "[degF]",
            "Fahrenheit": "[degF]",
            
            # Lab values
            "mg/dL": "mg/dL",
            "mmol/L": "mmol/L",
            "g/dL": "g/dL",
            "ng/mL": "ng/mL",
            "pg/mL": "pg/mL",
            "U/L": "U/L",
            "mIU/L": "mIU/L"
        }
    
    def _load_unit_conversions(self) -> Dict[str, Dict[str, float]]:
        """Load unit conversion factors for SI normalization"""
        return {
            # Mass conversions
            "g/dL": {"g/L": 10.0},  # g/dL to g/L
            "mg/dL": {"mg/L": 10.0},  # mg/dL to mg/L
            "ng/mL": {"ng/L": 1000.0},  # ng/mL to ng/L
            "pg/mL": {"pg/L": 1000.0},  # pg/mL to pg/L
            
            # Volume conversions
            "L": {"L": 1.0},  # Base unit
            "mL": {"L": 0.001},  # mL to L
            "dL": {"L": 0.1},  # dL to L
            
            # Temperature conversions
            "°F": {"°C": lambda f: (f - 32) * 5/9},  # Fahrenheit to Celsius
            "°C": {"°C": lambda c: c},  # Celsius to Celsius (no change)
            
            # Pressure conversions
            "mmHg": {"Pa": 133.322},  # mmHg to Pascal
            "mm Hg": {"Pa": 133.322},  # mm Hg to Pascal
            
            # Length conversions
            "cm": {"m": 0.01},  # cm to m
            "mm": {"m": 0.001},  # mm to m
            "inches": {"m": 0.0254},  # inches to m
            "in": {"m": 0.0254},  # in to m
            
            # Weight conversions
            "lbs": {"kg": 0.453592},  # lbs to kg
            "pounds": {"kg": 0.453592},  # pounds to kg
        }
    
    def extract_patient_features(self, patient_bundle: Dict[str, Any]) -> PatientFeatures:
        """Extract patient features from FHIR bundle"""
        features = PatientFeatures()
        
        if not patient_bundle or 'entry' not in patient_bundle:
            logger.warning("Invalid patient bundle format")
            return features
        
        for entry in patient_bundle['entry']:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            
            if resource_type == 'Patient':
                self._extract_patient_demographics(resource, features)
            elif resource_type == 'Condition':
                self._extract_condition(resource, features)
            elif resource_type == 'Observation':
                self._extract_observation(resource, features)
            elif resource_type == 'MedicationRequest':
                self._extract_medication(resource, features)
        
        return features
    
    def extract_trial_predicates(self, trial_bundle: Dict[str, Any]) -> TrialPredicates:
        """Extract trial inclusion/exclusion criteria from FHIR bundle"""
        predicates = TrialPredicates()
        
        if not trial_bundle or 'entry' not in trial_bundle:
            logger.warning("Invalid trial bundle format")
            return predicates
        
        for entry in trial_bundle['entry']:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType')
            
            if resource_type == 'ResearchStudy':
                self._extract_research_study_criteria(resource, predicates)
            elif resource_type == 'Condition':
                # Conditions in trials are typically inclusion criteria
                self._extract_condition_criteria(resource, predicates, is_inclusion=True)
            elif resource_type == 'Observation':
                # Observations in trials are typically inclusion criteria
                self._extract_observation_criteria(resource, predicates, is_inclusion=True)
        
        return predicates
    
    def _extract_patient_demographics(self, patient: Dict[str, Any], features: PatientFeatures):
        """Extract age and gender from Patient resource"""
        # Extract birth date and calculate age
        birth_date = patient.get('birthDate')
        if birth_date:
            try:
                birth_dt = datetime.strptime(birth_date, '%Y-%m-%d').date()
                today = date.today()
                features.age = today.year - birth_dt.year - ((today.month, today.day) < (birth_dt.month, birth_dt.day))
            except (ValueError, TypeError):
                logger.warning(f"Invalid birth date format: {birth_date}")
        
        # Extract gender
        features.gender = patient.get('gender', '').lower()
    
    def _extract_condition(self, condition: Dict[str, Any], features: PatientFeatures):
        """Extract condition information"""
        condition_info = {
            'text': '',
            'codes': [],
            'severity': None,
            'onset': None,
            'status': condition.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', '')
        }
        
        # Extract condition text and codes
        code = condition.get('code', {})
        if code:
            # Get display text
            coding_list = code.get('coding', [])
            if coding_list:
                condition_info['text'] = coding_list[0].get('display', '')
                # Add all codes
                for coding in coding_list:
                    condition_info['codes'].append({
                        'system': coding.get('system', ''),
                        'code': coding.get('code', ''),
                        'display': coding.get('display', '')
                    })
            
            # Fallback to text if no coding
            if not condition_info['text']:
                condition_info['text'] = code.get('text', '')
        
        # Extract severity
        severity = condition.get('severity', {})
        if severity:
            severity_coding = severity.get('coding', [{}])[0]
            condition_info['severity'] = {
                'system': severity_coding.get('system', ''),
                'code': severity_coding.get('code', ''),
                'display': severity_coding.get('display', '')
            }
        
        # Extract onset
        onset = condition.get('onsetDateTime')
        if onset:
            condition_info['onset'] = onset
        
        features.conditions.append(condition_info)
    
    def _extract_observation(self, observation: Dict[str, Any], features: PatientFeatures):
        """Extract observation information (lab results, vital signs, etc.)"""
        obs_info = {
            'text': '',
            'codes': [],
            'value': None,
            'unit': None,
            'normalized_unit': None,
            'category': None,
            'status': observation.get('status', '')
        }
        
        # Extract observation text and codes
        code = observation.get('code', {})
        if code:
            coding_list = code.get('coding', [])
            if coding_list:
                obs_info['text'] = coding_list[0].get('display', '')
                for coding in coding_list:
                    obs_info['codes'].append({
                        'system': coding.get('system', ''),
                        'code': coding.get('code', ''),
                        'display': coding.get('display', '')
                    })
            
            if not obs_info['text']:
                obs_info['text'] = code.get('text', '')
        
        # Extract value and unit using the same logic as predicates
        value_codeable = observation.get('valueCodeableConcept')
        if value_codeable:
            # Prioritize text over coding for better readability
            text = value_codeable.get('text')
            if text:
                obs_info['value'] = text
            else:
                coding = value_codeable.get('coding', [])
                if coding:
                    obs_info['value'] = coding[0].get('display') or coding[0].get('code')
        elif observation.get('valueInteger') is not None:
            obs_info['value'] = observation.get('valueInteger')
        elif observation.get('valueString') is not None:
            obs_info['value'] = observation.get('valueString')
        else:
            # Fallback to valueQuantity
            value_quantity = observation.get('valueQuantity')
            if value_quantity:
                original_value = value_quantity.get('value')
                original_unit = value_quantity.get('unit', '')
                
                # Apply unit normalization for lab values
                if isinstance(original_value, (int, float)) and original_unit:
                    # Try to determine test type from observation text for context-specific conversion
                    test_type = self._determine_test_type(obs_info['text'])
                    normalized_value = normalize_unit(original_value, original_unit, test_type)
                    obs_info['value'] = normalized_value
                    obs_info['unit'] = original_unit
                    obs_info['normalized_unit'] = self._normalize_unit(original_unit)
                    obs_info['original_value'] = original_value  # Keep original for reference
                    obs_info['test_type'] = test_type  # Store test type for reference
                else:
                    obs_info['value'] = original_value
                    obs_info['unit'] = original_unit
                    obs_info['normalized_unit'] = self._normalize_unit(original_unit)
        
        # Determine category
        category = observation.get('category', [])
        if category:
            category_coding = category[0].get('coding', [{}])[0]
            obs_info['category'] = category_coding.get('code', '')
        
        # Categorize observation
        if obs_info['category'] == 'vital-signs':
            if obs_info['text'].lower() in ['blood pressure', 'systolic', 'diastolic']:
                features.vital_signs[obs_info['text'].lower()] = obs_info
            else:
                features.vital_signs[obs_info['text'].lower()] = obs_info
        elif obs_info['category'] == 'laboratory':
            features.lab_results.append(obs_info)
        else:
            features.observations.append(obs_info)
    
    def _extract_medication(self, medication: Dict[str, Any], features: PatientFeatures):
        """Extract medication information"""
        med_info = {
            'text': '',
            'codes': [],
            'status': medication.get('status', ''),
            'intent': medication.get('intent', ''),
            'dosage': None
        }
        
        # Extract medication text and codes
        medication_codeable = medication.get('medicationCodeableConcept', {})
        if medication_codeable:
            coding_list = medication_codeable.get('coding', [])
            if coding_list:
                med_info['text'] = coding_list[0].get('display', '')
                for coding in coding_list:
                    med_info['codes'].append({
                        'system': coding.get('system', ''),
                        'code': coding.get('code', ''),
                        'display': coding.get('display', '')
                    })
            
            if not med_info['text']:
                med_info['text'] = medication_codeable.get('text', '')
        
        # Extract dosage information
        dosage = medication.get('dosage', [])
        if dosage:
            med_info['dosage'] = dosage[0] if dosage else None
        
        features.medications.append(med_info)
    
    def _normalize_unit(self, unit: str) -> str:
        """Normalize units using UCUM mappings"""
        if not unit:
            return unit
        
        # Clean unit string
        unit_clean = unit.strip().lower()
        
        # Check UCUM mappings
        if unit_clean in self.ucum_units:
            return self.ucum_units[unit_clean]
        
        # Try to match partial units
        for ucum_unit, normalized in self.ucum_units.items():
            if ucum_unit in unit_clean or unit_clean in ucum_unit:
                return normalized
        
        return unit  # Return original if no mapping found
    
    def _determine_test_type(self, observation_text: str) -> Optional[str]:
        """
        Determine test type from observation text for context-specific unit conversion
        
        Args:
            observation_text: Text description of the observation
            
        Returns:
            Test type string or None if not recognized
        """
        if not observation_text:
            return None
        
        text_lower = observation_text.lower()
        
        # Map observation text to test types
        test_type_mappings = {
            # Glucose-related
            'glucose': 'glucose',
            'blood glucose': 'glucose',
            'fasting glucose': 'glucose',
            'random glucose': 'glucose',
            
            # Creatinine-related
            'creatinine': 'creatinine',
            'serum creatinine': 'creatinine',
            'blood creatinine': 'creatinine',
            
            # Calcium-related
            'calcium': 'calcium',
            'total calcium': 'calcium',
            'serum calcium': 'calcium',
            'blood calcium': 'calcium',
            
            # Bilirubin-related
            'bilirubin': 'bilirubin',
            'total bilirubin': 'bilirubin',
            'serum bilirubin': 'bilirubin',
            'blood bilirubin': 'bilirubin',
            
            # Albumin-related
            'albumin': 'albumin',
            'serum albumin': 'albumin',
            'blood albumin': 'albumin',
            
            # Total protein-related
            'total protein': 'total_protein',
            'serum total protein': 'total_protein',
            'blood total protein': 'total_protein',
            
            # Cholesterol-related
            'cholesterol': 'cholesterol',
            'total cholesterol': 'cholesterol',
            'serum cholesterol': 'cholesterol',
            
            # Triglycerides-related
            'triglycerides': 'triglycerides',
            'serum triglycerides': 'triglycerides',
            'blood triglycerides': 'triglycerides',
            
            # BUN-related
            'bun': 'bun',
            'urea nitrogen': 'bun',
            'blood urea nitrogen': 'bun',
            'serum urea nitrogen': 'bun',
            
            # Uric acid-related
            'uric acid': 'uric_acid',
            'serum uric acid': 'uric_acid',
            'blood uric acid': 'uric_acid',
        }
        
        # Check for exact matches first
        for key, test_type in test_type_mappings.items():
            if key in text_lower:
                return test_type
        
        # Check for partial matches
        for key, test_type in test_type_mappings.items():
            if any(word in text_lower for word in key.split()):
                return test_type
        
        return None
    
    def normalize_code(self, concept: Dict[str, Any]) -> Tuple[str, str]:
        """
        Normalize a FHIR CodeableConcept to (system, code) tuple
        
        Args:
            concept: FHIR CodeableConcept with coding array
            
        Returns:
            Tuple of (system, code) for the most preferred coding
        """
        if not concept or 'coding' not in concept:
            return ("", "")
        
        coding_list = concept.get('coding', [])
        if not coding_list:
            return ("", "")
        
        # Prefer SNOMED CT, then LOINC, then others
        preferred_systems = [
            "http://snomed.info/sct",
            "http://loinc.org", 
            "http://www.nlm.nih.gov/research/umls/rxnorm",
            "http://hl7.org/fhir/sid/icd-10"
        ]
        
        # Find preferred coding
        for system in preferred_systems:
            for coding in coding_list:
                if coding.get('system') == system and coding.get('code'):
                    return (system, coding['code'])
        
        # Fallback to first available coding
        for coding in coding_list:
            if coding.get('code'):
                return (coding.get('system', ''), coding['code'])
        
        return ("", "")
    
    def normalize_unit(self, value: float, unit: str) -> Tuple[float, str]:
        """
        Normalize value and unit to SI units
        
        Args:
            value: Numeric value
            unit: Unit string
            
        Returns:
            Tuple of (normalized_value, normalized_unit)
        """
        if not unit or not isinstance(value, (int, float)):
            return (value, unit)
        
        unit_clean = unit.strip()
        conversions = self._load_unit_conversions()
        
        if unit_clean in conversions:
            # Get the first target unit (SI unit)
            target_unit = list(conversions[unit_clean].keys())[0]
            conversion_factor = conversions[unit_clean][target_unit]
            
            # Handle lambda functions for complex conversions (like temperature)
            if callable(conversion_factor):
                normalized_value = conversion_factor(value)
            else:
                normalized_value = value * conversion_factor
            
            return (normalized_value, target_unit)
        
        return (value, unit)
    
    def normalize_boolean(self, text: str) -> Optional[bool]:
        """
        Normalize text to boolean value
        
        Args:
            text: Text string to normalize
            
        Returns:
            Boolean value or None if not recognized
        """
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Positive values
        positive_values = {
            'true', 'yes', 'positive', 'present', 'detected', 'found',
            'elevated', 'high', 'increased', 'abnormal', 'positive',
            '1', 'one', 'on', 'active', 'confirmed'
        }
        
        # Negative values
        negative_values = {
            'false', 'no', 'negative', 'absent', 'not detected', 'not found',
            'normal', 'low', 'decreased', '0', 'zero', 'off', 'inactive',
            'unconfirmed', 'none', 'undetected'
        }
        
        if text_lower in positive_values:
            return True
        elif text_lower in negative_values:
            return False
        
        return None
    
    def normalize_enum(self, text: str, valid_values: List[str] = None) -> Optional[str]:
        """
        Normalize text to enum value
        
        Args:
            text: Text string to normalize
            valid_values: List of valid enum values (optional)
            
        Returns:
            Normalized enum value or None if not recognized
        """
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Common medical enum normalizations
        enum_mappings = {
            # Gender
            'male': 'male',
            'm': 'male',
            'man': 'male',
            'female': 'female', 
            'f': 'female',
            'woman': 'female',
            
            # Severity
            'mild': 'mild',
            'moderate': 'moderate',
            'severe': 'severe',
            'critical': 'critical',
            
            # Status
            'active': 'active',
            'inactive': 'inactive',
            'resolved': 'resolved',
            'chronic': 'chronic',
            'acute': 'acute',
            
            # HER2 status
            'positive': 'positive',
            'pos': 'positive',
            '+': 'positive',
            'negative': 'negative',
            'neg': 'negative',
            '-': 'negative',
            'equivocal': 'equivocal',
            'unknown': 'unknown',
            
            # ECOG performance status
            '0': '0',
            '1': '1', 
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            'zero': '0',
            'one': '1',
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5'
        }
        
        # Check exact match first
        if text_lower in enum_mappings:
            return enum_mappings[text_lower]
        
        # Check if it's in valid_values (if provided)
        if valid_values:
            for valid_value in valid_values:
                if text_lower == valid_value.lower():
                    return valid_value
        
        # Try partial matching
        for key, value in enum_mappings.items():
            if key in text_lower or text_lower in key:
                return value
        
        return None
    
    def normalize_lab_value(self, value: float, unit: str, test_name: str = None) -> Dict[str, Any]:
        """
        Comprehensive lab value normalization using the new LabUnitNormalizer
        
        Args:
            value: Numeric value
            unit: Unit string
            test_name: Name of the lab test (optional)
            
        Returns:
            Dictionary with normalized values and metadata
        """
        # Import the lab normalizer
        try:
            from .unit_normalizer import lab_normalizer
        except ImportError:
            from matcher.unit_normalizer import lab_normalizer
        
        result = {
            'original_value': value,
            'original_unit': unit,
            'normalized_value': value,
            'normalized_unit': unit,
            'ucum_unit': self._normalize_unit(unit)
        }
        
        # Use the new lab normalizer for test-specific conversions
        if test_name and unit:
            normalized_value, normalized_unit = lab_normalizer.normalize_unit(value, unit, test_name)
            result['normalized_value'] = normalized_value
            result['normalized_unit'] = normalized_unit
            
            # Also store as SI value for backward compatibility
            result['si_value'] = normalized_value
            result['si_unit'] = normalized_unit
        
        return result
    
    def _extract_research_study_criteria(self, research_study: Dict[str, Any], predicates: TrialPredicates):
        """Extract criteria from ResearchStudy resource"""
        # Extract from description or notes
        description = research_study.get('description', '')
        notes = research_study.get('note', [])
        
        if description:
            self._parse_criteria_text(description, predicates)
        
        for note in notes:
            if isinstance(note, dict) and 'text' in note:
                self._parse_criteria_text(note['text'], predicates)
    
    def _extract_condition_criteria(self, condition: Dict[str, Any], predicates: TrialPredicates, is_inclusion: bool = True):
        """Extract condition-based criteria"""
        criteria = {
            'type': 'condition',
            'text': '',
            'codes': [],
            'severity': None,
            'is_inclusion': is_inclusion
        }
        
        # Extract condition information (similar to patient extraction)
        code = condition.get('code', {})
        if code:
            coding_list = code.get('coding', [])
            if coding_list:
                criteria['text'] = coding_list[0].get('display', '')
                for coding in coding_list:
                    criteria['codes'].append({
                        'system': coding.get('system', ''),
                        'code': coding.get('code', ''),
                        'display': coding.get('display', '')
                    })
            
            if not criteria['text']:
                criteria['text'] = code.get('text', '')
        
        # Extract severity
        severity = condition.get('severity', {})
        if severity:
            severity_coding = severity.get('coding', [{}])[0]
            criteria['severity'] = {
                'system': severity_coding.get('system', ''),
                'code': severity_coding.get('code', ''),
                'display': severity_coding.get('display', '')
            }
        
        if is_inclusion:
            predicates.inclusion.append(criteria)
        else:
            predicates.exclusion.append(criteria)
    
    def _extract_observation_criteria(self, observation: Dict[str, Any], predicates: TrialPredicates, is_inclusion: bool = True):
        """Extract observation-based criteria"""
        criteria = {
            'type': 'observation',
            'text': '',
            'codes': [],
            'value': None,
            'unit': None,
            'normalized_unit': None,
            'comparator': None,  # e.g., '>', '<', '>=', '<=', '='
            'is_inclusion': is_inclusion
        }
        
        # Extract observation information
        code = observation.get('code', {})
        if code:
            coding_list = code.get('coding', [])
            if coding_list:
                criteria['text'] = coding_list[0].get('display', '')
                for coding in coding_list:
                    criteria['codes'].append({
                        'system': coding.get('system', ''),
                        'code': coding.get('code', ''),
                        'display': coding.get('display', '')
                    })
            
            if not criteria['text']:
                criteria['text'] = code.get('text', '')
        
        # Extract value and unit
        value_quantity = observation.get('valueQuantity')
        if value_quantity:
            criteria['value'] = value_quantity.get('value')
            criteria['unit'] = value_quantity.get('unit', '')
            criteria['normalized_unit'] = self._normalize_unit(value_quantity.get('unit', ''))
        
        if is_inclusion:
            predicates.inclusion.append(criteria)
        else:
            predicates.exclusion.append(criteria)
    
    def _parse_criteria_text(self, text: str, predicates: TrialPredicates):
        """Parse free text criteria into structured format"""
        # Simple parsing - look for inclusion/exclusion keywords
        text_lower = text.lower()
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Determine if inclusion or exclusion
            is_inclusion = True
            if any(word in sentence.lower() for word in ['exclude', 'exclusion', 'not', 'without', 'absence']):
                is_inclusion = False
            
            # Extract criteria
            criteria = {
                'type': 'text',
                'text': sentence,
                'is_inclusion': is_inclusion,
                'extracted_entities': self._extract_entities_from_text(sentence)
            }
            
            if is_inclusion:
                predicates.inclusion.append(criteria)
            else:
                predicates.exclusion.append(criteria)
    
    def _extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from free text using EMR mappings"""
        entities = []
        
        # Look for known terms in EMR mappings
        for term, mapping in self.emr_mappings.items():
            if term.lower() in text.lower():
                entities.append({
                    'text': term,
                    'type': 'mapped_term',
                    'mapping': mapping
                })
        
        # Look for age patterns
        age_patterns = [
            r'(\d+)\s*(?:years?|yrs?|y)\s*old',
            r'age\s*(?:of\s*)?(\d+)',
            r'(\d+)\s*(?:years?|yrs?|y)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities.append({
                    'text': match.group(0),
                    'type': 'age',
                    'value': int(match.group(1))
                })
        
        # Look for lab value patterns
        lab_patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg/dL|mmol/L|g/dL|ng/mL|pg/mL|U/L|mIU/L)',
            r'(\d+(?:\.\d+)?)\s*(mmHg|mm Hg|°C|°F)'
        ]
        
        for pattern in lab_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'text': match.group(0),
                    'type': 'lab_value',
                    'value': float(match.group(1)),
                    'unit': match.group(2),
                    'normalized_unit': self._normalize_unit(match.group(2))
                })
        
        return entities

def create_sample_patient_bundle() -> Dict[str, Any]:
    """Create a sample patient FHIR bundle for testing"""
    return {
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
                    "resourceType": "Condition",
                    "id": "condition-001",
                    "clinicalStatus": {
                        "coding": [{"code": "active"}]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "254637007",
                                "display": "Biliary tract cancer"
                            }
                        ]
                    },
                    "severity": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "255604002",
                                "display": "Moderate"
                            }
                        ]
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "observation-001",
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
                    ],
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "85319-0",
                                "display": "HER2"
                            }
                        ]
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "260413007",
                                "display": "Positive"
                            }
                        ]
                    }
                }
            }
        ]
    }

def create_sample_trial_bundle() -> Dict[str, Any]:
    """Create a sample trial FHIR bundle for testing"""
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "ResearchStudy",
                    "id": "trial-001",
                    "title": "HER2+ Biliary Tract Cancer Study",
                    "description": "Study for patients with HER2 positive biliary tract cancer. Inclusion: Age 18-75, ECOG ≤ 2. Exclusion: Previous treatment with Trastuzumab."
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "trial-condition-001",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "254637007",
                                "display": "Biliary tract cancer"
                            }
                        ]
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "trial-obs-001",
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "85319-0",
                                "display": "HER2"
                            }
                        ]
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "260413007",
                                "display": "Positive"
                            }
                        ]
                    }
                }
            }
        ]
    }

def test_feature_extraction():
    """Test the feature extraction functionality"""
    print("🧪 Testing Feature Extraction")
    print("=" * 50)
    
    # Initialize extractor
    extractor = FeatureExtractor()
    
    # Create sample bundles
    patient_bundle = create_sample_patient_bundle()
    trial_bundle = create_sample_trial_bundle()
    
    # Extract patient features
    print("\n📋 Extracting Patient Features:")
    patient_features = extractor.extract_patient_features(patient_bundle)
    
    print(f"   • Age: {patient_features.age}")
    print(f"   • Gender: {patient_features.gender}")
    print(f"   • Conditions: {len(patient_features.conditions)}")
    for condition in patient_features.conditions:
        print(f"     - {condition['text']} ({condition['status']})")
    
    print(f"   • Observations: {len(patient_features.observations)}")
    for obs in patient_features.observations:
        print(f"     - {obs['text']} ({obs['status']})")
    
    print(f"   • Medications: {len(patient_features.medications)}")
    for med in patient_features.medications:
        print(f"     - {med['text']} ({med['status']})")
    
    # Extract trial predicates
    print("\n🔬 Extracting Trial Predicates:")
    trial_predicates = extractor.extract_trial_predicates(trial_bundle)
    
    print(f"   • Inclusion Criteria: {len(trial_predicates.inclusion)}")
    for criteria in trial_predicates.inclusion:
        print(f"     - {criteria['text']} ({criteria['type']})")
    
    print(f"   • Exclusion Criteria: {len(trial_predicates.exclusion)}")
    for criteria in trial_predicates.exclusion:
        print(f"     - {criteria['text']} ({criteria['type']})")
    
    print("\n✅ Feature extraction test completed!")

if __name__ == "__main__":
    test_feature_extraction()
