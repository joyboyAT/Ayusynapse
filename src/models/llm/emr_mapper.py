"""
EMR Mapping Engine using LLMs
Maps medical terminologies to FHIR structures and report formats.
"""

import json
import requests
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Types of data representation in EMR."""
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    SEMI_STRUCTURED = "semi_structured"

class ReportType(Enum):
    """Types of medical reports."""
    LABORATORY = "laboratory"
    PATHOLOGY = "pathology"
    RADIOLOGY = "radiology"
    CLINICAL = "clinical"
    MEDICATION = "medication"
    VITAL_SIGNS = "vital_signs"

@dataclass
class FHIRMapping:
    """FHIR resource mapping information."""
    resource_type: str
    resource_id: str
    field_path: str
    data_type: str
    code_system: Optional[str] = None
    code_value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None

@dataclass
class ReportMapping:
    """Report mapping information."""
    report_type: ReportType
    section: str
    field_name: str
    extraction_method: str
    confidence: float

class EMRMappingEngine:
    """Maps medical terminologies to EMR data structures using LLMs."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the EMR mapping engine.
        
        Args:
            openai_api_key: OpenAI API key for LLM integration
        """
        self.openai_api_key = openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
        # FHIR resource mappings
        self.fhir_resources = {
            'demographics': {
                'Patient': ['birthDate', 'gender', 'race', 'ethnicity'],
                'Observation': ['bodyMassIndex', 'height', 'weight']
            },
            'laboratory': {
                'Observation': ['laboratory', 'labResults'],
                'DiagnosticReport': ['laboratory', 'pathology']
            },
            'clinical': {
                'Observation': ['vitalSigns', 'performanceStatus'],
                'Condition': ['clinicalStatus', 'severity']
            },
            'pathology': {
                'Observation': ['pathology', 'tumorMarkers'],
                'DiagnosticReport': ['pathology', 'histology']
            },
            'imaging': {
                'DiagnosticReport': ['radiology', 'imaging'],
                'ImagingStudy': ['modality', 'bodySite']
            },
            'medications': {
                'MedicationRequest': ['medication', 'dosage'],
                'MedicationAdministration': ['medication', 'timing']
            }
        }
        
        # Standard medical codes
        self.standard_codes = {
            'LOINC': 'http://loinc.org',
            'SNOMED': 'http://snomed.info/sct',
            'ICD10': 'http://hl7.org/fhir/sid/icd-10-cm',
            'RxNorm': 'http://www.nlm.nih.gov/research/umls/rxnorm',
            'UCUM': 'http://unitsofmeasure.org'
        }
    
    def map_terminology_to_fhir(self, terminology: str, category: str) -> List[FHIRMapping]:
        """
        Map a medical terminology to FHIR resources using LLM.
        
        Args:
            terminology: Medical terminology to map
            category: Category of the terminology
            
        Returns:
            List of FHIR mappings
        """
        prompt = self._create_fhir_mapping_prompt(terminology, category)
        
        try:
            response = self._call_llm(prompt)
            mappings = self._parse_fhir_response(response, terminology, category)
            return mappings
        except Exception as e:
            logger.error(f"Error mapping terminology {terminology}: {e}")
            return self._get_fallback_mapping(terminology, category)
    
    def map_terminology_to_reports(self, terminology: str, category: str) -> List[ReportMapping]:
        """
        Map a medical terminology to report structures using LLM.
        
        Args:
            terminology: Medical terminology to map
            category: Category of the terminology
            
        Returns:
            List of report mappings
        """
        prompt = self._create_report_mapping_prompt(terminology, category)
        
        try:
            response = self._call_llm(prompt)
            mappings = self._parse_report_response(response, terminology, category)
            return mappings
        except Exception as e:
            logger.error(f"Error mapping terminology to reports {terminology}: {e}")
            return self._get_fallback_report_mapping(terminology, category)
    
    def _create_fhir_mapping_prompt(self, terminology: str, category: str) -> str:
        """Create prompt for FHIR mapping."""
        return f"""
        You are a medical informatics expert. Map the medical terminology "{terminology}" 
        (category: {category}) to FHIR resources and fields.
        
        Consider:
        1. Which FHIR resources should contain this data?
        2. What specific fields within those resources?
        3. What standard medical codes (LOINC, SNOMED, etc.) apply?
        4. What units of measurement are relevant?
        5. What reference ranges might apply?
        
        Return your response as a JSON array with objects containing:
        - resource_type: FHIR resource type (e.g., "Observation", "Patient", "Condition")
        - resource_id: Suggested resource ID
        - field_path: Path to the field within the resource
        - data_type: Data type (string, number, code, etc.)
        - code_system: Standard code system (LOINC, SNOMED, etc.)
        - code_value: Specific code value
        - unit: Unit of measurement
        - reference_range: Reference range if applicable
        
        Terminology: {terminology}
        Category: {category}
        """
    
    def _create_report_mapping_prompt(self, terminology: str, category: str) -> str:
        """Create prompt for report mapping."""
        return f"""
        You are a medical informatics expert. Map the medical terminology "{terminology}" 
        (category: {category}) to medical report structures.
        
        Consider:
        1. Which types of reports might contain this data?
        2. What sections within those reports?
        3. How is this data typically extracted from reports?
        4. What is the confidence level for extraction?
        
        Report types: Laboratory, Pathology, Radiology, Clinical, Medication, Vital Signs
        
        Return your response as a JSON array with objects containing:
        - report_type: Type of report (laboratory, pathology, radiology, etc.)
        - section: Section within the report
        - field_name: Field name or label
        - extraction_method: How to extract this data (regex, NLP, etc.)
        - confidence: Confidence level (0.0 to 1.0)
        
        Terminology: {terminology}
        Category: {category}
        """
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        if not self.openai_api_key:
            # Return mock response for demo
            return self._get_mock_llm_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a medical informatics expert specializing in FHIR and EMR data mapping."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _get_mock_llm_response(self, prompt: str) -> str:
        """Get mock LLM response for demo purposes."""
        # Extract terminology and category from prompt
        terminology_match = re.search(r'terminology "(.*?)"', prompt)
        category_match = re.search(r'category: (.*?)\)', prompt)
        
        terminology = terminology_match.group(1) if terminology_match else "unknown"
        category = category_match.group(1) if category_match else "unknown"
        
        # Mock responses based on terminology and category
        if "fhir" in prompt.lower():
            return self._get_mock_fhir_response(terminology, category)
        else:
            return self._get_mock_report_response(terminology, category)
    
    def _get_mock_fhir_response(self, terminology: str, category: str) -> str:
        """Get mock FHIR mapping response."""
        mock_mappings = {
            "ecog": [
                {
                    "resource_type": "Observation",
                    "resource_id": "performance-status-001",
                    "field_path": "valueCodeableConcept",
                    "data_type": "code",
                    "code_system": "http://snomed.info/sct",
                    "code_value": "424144002",
                    "unit": None,
                    "reference_range": "0-4"
                }
            ],
            "hemoglobin": [
                {
                    "resource_type": "Observation",
                    "resource_id": "lab-hemoglobin-001",
                    "field_path": "valueQuantity",
                    "data_type": "quantity",
                    "code_system": "http://loinc.org",
                    "code_value": "789-8",
                    "unit": "g/dL",
                    "reference_range": "12.0-15.5"
                }
            ],
            "her2": [
                {
                    "resource_type": "Observation",
                    "resource_id": "pathology-her2-001",
                    "field_path": "valueCodeableConcept",
                    "data_type": "code",
                    "code_system": "http://loinc.org",
                    "code_value": "85319-0",
                    "unit": None,
                    "reference_range": "Positive/Negative"
                }
            ]
        }
        
        return json.dumps(mock_mappings.get(terminology.lower(), []))
    
    def _get_mock_report_response(self, terminology: str, category: str) -> str:
        """Get mock report mapping response."""
        mock_mappings = {
            "ecog": [
                {
                    "report_type": "clinical",
                    "section": "Physical Examination",
                    "field_name": "Performance Status",
                    "extraction_method": "regex: ECOG\\s*([0-4])",
                    "confidence": 0.9
                }
            ],
            "hemoglobin": [
                {
                    "report_type": "laboratory",
                    "section": "Complete Blood Count",
                    "field_name": "Hemoglobin",
                    "extraction_method": "regex: Hemoglobin\\s*([0-9.]+)\\s*g/dL",
                    "confidence": 0.95
                }
            ],
            "her2": [
                {
                    "report_type": "pathology",
                    "section": "Immunohistochemistry",
                    "field_name": "HER2 Status",
                    "extraction_method": "regex: HER2\\s*(Positive|Negative)",
                    "confidence": 0.85
                }
            ]
        }
        
        return json.dumps(mock_mappings.get(terminology.lower(), []))
    
    def _parse_fhir_response(self, response: str, terminology: str, category: str) -> List[FHIRMapping]:
        """Parse LLM response into FHIR mapping objects."""
        try:
            mappings_data = json.loads(response)
            mappings = []
            
            for mapping_data in mappings_data:
                mapping = FHIRMapping(
                    resource_type=mapping_data.get('resource_type', 'Observation'),
                    resource_id=mapping_data.get('resource_id', f'{terminology}-001'),
                    field_path=mapping_data.get('field_path', 'value'),
                    data_type=mapping_data.get('data_type', 'string'),
                    code_system=mapping_data.get('code_system'),
                    code_value=mapping_data.get('code_value'),
                    unit=mapping_data.get('unit'),
                    reference_range=mapping_data.get('reference_range')
                )
                mappings.append(mapping)
            
            return mappings
        except Exception as e:
            logger.error(f"Error parsing FHIR response: {e}")
            return self._get_fallback_mapping(terminology, category)
    
    def _parse_report_response(self, response: str, terminology: str, category: str) -> List[ReportMapping]:
        """Parse LLM response into report mapping objects."""
        try:
            mappings_data = json.loads(response)
            mappings = []
            
            for mapping_data in mappings_data:
                mapping = ReportMapping(
                    report_type=ReportType(mapping_data.get('report_type', 'clinical')),
                    section=mapping_data.get('section', 'General'),
                    field_name=mapping_data.get('field_name', terminology),
                    extraction_method=mapping_data.get('extraction_method', 'text_search'),
                    confidence=mapping_data.get('confidence', 0.5)
                )
                mappings.append(mapping)
            
            return mappings
        except Exception as e:
            logger.error(f"Error parsing report response: {e}")
            return self._get_fallback_report_mapping(terminology, category)
    
    def _get_fallback_mapping(self, terminology: str, category: str) -> List[FHIRMapping]:
        """Get fallback FHIR mapping when LLM fails."""
        return [
            FHIRMapping(
                resource_type='Observation',
                resource_id=f'{terminology}-fallback',
                field_path='valueString',
                data_type='string',
                code_system=None,
                code_value=None,
                unit=None,
                reference_range=None
            )
        ]
    
    def _get_fallback_report_mapping(self, terminology: str, category: str) -> List[ReportMapping]:
        """Get fallback report mapping when LLM fails."""
        return [
            ReportMapping(
                report_type=ReportType.CLINICAL,
                section='General',
                field_name=terminology,
                extraction_method='text_search',
                confidence=0.3
            )
        ]
    
    def generate_mapping_summary(self, terminologies: List[str], categories: List[str]) -> Dict:
        """
        Generate a comprehensive mapping summary for multiple terminologies.
        
        Args:
            terminologies: List of medical terminologies
            categories: List of corresponding categories
            
        Returns:
            Dictionary with mapping summary
        """
        summary = {
            'total_terminologies': len(terminologies),
            'fhir_mappings': {},
            'report_mappings': {},
            'coverage_analysis': {}
        }
        
        for terminology, category in zip(terminologies, categories):
            # Get FHIR mappings
            fhir_mappings = self.map_terminology_to_fhir(terminology, category)
            summary['fhir_mappings'][terminology] = fhir_mappings
            
            # Get report mappings
            report_mappings = self.map_terminology_to_reports(terminology, category)
            summary['report_mappings'][terminology] = report_mappings
            
            # Analyze coverage
            summary['coverage_analysis'][terminology] = {
                'fhir_resources': len(set(m.resource_type for m in fhir_mappings)),
                'report_types': len(set(m.report_type for m in report_mappings)),
                'avg_confidence': sum(m.confidence for m in report_mappings) / len(report_mappings) if report_mappings else 0
            }
        
        return summary


def main():
    """Demo function to test EMR mapping."""
    mapper = EMRMappingEngine()
    
    # Test terminologies
    test_terminologies = ['ECOG', 'hemoglobin', 'HER2']
    test_categories = ['clinical', 'laboratory', 'pathology']
    
    print("Testing EMR Mapping Engine...")
    
    for terminology, category in zip(test_terminologies, test_categories):
        print(f"\n=== Mapping {terminology} ({category}) ===")
        
        # FHIR mapping
        fhir_mappings = mapper.map_terminology_to_fhir(terminology, category)
        print(f"FHIR Mappings ({len(fhir_mappings)}):")
        for mapping in fhir_mappings:
            print(f"  - {mapping.resource_type}.{mapping.field_path}")
        
        # Report mapping
        report_mappings = mapper.map_terminology_to_reports(terminology, category)
        print(f"Report Mappings ({len(report_mappings)}):")
        for mapping in report_mappings:
            print(f"  - {mapping.report_type.value}: {mapping.section} -> {mapping.field_name} (confidence: {mapping.confidence})")


if __name__ == "__main__":
    main() 