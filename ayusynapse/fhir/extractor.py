#!/usr/bin/env python3
"""
FHIR Extractor - Single file to extract clinical trial criteria from dataset
"""

import json
import re
from typing import List, Dict, Any
from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FHIRExtractor:
    """Extract clinical trial criteria from dataset"""
    
    def __init__(self):
        self.extracted_data = {
            'trials': [],
            'summary': {
                'total_trials': 0,
                'total_criteria': 0,
                'extraction_timestamp': None
            }
        }
    
    def read_criteria_dataset(self, file_path: str = 'criteria_dataset.docx') -> Dict:
        """Read and parse the criteria dataset"""
        try:
            logger.info(f"Reading criteria dataset from: {file_path}")
            doc = Document(file_path)
            
            # Extract all paragraphs
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text.strip())
            
            logger.info(f"Extracted {len(paragraphs)} paragraphs")
            return {'paragraphs': paragraphs}
            
        except Exception as e:
            logger.error(f"Error reading criteria dataset: {e}")
            return {'paragraphs': []}
    
    def extract_trial_criteria(self, raw_content: Dict) -> List[Dict]:
        """Extract trial criteria from raw content"""
        trials = []
        current_trial = None
        current_criteria = []
        
        for paragraph in raw_content.get('paragraphs', []):
            # Check if this is a new trial (starts with number and NCT)
            trial_match = re.match(r'(\d+)\.\s*(NCT\d+)\s*[–-]\s*(.+)', paragraph)
            
            if trial_match:
                # Save previous trial if exists
                if current_trial:
                    current_trial['criteria'] = current_criteria
                    trials.append(current_trial)
                
                # Start new trial
                trial_num = trial_match.group(1)
                nct_id = trial_match.group(2)
                title = trial_match.group(3).strip()
                
                current_trial = {
                    'trial_id': f"trial_{trial_num}",
                    'nct_id': nct_id,
                    'title': title,
                    'criteria': []
                }
                current_criteria = []
                
            elif current_trial and paragraph.strip():
                # Add criteria to current trial
                current_criteria.append({
                    'text': paragraph.strip(),
                    'type': self._classify_criteria_type(paragraph)
                })
        
        # Add the last trial
        if current_trial:
            current_trial['criteria'] = current_criteria
            trials.append(current_trial)
        
        logger.info(f"Extracted {len(trials)} trials")
        return trials
    
    def _classify_criteria_type(self, text: str) -> str:
        """Classify the type of criteria"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['inclusion criteria', 'inclusion']):
            return 'inclusion'
        elif any(keyword in text_lower for keyword in ['exclusion criteria', 'exclusion']):
            return 'exclusion'
        elif any(keyword in text_lower for keyword in ['ages eligible', 'age']):
            return 'demographic'
        elif any(keyword in text_lower for keyword in ['sexes eligible', 'sex', 'gender']):
            return 'demographic'
        else:
            return 'clinical'
    
    def extract_entities_from_criteria(self, criteria_text: str) -> List[Dict]:
        """Extract clinical entities from criteria text"""
        entities = []
        
        # Age extraction
        age_patterns = [
            r'(\d+)\s*(?:years?\s*old?|y\.?o\.?)',
            r'age\s*(?:of\s*)?(\d+)\s*(?:years?|y\.?)',
            r'(\d+)\s*years?\s*and\s*older',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in age_patterns:
            age_match = re.search(pattern, criteria_text, re.IGNORECASE)
            if age_match:
                entities.append({
                    'text': age_match.group(0),
                    'entity_type': 'AGE',
                    'value': int(age_match.group(1)),
                    'resource_type': 'Patient'
                })
                break
        
        # Gender extraction
        gender_match = re.search(r'\b(male|female|all)\b', criteria_text, re.IGNORECASE)
        if gender_match:
            gender_value = gender_match.group(1).lower()
            if gender_value == 'all':
                gender_value = 'unknown'
            entities.append({
                'text': gender_match.group(0),
                'entity_type': 'GENDER',
                'value': gender_value,
                'resource_type': 'Patient'
            })
        
        # Diagnosis extraction
        diagnosis_patterns = [
            r'\b(histologically\s+confirmed\s+)?(adenocarcinoma|carcinoma|cancer)\b',
            r'\b(breast|lung|colorectal|prostate|pancreatic|ovarian|biliary\s+tract|gastric|gastroesophageal)\s+cancer\b',
            r'\b(aml|all|cll|mds|multiple\s+myeloma|myelodysplastic\s+syndrome)\b',
            r'\b(metastatic|advanced|localized|unresectable)\s+(disease|tumor|cancer)\b',
            r'\b(relapsed|refractory)\s+(disease|tumor|cancer)\b',
            r'\b(solid\s+tumors?)\b'
        ]
        
        for pattern in diagnosis_patterns:
            for match in re.finditer(pattern, criteria_text, re.IGNORECASE):
                entities.append({
                    'text': match.group(0),
                    'entity_type': 'DIAGNOSIS',
                    'value': match.group(0),
                    'resource_type': 'Condition'
                })
        
        # ECOG extraction
        ecog_patterns = [
            r'\b(ecog|eastern\s+cooperative\s+oncology\s+group)\s*(?:performance\s+status\s*)?(\d+)\b',
            r'\bperformance\s+status\s*(\d+)\b',
            r'\becog\s*(\d+)\s*-\s*(\d+)\b'
        ]
        
        for pattern in ecog_patterns:
            ecog_match = re.search(pattern, criteria_text, re.IGNORECASE)
            if ecog_match:
                # Get the numeric group (group 2 for first pattern, group 1 for others)
                if pattern == r'\b(ecog|eastern\s+cooperative\s+oncology\s+group)\s*(?:performance\s+status\s*)?(\d+)\b':
                    ecog_score = int(ecog_match.group(2))
                else:
                    ecog_score = int(ecog_match.group(1))
                entities.append({
                    'text': ecog_match.group(0),
                    'entity_type': 'ECOG',
                    'value': ecog_score,
                    'resource_type': 'Observation'
                })
                break
        
        # Biomarker extraction
        biomarker_patterns = [
            r'\b(her2|egfr|alk|ros1|braf|kras|nras|p53|ki67)\s*(positive|negative)?\b',
            r'\b(estrogen\s+receptor|progesterone\s+receptor)\s*(positive|negative)?\b',
            r'\b(er|pr)\s*(positive|negative)\b',
            r'\b(her2|egfr|alk)\s*positive\s+status\b'
        ]
        
        for pattern in biomarker_patterns:
            for match in re.finditer(pattern, criteria_text, re.IGNORECASE):
                entities.append({
                    'text': match.group(0),
                    'entity_type': 'BIOMARKER',
                    'value': match.group(0),
                    'resource_type': 'Observation'
                })
        
        # Measurable disease extraction
        measurable_patterns = [
            r'\b(at\s+least\s+one\s+)?measurable\s+(lesion|disease|tumor)\b',
            r'\b(recist\s+v?1\.1)\b',
            r'\b(measurable\s+disease)\b'
        ]
        
        for pattern in measurable_patterns:
            measurable_match = re.search(pattern, criteria_text, re.IGNORECASE)
            if measurable_match:
                entities.append({
                    'text': measurable_match.group(0),
                    'entity_type': 'MEASURABLE_DISEASE',
                    'value': measurable_match.group(0),
                    'resource_type': 'Observation'
                })
                break
        
        # Life expectancy extraction
        life_expectancy_match = re.search(r'\b(life\s+expectancy)\s*≥?\s*(\d+)\s*(weeks?|months?|years?)\b', criteria_text, re.IGNORECASE)
        if life_expectancy_match:
            entities.append({
                'text': life_expectancy_match.group(0),
                'entity_type': 'LIFE_EXPECTANCY',
                'value': {
                    'value': int(life_expectancy_match.group(2)),
                    'unit': life_expectancy_match.group(3)
                },
                'resource_type': 'Observation'
            })
        
        # Exclusion criteria extraction
        exclusion_patterns = [
            r'\b(prior|previous)\s+(systemic\s+therapy|treatment)\s+for\s+(advanced|metastatic|unresectable)\s+disease\b',
            r'\b(cns\s+metastases|brain\s+metastases)\b',
            r'\b(pregnant|breastfeeding|pregnancy)\b',
            r'\b(significant\s+cardiovascular\s+disease|uncontrolled\s+infection)\b',
            r'\b(active\s+uncontrolled\s+infections?)\b'
        ]
        
        for pattern in exclusion_patterns:
            for match in re.finditer(pattern, criteria_text, re.IGNORECASE):
                entities.append({
                    'text': match.group(0),
                    'entity_type': 'EXCLUSION',
                    'value': match.group(0),
                    'resource_type': 'Condition'
                })
        
        return entities
    
    def process_dataset(self, file_path: str = 'criteria_dataset.docx') -> Dict:
        """Main method to process the entire dataset"""
        logger.info("Starting FHIR extraction process...")
        
        # Read raw content
        raw_content = self.read_criteria_dataset(file_path)
        
        # Extract trial criteria
        trials = self.extract_trial_criteria(raw_content)
        
        # Extract entities for each trial
        total_entities = 0
        for trial in trials:
            trial_entities = []
            for criteria in trial['criteria']:
                entities = self.extract_entities_from_criteria(criteria['text'])
                criteria['entities'] = entities
                trial_entities.extend(entities)
                total_entities += len(entities)
            
            trial['total_entities'] = len(trial_entities)
            trial['all_entities'] = trial_entities
        
        # Update summary
        self.extracted_data['trials'] = trials
        self.extracted_data['summary'] = {
            'total_trials': len(trials),
            'total_criteria': sum(len(trial['criteria']) for trial in trials),
            'total_entities': total_entities,
            'extraction_timestamp': None
        }
        
        logger.info(f"Extraction complete: {len(trials)} trials, {total_entities} entities")
        return self.extracted_data

def main():
    """Main function to run the extractor"""
    extractor = FHIRExtractor()
    extracted_data = extractor.process_dataset()
    
    # Save extracted data
    with open('extracted_criteria_data.json', 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Extracted {extracted_data['summary']['total_trials']} trials")
    print(f"✅ Found {extracted_data['summary']['total_entities']} entities")
    print("✅ Saved as: extracted_criteria_data.json")

if __name__ == "__main__":
    main()
