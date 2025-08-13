"""
Patient-Trial Matching Module using Generative AI
Step 7 of the Clinical Trials Analytics Pipeline
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PatientEMR:
    """Patient EMR data structure"""
    demographics: Dict[str, Any]
    clinical_data: Dict[str, Any]
    lab_results: Dict[str, Any]
    pathology_reports: List[str]
    radiology_reports: List[str]
    medications: List[str]
    comorbidities: List[str]

@dataclass
class TrialRequirements:
    """Clinical trial requirements structure"""
    trial_id: str
    trial_name: str
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    required_indicators: Dict[str, Any]
    disease_area: str

@dataclass
class MatchingResult:
    """Patient-trial matching result"""
    trial_id: str
    trial_name: str
    overall_score: float
    category_scores: Dict[str, float]
    matched_indicators: List[str]
    missing_indicators: List[str]
    conflicting_indicators: List[str]
    reasoning: str
    confidence_level: str

class PatientTrialMatcher:
    """
    Generative AI module for matching patients to clinical trials
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.llm_available = openai_api_key is not None
        
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt (mock implementation if no API key)"""
        if not self.llm_available:
            # Mock response for demonstration
            return self._generate_mock_response(prompt)
        
        # Real OpenAI API call would go here
        try:
            import openai
            openai.api_key = self.openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock LLM response for demonstration"""
        if "demographics" in prompt.lower():
            return "Patient meets age requirements (45 years old) and gender criteria (female)."
        elif "clinical" in prompt.lower():
            return "ECOG performance status is 1, which meets trial requirements. No brain metastases detected."
        elif "biomarker" in prompt.lower():
            return "EGFR mutation positive, ALK negative. Liver function tests within normal limits."
        elif "exclusion" in prompt.lower():
            return "Patient has no exclusion criteria: not pregnant, no recent chemotherapy, no uncontrolled diabetes."
        else:
            return "Patient appears to meet most trial criteria with good overall match."
    
    def extract_patient_indicators(self, patient_emr: PatientEMR) -> Dict[str, Any]:
        """Extract key indicators from patient EMR data"""
        indicators = {
            'demographics': {},
            'clinical': {},
            'biomarkers': {},
            'pathology': {},
            'medications': [],
            'comorbidities': []
        }
        
        # Extract demographics
        indicators['demographics'] = {
            'age': patient_emr.demographics.get('age'),
            'gender': patient_emr.demographics.get('gender'),
            'race': patient_emr.demographics.get('race')
        }
        
        # Extract clinical data
        indicators['clinical'] = {
            'ecog_status': patient_emr.clinical_data.get('ecog_status'),
            'karnofsky_score': patient_emr.clinical_data.get('karnofsky_score'),
            'tumor_grade': patient_emr.clinical_data.get('tumor_grade'),
            'tumor_stage': patient_emr.clinical_data.get('tumor_stage'),
            'metastases': patient_emr.clinical_data.get('metastases', [])
        }
        
        # Extract lab results and biomarkers
        indicators['biomarkers'] = {
            'egfr_mutation': patient_emr.lab_results.get('egfr_mutation'),
            'alk_rearrangement': patient_emr.lab_results.get('alk_rearrangement'),
            'liver_function': patient_emr.lab_results.get('liver_function'),
            'kidney_function': patient_emr.lab_results.get('kidney_function'),
            'blood_counts': patient_emr.lab_results.get('blood_counts', {})
        }
        
        # Extract medications and comorbidities
        indicators['medications'] = patient_emr.medications
        indicators['comorbidities'] = patient_emr.comorbidities
        
        return indicators
    
    def evaluate_demographics_match(self, patient_indicators: Dict, trial_requirements: TrialRequirements) -> Tuple[float, List[str], List[str]]:
        """Evaluate demographic criteria match"""
        matched = []
        missing = []
        score = 0.0
        
        patient_demo = patient_indicators['demographics']
        required_demo = trial_requirements.required_indicators.get('demographics', {})
        
        # Age evaluation
        if 'age_range' in required_demo:
            min_age, max_age = required_demo['age_range']
            patient_age = patient_demo.get('age')
            if patient_age and min_age <= patient_age <= max_age:
                matched.append(f"Age {patient_age} within range {min_age}-{max_age}")
                score += 0.4
            else:
                missing.append(f"Age {patient_age} outside required range {min_age}-{max_age}")
        
        # Gender evaluation
        if 'gender' in required_demo:
            required_gender = required_demo['gender']
            patient_gender = patient_demo.get('gender')
            if patient_gender == required_gender:
                matched.append(f"Gender {patient_gender} matches requirement")
                score += 0.3
            else:
                missing.append(f"Gender {patient_gender} doesn't match required {required_gender}")
        
        # Race evaluation (if applicable)
        if 'race' in required_demo:
            required_races = required_demo['race']
            patient_race = patient_demo.get('race')
            if patient_race in required_races:
                matched.append(f"Race {patient_race} matches requirements")
                score += 0.3
            else:
                missing.append(f"Race {patient_race} not in required list")
        
        return min(score, 1.0), matched, missing
    
    def evaluate_clinical_match(self, patient_indicators: Dict, trial_requirements: TrialRequirements) -> Tuple[float, List[str], List[str]]:
        """Evaluate clinical criteria match"""
        matched = []
        missing = []
        score = 0.0
        
        patient_clinical = patient_indicators['clinical']
        required_clinical = trial_requirements.required_indicators.get('clinical', {})
        
        # ECOG Performance Status
        if 'ecog_status' in required_clinical:
            required_ecog = required_clinical['ecog_status']
            patient_ecog = patient_clinical.get('ecog_status')
            if patient_ecog is not None and patient_ecog <= required_ecog:
                matched.append(f"ECOG status {patient_ecog} meets requirement ≤{required_ecog}")
                score += 0.3
            else:
                missing.append(f"ECOG status {patient_ecog} doesn't meet requirement ≤{required_ecog}")
        
        # Tumor Grade
        if 'tumor_grade' in required_clinical:
            required_grade = required_clinical['tumor_grade']
            patient_grade = patient_clinical.get('tumor_grade')
            if patient_grade and patient_grade <= required_grade:
                matched.append(f"Tumor grade {patient_grade} meets requirement ≤{required_grade}")
                score += 0.3
            else:
                missing.append(f"Tumor grade {patient_grade} doesn't meet requirement ≤{required_grade}")
        
        # Metastases evaluation
        if 'no_brain_metastases' in required_clinical and required_clinical['no_brain_metastases']:
            patient_metastases = patient_clinical.get('metastases', [])
            if 'brain' not in patient_metastases:
                matched.append("No brain metastases detected")
                score += 0.4
            else:
                missing.append("Brain metastases detected (exclusion criteria)")
        
        return min(score, 1.0), matched, missing
    
    def evaluate_biomarker_match(self, patient_indicators: Dict, trial_requirements: TrialRequirements) -> Tuple[float, List[str], List[str]]:
        """Evaluate biomarker criteria match"""
        matched = []
        missing = []
        score = 0.0
        
        patient_biomarkers = patient_indicators['biomarkers']
        required_biomarkers = trial_requirements.required_indicators.get('biomarkers', {})
        
        # EGFR mutation
        if 'egfr_mutation' in required_biomarkers:
            required_egfr = required_biomarkers['egfr_mutation']
            patient_egfr = patient_biomarkers.get('egfr_mutation')
            if patient_egfr == required_egfr:
                matched.append(f"EGFR mutation {patient_egfr} matches requirement")
                score += 0.4
            else:
                missing.append(f"EGFR mutation {patient_egfr} doesn't match required {required_egfr}")
        
        # ALK rearrangement
        if 'alk_rearrangement' in required_biomarkers:
            required_alk = required_biomarkers['alk_rearrangement']
            patient_alk = patient_biomarkers.get('alk_rearrangement')
            if patient_alk == required_alk:
                matched.append(f"ALK rearrangement {patient_alk} matches requirement")
                score += 0.3
            else:
                missing.append(f"ALK rearrangement {patient_alk} doesn't match required {required_alk}")
        
        # Liver function
        if 'liver_function_normal' in required_biomarkers and required_biomarkers['liver_function_normal']:
            liver_function = patient_biomarkers.get('liver_function', {})
            if liver_function.get('normal', False):
                matched.append("Liver function tests normal")
                score += 0.3
            else:
                missing.append("Liver function tests abnormal")
        
        return min(score, 1.0), matched, missing
    
    def evaluate_exclusion_criteria(self, patient_indicators: Dict, trial_requirements: TrialRequirements) -> Tuple[float, List[str], List[str]]:
        """Evaluate exclusion criteria"""
        conflicting = []
        safe = []
        score = 1.0  # Start with perfect score, deduct for conflicts
        
        patient_meds = patient_indicators['medications']
        patient_comorbidities = patient_indicators['comorbidities']
        
        # Check exclusion medications
        exclusion_meds = trial_requirements.required_indicators.get('exclusion_medications', [])
        for med in exclusion_meds:
            if med.lower() in [m.lower() for m in patient_meds]:
                conflicting.append(f"Taking exclusion medication: {med}")
                score -= 0.5
        
        # Check exclusion comorbidities
        exclusion_comorbidities = trial_requirements.required_indicators.get('exclusion_comorbidities', [])
        for comorbidity in exclusion_comorbidities:
            if comorbidity.lower() in [c.lower() for c in patient_comorbidities]:
                conflicting.append(f"Has exclusion comorbidity: {comorbidity}")
                score -= 0.5
        
        if not conflicting:
            safe.append("No exclusion criteria conflicts detected")
        
        return max(score, 0.0), safe, conflicting
    
    def calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate overall matching score"""
        weights = {
            'demographics': 0.2,
            'clinical': 0.3,
            'biomarkers': 0.3,
            'exclusion': 0.2
        }
        
        overall_score = 0.0
        for category, score in category_scores.items():
            weight = weights.get(category, 0.1)
            overall_score += score * weight
        
        return min(overall_score, 1.0)
    
    def determine_confidence_level(self, overall_score: float) -> str:
        """Determine confidence level based on score"""
        if overall_score >= 0.9:
            return "HIGH"
        elif overall_score >= 0.7:
            return "MEDIUM"
        elif overall_score >= 0.5:
            return "LOW"
        else:
            return "POOR"
    
    def match_patient_to_trial(self, patient_emr: PatientEMR, trial_requirements: TrialRequirements) -> MatchingResult:
        """Match a patient to a specific clinical trial"""
        
        # Extract patient indicators
        patient_indicators = self.extract_patient_indicators(patient_emr)
        
        # Evaluate each category
        demo_score, demo_matched, demo_missing = self.evaluate_demographics_match(patient_indicators, trial_requirements)
        clinical_score, clinical_matched, clinical_missing = self.evaluate_clinical_match(patient_indicators, trial_requirements)
        biomarker_score, biomarker_matched, biomarker_missing = self.evaluate_biomarker_match(patient_indicators, trial_requirements)
        exclusion_score, exclusion_safe, exclusion_conflicts = self.evaluate_exclusion_criteria(patient_indicators, trial_requirements)
        
        # Calculate category scores
        category_scores = {
            'demographics': demo_score,
            'clinical': clinical_score,
            'biomarkers': biomarker_score,
            'exclusion': exclusion_score
        }
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(category_scores)
        
        # Compile results
        all_matched = demo_matched + clinical_matched + biomarker_matched + exclusion_safe
        all_missing = demo_missing + clinical_missing + biomarker_missing
        all_conflicting = exclusion_conflicts
        
        # Generate reasoning using LLM
        reasoning_prompt = f"""
        Patient-Trial Matching Analysis:
        
        Trial: {trial_requirements.trial_name}
        Overall Score: {overall_score:.2f}
        
        Matched Criteria: {all_matched}
        Missing Criteria: {all_missing}
        Conflicting Criteria: {all_conflicting}
        
        Provide a concise summary of this patient's suitability for this trial.
        """
        
        reasoning = self._call_llm(reasoning_prompt)
        confidence_level = self.determine_confidence_level(overall_score)
        
        return MatchingResult(
            trial_id=trial_requirements.trial_id,
            trial_name=trial_requirements.trial_name,
            overall_score=overall_score,
            category_scores=category_scores,
            matched_indicators=all_matched,
            missing_indicators=all_missing,
            conflicting_indicators=all_conflicting,
            reasoning=reasoning,
            confidence_level=confidence_level
        )
    
    def match_patient_to_multiple_trials(self, patient_emr: PatientEMR, trials: List[TrialRequirements]) -> List[MatchingResult]:
        """Match a patient to multiple clinical trials"""
        results = []
        
        for trial in trials:
            try:
                result = self.match_patient_to_trial(patient_emr, trial)
                results.append(result)
            except Exception as e:
                logger.error(f"Error matching patient to trial {trial.trial_id}: {e}")
                continue
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x.overall_score, reverse=True)
        return results

def create_sample_patient_data() -> PatientEMR:
    """Create sample patient EMR data for demonstration"""
    return PatientEMR(
        demographics={
            'age': 45,
            'gender': 'female',
            'race': 'caucasian'
        },
        clinical_data={
            'ecog_status': 1,
            'karnofsky_score': 80,
            'tumor_grade': 2,
            'tumor_stage': 'IIIA',
            'metastases': ['lung']
        },
        lab_results={
            'egfr_mutation': 'positive',
            'alk_rearrangement': 'negative',
            'liver_function': {'normal': True, 'alt': 25, 'ast': 22},
            'kidney_function': {'normal': True, 'creatinine': 0.8},
            'blood_counts': {'wbc': 6.5, 'hgb': 12.5, 'platelets': 250}
        },
        pathology_reports=[
            "Adenocarcinoma of the lung, moderately differentiated, EGFR mutation positive"
        ],
        radiology_reports=[
            "CT chest shows 3cm mass in right upper lobe, no brain metastases"
        ],
        medications=['metformin', 'aspirin'],
        comorbidities=['diabetes', 'hypertension']
    )

def create_sample_trial_requirements() -> TrialRequirements:
    """Create sample trial requirements for demonstration"""
    return TrialRequirements(
        trial_id="NCT12345678",
        trial_name="EGFR-Targeted Therapy for Lung Cancer",
        inclusion_criteria=[
            "Age 18-75 years",
            "ECOG performance status 0-1",
            "EGFR mutation positive",
            "No brain metastases"
        ],
        exclusion_criteria=[
            "Pregnant women",
            "Uncontrolled diabetes",
            "Recent chemotherapy within 4 weeks"
        ],
        required_indicators={
            'demographics': {
                'age_range': (18, 75),
                'gender': 'any'
            },
            'clinical': {
                'ecog_status': 1,
                'tumor_grade': 3,
                'no_brain_metastases': True
            },
            'biomarkers': {
                'egfr_mutation': 'positive',
                'alk_rearrangement': 'negative',
                'liver_function_normal': True
            },
            'exclusion_medications': ['warfarin', 'chemotherapy'],
            'exclusion_comorbidities': ['uncontrolled_diabetes', 'pregnancy']
        },
        disease_area="oncology"
    )

def demo_patient_matching():
    """Demonstrate patient-trial matching functionality"""
    print("=== Patient-Trial Matching Demo ===")
    
    # Create sample data
    patient = create_sample_patient_data()
    trial = create_sample_trial_requirements()
    
    # Initialize matcher
    matcher = PatientTrialMatcher()
    
    # Perform matching
    result = matcher.match_patient_to_trial(patient, trial)
    
    print(f"\nTrial: {result.trial_name}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Confidence Level: {result.confidence_level}")
    
    print(f"\nCategory Scores:")
    for category, score in result.category_scores.items():
        print(f"  {category.capitalize()}: {score:.2f}")
    
    print(f"\nMatched Indicators ({len(result.matched_indicators)}):")
    for indicator in result.matched_indicators:
        print(f"  ✓ {indicator}")
    
    print(f"\nMissing Indicators ({len(result.missing_indicators)}):")
    for indicator in result.missing_indicators:
        print(f"  ✗ {indicator}")
    
    print(f"\nConflicting Indicators ({len(result.conflicting_indicators)}):")
    for indicator in result.conflicting_indicators:
        print(f"  ⚠ {indicator}")
    
    print(f"\nReasoning: {result.reasoning}")
    
    return result

if __name__ == "__main__":
    demo_patient_matching() 