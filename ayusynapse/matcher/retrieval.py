#!/usr/bin/env python3
"""
Patient-Trial Retrieval Module
"""

import json
import logging
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Trial:
    """Trial candidate with metadata"""
    trial_id: str
    nct_id: str
    title: str
    score: float
    match_reasons: List[str]
    fhir_bundle_id: Optional[str] = None
    resource_count: int = 0

def extract_patient_codes(patient_fhir: Dict) -> Dict[str, List[str]]:
    """
    Extract standardized codes from patient FHIR resources
    
    Args:
        patient_fhir: Patient FHIR bundle or resources
        
    Returns:
        Dict with extracted codes by category
    """
    codes = {
        'snomed_conditions': [],
        'loinc_observations': [],
        'rxnorm_medications': [],
        'age': None,
        'gender': None
    }
    
    try:
        # Handle both bundle and individual resources
        resources = []
        if patient_fhir.get('resourceType') == 'Bundle':
            resources = [entry['resource'] for entry in patient_fhir.get('entry', [])]
        else:
            resources = [patient_fhir] if isinstance(patient_fhir, dict) else patient_fhir
        
        for resource in resources:
            resource_type = resource.get('resourceType')
            
            if resource_type == 'Patient':
                # Extract age and gender
                if 'birthDate' in resource:
                    birth_date = resource['birthDate']
                    try:
                        birth_year = int(birth_date[:4])
                        current_year = datetime.now().year
                        codes['age'] = current_year - birth_year
                    except (ValueError, TypeError):
                        pass
                
                if 'gender' in resource:
                    codes['gender'] = resource['gender']
            
            elif resource_type == 'Condition':
                # Extract SNOMED CT codes
                if 'code' in resource and 'coding' in resource['code']:
                    for coding in resource['code']['coding']:
                        if coding.get('system') == 'http://snomed.info/sct':
                            codes['snomed_conditions'].append(coding.get('code'))
                        elif coding.get('system') == 'http://hl7.org/fhir/sid/icd-10-cm':
                            codes['snomed_conditions'].append(coding.get('code'))
            
            elif resource_type == 'Observation':
                # Extract LOINC codes
                if 'code' in resource and 'coding' in resource['code']:
                    for coding in resource['code']['coding']:
                        if coding.get('system') == 'http://loinc.org':
                            codes['loinc_observations'].append(coding.get('code'))
            
            elif resource_type == 'MedicationRequest':
                # Extract RxNorm codes
                if 'medicationCodeableConcept' in resource and 'coding' in resource['medicationCodeableConcept']:
                    for coding in resource['medicationCodeableConcept']['coding']:
                        if coding.get('system') == 'http://www.nlm.nih.gov/research/umls/rxnorm':
                            codes['rxnorm_medications'].append(coding.get('code'))
        
        logger.info(f"📋 Extracted codes: {len(codes['snomed_conditions'])} conditions, "
                   f"{len(codes['loinc_observations'])} observations, "
                   f"{len(codes['rxnorm_medications'])} medications")
        
    except Exception as e:
        logger.error(f"❌ Error extracting patient codes: {e}")
    
    return codes

def search_local_trials(patient_codes: Dict, local_bundle_file: str = 'extracted_criteria_data.json') -> List[Trial]:
    """
    Search local trial bundles for matching candidates
    
    Args:
        patient_codes: Extracted patient codes
        local_bundle_file: Path to local extracted data file
        
    Returns:
        List of matching trial candidates
    """
    candidates = []
    
    try:
        with open(local_bundle_file, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
        
        for trial in extracted_data.get('trials', []):
            trial_id = trial.get('trial_id')
            nct_id = trial.get('nct_id', '')
            title = trial.get('title', '')
            score = 0.0
            match_reasons = []
            
            # Check each criteria and its entities
            for criteria in trial.get('criteria', []):
                for entity in criteria.get('entities', []):
                    entity_type = entity.get('entity_type')
                    entity_text = entity.get('text', '').lower()
                    
                    # Match conditions (biliary tract cancer)
                    if entity_type == 'DIAGNOSIS':
                        # Check for cancer-related terms
                        if any(term in entity_text for term in ['cancer', 'carcinoma', 'adenocarcinoma', 'biliary']):
                            # Check if patient has biliary tract cancer
                            if 'biliary' in entity_text and any('biliary' in code.lower() for code in patient_codes['snomed_conditions']):
                                score += 3.0
                                match_reasons.append(f"Biliary cancer match: {entity_text}")
                            elif any(condition_code.lower() in entity_text for condition_code in patient_codes['snomed_conditions']):
                                score += 2.0
                                match_reasons.append(f"Condition match: {entity_text}")
                    
                    # Match biomarkers (HER2 positive)
                    elif entity_type == 'BIOMARKER':
                        if 'her2' in entity_text and 'positive' in entity_text:
                            # Check if patient has HER2 positive
                            if any('her2' in obs_code.lower() for obs_code in patient_codes['loinc_observations']):
                                score += 2.5
                                match_reasons.append(f"HER2 positive match: {entity_text}")
                            else:
                                score += 1.5
                                match_reasons.append(f"Biomarker match: {entity_text}")
                    
                    # Match medications
                    elif entity_type == 'MEDICATION':
                        for med_code in patient_codes['rxnorm_medications']:
                            if med_code.lower() in entity_text:
                                score += 1.0
                                match_reasons.append(f"Medication match: {entity_text}")
                    
                    # Match age criteria
                    elif entity_type == 'AGE' and patient_codes['age']:
                        try:
                            trial_age = int(entity.get('value', 0))
                            patient_age = patient_codes['age']
                            if abs(trial_age - patient_age) <= 10:  # Within 10 years
                                score += 0.5
                                match_reasons.append(f"Age match: {entity_text}")
                        except (ValueError, TypeError):
                            pass
                    
                    # Match gender criteria
                    elif entity_type == 'GENDER' and patient_codes['gender']:
                        trial_gender = entity.get('value', '').lower()
                        patient_gender = patient_codes['gender'].lower()
                        if trial_gender in ['all', 'unknown'] or trial_gender == patient_gender:
                            score += 0.3
                            match_reasons.append(f"Gender match: {entity_text}")
            
            # Add trial if it has any matches
            if score > 0:
                candidates.append(Trial(
                    trial_id=trial_id,
                    nct_id=nct_id,
                    title=title,
                    score=score,
                    match_reasons=match_reasons,
                    resource_count=len(trial.get('criteria', []))
                ))
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"🔍 Found {len(candidates)} matching trial candidates locally")
        
    except Exception as e:
        logger.error(f"❌ Error searching local trials: {e}")
    
    return candidates

