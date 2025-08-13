"""
Clinical Trial Data Collector
Collects and processes clinical trial data from public sources.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ClinicalTrialCollector:
    """Collects clinical trial data from various public sources."""
    
    def __init__(self):
        self.base_urls = {
            'clinicaltrials_gov': 'https://clinicaltrials.gov/api/query/study_fields',
            'who_ictrp': 'https://trialsearch.who.int/',
            'eudract': 'https://www.clinicaltrialsregister.eu/'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_trials_by_condition(self, condition: str, max_results: int = 100) -> List[Dict]:
        """
        Search for clinical trials by medical condition.
        
        Args:
            condition: Medical condition to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of trial dictionaries
        """
        trials = []
        
        # ClinicalTrials.gov API search
        params = {
            'expr': condition,
            'fields': 'NCTId,BriefTitle,Condition,InclusionCriteria,ExclusionCriteria,StudyType,Phase,Enrollment,LeadSponsorName,StartDate,CompletionDate',
            'min_rnk': 1,
            'max_rnk': max_results,
            'fmt': 'json'
        }
        
        try:
            response = self.session.get(self.base_urls['clinicaltrials_gov'], params=params)
            response.raise_for_status()
            
            data = response.json()
            if 'StudyFieldsResponse' in data:
                for study in data['StudyFieldsResponse']['StudyFields']:
                    trial = self._parse_trial_data(study)
                    if trial:
                        trials.append(trial)
                        
        except Exception as e:
            logger.error(f"Error fetching trials for condition {condition}: {e}")
        
        return trials
    
    def _parse_trial_data(self, study_data: Dict) -> Optional[Dict]:
        """Parse raw trial data into structured format."""
        try:
            # Extract NCT ID
            nct_id = study_data.get('NCTId', [''])[0] if study_data.get('NCTId') else ''
            
            # Extract title
            title = study_data.get('BriefTitle', [''])[0] if study_data.get('BriefTitle') else ''
            
            # Extract conditions
            conditions = study_data.get('Condition', [])
            
            # Extract inclusion criteria
            inclusion = study_data.get('InclusionCriteria', [''])[0] if study_data.get('InclusionCriteria') else ''
            
            # Extract exclusion criteria
            exclusion = study_data.get('ExclusionCriteria', [''])[0] if study_data.get('ExclusionCriteria') else ''
            
            # Extract other fields
            study_type = study_data.get('StudyType', [''])[0] if study_data.get('StudyType') else ''
            phase = study_data.get('Phase', [''])[0] if study_data.get('Phase') else ''
            enrollment = study_data.get('Enrollment', [''])[0] if study_data.get('Enrollment') else ''
            sponsor = study_data.get('LeadSponsorName', [''])[0] if study_data.get('LeadSponsorName') else ''
            
            return {
                'nct_id': nct_id,
                'title': title,
                'conditions': conditions,
                'inclusion_criteria': inclusion,
                'exclusion_criteria': exclusion,
                'study_type': study_type,
                'phase': phase,
                'enrollment': enrollment,
                'sponsor': sponsor,
                'collected_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing trial data: {e}")
            return None
    
    def collect_oncology_trials(self) -> List[Dict]:
        """Collect oncology-specific clinical trials."""
        oncology_conditions = [
            'breast cancer', 'lung cancer', 'colorectal cancer', 'prostate cancer',
            'pancreatic cancer', 'ovarian cancer', 'melanoma', 'leukemia',
            'lymphoma', 'multiple myeloma'
        ]
        
        all_trials = []
        for condition in oncology_conditions:
            logger.info(f"Collecting trials for condition: {condition}")
            trials = self.search_trials_by_condition(condition, max_results=50)
            all_trials.extend(trials)
            time.sleep(1)  # Rate limiting
        
        return all_trials
    
    def collect_neurology_trials(self) -> List[Dict]:
        """Collect neurology-specific clinical trials."""
        neurology_conditions = [
            'Alzheimer disease', 'Parkinson disease', 'multiple sclerosis',
            'epilepsy', 'stroke', 'migraine', 'dementia', 'amyotrophic lateral sclerosis'
        ]
        
        all_trials = []
        for condition in neurology_conditions:
            logger.info(f"Collecting trials for condition: {condition}")
            trials = self.search_trials_by_condition(condition, max_results=50)
            all_trials.extend(trials)
            time.sleep(1)  # Rate limiting
        
        return all_trials
    
    def save_trials_to_file(self, trials: List[Dict], filename: str):
        """Save collected trials to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(trials, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(trials)} trials to {filename}")
        except Exception as e:
            logger.error(f"Error saving trials to file: {e}")
    
    def load_trials_from_file(self, filename: str) -> List[Dict]:
        """Load trials from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                trials = json.load(f)
            logger.info(f"Loaded {len(trials)} trials from {filename}")
            return trials
        except Exception as e:
            logger.error(f"Error loading trials from file: {e}")
            return []


def main():
    """Main function to demonstrate trial collection."""
    collector = ClinicalTrialCollector()
    
    # Collect oncology trials
    print("Collecting oncology trials...")
    oncology_trials = collector.collect_oncology_trials()
    collector.save_trials_to_file(oncology_trials, 'data/raw/oncology_trials.json')
    
    # Collect neurology trials
    print("Collecting neurology trials...")
    neurology_trials = collector.collect_neurology_trials()
    collector.save_trials_to_file(neurology_trials, 'data/raw/neurology_trials.json')
    
    print(f"Collected {len(oncology_trials)} oncology trials and {len(neurology_trials)} neurology trials")


if __name__ == "__main__":
    main() 