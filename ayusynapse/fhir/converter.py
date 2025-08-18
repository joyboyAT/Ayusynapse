#!/usr/bin/env python3
"""
FHIR Converter - Single file to convert extracted data to standard HL7 FHIR format
"""

import json
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
from .validator import FHIRValidator
from .fhir_storage import FHIRStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load EMR mappings from processed data
try:
    with open("data/processed/emr_mappings.json", "r") as f:
        emr_mappings = json.load(f)
    logger.info("Loaded EMR mappings successfully")
except Exception as e:
    logger.warning(f"Could not load EMR mappings: {e}")
    emr_mappings = {}

class FHIRConverter:
    """Convert extracted clinical trial data to HL7 FHIR format"""
    
    def __init__(self):
        self.coding_systems = {
            'SNOMED_CT': 'http://snomed.info/sct',
            'LOINC': 'http://loinc.org',
            'ICD_10_CM': 'http://hl7.org/fhir/sid/icd-10-cm',
            'RX_NORM': 'http://www.nlm.nih.gov/research/umls/rxnorm',
            'UCUM': 'http://unitsofmeasure.org'
        }
        
        # ICD-10-CM codes for diagnoses
        self.icd10_codes = {
            'breast cancer': 'C50.9',
            'lung cancer': 'C34.90',
            'colorectal cancer': 'C18.9',
            'prostate cancer': 'C61',
            'pancreatic cancer': 'C25.9',
            'ovarian cancer': 'C56.9',
            'biliary tract cancer': 'C24.9',
            'gastric cancer': 'C16.9',
            'gastroesophageal cancer': 'C16.0',
            'aml': 'C92.0',
            'all': 'C91.0',
            'cll': 'C91.1',
            'mds': 'D46.9',
            'multiple myeloma': 'C90.0',
            'myelodysplastic syndrome': 'D46.9',
            'adenocarcinoma': 'M8140/3',
            'carcinoma': 'M8010/3',
            'cancer': 'C80.1',
            'solid tumors': 'C80.1',
            'metastatic disease': 'C79.9',
            'advanced disease': 'C80.1',
            'relapsed disease': 'C80.1',
            'refractory disease': 'C80.1'
        }
        
        # LOINC codes for lab tests and biomarkers
        self.loinc_codes = {
            'ecog': '424144002',
            'her2': '85319-0',
            'egfr': '85319-1',
            'alk': '85319-2',
            'braf': '85319-3',
            'kras': '85319-4',
            'measurable disease': '260413007'
        }
    
    def get_coding(self, entity_text: str) -> Dict:
        """
        Get coding information for an entity from EMR mappings
        
        Args:
            entity_text: The entity text to look up
            
        Returns:
            Dict with coding information or fallback to text
        """
        # Search through all categories in EMR mappings
        for category, subcategories in emr_mappings.items():
            for subcategory, terms in subcategories.items():
                if entity_text.lower() in terms:
                    term_data = terms[entity_text.lower()]
                    if term_data.get('fhir_mappings'):
                        # Extract coding from FHIR mapping string
                        fhir_mapping = term_data['fhir_mappings'][0]
                        # Parse the FHIR mapping string to extract code_system and code_value
                        if 'code_system=' in fhir_mapping and 'code_value=' in fhir_mapping:
                            code_system_match = re.search(r"code_system='([^']+)'", fhir_mapping)
                            code_value_match = re.search(r"code_value='([^']+)'", fhir_mapping)
                            
                            if code_system_match and code_value_match:
                                return {
                                    "system": code_system_match.group(1),
                                    "code": code_value_match.group(1),
                                    "display": entity_text
                                }
        
        # Fallback to text if no mapping found
        return {"text": entity_text}
    
    def load_extracted_data(self, file_path: str = 'extracted_criteria_data.json') -> Dict:
        """Load extracted data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded extracted data: {data['summary']['total_trials']} trials")
            return data
        except Exception as e:
            logger.error(f"Error loading extracted data: {e}")
            return {'trials': [], 'summary': {}}
    
    def create_patient_resource(self, trial_id: str, entities: List[Dict]) -> Dict:
        """Create Patient resource for a trial"""
        patient_id = str(uuid.uuid4())
        
        patient = {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
            },
            "identifier": [
                {
                    "system": "http://hospital.example.org/identifiers/patient",
                    "value": f"TRIAL-{trial_id}"
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "text": f"Trial {trial_id} Patient"
                }
            ],
            "gender": "unknown",
            "birthDate": "1980-01-01"
        }
        
        # Update patient with extracted age and gender
        for entity in entities:
            if entity['entity_type'] == 'AGE':
                age = entity['value']
                birth_date = datetime.now() - timedelta(days=age * 365)
                patient['birthDate'] = birth_date.strftime('%Y-%m-%d')
            elif entity['entity_type'] == 'GENDER':
                patient['gender'] = entity['value']
        
        return patient, patient_id
    
    def create_condition_resource(self, entity: Dict, resource_id: int, patient_id: str) -> Dict:
        """Create Condition resource"""
        return {
            "resourceType": "Condition",
            "id": f"condition-{resource_id}",
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Condition"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "problem-list-item",
                            "display": "Problem List Item"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    self.get_coding(entity['text'])
                ],
                "text": entity['text']
            },
            "onsetDateTime": "2024-01-01",
            "recordedDate": datetime.now().isoformat()
        }
    
    def create_observation_resource(self, entity: Dict, resource_id: int, patient_id: str) -> Dict:
        """Create Observation resource"""
        observation = {
            "resourceType": "Observation",
            "id": f"observation-{resource_id}",
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Observation"]
            },
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    self.get_coding(entity['text'])
                ],
                "text": entity['text']
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "issued": datetime.now().isoformat(),
            "performer": [
                {
                    "reference": "Practitioner/example",
                    "display": "Dr. Smith"
                }
            ]
        }
        
        # Add value based on entity type
        if entity['entity_type'] == 'ECOG':
            observation["valueCodeableConcept"] = {
                "coding": [
                    self.get_coding("ECOG")
                ],
                "text": f"ECOG {entity['value']}"
            }
        elif entity['entity_type'] == 'BIOMARKER':
            observation["valueCodeableConcept"] = {
                "coding": [
                    self.get_coding(entity['text'])
                ],
                "text": entity['text']
            }
        elif entity['entity_type'] == 'MEASURABLE_DISEASE':
            observation["valueCodeableConcept"] = {
                "coding": [
                    {
                        "system": self.coding_systems['SNOMED_CT'],
                        "code": "260413007",
                        "display": "Measurable disease"
                    }
                ],
                "text": entity['text']
            }
        elif entity['entity_type'] == 'LIFE_EXPECTANCY':
            if isinstance(entity['value'], dict):
                observation["valueQuantity"] = {
                    "value": entity['value']['value'],
                    "unit": entity['value']['unit'],
                    "system": self.coding_systems['UCUM'],
                    "code": self._get_ucum_code(entity['value']['unit'])
                }
        
        return observation
    
    def _get_icd10_code(self, entity: Dict) -> str:
        """Get ICD-10-CM code for diagnosis"""
        text_lower = entity['text'].lower()
        
        for key, code in self.icd10_codes.items():
            if key in text_lower:
                return code
        
        return 'unknown'
    
    def _get_loinc_code(self, entity: Dict) -> str:
        """Get LOINC code for lab test"""
        text_lower = entity['text'].lower()
        
        for key, code in self.loinc_codes.items():
            if key in text_lower:
                return code
        
        return 'unknown'
    
    def _get_ucum_code(self, unit: str) -> str:
        """Get UCUM code for units"""
        ucum_mapping = {
            'weeks': 'wk',
            'months': 'mo',
            'years': 'a',
            'days': 'd',
            'hours': 'h',
            'minutes': 'min'
        }
        return ucum_mapping.get(unit.lower(), unit)
    
    def convert_trial_to_fhir(self, trial: Dict) -> Dict:
        """Convert a single trial to FHIR Bundle"""
        trial_id = trial['trial_id']
        entities = trial.get('all_entities', [])
        
        # Create Patient resource
        patient_resource, patient_id = self.create_patient_resource(trial_id, entities)
        
        # Create FHIR resources for each entity
        fhir_resources = [patient_resource]
        resource_counter = 1
        
        for entity in entities:
            if entity['resource_type'] == 'Patient':
                continue  # Skip patient entities as we already created the patient resource
            
            if entity['resource_type'] == 'Condition':
                fhir_resource = self.create_condition_resource(entity, resource_counter, patient_id)
            elif entity['resource_type'] == 'Observation':
                fhir_resource = self.create_observation_resource(entity, resource_counter, patient_id)
            else:
                continue
            
            fhir_resources.append(fhir_resource)
            resource_counter += 1
        
        # Create Bundle
        bundle = {
            "resourceType": "Bundle",
            "id": f"trial-{trial_id}-bundle",
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": []
        }
        
        # Add all resources to bundle
        for resource in fhir_resources:
            bundle["entry"].append({
                "resource": resource
            })
        
        return bundle
    
    def convert_all_trials_to_fhir(self, extracted_data: Dict) -> Dict:
        """Convert all trials to FHIR format"""
        logger.info("Starting FHIR conversion...")
        
        all_bundles = []
        total_resources = 0
        
        for trial in extracted_data.get('trials', []):
            bundle = self.convert_trial_to_fhir(trial)
            all_bundles.append({
                'trial_id': trial['trial_id'],
                'nct_id': trial.get('nct_id', ''),
                'title': trial.get('title', ''),
                'fhir_bundle': bundle,
                'resource_count': len(bundle['entry'])
            })
            total_resources += len(bundle['entry'])
        
        # Create master bundle containing all trials
        master_bundle = {
            "resourceType": "Bundle",
            "id": "clinical-trials-master-bundle",
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "entry": []
        }
        
        # Add all trial bundles to master bundle
        for trial_bundle in all_bundles:
            master_bundle["entry"].append({
                "resource": trial_bundle['fhir_bundle']
            })
        
        result = {
            'master_bundle': master_bundle,
            'individual_bundles': all_bundles,
            'summary': {
                'total_trials': len(all_bundles),
                'total_resources': total_resources,
                'conversion_timestamp': datetime.now().isoformat()
            }
        }
        
        logger.info(f"Conversion complete: {len(all_bundles)} trials, {total_resources} resources")
        return result
    
    def save_fhir_data(self, fhir_data: Dict, output_file: str = 'clinical_trials_fhir.json', store_to_server: bool = True) -> None:
        """Save FHIR data to JSON file with validation and optionally store to FHIR server"""
        # Validate the master bundle before saving
        validator = FHIRValidator()
        
        if 'master_bundle' in fhir_data:
            logger.info("Validating master FHIR bundle...")
            if validator.validate_bundle(fhir_data['master_bundle']):
                logger.info("✅ Master bundle validation passed")
            else:
                logger.error("❌ Master bundle validation failed - stopping save")
                return
        
        # Also validate individual bundles
        if 'individual_bundles' in fhir_data:
            logger.info("Validating individual trial bundles...")
            for i, trial_bundle in enumerate(fhir_data['individual_bundles']):
                if 'fhir_bundle' in trial_bundle:
                    if not validator.validate_bundle(trial_bundle['fhir_bundle']):
                        logger.error(f"❌ Trial bundle {i+1} validation failed - stopping save")
                        return
                    else:
                        logger.info(f"✅ Trial bundle {i+1} validation passed")
        
        # Save the validated data to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fhir_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved validated FHIR data to: {output_file}")
        
        # Store to FHIR server if requested
        if store_to_server:
            self.store_fhir_data_to_server(fhir_data)
    
    def store_fhir_data_to_server(self, fhir_data: Dict) -> None:
        """Store FHIR data to HAPI FHIR server"""
        try:
            logger.info("🔄 Connecting to FHIR server for storage...")
            storage = FHIRStorage()
            
            # Store individual trial bundles
            if 'individual_bundles' in fhir_data:
                logger.info(f"📦 Storing {len(fhir_data['individual_bundles'])} individual trial bundles...")
                
                stored_count = 0
                for i, trial_bundle in enumerate(fhir_data['individual_bundles']):
                    if 'fhir_bundle' in trial_bundle:
                        trial_id = trial_bundle.get('trial_id', f'trial_{i+1}')
                        logger.info(f"📤 Storing trial {i+1}: {trial_id}")
                        
                        result = storage.store_bundle(trial_bundle['fhir_bundle'])
                        if result['success']:
                            bundle_id = result['resource_id']
                            logger.info(f"✅ Successfully stored Bundle with ID: {bundle_id}")
                            stored_count += 1
                        else:
                            logger.error(f"❌ Failed to store trial {trial_id}: {result['message']}")
                
                logger.info(f"✅ Successfully stored {stored_count}/{len(fhir_data['individual_bundles'])} trial bundles to FHIR server")
            
            # Store master bundle
            if 'master_bundle' in fhir_data:
                logger.info("📦 Storing master bundle...")
                result = storage.store_bundle(fhir_data['master_bundle'])
                if result['success']:
                    bundle_id = result['resource_id']
                    logger.info(f"✅ Successfully stored Master Bundle with ID: {bundle_id}")
                else:
                    logger.error(f"❌ Failed to store master bundle: {result['message']}")
            
        except Exception as e:
            logger.error(f"❌ Error storing FHIR data to server: {e}")
            logger.info("💡 FHIR data saved locally but not stored to server")

def main():
    """Main function to run the converter"""
    import sys
    
    # Check command line arguments
    store_to_server = True
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-server":
            store_to_server = False
            print("ℹ️  Server storage disabled - will only save locally")
    
    converter = FHIRConverter()
    
    # Load extracted data (try test data first, then fallback to extracted_criteria_data.json)
    try:
        extracted_data = converter.load_extracted_data('test_extracted_data.json')
        if not extracted_data.get('trials'):
            extracted_data = converter.load_extracted_data()
    except:
        extracted_data = converter.load_extracted_data()
    
    if not extracted_data.get('trials'):
        print("❌ No trials found in extracted data. Please run fhir_extractor.py first.")
        return
    
    # Convert to FHIR format
    fhir_data = converter.convert_all_trials_to_fhir(extracted_data)
    
    # Save FHIR data (with optional server storage)
    converter.save_fhir_data(fhir_data, store_to_server=store_to_server)
    
    print(f"✅ Converted {fhir_data['summary']['total_trials']} trials to FHIR")
    print(f"✅ Generated {fhir_data['summary']['total_resources']} FHIR resources")
    print("✅ Saved as: clinical_trials_fhir.json")
    
    if store_to_server:
        print("✅ Stored to FHIR server")
    else:
        print("ℹ️  Skipped server storage")
    
    # Show sample of first trial
    if fhir_data['individual_bundles']:
        first_trial = fhir_data['individual_bundles'][0]
        print(f"\n📋 Sample Trial: {first_trial['trial_id']}")
        print(f"   Title: {first_trial['title'][:50]}...")
        print(f"   Resources: {first_trial['resource_count']}")

if __name__ == "__main__":
    # Test the get_coding function
    converter = FHIRConverter()
    
    print("=== Testing get_coding function ===")
    print("HER2:", converter.get_coding("HER2"))
    print("ECOG:", converter.get_coding("ECOG"))
    print("RandomTerm:", converter.get_coding("RandomTerm"))
    
    print("\n=== Running main conversion ===")
    main()