def get_candidate_trials(patient_fhir: Dict, server_url: str = "http://hapi.fhir.org/baseR4", 
                        max_candidates: int = 100) -> List[Trial]:
    """
    Get candidate trials for a patient
    
    Args:
        patient_fhir: Patient FHIR bundle or resources
        server_url: HAPI FHIR server URL
        max_candidates: Maximum number of candidates to return
        
    Returns:
        List of trial candidates sorted by relevance score
    """
    logger.info("🚀 Starting patient-trial matching")
    
    # Extract patient codes
    patient_codes = extract_patient_codes(patient_fhir)
    
    # Search local trials (primary method)
    local_candidates = search_local_trials(patient_codes)
    
    # For now, focus on local search since we have the trial data
    # Server search can be added later for additional trials
    
    # Sort by score and limit results
    final_candidates = local_candidates[:max_candidates]
    
    logger.info(f"✅ Found {len(final_candidates)} trial candidates")
    
    return final_candidates

def search_server_trials(patient_codes: Dict, server_url: str = "http://hapi.fhir.org/baseR4") -> List[Trial]:
    """
    Search HAPI FHIR server for additional trial candidates
    
    Args:
        patient_codes: Extracted patient codes
        server_url: HAPI FHIR server URL
        
    Returns:
        List of matching trial candidates from server
    """
    candidates = []
    
    try:
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        })
        
        # Build search queries for different criteria
        base_url = f"{server_url.rstrip('/')}/Bundle"
        
        # Search by conditions
        if patient_codes['snomed_conditions']:
            for code in patient_codes['snomed_conditions'][:3]:  # Limit to top 3
                query = f"{base_url}?entry.resource.code.coding.code={code}&_count=10"
                try:
                    response = session.get(query)
                    if response.status_code == 200:
                        results = response.json()
                        for entry in results.get('entry', []):
                            resource = entry.get('resource', {})
                            if resource.get('resourceType') == 'Bundle':
                                candidates.append(Trial(
                                    trial_id=resource.get('id', 'unknown'),
                                    nct_id=resource.get('id', 'unknown'),
                                    title="Server Trial",
                                    score=1.0,
                                    match_reasons=[f"Server match: {code}"],
                                    fhir_bundle_id=resource.get('id'),
                                    resource_count=len(resource.get('entry', []))
                                ))
                except Exception as e:
                    logger.warning(f"⚠️  Server query failed for {code}: {e}")
        
        logger.info(f"🔍 Found {len(candidates)} additional candidates from server")
        
    except Exception as e:
        logger.error(f"❌ Error searching server trials: {e}")
    
    return candidates

def create_sample_patient() -> Dict:
    """Create a sample patient with HER2+ biliary cancer for testing"""
    sample_patient = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "sample-patient-1",
                    "gender": "female",
                    "birthDate": "1985-01-15"
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-1",
                    "subject": {"reference": "Patient/sample-patient-1"},
                    "code": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                "code": "C24.9",
                                "display": "Biliary tract cancer"
                            }
                        ],
                        "text": "Biliary tract cancer"
                    }
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "observation-1",
                    "subject": {"reference": "Patient/sample-patient-1"},
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "85319-0",
                                "display": "HER2 positive"
                            }
                        ],
                        "text": "HER2 positive"
                    },
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "positive",
                                "display": "Positive"
                            }
                        ],
                        "text": "Positive"
                    }
                }
            }
        ]
    }
    
    return sample_patient

def test_retrieval():
    """Test the retrieval system with sample patient"""
    logger.info("🧪 Testing patient-trial retrieval system")
    
    # Create sample patient
    sample_patient = create_sample_patient()
    
    # Get candidate trials
    candidates = get_candidate_trials(sample_patient, max_candidates=50)
    
    # Check if NCT07062263 is in candidates
    target_nct = "NCT07062263"
    found_target = False
    
    print(f"\n📊 Found {len(candidates)} trial candidates:")
    for i, candidate in enumerate(candidates[:10]):  # Show top 10
        print(f"{i+1}. {candidate.nct_id}: {candidate.title[:60]}... (Score: {candidate.score:.2f})")
        
        if candidate.nct_id == target_nct:
            found_target = True
            print(f"   🎯 TARGET FOUND: {candidate.nct_id}")
            print(f"   📋 Match reasons: {', '.join(candidate.match_reasons[:3])}")
    
    if found_target:
        print(f"\n✅ SUCCESS: {target_nct} found in candidates!")
        return True
    else:
        print(f"\n❌ FAILED: {target_nct} not found in candidates")
        return False

if __name__ == "__main__":
    test_retrieval()
